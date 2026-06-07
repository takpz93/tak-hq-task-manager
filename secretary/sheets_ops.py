"""
動画制作スケジュール用 Google Sheets 読み込み & パーサ

スプレッドシート（1枚のシートに制作リスト・断片メモ・カレンダー・分析が
混在している）から「制作リスト本体」だけを抜き出し、扱いやすい
レコードのリストに変換する。

UI からは `load_video_records(spreadsheet_id)` を呼べばよい。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Optional

# ── 制作ワークフローのステージ（左ほど序盤、右ほど完了に近い）─────────
STAGE_ORDER = [
    "企画", "撮影", "共有", "台本", "アフレコ",
    "初稿", "FB", "修正", "完成", "提出", "投稿", "クローズ",
]
# 表記ゆれ → 正規化後ステージ
_STAGE_ALIASES = {
    "アフ": "アフレコ",
    "アフレコ": "アフレコ",
    "m提出": "提出",
    "c提出": "提出",
    "提出": "提出",
}

# 投稿（最終状態）列の値
STATUS_DONE = "済"
STATUS_KILLED = "ボツ"

# ヘッダ名 → 内部キー（表記ゆれ・余分な注記を吸収）
_HEADER_MAP = {
    "投稿": "status",
    "担当": "assignee",
    "クライアント": "client",
    "no.": "no",
    "no": "no",
    "投稿順": "order",
    "投稿日": "post_date",
    "タイプ": "type",
    "企画": "title",
    "待ち状態": "stage",
    "元素材": "source_url",
    "dl期限": "dl_deadline",
    "共有url": "share_url",
    "サムネ": "thumbnail",
    "動画dl用": "video_dl",
}


@dataclass
class VideoRecord:
    status: str = ""            # "済" / "ボツ" / "" (進行中)
    assignee: str = ""
    client: str = ""
    no: str = ""
    order: str = ""
    post_date: str = ""
    type: str = ""
    title: str = ""
    stage: str = ""            # 正規化済みステージ
    stage_raw: str = ""        # シート上の元表記
    source_url: str = ""
    dl_deadline: str = ""      # シート上の元表記
    share_url: str = ""
    thumbnail: str = ""
    video_dl: str = ""
    row: int = 0               # シート上の行番号（1始まり、参考用）
    deadline_date: Optional[date] = field(default=None)

    @property
    def is_done(self) -> bool:
        return self.status == STATUS_DONE

    @property
    def is_killed(self) -> bool:
        return self.status == STATUS_KILLED

    @property
    def is_active(self) -> bool:
        """進行中（完了でもボツでもない）案件か"""
        return not self.is_done and not self.is_killed

    @property
    def stage_index(self) -> int:
        try:
            return STAGE_ORDER.index(self.stage)
        except ValueError:
            return -1


# ── ステージ正規化 ────────────────────────────────────────────────
def normalize_stage(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    return _STAGE_ALIASES.get(s.lower(), s)


# ── DL期限のパース ────────────────────────────────────────────────
def parse_deadline(raw: str, *, default_year: int) -> Optional[date]:
    """ "1/27/2026" / "3/24" / "12/30/2025" 等をできる範囲で date に。

    年が省略されている場合は default_year を採用する。
    パースできない（URL やメモが入っている）場合は None。
    """
    s = (raw or "").strip()
    if not s:
        return None
    m = re.match(r"^\s*(\d{1,2})\s*[/／]\s*(\d{1,2})(?:\s*[/／]\s*(\d{2,4}))?\s*$", s)
    if not m:
        return None
    month, day = int(m.group(1)), int(m.group(2))
    year = m.group(3)
    if year:
        year = int(year)
        if year < 100:
            year += 2000
    else:
        year = default_year
    try:
        return date(year, month, day)
    except ValueError:
        return None


# ── ヘッダ行の検出と列マッピング ──────────────────────────────────
def _normalize_header(cell: str) -> str:
    """ヘッダ文字列を内部キーに。'サムネ(PSD含む)' → 'サムネ' 等の注記を除去。"""
    c = (cell or "").strip().lower()
    c = re.split(r"[（(]", c)[0].strip()  # 括弧以降の注記を落とす
    return _HEADER_MAP.get(c, "")


def _find_header(values: list[list[str]]) -> tuple[int, dict[str, int]]:
    """制作リスト本体のヘッダ行を探し、(行index, {内部キー: 列index}) を返す。"""
    for i, row in enumerate(values):
        mapping: dict[str, int] = {}
        for j, cell in enumerate(row):
            key = _normalize_header(str(cell))
            if key and key not in mapping:
                mapping[key] = j
        # 制作リストと判定できる最低条件
        if {"client", "title", "stage"} <= set(mapping):
            return i, mapping
    return -1, {}


# ── 本体パース ────────────────────────────────────────────────────
def parse_video_records(
    values: list[list[str]],
    *,
    default_year: int,
) -> list[VideoRecord]:
    """シートの2次元セル配列から制作リストのレコードを抽出する。

    1枚のシートに断片テーブルやカレンダーが混在していても、
    「クライアント列・企画列の両方が埋まっている行」だけを本体行とみなす。
    """
    header_i, cols = _find_header(values)
    if header_i < 0:
        return []

    def cell(row: list[str], key: str) -> str:
        idx = cols.get(key, -1)
        if idx < 0 or idx >= len(row):
            return ""
        return str(row[idx]).strip()

    records: list[VideoRecord] = []
    for i in range(header_i + 1, len(values)):
        row = values[i]
        if not row:
            continue
        client = cell(row, "client")
        title = cell(row, "title")
        # 本体行の条件：クライアントと企画がどちらも入っている
        if not client or not title:
            continue
        stage_raw = cell(row, "stage")
        deadline_raw = cell(row, "dl_deadline")
        rec = VideoRecord(
            status=cell(row, "status"),
            assignee=cell(row, "assignee"),
            client=client,
            no=cell(row, "no"),
            order=cell(row, "order"),
            post_date=cell(row, "post_date"),
            type=cell(row, "type"),
            title=title,
            stage=normalize_stage(stage_raw),
            stage_raw=stage_raw,
            source_url=cell(row, "source_url"),
            dl_deadline=deadline_raw,
            share_url=cell(row, "share_url"),
            thumbnail=cell(row, "thumbnail"),
            video_dl=cell(row, "video_dl"),
            row=i + 1,
            deadline_date=parse_deadline(deadline_raw, default_year=default_year),
        )
        records.append(rec)
    return records


# ── Google Sheets からの取得 ──────────────────────────────────────
def _service():
    from googleapiclient.discovery import build

    from secretary.auth import get_credentials

    return build("sheets", "v4", credentials=get_credentials(), cache_discovery=False)


def _first_sheet_title(service, spreadsheet_id: str) -> str:
    meta = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id, fields="sheets.properties.title"
    ).execute()
    sheets = meta.get("sheets", [])
    if not sheets:
        return ""
    return sheets[0]["properties"]["title"]


def fetch_grid(
    spreadsheet_id: str,
    *,
    sheet_title: Optional[str] = None,
    max_cols: str = "N",
    max_rows: int = 400,
) -> list[list[str]]:
    """制作リスト本体が収まる範囲のセル値を取得する。

    巨大なカレンダーグリッド（数百列）を避けるため、列は既定で A:N に絞る。
    """
    service = _service()
    if sheet_title is None:
        sheet_title = _first_sheet_title(service, spreadsheet_id)
    rng = f"'{sheet_title}'!A1:{max_cols}{max_rows}" if sheet_title else f"A1:{max_cols}{max_rows}"
    resp = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=rng,
        valueRenderOption="FORMATTED_VALUE",
    ).execute()
    return resp.get("values", [])


def load_video_records(
    spreadsheet_id: str,
    *,
    sheet_title: Optional[str] = None,
    default_year: Optional[int] = None,
) -> list[VideoRecord]:
    """スプレッドシートを読み込んで制作レコードのリストを返す（高レベルAPI）。"""
    if default_year is None:
        default_year = date.today().year
    values = fetch_grid(spreadsheet_id, sheet_title=sheet_title)
    return parse_video_records(values, default_year=default_year)


# ── 集計ヘルパ ────────────────────────────────────────────────────
def summarize(records: list[VideoRecord], *, today: Optional[date] = None) -> dict[str, Any]:
    """ダッシュボード用の集計値をまとめて返す。"""
    if today is None:
        today = date.today()
    active = [r for r in records if r.is_active]
    overdue = [r for r in active if r.deadline_date and r.deadline_date < today]
    week_later = today + timedelta(days=7)
    due_soon = [
        r for r in active
        if r.deadline_date and today <= r.deadline_date <= week_later
    ]
    by_stage: dict[str, int] = {}
    for r in active:
        key = r.stage or "（未設定）"
        by_stage[key] = by_stage.get(key, 0) + 1
    return {
        "total": len(records),
        "active": active,
        "done": [r for r in records if r.is_done],
        "killed": [r for r in records if r.is_killed],
        "overdue": overdue,
        "due_soon": due_soon,
        "by_stage": by_stage,
    }
