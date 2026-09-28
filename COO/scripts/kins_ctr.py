#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KINS サムネ×タイトル×CTR 一覧: InnerTube メタデータ + Studio エクスポート(CSV) を videoId で結合"""
import csv, io, json, os, re, statistics, sys
from datetime import date
S = sys.argv[1]; OUT = "clients/KINS/output"; D = "20260928"
meta = json.load(open(f"{S}/kins_meta.json", encoding="utf-8"))
rows = list(csv.reader(open(f"{S}/kins_studio_20260827.csv", encoding="utf-8")))
hdr = rows[0]; st = {}
for r in rows[2:]:
    if not r or not r[0]: continue
    st[r[0]] = dict(zip(hdr, r))
def num(x):
    try: return float(x.replace(",", "")) if x not in ("", None) else None
    except: return None
vids = []
for v in meta["long"]:
    s = st.get(v["videoId"])
    imp = num(s["インプレッション数"]) if s else None; ctr = num(s["インプレッションのクリック率 (%)"]) if s else None
    old = None
    if s:
        t0 = s["動画のタイトル"].rstrip(".").rstrip("…")
        if t0 and not v["title"].startswith(t0[:15]): old = s["動画のタイトル"]
    vids.append({**v, "imp": int(imp) if imp is not None else None, "ctr": ctr, "st_views": int(num(s["視聴回数"])) if s and num(s["視聴回数"]) is not None else None,
                 "avp": num(s["平均視聴率 (%)"]) if s else None, "avd": s["平均視聴時間"] if s else None, "old_title": old, "in_studio": bool(s)})
TAGS = {
 "【】あり": lambda t: t.startswith("【"),
 "数字あり": lambda t: bool(re.search(r"\d", t)),
 "店名あり": lambda t: bool(re.search(r"無印|コストコ|COSTCO|Costco|カルディ|KALDI|業務スーパー|成城石井|久世福|コンビニ|スタバ|スターバックス|サイゼ|ガスト|大戸屋|しんぱち|イオン", t)),
 "格付けワード": lambda t: bool(re.search(r"格付け|ランキング|比較|徹底比較|ベスト|ワースト", t)),
 "NGワード": lambda t: bool(re.search(r"絶対|やめて|NG|買わない|食べない|危険|警告|逆効果", t)),
 "肩書きワード": lambda t: bool(re.search(r"腸活のプロ|菌ケアの専門家|歯科医|プロ", t)),
 "衝撃・有料級・保存版系": lambda t: bool(re.search(r"衝撃|有料級|超有料級|保存版|忖度", t)),
 "悩みワード": lambda t: bool(re.search(r"便秘|下痢|疲れ|臭い|口臭|薄毛|肌|老け|眠", t)),
}
for v in vids:
    v["tags"] = [k for k, f in TAGS.items() if f(v["title"])]; v["len"] = len(v["title"])
    v["low_imp"] = v["imp"] is not None and v["imp"] < 10000
by_ctr = sorted([v for v in vids if v["ctr"] is not None], key=lambda v: -v["ctr"]) + [v for v in vids if v["ctr"] is None]
for i, v in enumerate(by_ctr, 1): v["rank"] = i if v["ctr"] is not None else None
def n(x): return f"{x:,}" if isinstance(x, int) else ("" if x is None else x)
def pct(x): return f"{x:.2f}%" if x is not None else ""
def dur(s): return f"{s//60}:{s%60:02d}"
def esc(t): return t.replace("|", "｜")
def row(v, i):
    mark = "（インプ1万未満）" if v["low_imp"] else ""
    ctr = pct(v["ctr"]) if v["in_studio"] else "未取得"; imp = n(v["imp"]) if v["in_studio"] else "未取得"; avp = pct(v["avp"]) if v["in_studio"] else "未取得"
    note = f"旧タイトル: {esc(v['old_title'])}" if v["old_title"] else ""
    return f"| {i} | [サムネ]({v['thumb']}) | {esc(v['title'])} | {v['publishDate']} | {dur(v['durationSec'])} | {imp}{mark} | {ctr} | {n(v['viewCount'])} | {avp} | {v['len']}字 / {'・'.join(v['tags']) or '—'} | {note} |\n"
H = "| 順位 | サムネ | タイトル | 公開日 | 尺 | インプ | CTR | 再生数(現在) | 平均視聴率 | タグ | 備考 |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
in_st = sum(1 for v in vids if v["in_studio"]); L = []
L.append(f"# KINS サムネ×タイトル×CTR 一覧（{D}）\n\n対象: 【下川先生】の菌ケア大学（UCXAU7ks-wPVoFJykHn08zvA）　長尺（180秒超）{len(vids)}本　登録者 {meta['subs']}（チャンネル表示）\n\n")
L.append("## データ源\n\n")
L.append("- 動画メタデータ（videoId／タイトル／公開日／尺／再生数(現在)／サムネURL）: YouTube InnerTube（Data API と同じ公開情報。APIキーが無いため代替）。2026-09-28 取得\n")
L.append(f"- インプレッション／CTR／平均視聴率／平均視聴時間: Drive「KINS Studio」スプレッドシート（Studio エクスポート、2026-08-27 作成、表データ {len(st)}行）。グラフデータの開始日が 2025-08-27 のため、集計期間は 2025-08-27〜2026-08-27 の365日分と判断できる（全期間ではない）\n")
L.append(f"- 結合キー: videoId。結合できた長尺: {in_st}本／未取得（8/27以降公開で新CSV未受領）: {len(vids)-in_st}本\n")
L.append("- Drive の「本編メタデータCSV」（2026-08-27_菌ケア大学_全動画メタデータ_本編.csv）は公開メタデータのみで CTR 列を含まないため、結合には使用していない\n")
L.append("- サムネ画像の実体・コンタクトシート: この環境から画像ホスト（i.ytimg.com）へ接続できないため **取得不可**。ローカルで生成するスクリプト `COO/scripts/kins_contact_sheet.py` を同梱（下記）\n")
L.append("- 「インプ1万未満」は一覧に残し印を付けた。タグ集計（別ファイル）からは除外\n\n")
L.append(f"## CTR上位20本（インプ1万以上・結合済み）\n\n" + H + "".join(row(v, v["rank"]) for v in [x for x in by_ctr if x["ctr"] is not None and not x["low_imp"]][:20]))
L.append(f"\n## CTR下位20本（インプ1万以上・結合済み）\n\n" + H + "".join(row(v, v["rank"]) for v in [x for x in by_ctr if x["ctr"] is not None and not x["low_imp"]][-20:]))
L.append(f"\n## 全動画（CTR降順。CTR未取得は末尾に公開日順）\n\n" + H + "".join(row(v, v["rank"] or "—") for v in by_ctr))
L.append("\n## コンタクトシートの生成（ローカル実行）\n\n```bash\npip install pillow requests\npython3 COO/scripts/kins_contact_sheet.py clients/KINS/output/KINS_サムネCTR一覧_20260928.csv clients/KINS/output\n```\n出力: `thumbs/{videoId}.jpg`、`KINS_サムネ一覧_CTR順_01.png…`、`KINS_サムネ一覧_公開日順_01.png…`（5列×8行、各サムネ下に 順位｜CTR｜インプ｜再生数｜公開日）\n")
open(f"{OUT}/KINS_サムネCTR一覧_{D}.md", "w", encoding="utf-8").write("".join(L))
with open(f"{OUT}/KINS_サムネCTR一覧_{D}.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["順位", "videoId", "タイトル", "公開日", "尺(秒)", "インプレッション", "CTR(%)", "再生数(現在)", "再生数(Studio)", "平均視聴率(%)", "平均視聴時間", "文字数", "タグ", "インプ1万未満", "旧タイトル", "動画URL", "サムネURL", "サムネURL(hq720)"])
    for v in by_ctr: w.writerow([v["rank"] or "", v["videoId"], v["title"], v["publishDate"], v["durationSec"], v["imp"] if v["in_studio"] else "未取得", v["ctr"] if v["in_studio"] else "未取得", v["viewCount"], v["st_views"] if v["in_studio"] else "未取得", v["avp"] if v["in_studio"] else "未取得", v["avd"] if v["in_studio"] else "未取得", v["len"], "・".join(v["tags"]), "1" if v["low_imp"] else "", v["old_title"] or "", v["url"], v["thumb"], f"https://i.ytimg.com/vi/{v['videoId']}/hq720.jpg"])
# ④ 集計
pool = [v for v in vids if v["ctr"] is not None and not v["low_imp"]]
def agg(rs):
    if not rs: return "—", "—", "—", 0
    return f"{statistics.median([v['ctr'] for v in rs]):.2f}%", f"{statistics.mean([v['imp'] for v in rs]):,.0f}", f"{statistics.mean([v['viewCount'] for v in rs]):,.0f}", len(rs)
T = [f"# KINS タイトル特徴×CTR（{D}）\n\n母集団: Studio エクスポートと結合できインプレッション1万以上の長尺 {len(pool)}本（全長尺{len(vids)}本のうち、未取得{len(vids)-in_st}本・インプ1万未満{sum(1 for v in vids if v['low_imp'])}本を除外）。タグはタイトルの機械判定。\n\n"]
T.append("| タグ | 区分 | CTR中央値 | 平均インプ | 平均再生数(現在) | 本数 |\n|---|---|---|---|---|---|\n")
for k in TAGS:
    a = agg([v for v in pool if k in v["tags"]]); b = agg([v for v in pool if k not in v["tags"]])
    T.append(f"| {k} | あり | {a[0]} | {a[1]} | {a[2]} | {a[3]} |\n| {k} | なし | {b[0]} | {b[1]} | {b[2]} | {b[3]} |\n")
T.append("\n## 文字数帯\n\n| 文字数 | CTR中央値 | 平均インプ | 平均再生数(現在) | 本数 |\n|---|---|---|---|---|\n")
for lo, hi in [(0, 30), (31, 40), (41, 50), (51, 60), (61, 999)]:
    a = agg([v for v in pool if lo <= v["len"] <= hi]); T.append(f"| {lo}〜{hi if hi < 999 else ''}字 | {a[0]} | {a[1]} | {a[2]} | {a[3]} |\n")
T.append("\n## 店名別（店名ありのみ）\n\n| 店名 | CTR中央値 | 平均インプ | 平均再生数(現在) | 本数 |\n|---|---|---|---|---|\n")
for nm, rx in [("無印", "無印"), ("コストコ", "コストコ|COSTCO|Costco"), ("カルディ", "カルディ|KALDI"), ("業務スーパー", "業務スーパー"), ("成城石井", "成城石井"), ("久世福", "久世福"), ("コンビニ", "コンビニ"), ("スタバ", "スタバ|スターバックス"), ("サイゼ", "サイゼ"), ("ガスト", "ガスト"), ("大戸屋", "大戸屋"), ("しんぱち", "しんぱち"), ("イオン", "イオン")]:
    a = agg([v for v in pool if re.search(rx, v["title"])]); T.append(f"| {nm} | {a[0]} | {a[1]} | {a[2]} | {a[3]} |\n")
open(f"{OUT}/KINS_タイトル特徴×CTR_{D}.md", "w", encoding="utf-8").write("".join(T))
print(f"vids={len(vids)} joined={in_st} pool={len(pool)} low_imp={sum(1 for v in vids if v['low_imp'])} old_title={sum(1 for v in vids if v['old_title'])}")
