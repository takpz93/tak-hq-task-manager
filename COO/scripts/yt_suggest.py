#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube検索サジェスト（オートコンプリート）取得
  シード語そのまま ＋ シード語＋あ〜わ行の各1文字 の候補を取得し、重複を除いて md に出力する。
  ※ suggestqueries.google.com へ直接アクセスするため、手元のPC（通常のネット環境）で実行する。

使い方:
  pip install requests
  python3 COO/scripts/yt_suggest.py                       # 既定のシード語（歯の神経治療回）
  python3 COO/scripts/yt_suggest.py --seeds "根管治療" "抜髄" --out out.md
"""
import argparse, json, os, re, sys, time
from datetime import date
import requests

DEFAULT_SEEDS = ["歯の神経", "歯の神経を抜く", "根管治療", "虫歯 進行", "虫歯 段階", "歯の痛み 消えた", "神経を抜いた歯", "虫歯 放置"]
KANA = list("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわ")
URL = "https://suggestqueries.google.com/complete/search"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
           "Accept-Language": "ja,en;q=0.8"}

def fetch(q, hl="ja", gl="jp", retries=3):
    """client=firefox は素のJSON ["q", ["候補", ...]] を返す"""
    for i in range(retries):
        try:
            r = requests.get(URL, params={"client": "firefox", "ds": "yt", "hl": hl, "gl": gl, "q": q}, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                r.encoding = "utf-8"
                data = json.loads(r.text)
                return [s if isinstance(s, str) else s[0] for s in data[1]]
        except Exception as e:
            err = e
        time.sleep(1.0 * (i + 1))
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", default=DEFAULT_SEEDS)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "output", f"youtube_suggest_{date.today():%Y%m%d}.md"))
    ap.add_argument("--sleep", type=float, default=0.3, help="リクエスト間隔（秒）")
    a = ap.parse_args()

    rows = []          # (seed, query, rank, suggestion)
    failed = []
    for seed in a.seeds:
        queries = [seed] + [f"{seed} {k}" for k in KANA]
        for q in queries:
            sug = fetch(q)
            if sug is None: failed.append(q); continue
            for rank, s in enumerate(sug, 1): rows.append((seed, q, rank, s))
            time.sleep(a.sleep)
        print(f"[{seed}] done", file=sys.stderr, flush=True)

    # 重複除去（シード語ごと。同じ候補が複数クエリで出た場合は最も良い順位・最初のクエリを残す）
    L = [f"# YouTube検索サジェスト一覧（歯の神経治療回）\n\n取得日: {date.today().isoformat()}　取得元: YouTube オートコンプリート（suggestqueries.google.com, hl=ja/gl=jp）\n\n"]
    L.append("各シード語について「そのまま」と「シード語＋あ〜わ行の1文字（45通り）」の候補を取得し、シード語ごとに重複を除去。順位は各クエリでの表示順（1が最上位）。\n\n")
    total = 0
    for seed in a.seeds:
        best = {}
        for s_, q, rank, sug in rows:
            if s_ != seed: continue
            if sug not in best or rank < best[sug][0]: best[sug] = (rank, q)
        items = sorted(best.items(), key=lambda kv: (kv[1][1] != seed, kv[1][1], kv[1][0]))
        total += len(items)
        L.append(f"## {seed}（{len(items)}語）\n\n| # | サジェスト候補 | 表示順位 | 取得クエリ |\n|---|---|---|---|\n")
        for i, (sug, (rank, q)) in enumerate(items, 1): L.append(f"| {i} | {sug} | {rank} | {q} |\n")
        L.append("\n")
    allsug = sorted(set(r[3] for r in rows))
    L.append(f"## 全シード語横断・重複除去（{len(allsug)}語、五十音順）\n\n" + "、".join(allsug) + "\n")
    if failed: L.append(f"\n---\n取得失敗クエリ（{len(failed)}件）: " + "、".join(failed) + "\n")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("".join(L))
    json.dump(rows, open(re.sub(r"\.md$", ".json", a.out), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"[done] {total} rows -> {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
