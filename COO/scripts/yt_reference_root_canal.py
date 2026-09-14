#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千勝会「歯の神経治療（根管治療）」回 サムネ・タイトル参考材料
 A: YouTube横断検索（8KW）→ 倍率基準クリア動画
 B: 自チャンネル @chikatsukai 本編 再生数上位5本
 C: 指名6チャンネル内の「神経・根管治療・抜髄」関連動画（2年以内・全件・再生数順）
"""
import argparse, json, os, re, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import Cache, it_post, walk, text, parse_duration, parse_views, parse_rel_days, has_kana, threshold, PARAMS, MAX_AGE_DAYS, PRIMARY_AGE_DAYS, parse_subs
from yt_reference_dental import search_videos_thumb, enrich, scale, fmt_subs, clean, OWN_CHANNEL_ID

KEYWORDS = ["根管治療", "歯の神経を抜く", "抜髄", "根尖性歯周炎", "神経のない歯 寿命", "虫歯 放置 痛み消えた", "根管治療 痛い", "虫歯 進行 C3 C4"]
TOPIC_RE = re.compile(r"歯|神経|根管|抜髄|根尖|歯髄|虫歯|むし歯|C3|C4|痛|dental|dentist|tooth|teeth|root canal", re.I)
EXCL_RE = re.compile(r"ドラマ|ヤクザ|一目惚れ|社長", re.I)
MIN_VIEWS = 1000
C_CHANNELS = ["歯科医の暴露チャンネル【前岡遼馬】", "ザ・ホワイトデンタルクリニック", "稲葉院長のあのネェ", "君のための歯医者さん", "歯医者のさくら先生", "木村先生には歯が立たない!!"]
C_RE = re.compile(r"神経|根管|抜髄|根尖|歯髄|根の治療|根っこ|膿|フィステル|マイクロスコープ|ラバーダム")
C_MAX_AGE = 730

def log(*a): print(*a, file=sys.stderr, flush=True)

def resolve_channel(name, cache):
    """チャンネル名で検索し channelRenderer の browseId を返す"""
    d = it_post("search", {"query": name, "params": "EgIQAg%3D%3D".replace("%3D", "=")}, cache, f"chsearch_{name}")
    best = None
    for c in walk(d or {}, "channelRenderer"):
        title = text(c.get("title")); cid = c.get("channelId")
        key = re.sub(r"[\s!！【】\[\]]", "", name)[:6]
        if key in re.sub(r"[\s!！【】\[\]]", "", title):
            return cid, title, parse_subs(text(c.get("videoCountText")) or text(c.get("subscriberCountText")))
        if best is None: best = (cid, title, None)
    return best or (None, None, None)

def channel_videos(cid, cache, max_age):
    """動画タブを新着順に、公開 max_age 日以内の範囲で取得"""
    d = it_post("browse", {"browseId": cid, "params": "EgZ2aWRlb3PyBgQKAjoA"}, cache, f"browse_{cid}_videos_p1")
    hdr = json.dumps((d or {}).get("header", {}), ensure_ascii=False)
    m = re.search(r"チャンネル登録者数 ([\d.,]+(?:万|億)?人)", hdr); subs = parse_subs(m.group(0)) if m else None
    name = ((d or {}).get("header", {}).get("pageHeaderRenderer", {}) or {}).get("pageTitle")
    vids = []; page = 1; stop = False
    while d and not stop:
        for lk in walk(d, "lockupViewModel"):
            if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO": continue
            s = json.dumps(lk, ensure_ascii=False)
            md = lk.get("metadata", {}).get("lockupMetadataViewModel", {})
            parts = [p.get("text", {}).get("content", "") for row in md.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", []) for p in row.get("metadataParts", [])]
            dur = re.search(r'"text":\s*"(\d+:\d+(?::\d+)?)"', s)
            rel = next((parse_rel_days(p) for p in parts if "前" in p), None)
            vids.append({"videoId": lk.get("contentId"), "title": md.get("title", {}).get("content", ""),
                         "views_s": next((parse_views(p) for p in parts if "回視聴" in p or "views" in p), None),
                         "relDays_s": rel, "durationSec_s": parse_duration(dur.group(1)) if dur else None, "thumbKind": None})
            if rel is not None and rel > max_age + 60: stop = True
        tok = None
        for c in walk(d, "continuationItemRenderer"):
            tok = (c.get("continuationEndpoint") or {}).get("continuationCommand", {}).get("token"); break
        if not tok or stop: break
        page += 1
        d = it_post("browse", {"continuation": tok}, cache, f"browse_{cid}_videos_p{page}")
    return name, subs, vids

def a_table(rs):
    h = "| # | チャンネル名 | 登録者数 | 規模帯 | タイトル | 再生数 | 倍率 | 公開日 | 動画URL | サムネ画像URL |\n|---|---|---|---|---|---|---|---|---|---|\n"
    for i, r in enumerate(rs, 1):
        h += f"| {i} | {clean(r['channel'])} | {fmt_subs(r['subs'])} | {scale(r['subs'] or 0)} | {clean(r['title'])} | {r['viewCount']:,} | {r['ratio']:.1f}倍 | {r['publishDate']} | {r['url']} | {r['thumb']} |\n"
    return h

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
                hits.setdefault(v["videoId"], set()).add(kw); cands.setdefault(v["videoId"], v)
        log(f"[A search] {kw}: +{len(cands)-n0} (total {len(cands)})")
    pre = [v for v in cands.values() if v["durationSec_s"] and v["durationSec_s"] > 180
           and (v["relDays_s"] is None or v["relDays_s"] <= MAX_AGE_DAYS) and (v["views_s"] is None or v["views_s"] >= MIN_VIEWS)]
    log(f"[A prefilter] {len(pre)}/{len(cands)}")
    rows, hidden, offtopic, foreign = [], [], [], []
    for i, v in enumerate(pre):
        v = enrich(v, cache, today)
        if not v or v["ageDays"] > MAX_AGE_DAYS or v["viewCount"] is None or v["viewCount"] < MIN_VIEWS: continue
        v["keywordsHit"] = " / ".join(sorted(hits[v["videoId"]]))
        if (not TOPIC_RE.search(v["title"]) and not TOPIC_RE.search(v.get("title_en") or "")) or EXCL_RE.search(v["title"]):
            offtopic.append(v); continue
        ja = has_kana(v.get("title_en")) or has_kana(v["channel"]) or (has_kana(v["title"]) and re.search(r"[一-鿿]", v["channel"]))
        if not ja: foreign.append(v); continue
        if not v["subs"]: hidden.append(v); continue
        v["ratio"] = v["viewCount"] / v["subs"]
        if v["ratio"] >= threshold(v["subs"]): rows.append(v)
        if (i + 1) % 50 == 0: log(f"[A details] {i+1}/{len(pre)}")
    rows.sort(key=lambda r: -r["ratio"])
    a_1y = [r for r in rows if r["ageDays"] <= PRIMARY_AGE_DAYS]; a_2y = [r for r in rows if r["ageDays"] > PRIMARY_AGE_DAYS]
    log(f"[A select] 1y {len(a_1y)}, 1-2y {len(a_2y)}, foreign {len(foreign)}, hidden {len(hidden)}, offtopic {len(offtopic)}")

    # ---- B ----
    ch_name, ch_subs, vids = channel_videos(OWN_CHANNEL_ID, cache, 100000)
    vids = [v for v in vids if v["videoId"]]
    vids.sort(key=lambda v: -(v["views_s"] or 0))
    top5 = []
    for v in vids[:5]:
        v["channel"] = ch_name; v["channelId"] = OWN_CHANNEL_ID
        v = enrich(v, cache, today)
        if v: top5.append(v)
    top5.sort(key=lambda v: -v["viewCount"])
    log(f"[B] {ch_name} subs={ch_subs} videos={len(vids)}")

    # ---- C ----
    c_rows = []; c_info = []
    for name in C_CHANNELS:
        cid, found, _ = resolve_channel(name, cache)
        if not cid:
            c_info.append((name, None, None, 0, 0)); log(f"[C] {name}: channel NOT FOUND"); continue
        cname, csubs, cv = channel_videos(cid, cache, C_MAX_AGE)
        cv = [v for v in cv if v["videoId"] and (v["relDays_s"] is None or v["relDays_s"] <= C_MAX_AGE + 60)]
        hitv = [v for v in cv if C_RE.search(v["title"])]
        kept = []
        for v in hitv:
            v["channel"] = cname or found; v["channelId"] = cid
            e = enrich(v, cache, today)
            if not e or e["ageDays"] > C_MAX_AGE: continue
            e["subs"] = e["subs"] or csubs; e["ratio"] = (e["viewCount"] / e["subs"]) if e["subs"] else 0
            kept.append(e)
        c_rows += kept
        c_info.append((name, cname or found, csubs, len(cv), len(kept)))
        log(f"[C] {name} -> {cname} ({cid}) subs={csubs} videos<=2y={len(cv)} hits={len(kept)}")
    c_rows.sort(key=lambda r: -r["viewCount"])

    # ---- 出力 ----
    L = [f"# 千勝会「歯の神経治療（根管治療）」回 サムネ・タイトル参考材料\n\n生成日: {today.isoformat()}　データ源: YouTube InnerTube（search / next / browse）\n\n"]
    L.append("## 【A】YouTube横断 参考動画（倍率順）\n\n")
    L.append(f"検索KW: {' / '.join(KEYWORDS)}（各KW 関連順・再生順・新着順×1年以内＋期間なし関連順・再生順、続きページ込み）\n\n")
    L.append("抽出条件: 公開1年以内（主表）／180秒超／倍率 = 再生数÷登録者数 が 大規模(10万人以上)1.0倍・中規模(1万〜10万人)2.0倍・小規模(1万人未満)3.0倍 以上／サムネURLは検索結果にHD版(hq720)がある動画は maxresdefault、無い動画は hqdefault。\n")
    L.append(f"補足: 再生数{MIN_VIEWS:,}回未満、タイトルに歯科関連語を含まない検索ノイズは除外（追加の前提）。縦型判定はショート枠(ショート専用レンダラー・180秒以下)の除外によるもので、180秒超の縦型長尺は検索データから判別不可。\n\n")
    L.append(f"| 項目 | 件数 |\n|---|---|\n| 検索ヒットのユニーク動画 | {len(cands)} |\n| 事前フィルタ通過（尺・期間・再生数） | {len(pre)} |\n| 倍率基準クリア・1年以内 | {len(a_1y)} |\n| 倍率基準クリア・1〜2年（拡張枠） | {len(a_2y)} |\n| 歯科関連語なしで除外 | {len(offtopic)} |\n| 日本語以外 | {len(foreign)} |\n| 登録者非公開で判定不可 | {len(hidden)} |\n\n")
    L.append(f"### A-1 公開1年以内（{len(a_1y)}本）\n\n" + (a_table(a_1y) if a_1y else "該当なし\n"))
    L.append(f"\n### A-2 公開1〜2年（拡張枠、{len(a_2y)}本）\n\n" + (a_table(a_2y) if a_2y else "該当なし\n"))
    if foreign: L.append(f"\n### A-3 日本語以外（{len(foreign)}本）\n\n" + a_table(foreign))
    L.append(f"\n## 【B】自チャンネル 本編 再生数上位5本\n\nチャンネル: {ch_name}（https://www.youtube.com/@chikatsukai ／ {OWN_CHANNEL_ID}）　登録者数 {fmt_subs(ch_subs)}　本編 {len(vids)}本\n\n")
    L.append("| # | タイトル | 再生数 | 公開日 | 動画URL | サムネ画像URL（maxresdefault） |\n|---|---|---|---|---|---|\n")
    for i, v in enumerate(top5, 1):
        L.append(f"| {i} | {clean(v['title'])} | {v['viewCount']:,} | {v['publishDate']} | {v['url']} | https://i.ytimg.com/vi/{v['videoId']}/maxresdefault.jpg |\n")
    L.append(f"\n## 【C】指名6チャンネル内「神経・根管治療・抜髄」関連動画（2年以内・全件・再生数順、{len(c_rows)}本）\n\n")
    L.append("抽出: 各チャンネルの動画タブ（本編）を2年分取得し、タイトルに 神経／根管／抜髄／根尖／歯髄／根の治療／根っこ／膿／フィステル／マイクロスコープ／ラバーダム を含むもの。倍率基準は適用せず（倍率は参考表示）。\n\n")
    L.append("| チャンネル（指定名） | 解決したチャンネル | 登録者数 | 2年以内の本編 | 関連動画 |\n|---|---|---|---|---|\n")
    for name, cname, csubs, n, k in c_info: L.append(f"| {name} | {cname or '未特定'} | {fmt_subs(csubs)} | {n} | {k} |\n")
    L.append("\n" + (a_table(c_rows) if c_rows else "該当なし\n"))
    L.append("\n---\n注記: サムネURLの maxresdefault/hqdefault の有無は検索結果のサムネ種別（hq720=HD版あり）から判定（Cはチャンネル一覧由来のため全て maxresdefault 表記。実体はこの環境から確認不可）。\n")
    with open(os.path.join(a.out, "root_canal_reference.md"), "w", encoding="utf-8") as f: f.write("".join(L))
    json.dump({"A_1y": a_1y, "A_2y": a_2y, "A_foreign": a_foreign if False else foreign, "B": top5, "C": c_rows, "C_info": c_info},
              open(os.path.join(a.out, "root_canal_reference.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)
    log("[done]")

if __name__ == "__main__":
    main()
