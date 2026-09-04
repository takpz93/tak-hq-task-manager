#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千勝会「歯の詰め物」回 サムネ・タイトル参考材料の収集
 A: YouTube横断検索（8KW）→ 倍率基準クリア動画
 B: 自チャンネル @chikatsukai 本編 再生数上位5本
 C: 指名1本（前岡遼馬 CAD/CAM冠）
使い方: python3 COO/scripts/yt_reference_dental.py [--cache DIR] [--out DIR]
"""
import argparse, json, os, re, sys, unicodedata
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import (Cache, it_post, walk, text, parse_duration, parse_views, parse_rel_days,
                                video_details, has_kana, threshold, PARAMS, MIN_DURATION, MAX_AGE_DAYS,
                                PRIMARY_AGE_DAYS, parse_subs)

KEYWORDS = ["銀歯 デメリット", "銀歯 白くする", "詰め物 セラミック", "CAD/CAM冠", "二次虫歯 詰め物", "詰め物 寿命", "保険 自費 歯 違い", "インレー 種類"]
MIN_VIEWS = 1000
OWN_CHANNEL_ID = "UCqGpNSBrcuKv_qTLeiD7hvg"
TARGET_TITLE_KEY = "CAD/CAM冠の闇"; TARGET_CHANNEL_KEY = "前岡"

def log(*a): print(*a, file=sys.stderr, flush=True)

def thumb_urls(vid, kind):
    """検索結果のサムネが hq720 なら maxresdefault が存在する。hqdefault のみなら maxres は無い"""
    main = f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg" if kind == "hq720" else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
    return main

def thumb_kind(v):
    th = ((v.get("thumbnail") or {}).get("thumbnails") or [])
    if not th: return None
    m = re.search(r"/vi(?:_webp|_lc)?/[^/]+/([a-z0-9]+)", th[-1].get("url", ""))
    return (m.group(1) if m else None)

def search_videos_thumb(query, params, pages, cache):
    import requests
    out = []
    body = {"query": query}
    if params: body["params"] = requests.utils.unquote(params)
    d = it_post("search", body, cache, f"search_{query}_{params}_p1")
    for page in range(1, pages + 1):
        if not d: break
        for v in walk(d, "videoRenderer"):
            vid = v.get("videoId")
            if not vid: continue
            owner = v.get("ownerText") or v.get("longBylineText") or {}
            ch_id = None
            for r in owner.get("runs", []):
                ch_id = r.get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId")
                if ch_id: break
            out.append({"videoId": vid, "title": text(v.get("title")), "channel": text(owner), "channelId": ch_id,
                        "durationSec_s": parse_duration(text(v.get("lengthText"))), "views_s": parse_views(text(v.get("viewCountText"))),
                        "relDays_s": parse_rel_days(text(v.get("publishedTimeText"))), "thumbKind": thumb_kind(v)})
        tok = None
        for c in walk(d, "continuationCommand"):
            tok = c.get("token"); break
        if not tok or page == pages: break
        d = it_post("search", {"continuation": tok}, cache, f"search_{query}_{params}_p{page+1}")
    return out

def scale(subs):
    if subs >= 100000: return "大規模"
    if subs >= 10000: return "中規模"
    return "小規模"

def fmt_subs(n):
    if n is None: return "非公開"
    return f"{n/10000:.1f}万人" if n >= 10000 else f"{n:,}人"

def clean(x): return re.sub(r"\s+", " ", x or "").replace("|", "｜").strip()

def enrich(v, cache, today):
    d = video_details(v["videoId"], cache)
    if not d or not d["publishDate"]: return None
    if d["viewCount"] is None: d["viewCount"] = v.get("views_s")
    v.update(d)
    v["ageDays"] = (today - datetime.strptime(d["publishDate"], "%Y-%m-%d").date()).days
    v["url"] = f"https://www.youtube.com/watch?v={v['videoId']}"
    v["thumb"] = thumb_urls(v["videoId"], v.get("thumbKind"))
    return v

def channel_videos(cache):
    """チャンネルの動画タブ（本編のみ。ショートは別タブ）を全ページ取得"""
    d = it_post("browse", {"browseId": OWN_CHANNEL_ID, "params": "EgZ2aWRlb3PyBgQKAjoA"}, cache, f"browse_{OWN_CHANNEL_ID}_videos_p1")
    hdr = json.dumps(d.get("header", {}), ensure_ascii=False)
    m = re.search(r"チャンネル登録者数 ([\d.,]+(?:万|億)?人)", hdr); subs = parse_subs(m.group(0)) if m else None
    name = (d.get("header", {}).get("pageHeaderRenderer", {}) or {}).get("pageTitle")
    vids = []; page = 1
    while d:
        for lk in walk(d, "lockupViewModel"):
            if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO": continue
            s = json.dumps(lk, ensure_ascii=False)
            md = lk.get("metadata", {}).get("lockupMetadataViewModel", {})
            parts = [p.get("text", {}).get("content", "") for row in md.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", []) for p in row.get("metadataParts", [])]
            dur = re.search(r'"text":\s*"(\d+:\d+(?::\d+)?)"', s)
            vids.append({"videoId": lk.get("contentId"), "title": md.get("title", {}).get("content", ""),
                         "views_s": next((parse_views(p) for p in parts if "回視聴" in p or "views" in p), None),
                         "relDays_s": next((parse_rel_days(p) for p in parts if "前" in p), None),
                         "durationSec_s": parse_duration(dur.group(1)) if dur else None, "thumbKind": None})
        tok = None
        for c in walk(d, "continuationItemRenderer"):
            tok = (c.get("continuationEndpoint") or {}).get("continuationCommand", {}).get("token"); break
        if not tok: break
        page += 1
        d = it_post("browse", {"continuation": tok}, cache, f"browse_{OWN_CHANNEL_ID}_videos_p{page}")
    return name, subs, vids

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(__file__), "..", ".cache_yt"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "output"))
    a = ap.parse_args()
    cache = Cache(a.cache); os.makedirs(a.out, exist_ok=True)
    today = datetime.now(timezone.utc).date()

    # ---- A ----
    cands = {}; hits = {}
    for kw in KEYWORDS:
        n0 = len(cands)
        for label, params, pages in PARAMS:
            for v in search_videos_thumb(kw, params, pages, cache):
                hits.setdefault(v["videoId"], set()).add(kw)
                cands.setdefault(v["videoId"], v)
        log(f"[A search] {kw}: +{len(cands)-n0} (total {len(cands)})")
    pre = [v for v in cands.values() if v["durationSec_s"] and v["durationSec_s"] > 180
           and (v["relDays_s"] is None or v["relDays_s"] <= MAX_AGE_DAYS) and (v["views_s"] is None or v["views_s"] >= MIN_VIEWS)]
    log(f"[A prefilter] {len(pre)}/{len(cands)}")
    rows = []; hidden = []
    for i, v in enumerate(pre):
        v = enrich(v, cache, today)
        if not v or v["ageDays"] > MAX_AGE_DAYS or v["viewCount"] is None or v["viewCount"] < MIN_VIEWS: continue
        v["keywordsHit"] = " / ".join(sorted(hits[v["videoId"]]))
        v["lang"] = "ja" if (has_kana(v.get("title_en")) or has_kana(v["channel"])) else "other"
        if v["subs"] is None or v["subs"] == 0: hidden.append(v); continue
        v["ratio"] = v["viewCount"] / v["subs"]; v["threshold"] = threshold(v["subs"])
        if v["ratio"] >= v["threshold"]: rows.append(v)
        if (i + 1) % 50 == 0: log(f"[A details] {i+1}/{len(pre)}")
    rows.sort(key=lambda r: -r["ratio"])
    a_1y = [r for r in rows if r["ageDays"] <= PRIMARY_AGE_DAYS and r["lang"] == "ja"]
    a_2y = [r for r in rows if r["ageDays"] > PRIMARY_AGE_DAYS and r["lang"] == "ja"]
    a_foreign = [r for r in rows if r["lang"] != "ja"]
    log(f"[A select] 1y {len(a_1y)}, 1-2y {len(a_2y)}, foreign {len(a_foreign)}, hidden {len(hidden)}")

    # ---- B ----
    ch_name, ch_subs, vids = channel_videos(cache)
    vids = [v for v in vids if v["videoId"]]
    vids.sort(key=lambda v: -(v["views_s"] or 0))
    top5 = []
    for v in vids[:5]:
        v["channel"] = ch_name; v["channelId"] = OWN_CHANNEL_ID
        v = enrich(v, cache, today)
        if v: top5.append(v)
    top5.sort(key=lambda v: -v["viewCount"])
    log(f"[B] {ch_name} subs={ch_subs} videos={len(vids)} top5 ok={len(top5)}")

    # ---- C ----
    target = None
    for label, params, pages in [("関連順", None, 1)]:
        for v in search_videos_thumb("【暴露】「銀歯を白くしませんか？」保険のCAD/CAM冠の闇 前岡遼馬", params, pages, cache):
            if TARGET_TITLE_KEY in v["title"] and TARGET_CHANNEL_KEY in v["channel"]:
                target = enrich(v, cache, today); break
    if not target:
        for v in search_videos_thumb("前岡遼馬 CAD/CAM冠の闇", None, 1, cache):
            if TARGET_TITLE_KEY in v["title"]:
                target = enrich(v, cache, today); break
    log(f"[C] {'found ' + target['videoId'] if target else 'NOT FOUND'}")

    # ---- 出力 ----
    def a_table(rs):
        h = "| # | チャンネル名 | 登録者数 | 規模帯 | タイトル | 再生数 | 倍率 | 公開日 | 動画URL | サムネ画像URL |\n|---|---|---|---|---|---|---|---|---|---|\n"
        for i, r in enumerate(rs, 1):
            h += f"| {i} | {clean(r['channel'])} | {fmt_subs(r['subs'])} | {scale(r['subs'])} | {clean(r['title'])} | {r['viewCount']:,} | {r['ratio']:.1f}倍 | {r['publishDate']} | {r['url']} | {r['thumb']} |\n"
        return h
    L = [f"# 千勝会「歯の詰め物（レジン・金属・セラミック）」回 サムネ・タイトル参考材料\n\n生成日: {today.isoformat()}　データ源: YouTube InnerTube（search / next / browse）\n\n"]
    L.append("## 【A】YouTube横断 参考動画（倍率順）\n\n")
    L.append(f"検索KW: {' / '.join(KEYWORDS)}（各KW 関連順・再生順・新着順×1年以内＋期間なし関連順・再生順、続きページ込み）\n\n")
    L.append("抽出条件: 公開1年以内（主表）／180秒超／倍率 = 再生数÷登録者数 が 大規模(10万人以上)1.0倍・中規模(1万〜10万人)2.0倍・小規模(1万人未満)3.0倍 以上／サムネURLは検索結果にHD版(hq720)がある動画は maxresdefault、無い動画は hqdefault。\n")
    L.append(f"補足: 再生数{MIN_VIEWS:,}回未満は除外（追加の前提）。縦型判定はショート枠(ショート専用レンダラー・180秒以下)の除外によるもので、180秒超の縦型長尺は検索データから判別不可。\n\n")
    L.append(f"| 項目 | 件数 |\n|---|---|\n| 検索ヒットのユニーク動画 | {len(cands)} |\n| 事前フィルタ通過（尺・期間・再生数） | {len(pre)} |\n| 倍率基準クリア・1年以内 | {len(a_1y)} |\n| 倍率基準クリア・1〜2年（拡張枠） | {len(a_2y)} |\n| 登録者非公開で判定不可 | {len(hidden)} |\n\n")
    L.append(f"### A-1 公開1年以内（{len(a_1y)}本）\n\n" + (a_table(a_1y) if a_1y else "該当なし\n"))
    L.append(f"\n### A-2 公開1〜2年（拡張枠、{len(a_2y)}本）\n\n" + (a_table(a_2y) if a_2y else "該当なし\n"))
    if a_foreign: L.append(f"\n### A-3 日本語以外（{len(a_foreign)}本）\n\n" + a_table(a_foreign))
    if hidden:
        L.append("\n### 参考: 登録者数非公開（倍率判定不可、再生数順）\n\n| チャンネル名 | タイトル | 再生数 | 公開日 | 動画URL |\n|---|---|---|---|---|\n")
        for r in sorted(hidden, key=lambda r: -r["viewCount"])[:10]: L.append(f"| {clean(r['channel'])} | {clean(r['title'])} | {r['viewCount']:,} | {r['publishDate']} | {r['url']} |\n")
    L.append(f"\n## 【B】自チャンネル 本編 再生数上位5本\n\nチャンネル: {ch_name}（https://www.youtube.com/@chikatsukai ／ {OWN_CHANNEL_ID}）　登録者数 {fmt_subs(ch_subs)}　本編 {len(vids)}本\n\n")
    L.append("| # | タイトル | 再生数 | 公開日 | 動画URL | サムネ画像URL（maxresdefault） |\n|---|---|---|---|---|---|\n")
    for i, v in enumerate(top5, 1):
        L.append(f"| {i} | {clean(v['title'])} | {v['viewCount']:,} | {v['publishDate']} | {v['url']} | https://i.ytimg.com/vi/{v['videoId']}/maxresdefault.jpg |\n")
    L.append("\n## 【C】指名: 前岡遼馬「【暴露】「銀歯を白くしませんか？」保険のCAD/CAM冠の闇」\n\n")
    if target:
        L.append(f"| 項目 | 値 |\n|---|---|\n| チャンネル名 | {clean(target['channel'])} |\n| 登録者数 | {fmt_subs(target['subs'])} |\n| タイトル | {clean(target['title'])} |\n| 再生数 | {target['viewCount']:,} |\n| 倍率 | {target['viewCount']/target['subs']:.1f}倍 |\n| 公開日 | {target['publishDate']} |\n| 動画URL | {target['url']} |\n| サムネ画像URL | {target['thumb']} |\n")
    else:
        L.append("検索で該当動画を特定できませんでした。\n")
    L.append("\n---\n注記: サムネURLの maxresdefault/hqdefault の有無は検索結果のサムネ種別（hq720=HD版あり）から判定。この実行環境からは画像ホストへ接続できないため実体の取得確認は未実施。\n")
    with open(os.path.join(a.out, "dental_filling_reference.md"), "w", encoding="utf-8") as f: f.write("".join(L))
    json.dump({"A_1y": a_1y, "A_2y": a_2y, "A_foreign": a_foreign, "B": top5, "C": target, "B_channel": {"name": ch_name, "subs": ch_subs, "count": len(vids)}},
              open(os.path.join(a.out, "dental_filling_reference.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)
    log("[done]")

if __name__ == "__main__":
    main()
