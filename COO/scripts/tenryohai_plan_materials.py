#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天領盃 次回撮影の企画精査 材料: 1) 自ch全動画 CSV 2) 候補テーマのかぶり判定 3) 日本酒ジャンルで直近1年に伸びた動画 TOP20
使い方: python3 COO/scripts/tenryohai_plan_materials.py --own-csv A.csv --genre-json G.json --out-dir clients/天領盃/output --tag 20261027
"""
import argparse, csv, json, os, re, sys, unicodedata
from datetime import date

OWN_ID, OWN_HANDLE = "UCx8tnZhehtNYsHBHpeHqHOg", "senichi_kato_tenryohai"
MIN_SUBS = 1000
# 候補テーマ → タイトル判定の正規表現（NFKC 正規化後、大文字小文字無視）
CANDIDATES = [
    ("甘口ランキング", r"甘口|甘旨|甘酸", "甘口・甘旨・甘酸 を含む"),
    ("辛口ランキング", r"辛口|ドライ|キレ", "辛口・ドライ・キレ を含む"),
    ("生産量ランキング", r"生産量|出荷|石高|蔵の数|蔵数", "生産量・出荷・石高・蔵数 を含む"),
    ("燗", r"燗", "燗（熱燗・ぬる燗・燗酒）を含む"),
    ("保存NG", r"保存|保管|冷蔵|劣化|NG|やってはいけない|ダメ|開栓|賞味", "保存・保管・冷蔵・劣化・NG・やってはいけない・ダメ・開栓・賞味 を含む"),
    ("東京の居酒屋", r"東京|居酒屋|角打ち|飲める店|酒場", "東京・居酒屋・角打ち・飲める店・酒場 を含む"),
    ("値段の仕組み", r"値段|価格|円|高い|安い|コスパ|仕組み|原価|物価|高騰|利益", "値段・価格・円・高い・安い・コスパ・仕組み・原価・物価・高騰・利益 を含む"),
    ("総まとめ", r"総まとめ|まとめ|総集編|年間|振り返り|ベスト|今年|年版|年の", "総まとめ・まとめ・総集編・年間・振り返り・ベスト・今年・◯年版 を含む"),
    ("（参考）総まとめの対象: 地方別ランキング回", r"ランキング.*(編|地方|全国|関東|関西|東北|中部|四国|九州|中国|新潟)|(編|地方|全国|関東|関西|東北|中部|四国|九州|中国|新潟).*ランキング", "ランキング と 地方名・◯編・全国 を同時に含む（日本一周シリーズの回）"),
]

def norm(s): return unicodedata.normalize("NFKC", s or "")
def clean(x): return re.sub(r"\s+", " ", x or "").replace("|", "｜").strip()
def n(x): return f"{x:,}" if isinstance(x, int) else ("" if x is None else str(x))
def subs_s(x): return "" if x is None else (f"{x/10000:.1f}万人" if x >= 10000 else f"{x:,}人")
def scale(s): return "大規模" if s >= 100000 else ("中規模" if s >= 10000 else "小規模")
def rs(r): return f"{r['ratio']:.2f}" if r.get("ratio") is not None else "—"
def dur(r): return f"{r['durationSec']//60}:{r['durationSec']%60:02d}" if r.get("durationSec") else ""
def is_own(r): return r.get("channelId") == OWN_ID or OWN_HANDLE in (r.get("handle") or "") or OWN_HANDLE in (r.get("channelUrl") or "")

def load_own(path):
    rows = []
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        m = re.search(r"v=([\w-]+)", r["動画URL"])
        rows.append({"kind": r["区分"], "publishDate": r["公開日"], "title": r["タイトル"], "videoId": m.group(1) if m else "", "url": r["動画URL"],
                     "views": int(r["再生数"]) if r["再生数"].isdigit() else None, "likes": int(r["高評価数"]) if r["高評価数"].isdigit() else None,
                     "comments": int(r["コメント数"]) if r["コメント数"].isdigit() else None, "durationSec": int(r["動画尺(秒)"]) if r["動画尺(秒)"].isdigit() else None,
                     "ratio": float(r["対平均倍率(直近1年長尺)"]) if r["対平均倍率(直近1年長尺)"] else None})
    rows.sort(key=lambda r: r["publishDate"] or "", reverse=True)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--own-csv", required=True); ap.add_argument("--genre-json", required=True); ap.add_argument("--genre-config")
    ap.add_argument("--out-dir", default="clients/天領盃/output"); ap.add_argument("--tag", default=date.today().strftime("%Y%m%d"))
    ap.add_argument("--since", default=None, help="直近1年の起点（既定: 今日-365日）")
    a = ap.parse_args(); today = date.today(); os.makedirs(a.out_dir, exist_ok=True)
    since = a.since or (date.fromordinal(today.toordinal() - 365)).isoformat()
    own = load_own(a.own_csv)
    # ---- 1) 全件 CSV ----
    p1 = os.path.join(a.out_dir, f"自ch全動画一覧_{a.tag}.csv")
    with open(p1, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["公開日", "タイトル", "動画ID", "URL", "再生回数", "高評価", "コメント", "尺(秒)", "区分", "対平均倍率(直近1年長尺)"])
        for r in own: w.writerow([r["publishDate"], r["title"], r["videoId"], r["url"], r["views"], r["likes"], r["comments"], r["durationSec"], r["kind"], f"{r['ratio']:.2f}" if r["ratio"] is not None else ""])
    longs_1y = [r for r in own if r["kind"] == "長尺" and r["publishDate"] >= since and r["views"]]
    avg_1y = sum(r["views"] for r in longs_1y) / len(longs_1y) if longs_1y else 0
    # ---- 2) かぶり判定 ----
    overlap = []
    for name, rx, desc in CANDIDATES:
        hits = [r for r in own if re.search(rx, norm(r["title"]), re.I)]
        overlap.append({"candidate": name, "rule": desc, "regex": rx, "count": len(hits), "count_1y": sum(1 for r in hits if r["publishDate"] >= since),
                        "latest": max((r["publishDate"] for r in hits), default=None),
                        "max_views": max((r["views"] or 0 for r in hits), default=None), "hits": hits})
    # ---- 3) ジャンル横断 TOP20 ----
    g = json.load(open(a.genre_json, encoding="utf-8"))
    pool = [r for r in g["final"] if r["ageDays"] <= 365 and not is_own(r)]
    small = [r for r in pool if r["subs"] < MIN_SUBS]
    pool = sorted([r for r in pool if r["subs"] >= MIN_SUBS], key=lambda r: -r["ratio"])
    top20 = pool[:20]
    p3 = os.path.join(a.out_dir, f"ジャンル伸び動画_{a.tag}.csv")
    with open(p3, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["順位", "チャンネル名", "タイトル", "再生回数", "登録者数", "倍率", "公開日", "URL", "尺(秒)", "ヒット検索語"])
        for i, r in enumerate(pool, 1): w.writerow([i, r["channel"], r["title"], r["viewCount"], r["subs"], f"{r['ratio']:.2f}", r["publishDate"], r["url"], r["durationSec_s"], r.get("keywordsHit", "")])
    # ---- md ----
    L = [f"# 天領盃 次回撮影の企画精査 材料（{today.isoformat()} 取得）\n\n対象: 加登仙一の日本酒大学（{OWN_ID}）　データ源: YouTube InnerTube（browse / next / search。Data API と同じ公開値）\n\n"]
    L.append(f"## 1. 公開済み動画 全件（{len(own)}本）\n\nCSV: `{os.path.basename(p1)}`（公開日・タイトル・動画ID・URL・再生回数・高評価・コメント・尺・区分・対平均倍率）\n\n")
    L.append(f"- 直近1年（{since} 以降）の長尺 {len(longs_1y)}本、平均再生 {avg_1y:,.0f}回。対平均倍率 = 再生回数 ÷ この平均\n\n")
    L.append("| 公開日 | タイトル | 再生回数 | 対平均倍率 | 尺 |\n|---|---|---|---|---|\n")
    for r in own: L.append(f"| {r['publishDate']} | {clean(r['title'])} | {n(r['views'])} | {rs(r)} | {dur(r)} |\n")
    L.append("\n## 2. 候補テーマと過去動画のかぶり判定\n\nタイトルの語で機械判定（判定語は各行に明記）。「冬の日本酒5選」は確定のため判定対象外。\n\n| 候補 | 該当本数（うち直近1年） | 最新の公開日 | 該当の最大再生 | 判定語 |\n|---|---|---|---|---|\n")
    for o in overlap: L.append(f"| {o['candidate']} | {o['count']}（{o['count_1y']}） | {o['latest'] or '—'} | {n(o['max_views']) if o['max_views'] else '—'} | {o['rule']} |\n")
    for o in overlap:
        L.append(f"\n### {o['candidate']}（{o['count']}本）\n\n")
        if not o["hits"]: L.append("該当なし\n"); continue
        L.append("| 公開日 | タイトル | 再生回数 | 対平均倍率 |\n|---|---|---|---|\n")
        for r in sorted(o["hits"], key=lambda r: r["publishDate"], reverse=True): L.append(f"| {r['publishDate']} | {clean(r['title'])} | {n(r['views'])} | {rs(r)} |\n")
    L.append(f"\n## 3. 日本酒ジャンルの他チャンネルで直近1年に伸びている動画 TOP20（登録者に対する再生倍率順）\n\n")
    kws = json.load(open(a.genre_config, encoding="utf-8"))["keywords"] if a.genre_config else []
    L.append(f"- 検索語（{len(kws)}語、結果をマージ・重複排除）: {' ／ '.join(kws)}\n")
    L.append(f"- 条件: 公開1年以内／180秒超／日本語／再生1,000回以上／自ch除外／登録者{MIN_SUBS:,}人未満は除外（{len(small)}本）／タイトルにテーマ語なし・海外の反応・創作系は除外。基準クリア（大規模≧1倍・中規模≧2倍・小規模≧3倍）{len(pool)}本のうち上位20\n- 倍率 = 再生回数 ÷ 登録者数（取得時点）。CSV: `{os.path.basename(p3)}`（基準クリア全{len(pool)}本）\n\n")
    L.append("| # | チャンネル名 | タイトル | 再生回数 | 登録者数 | 倍率 | 公開日 | URL |\n|---|---|---|---|---|---|---|---|\n")
    for i, r in enumerate(top20, 1): L.append(f"| {i} | {clean(r['channel'])} | {clean(r['title'])} | {r['viewCount']:,} | {subs_s(r['subs'])}（{scale(r['subs'])}） | {r['ratio']:.2f} | {r['publishDate']} | {r['url']} |\n")
    if len(pool) > 20:
        L.append(f"\n### 参考: 21〜{min(len(pool), 40)}位\n\n| # | チャンネル名 | タイトル | 再生回数 | 登録者数 | 倍率 | 公開日 |\n|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(pool[20:40], 21): L.append(f"| {i} | {clean(r['channel'])} | {clean(r['title'])} | {r['viewCount']:,} | {subs_s(r['subs'])} | {r['ratio']:.2f} | {r['publishDate']} |\n")
    L.append("\n## 4. 伸びている企画の型（3 から）\n\n（本文は別途追記）\n")
    pm = os.path.join(a.out_dir, f"次回企画_材料_{a.tag}.md")
    open(pm, "w", encoding="utf-8").write("".join(L))
    json.dump({"generated": today.isoformat(), "own_count": len(own), "avg_1y": avg_1y, "overlap": [{k: v for k, v in o.items() if k != "hits"} | {"hits": [{"publishDate": h["publishDate"], "title": h["title"], "views": h["views"], "ratio": h["ratio"]} for h in o["hits"]]} for o in overlap],
               "top20": [{"channel": r["channel"], "title": r["title"], "views": r["viewCount"], "subs": r["subs"], "ratio": round(r["ratio"], 2), "publishDate": r["publishDate"], "url": r["url"]} for r in top20]},
              open(pm.replace(".md", ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[done] own={len(own)} avg1y={avg_1y:.0f} pool={len(pool)} small_excluded={len(small)} -> {pm}", file=sys.stderr)

if __name__ == "__main__":
    main()
