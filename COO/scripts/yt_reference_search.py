#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用: YouTube横断検索 → 規模帯別倍率基準で「伸びた動画」を抽出 → md 出力
使い方: python3 COO/scripts/yt_reference_search.py --config CONFIG.json [--cache DIR]
config 例:
{
 "title": "参考動画 純米大吟醸", "out": "clients/天領盃/output/参考動画_純米大吟醸_20260909.md",
 "keywords": ["純米大吟醸", ...], "topic_regex": "日本酒|酒|吟醸", "compounds": ["純米大吟醸", ...],
 "min_hits": 20, "min_views": 1000
}
"""
import argparse, json, os, re, sys, unicodedata
from collections import Counter
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import Cache, walk, text, has_kana, threshold, PARAMS, MAX_AGE_DAYS, PRIMARY_AGE_DAYS, STOP
from yt_reference_dental import search_videos_thumb, enrich, scale, fmt_subs, clean

def log(*a): print(*a, file=sys.stderr, flush=True)

def word_freq(titles, compounds):
    from janome.tokenizer import Tokenizer
    tk = Tokenizer(); cnt = Counter()
    comp_re = re.compile("|".join(re.escape(c) for c in sorted(compounds, key=len, reverse=True))) if compounds else None
    for t in titles:
        t = unicodedata.normalize("NFKC", t)
        seen = set()
        body = t
        if comp_re:
            seen |= set(comp_re.findall(body)); body = comp_re.sub(" ", body)
        for w in tk.tokenize(body):
            pos = w.part_of_speech.split(",")
            if pos[0] != "名詞" or pos[1] in ("数", "非自立", "接尾", "代名詞"): continue
            s = w.surface
            if len(s) < 2 or s in STOP or re.fullmatch(r"[\d\W_]+", s): continue
            seen.add(s)
        for s in seen: cnt[s] += 1
    return cnt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(__file__), "..", ".cache_yt"))
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))
    cache = Cache(a.cache); today = datetime.now(timezone.utc).date()
    min_views = cfg.get("min_views", 1000); min_hits = cfg.get("min_hits", 20)
    topic_re = re.compile(cfg["topic_regex"], re.I) if cfg.get("topic_regex") else None

    cands = {}; hits = {}
    for kw in cfg["keywords"]:
        n0 = len(cands)
        for label, params, pages in PARAMS:
            for v in search_videos_thumb(kw, params, pages, cache):
                hits.setdefault(v["videoId"], set()).add(kw); cands.setdefault(v["videoId"], v)
        log(f"[search] {kw}: +{len(cands)-n0} (total {len(cands)})")
    pre = [v for v in cands.values() if v["durationSec_s"] and v["durationSec_s"] > 180
           and (v["relDays_s"] is None or v["relDays_s"] <= MAX_AGE_DAYS) and (v["views_s"] is None or v["views_s"] >= min_views)]
    log(f"[prefilter] {len(pre)}/{len(cands)}")
    rows, hidden, offtopic, foreign = [], [], [], []
    for i, v in enumerate(pre):
        v = enrich(v, cache, today)
        if not v or v["ageDays"] > MAX_AGE_DAYS or v["viewCount"] is None or v["viewCount"] < min_views: continue
        v["keywordsHit"] = " / ".join(sorted(hits[v["videoId"]]))
        if topic_re and not topic_re.search(v["title"]) and not topic_re.search(v.get("title_en") or ""):
            offtopic.append(v); continue
        ja = has_kana(v.get("title_en")) or has_kana(v["channel"]) or (has_kana(v["title"]) and re.search(r"[一-鿿]", v["channel"]))
        if not ja: foreign.append(v); continue
        if not v["subs"]: hidden.append(v); continue
        v["ratio"] = v["viewCount"] / v["subs"]
        if v["ratio"] >= threshold(v["subs"]): rows.append(v)
        if (i + 1) % 50 == 0: log(f"[details] {i+1}/{len(pre)}")
    rows.sort(key=lambda r: -r["ratio"])
    r1 = [r for r in rows if r["ageDays"] <= PRIMARY_AGE_DAYS]; r2 = [r for r in rows if r["ageDays"] > PRIMARY_AGE_DAYS]
    extended = len(r1) < min_hits
    final = r1 + r2 if extended else r1
    log(f"[select] 1y {len(r1)}, 1-2y {len(r2)}, extended={extended}, hidden {len(hidden)}, offtopic {len(offtopic)}, foreign {len(foreign)}")

    def table(rs):
        h = "| # | 動画タイトル | 動画URL | チャンネル名 | 登録者数 | 規模帯 | 再生数 | 倍率 | 公開日 | 動画長(秒) | サムネイル画像URL |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
        for i, r in enumerate(rs, 1):
            th = r["thumb"] + ("" if "maxres" in r["thumb"] else "（maxres無し→high）")
            h += f"| {i} | {clean(r['title'])} | {r['url']} | {clean(r['channel'])} | {fmt_subs(r['subs'])} | {scale(r['subs'])} | {r['viewCount']:,} | {r['ratio']:.2f} | {r['publishDate']} | {r['durationSec_s']} | {th} |\n"
        return h
    freq = word_freq([r["title"] for r in final], cfg.get("compounds", []))
    L = [f"# {cfg['title']}\n\n取得日: {today.isoformat()}　データ源: YouTube InnerTube（search / next）※YouTube Data APIと同じ公開データ。APIキー不要のため代替使用\n\n"]
    L.append("## 検索・抽出条件\n\n")
    L.append(f"- 検索キーワード（{len(cfg['keywords'])}語、結果をマージ・重複排除）: {' ／ '.join(cfg['keywords'])}\n")
    L.append("- 各語につき 関連順・再生順・新着順×1年以内 ＋ 期間指定なし×関連順・再生順、続きページ込み\n")
    L.append(f"- 公開期間: 直近1年以内{'。1年以内が' + str(min_hits) + '本未満のため最大2年まで拡張（公開日で判別可）' if extended else '（1年以内で' + str(min_hits) + '本以上のため拡張なし。1〜2年前の該当は参考として別掲）'}\n")
    L.append("- 動画長180秒超のみ（ショート専用枠は除外。180秒超の縦動画は検索データから判別不可）／日本語チャンネルのみ\n")
    L.append("- 倍率 = 再生数 ÷ 登録者数。大規模(10万人以上)1倍以上／中規模(1万〜10万人)2倍以上／小規模(1万人未満)3倍以上\n")
    L.append(f"- 追加の前提: 再生数{min_views:,}回未満は除外。タイトルにテーマ語（{cfg.get('topic_regex','')[:60]}…）を含まない検索ノイズは別掲。登録者非公開は判定不可として別掲\n")
    L.append("- サムネURL: 検索結果にHD版(hq720)がある動画は maxresdefault、無い動画は hqdefault(high) を記載。実体の取得確認はこの環境からは不可\n\n")
    L.append(f"| 項目 | 件数 |\n|---|---|\n| 検索ヒットのユニーク動画 | {len(cands)} |\n| 事前フィルタ通過（尺・期間・再生数） | {len(pre)} |\n| 基準クリア・1年以内 | {len(r1)} |\n| 基準クリア・1〜2年 | {len(r2)} |\n| テーマ語なしで別掲 | {len(offtopic)} |\n| 日本語以外 | {len(foreign)} |\n| 登録者非公開 | {len(hidden)} |\n\n")
    L.append(f"## 抽出結果（倍率順、{len(final)}本）\n\n" + (table(final) if final else "該当なし\n"))
    if not extended and r2:
        L.append(f"\n## 参考: 公開1〜2年前で基準クリア（{len(r2)}本）\n\n" + table(r2))
    L.append(f"\n## タイトル出現ワード 頻度ランキング（上位20語、出現本数／全{len(final)}本）\n\n| 順位 | ワード | 出現本数 |\n|---|---|---|\n")
    for i, (w, c) in enumerate(freq.most_common(20), 1): L.append(f"| {i} | {w} | {c} |\n")
    if offtopic:
        L.append(f"\n## 別掲: 基準クリアだがタイトルにテーマ語なし（検索ノイズ、{len(offtopic)}本）\n\n")
        ot = [v for v in offtopic if v["subs"]]
        for v in ot: v["ratio"] = v["viewCount"] / v["subs"]
        ot = sorted([v for v in ot if v["ratio"] >= threshold(v["subs"])], key=lambda r: -r["ratio"])
        L.append(table(ot) if ot else "（倍率基準クリアなし）\n")
    if hidden:
        L.append("\n## 別掲: 登録者数非公開（倍率判定不可）\n\n")
        for v in sorted(hidden, key=lambda r: -r["viewCount"])[:10]: L.append(f"- {clean(v['title'])} | {clean(v['channel'])} | {v['viewCount']:,}回 | {v['publishDate']} | {v['url']}\n")
    out = cfg["out"]; os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write("".join(L))
    json.dump({"final": final, "r2": r2, "offtopic": offtopic, "hidden": hidden, "foreign": foreign}, open(re.sub(r"\.md$", ".json", out), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)
    log("[done]", out)

if __name__ == "__main__":
    main()
