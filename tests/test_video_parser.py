"""
sheets_ops のパーサのテスト。

実スプレッドシートの構造（制作リスト本体 + 下部の断片テーブル）を模した
2次元配列を使い、本体だけが正しく抽出されることを確認する。

    python tests/test_video_parser.py     # 単体実行
    pytest tests/                          # pytest でも可
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from secretary.sheets_ops import (  # noqa: E402
    normalize_stage,
    parse_deadline,
    parse_video_records,
    summarize,
)

# 実シートを模したグリッド（ヘッダ + 本体 + 断片テーブル）
HEADER = ["投稿", "担当", "クライアント", "No.", "投稿順", "投稿日", "タイプ",
          "企画", "待ち状態", "元素材", "DL期限", "共有URL", "サムネ(PSD含む)", "動画DL用"]

GRID = [
    ["動画制作スケジュール"],            # 余分な見出し行（ヘッダではない）
    HEADER,
    # --- 本体行 ---
    ["", "吉田さん", "BPP", "32", "", "", "", "ジムニー", "初稿", "", "6/10", "", "", ""],
    ["", "YH", "ワンポリ", "5", "5", "", "", "新作レビュー", "撮影", "", "6/3", "", "", ""],
    ["", "三浦", "ゆぴ優", "25", "24", "", "", "渋谷ロケ", "アフ", "url", "5/30", "", "", ""],
    ["済", "松村さん", "KINS", "1", "1", "9/6", "", "腸活", "クローズ", "url", "1/18/2026", "", "", ""],
    ["ボツ", "", "BPP", "24", "", "", "ショート", "VOXY", "撮影", "", "", "", "", ""],
    ["", "MEK", "iStory", "10", "10", "", "ショート", "新企画", "M提出", "", "", "", "", ""],
    [],                                  # 空行
    # --- 下部の断片テーブル（本体として拾ってはいけない）---
    ["FB", "", "修正"],
    ["完成", "提出", ""],
    ["撮影", "共有"],
    ["NO_HEADER", "NO_HEADER"],
    ["ルームツアー", "クローズ", "https://example.com/x"],
]


def test_normalize_stage():
    assert normalize_stage("アフ") == "アフレコ"
    assert normalize_stage("M提出") == "提出"
    assert normalize_stage("C提出") == "提出"
    assert normalize_stage("初稿") == "初稿"
    assert normalize_stage("") == ""


def test_parse_deadline():
    assert parse_deadline("1/27/2026", default_year=2026) == date(2026, 1, 27)
    assert parse_deadline("12/30/2025", default_year=2026) == date(2025, 12, 30)
    assert parse_deadline("3/24", default_year=2026) == date(2026, 3, 24)
    assert parse_deadline("", default_year=2026) is None
    # URL やメモはパース不可
    assert parse_deadline("https://example.com", default_year=2026) is None
    assert parse_deadline("大谷さん", default_year=2026) is None


def test_parse_records_extracts_body_only():
    recs = parse_video_records(GRID, default_year=2026)
    titles = [r.title for r in recs]
    # 本体6行（ジムニー/新作/渋谷/腸活/VOXY/新企画）だけが抽出される
    assert titles == ["ジムニー", "新作レビュー", "渋谷ロケ", "腸活", "VOXY", "新企画"]
    # 断片テーブル由来のものは混ざっていない
    assert "ルームツアー" not in titles
    assert "FB" not in titles


def test_status_flags_and_stage_normalization():
    recs = parse_video_records(GRID, default_year=2026)
    by_title = {r.title: r for r in recs}
    assert by_title["腸活"].is_done
    assert by_title["VOXY"].is_killed
    assert by_title["ジムニー"].is_active
    assert by_title["渋谷ロケ"].stage == "アフレコ"   # "アフ" が正規化される
    assert by_title["新企画"].stage == "提出"          # "M提出" が正規化される
    assert by_title["ジムニー"].deadline_date == date(2026, 6, 10)


def test_summarize_counts():
    recs = parse_video_records(GRID, default_year=2026)
    s = summarize(recs, today=date(2026, 6, 7))
    # active = ジムニー/新作レビュー/渋谷ロケ/新企画 の4件
    assert len(s["active"]) == 4
    assert len(s["done"]) == 1
    assert len(s["killed"]) == 1
    # 渋谷ロケ(5/30)・新作レビュー(6/3) は期限切れ
    overdue_titles = {r.title for r in s["overdue"]}
    assert overdue_titles == {"渋谷ロケ", "新作レビュー"}
    # ジムニー(6/10) は今週締切
    assert {r.title for r in s["due_soon"]} == {"ジムニー"}


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run() else 0)
