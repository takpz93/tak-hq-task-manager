"""note.com 予約投稿の自動化。

note には公開 API がないため、ログイン済みセッション Cookie を使った
ブラウザ自動操作（Playwright）で下書き作成 → サムネ設定 → マガジン追加 →
予約公開までを行う。

構成の方針:
  * 設定の読み込み・検証（PostConfig）は Playwright 非依存で単体テスト可能。
    サムネ未設定や誘導URL未差し込みは「予約せず停止」する（発注書の⚠️ルール）。
  * ブラウザ操作（NoteBrowser）は fragile な DOM セレクタを一箇所に隔離し、
    各ステップをログ出力する。note の DOM 変更時はここだけ直せばよい。

Cookie の渡し方（いずれか）:
  * 環境変数 NOTE_COOKIES … Playwright storage_state 形式の JSON 文字列
  * ファイル NOTE_COOKIES_FILE（既定: リポジトリ直下 note_cookies.json）
  取得は `secretary note-login` で対話的に行える（手動ログイン→Cookie保存）。
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

NOTE_BASE = "https://note.com"
_LINK_TOKEN_RE = re.compile(r"\{\{link:([A-Za-z0-9_]+)\}\}")
_PLACEHOLDER_URLS = {"", "http://", "https://", "[記事URL]", "TODO", "xxx"}


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def cookies_file() -> Path:
    return Path(
        os.environ.get("NOTE_COOKIES_FILE", repo_root() / "note_cookies.json")
    )


# --------------------------------------------------------------------------- #
# 設定モデルと検証（Playwright 非依存）
# --------------------------------------------------------------------------- #
@dataclass
class LinkRef:
    key: str
    url: str


@dataclass
class XAnnouncement:
    post_at: datetime | None
    text: str


@dataclass
class PostConfig:
    title: str
    body: str  # {{link:...}} トークンを含む生 Markdown
    hashtags: list[str]
    magazine: str | None
    thumbnail: Path | None
    publish_at: datetime | None
    links: dict[str, LinkRef] = field(default_factory=dict)
    x_announcement: XAnnouncement | None = None
    source_path: Path | None = None

    # ---- 読み込み ------------------------------------------------------- #
    @classmethod
    def load(cls, config_path: str | Path) -> "PostConfig":
        path = Path(config_path).resolve()
        raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        base = path.parent

        body_file = raw.get("body_file")
        if body_file:
            body = (base / body_file).read_text(encoding="utf-8").rstrip("\n")
        else:
            body = raw.get("body", "")

        thumb = raw.get("thumbnail")
        thumbnail = (repo_root() / thumb) if thumb else None

        links: dict[str, LinkRef] = {}
        for key, spec in (raw.get("links") or {}).items():
            url = (spec or {}).get("url", "") if isinstance(spec, dict) else str(spec)
            links[key] = LinkRef(key=key, url=(url or "").strip())

        xa = None
        if raw.get("x_announcement"):
            xr = raw["x_announcement"]
            xa = XAnnouncement(
                post_at=_parse_dt(xr.get("post_at")),
                text=(xr.get("text") or "").rstrip("\n"),
            )

        return cls(
            title=raw.get("title", "").strip(),
            body=body,
            hashtags=[str(t).lstrip("#").strip() for t in (raw.get("hashtags") or [])],
            magazine=(raw.get("magazine") or None),
            thumbnail=thumbnail,
            publish_at=_parse_dt(raw.get("publish_at")),
            links=links,
            x_announcement=xa,
            source_path=path,
        )

    # ---- 検証 ----------------------------------------------------------- #
    def link_tokens(self) -> list[str]:
        """本文に現れる {{link:key}} のキー一覧（重複排除・出現順）。"""
        seen: list[str] = []
        for m in _LINK_TOKEN_RE.finditer(self.body):
            if m.group(1) not in seen:
                seen.append(m.group(1))
        return seen

    def validate(self) -> list[str]:
        """予約を止めるべき致命的問題を列挙。空なら実行OK。"""
        errors: list[str] = []

        if not self.title:
            errors.append("title が空です。")
        if not self.body.strip():
            errors.append("本文が空です。")

        # サムネ必須（発注書の⚠️ルール: 未設定なら予約しない）
        if self.thumbnail is None:
            errors.append("サムネ画像が未設定です（thumbnail）。設定するまで予約しません。")
        elif not self.thumbnail.is_file():
            errors.append(f"サムネ画像が見つかりません: {self.thumbnail}")

        # 本文の誘導リンク: トークンに対応する URL が実在するか
        for key in self.link_tokens():
            ref = self.links.get(key)
            if ref is None:
                errors.append(f"本文の {{{{link:{key}}}}} に対応する links.{key} がありません。")
            elif ref.url in _PLACEHOLDER_URLS or not ref.url.startswith("http"):
                errors.append(
                    f"誘導リンク links.{key} の url が未差し込みです（現在: {ref.url!r}）。"
                    " ⚠️ note誘導URLを入れるまで予約しません。"
                )

        # publish_at
        if self.publish_at is None:
            errors.append("publish_at（予約日時）が未設定です。")

        return errors

    def rendered_body_plain(self) -> str:
        """トークンをアンカー文言のみに戻したプレーン本文（プレビュー用）。"""
        return _LINK_TOKEN_RE.sub("", self.body)


def _parse_dt(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    from dateutil import parser as date_parser

    return date_parser.parse(str(value))


# --------------------------------------------------------------------------- #
# 本文の段落分解（editor へ流し込むための中間表現）
# --------------------------------------------------------------------------- #
@dataclass
class Segment:
    text: str
    url: str | None = None  # None なら通常テキスト、非Noneならリンク


def body_to_paragraphs(cfg: PostConfig) -> list[list[Segment]]:
    """本文を段落（空行区切り）→ セグメント列へ分解する。

    各段落は Segment のリスト。{{link:key}} は links の URL を持つリンク
    セグメントに、それ以外は通常テキストセグメントになる。
    """
    url_by_key = {k: v.url for k, v in cfg.links.items()}
    paragraphs: list[list[Segment]] = []
    for block in cfg.body.split("\n\n"):
        block = block.strip("\n")
        if not block:
            continue
        segments: list[Segment] = []
        pos = 0
        for m in _LINK_TOKEN_RE.finditer(block):
            if m.start() > pos:
                segments.append(Segment(block[pos:m.start()]))
            key = m.group(1)
            segments.append(Segment(_anchor_before(block, m.start()), url=url_by_key.get(key)))
            pos = m.end()
        if pos < len(block):
            segments.append(Segment(block[pos:]))
        paragraphs.append([s for s in segments if s.text])
    return paragraphs


def _anchor_before(block: str, token_start: int) -> str:
    """Markdown リンク `[anchor]({{link:...}})` のアンカー部を取り出す。"""
    head = block[:token_start]
    m = re.search(r"\[([^\]]+)\]\(\s*$", head)
    return m.group(1) if m else ""


# --------------------------------------------------------------------------- #
# ブラウザ操作（Playwright）
# --------------------------------------------------------------------------- #
class NoteError(RuntimeError):
    pass


def _load_storage_state() -> dict:
    env = os.environ.get("NOTE_COOKIES")
    if env:
        return json.loads(env)
    path = cookies_file()
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    raise NoteError(
        "note のログイン情報が見つかりません。"
        " `secretary note-login` でログインするか、NOTE_COOKIES を設定してください。"
    )


def login_and_save(headless: bool = False) -> Path:
    """手動ログイン用。ブラウザを開き、ログイン完了後に Cookie を保存する。"""
    from playwright.sync_api import sync_playwright

    dest = cookies_file()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(f"{NOTE_BASE}/login")
        print("ブラウザで note にログインしてください。完了したら Enter を押します...")
        input()
        ctx.storage_state(path=str(dest))
        browser.close()
    print(f"Cookie を保存しました: {dest}")
    return dest


class NoteBrowser:
    """note の下書き作成〜予約公開を行う薄いラッパ。

    DOM セレクタは note の変更で壊れうる。壊れたらこのクラス内の
    セレクタ定数だけを直せばよいよう、外に出している。
    """

    # --- DOM セレクタ（note 変更時はここを更新） ---
    SEL_NEW_TEXT = 'a[href="/notes/new"]'
    SEL_TITLE = 'textarea[placeholder*="タイトル"]'
    SEL_BODY = 'div[contenteditable="true"]'
    SEL_PUBLISH_OPEN = 'button:has-text("公開に進む")'
    SEL_HASHTAG_INPUT = 'input[placeholder*="ハッシュタグ"]'
    SEL_RESERVE_TOGGLE = 'text=予約投稿'
    SEL_THUMB_INPUT = 'input[type="file"]'

    def __init__(self, headless: bool = True, slow_mo: int = 0):
        self.headless = headless
        self.slow_mo = slow_mo

    def schedule(self, cfg: PostConfig, dry_run: bool = False) -> dict:
        errors = cfg.validate()
        if errors:
            raise NoteError("設定エラーのため予約を中止しました:\n  - " + "\n  - ".join(errors))
        if dry_run:
            return {"status": "validated", "dry_run": True}

        from playwright.sync_api import sync_playwright

        storage = _load_storage_state()
        result: dict = {}
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
            ctx = browser.new_context(storage_state=storage)
            page = ctx.new_page()
            try:
                self._open_new_editor(page)
                self._fill_title(page, cfg.title)
                self._fill_body(page, cfg)
                self._upload_thumbnail(page, cfg)
                self._open_publish_panel(page)
                self._fill_hashtags(page, cfg.hashtags)
                self._add_to_magazine(page, cfg.magazine)
                self._set_schedule(page, cfg.publish_at)
                url = self._confirm_reserve(page)
                result = {"status": "scheduled", "url": url,
                          "publish_at": cfg.publish_at.isoformat() if cfg.publish_at else None}
            finally:
                browser.close()
        return result

    # ---- 各ステップ（全て log 付き） ---- #
    def _open_new_editor(self, page) -> None:
        _log("新規テキストエディタを開く")
        page.goto(f"{NOTE_BASE}/notes/new")
        page.wait_for_selector(self.SEL_TITLE, timeout=30000)

    def _fill_title(self, page, title: str) -> None:
        _log(f"タイトル入力: {title[:24]}…")
        page.fill(self.SEL_TITLE, title)

    def _fill_body(self, page, cfg: PostConfig) -> None:
        _log("本文を流し込み")
        editor = page.query_selector(self.SEL_BODY)
        if editor is None:
            raise NoteError("本文エディタが見つかりません（SEL_BODY 要確認）。")
        editor.click()
        paragraphs = body_to_paragraphs(cfg)
        for i, segs in enumerate(paragraphs):
            if i > 0:
                page.keyboard.press("Enter")
            for seg in segs:
                if seg.url:
                    self._type_link(page, seg.text, seg.url)
                else:
                    page.keyboard.type(seg.text)

    def _type_link(self, page, text: str, url: str) -> None:
        """リンク文字を入力し、選択して note のリンク UI で URL を付与する。"""
        _log(f"リンク挿入: {text} -> {url}")
        start = None
        # 現在位置から text を入力し、直後に text 長ぶん選択してリンク化
        page.keyboard.type(text)
        for _ in range(len(text)):
            page.keyboard.press("Shift+ArrowLeft")
        # note のツールバーのリンクボタン。DOM 変更時は要調整。
        link_btn = page.query_selector('button[aria-label*="リンク"]')
        if link_btn:
            link_btn.click()
            page.keyboard.type(url)
            page.keyboard.press("Enter")
        else:
            # フォールバック: リンク化できない場合は選択解除して素通し
            page.keyboard.press("ArrowRight")
            _log("  ⚠️ リンクボタン未検出。プレーンテキストのまま継続。")

    def _upload_thumbnail(self, page, cfg: PostConfig) -> None:
        if not cfg.thumbnail:
            raise NoteError("サムネ未設定（ここに来る前に validate で止まるはず）。")
        _log(f"サムネ設定: {cfg.thumbnail.name}")
        file_input = page.query_selector(self.SEL_THUMB_INPUT)
        if file_input is None:
            raise NoteError("サムネのファイル入力が見つかりません（SEL_THUMB_INPUT 要確認）。")
        file_input.set_input_files(str(cfg.thumbnail))
        page.wait_for_timeout(1500)

    def _open_publish_panel(self, page) -> None:
        _log("公開設定パネルを開く")
        page.click(self.SEL_PUBLISH_OPEN)
        page.wait_for_timeout(1000)

    def _fill_hashtags(self, page, tags: list[str]) -> None:
        if not tags:
            return
        _log(f"ハッシュタグ {len(tags)} 件を入力")
        box = page.query_selector(self.SEL_HASHTAG_INPUT)
        if box is None:
            _log("  ⚠️ ハッシュタグ入力欄未検出。スキップ。")
            return
        for tag in tags:
            box.click()
            page.keyboard.type(tag)
            page.keyboard.press("Enter")

    def _add_to_magazine(self, page, magazine: str | None) -> None:
        if not magazine:
            return
        _log(f"マガジンに追加: {magazine}")
        # マガジン選択 UI を開いて名前一致でチェック。DOM 変更時は要調整。
        opener = page.query_selector('button:has-text("マガジン")')
        if opener is None:
            raise NoteError(f'マガジン追加 UI が見つかりません（"{magazine}"）。')
        opener.click()
        page.wait_for_timeout(500)
        item = page.query_selector(f'label:has-text("{magazine}")')
        if item is None:
            raise NoteError(f'マガジン "{magazine}" が一覧に見つかりません。名称を確認してください。')
        item.click()

    def _set_schedule(self, page, publish_at: datetime | None) -> None:
        if publish_at is None:
            raise NoteError("予約日時が未設定です。")
        _log(f"予約日時を設定: {publish_at.isoformat()}")
        toggle = page.query_selector(self.SEL_RESERVE_TOGGLE)
        if toggle is None:
            raise NoteError("予約投稿トグルが見つかりません（SEL_RESERVE_TOGGLE 要確認）。")
        toggle.click()
        page.wait_for_timeout(500)
        # 日付・時刻入力。note の UI に合わせて調整が必要。
        date_input = page.query_selector('input[type="date"]')
        time_input = page.query_selector('input[type="time"]')
        if date_input:
            date_input.fill(publish_at.strftime("%Y-%m-%d"))
        if time_input:
            time_input.fill(publish_at.strftime("%H:%M"))
        if not (date_input and time_input):
            _log("  ⚠️ 日付/時刻入力欄が見つかりません。UI を確認してください。")

    def _confirm_reserve(self, page) -> str | None:
        _log("予約を確定")
        btn = page.query_selector('button:has-text("予約投稿する")') or \
            page.query_selector('button:has-text("投稿する")')
        if btn is None:
            raise NoteError("予約確定ボタンが見つかりません。")
        btn.click()
        page.wait_for_timeout(2000)
        return page.url


def _log(msg: str) -> None:
    print(f"[note] {msg}")
