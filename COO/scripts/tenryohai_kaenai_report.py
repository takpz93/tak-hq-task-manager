#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天領盃「人気銘柄はなぜ買えないのか」参考動画レポート
yt_reference_search.py の JSON を読み、追加条件（登録者1,000人未満・自ch除外）と追加集計を加えて md / json を出力
使い方: python3 COO/scripts/tenryohai_kaenai_report.py --search-json RAW.json --config CONFIG.json --out claude/参考動画_人気銘柄入手困難_20261012.md
"""
import argparse, json, os, re, sys, unicodedata
from collections import Counter
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import STOP, threshold

OWN_ID, OWN_HANDLE = "UCx8tnZhehtNYsHBHpeHqHOg", "senichi_kato_tenryohai"
MIN_SUBS = 1000
KEY_TERMS = ["入手困難", "幻", "プレミア", "転売", "定価", "買えない"]

def clean(x): return re.sub(r"\s+", " ", x or "").replace("|", "｜").strip()
def subs_s(n): return f"{n:,}人"
def scale(s): return "大規模" if s >= 100000 else ("中規模" if s >= 10000 else "小規模")

def word_freq(titles, compounds):
    from janome.tokenizer import Tokenizer
    tk = Tokenizer(); cnt = Counter()
    comp_re = re.compile("|".join(re.escape(c) for c in sorted(compounds, key=len, reverse=True) if c != "作"))
    for t in titles:
        t = unicodedata.normalize("NFKC", t)
        body = re.sub(r"[【】\[\]「」『』]", " ", t)
        seen = set(comp_re.findall(body)); body = comp_re.sub(" ", body)
        for w in tk.tokenize(body):
            pos = w.part_of_speech.split(",")
            if pos[0] != "名詞" or pos[1] in ("数", "非自立", "接尾", "代名詞"): continue
            s = w.surface
            if len(s) < 2 or s in STOP or re.fullmatch(r"[\d\W_]+", s): continue
            seen.add(s)
        for s in seen: cnt[s] += 1
    return cnt

def is_own(r):
    return r.get("channelId") == OWN_ID or OWN_HANDLE in (r.get("handle") or "") or OWN_HANDLE in (r.get("channelUrl") or "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--search-json", required=True); ap.add_argument("--config", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); cfg = json.load(open(a.config, encoding="utf-8")); d = json.load(open(a.search_json, encoding="utf-8"))
    today = date.today().isoformat()
    # final = 基準クリア（1年以内 + 20本未満なら2年まで）。r2 = 1〜2年（拡張しなかった場合の参考）
    passed = d["final"]; extended = any(r["ageDays"] > 365 for r in passed)
    own = [r for r in passed if is_own(r)]
    small = [r for r in passed if not is_own(r) and r["subs"] < MIN_SUBS]
    main_rows = sorted([r for r in passed if not is_own(r) and r["subs"] >= MIN_SUBS], key=lambda r: -r["ratio"])
    # 別掲: テーマ語なし／創作系（倍率基準クリアのみ）
    noise = [r for r in d.get("offtopic", []) if r.get("subs") and r["subs"] >= MIN_SUBS and not is_own(r)]
    for r in noise: r["ratio"] = r["viewCount"] / r["subs"]
    noise = sorted([r for r in noise if r["ratio"] >= threshold(r["subs"]) and r["ageDays"] <= (730 if extended else 365)], key=lambda r: -r["ratio"])
    r2 = [] if extended else sorted([r for r in d.get("r2", []) if not is_own(r) and r["subs"] >= MIN_SUBS], key=lambda r: -r["ratio"])

    def thumb(r):
        return r["thumb"] if "maxres" in r["thumb"] else f"取得不可（HD版なし。代替: {r['thumb']}）"
    def table(rs):
        h = "| # | タイトル全文 | 動画URL | チャンネル名 | 登録者数 | 再生数 | 倍率 | 公開日 | 動画長（秒） | サムネイル画像URL（maxresdefault） | ヒット検索語 |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
        return h + "".join(f"| {i} | {clean(r['title'])} | {r['url']} | {clean(r['channel'])} | {subs_s(r['subs'])}（{scale(r['subs'])}） | {r['viewCount']:,} | {r['ratio']:.2f} | {r['publishDate']} | {r['durationSec_s']} | {thumb(r)} | {r.get('keywordsHit','')} |\n" for i, r in enumerate(rs, 1))
    def freq_table(cnt, total, top=20):
        return f"| 順位 | 語 | 出現本数（/{total}本） |\n|---|---|---|\n" + "".join(f"| {i} | {w} | {c} |\n" for i, (w, c) in enumerate(cnt.most_common(top), 1))

    all_rows = main_rows + noise
    freq_all = word_freq([r["title"] for r in all_rows], cfg.get("compounds", []))
    freq_main = word_freq([r["title"] for r in main_rows], cfg.get("compounds", []))
    def term_count(rows, term):
        return sum(1 for r in rows if term in unicodedata.normalize("NFKC", r["title"]))
    kw_hit = Counter(); [kw_hit.update(r.get("keywordsHit", "").split(" / ")) for r in main_rows]
    n_1y = sum(1 for r in main_rows if r["ageDays"] <= 365); n_2y = len(main_rows) - n_1y

    L = [f"# 参考動画（人気銘柄はなぜ買えないのか）― 2026/10/17 公開回のサムネ・タイトル根拠データ\n\n取得日: {today}　データ源: YouTube InnerTube（search / next。Data API と同じ公開値。API キー不要のため代替使用）\n\n"]
    L.append("## 検索・抽出条件\n\n")
    L.append(f"- 検索キーワード（{len(cfg['keywords'])}語、各語で検索し結果をマージ・重複排除）: {' ／ '.join(cfg['keywords'])}\n")
    L.append("- 各語につき 関連順・再生順・新着順×1年以内 ＋ 期間指定なし×関連順・再生順、続きページ込み\n")
    L.append(f"- 公開期間: 直近1年以内で基準クリアが {n_1y}本" + ("（20本未満のため2年以内まで拡張。公開日列で判別可）" if extended else "（20本以上のため拡張なし。1〜2年前の該当は参考として別掲）") + "\n")
    L.append("- 動画長 180秒超のみ（ショート専用枠は除外。180秒超の縦動画は検索データから判別不可）／日本語チャンネルのみ（英語UIで取得した原題に仮名が残るかで判定）\n")
    L.append(f"- 除外: 登録者{MIN_SUBS:,}人未満 {len(small)}本（別掲）／自チャンネル @{OWN_HANDLE} {len(own)}本／再生数{cfg.get('min_views',1000):,}回未満／登録者非公開 {len(d.get('hidden', []))}本／日本語以外 {len(d.get('foreign', []))}本\n")
    L.append("- 倍率 = 再生数 ÷ チャンネル登録者数（登録者数は取得時点）。大規模(10万人以上)≧1倍／中規模(1万〜10万人)≧2倍／小規模(1万人未満)≧3倍\n")
    L.append(f"- 本表から外して別掲: タイトルにテーマ語（{cfg['topic_regex'][:50]}…）を含まない検索ノイズ、および除外語（{cfg['exclude_regex']}）を含む創作・ドラマ系\n")
    L.append("- サムネイル画像URL: YouTube の検索メタデータに HD 版（hq720）がある動画は maxresdefault.jpg が存在するため記載。無い動画は「取得不可」とし、代替の hqdefault.jpg を併記。画像ホスト（i.ytimg.com）へのアクセスはこの環境で遮断されており、実体の取得確認は未実施\n\n")
    L.append(f"| 項目 | 件数 |\n|---|---|\n| 検索ヒットのユニーク動画 | {d.get('candidates', '')} |\n| 基準クリア（期間内） | {len(passed)} |\n| 本表（日本酒テーマとして有効） | {len(main_rows)}（1年以内 {n_1y}／1〜2年 {n_2y}） |\n| 別掲: ノイズ・創作系 | {len(noise)} |\n| 別掲: 登録者{MIN_SUBS:,}人未満 | {len(small)} |\n| 除外: 自チャンネル | {len(own)} |\n\n")
    L.append(f"## 本表: 抽出結果（{len(main_rows)}本、倍率順）\n\n" + (table(main_rows) if main_rows else "該当なし\n"))
    L.append(f"\n## 別掲: 検索ノイズ・創作ドラマ系（基準クリアだがテーマ外、{len(noise)}本）\n\n" + (table(noise) if noise else "該当なし\n"))
    L.append(f"\n## 別掲: 登録者{MIN_SUBS:,}人未満（基準クリア、{len(small)}本）\n\n" + (table(sorted(small, key=lambda r: -r['ratio'])) if small else "該当なし\n"))
    if r2: L.append(f"\n## 参考: 公開1〜2年前で基準クリア（{len(r2)}本）\n\n" + table(r2))
    L.append(f"\n## タイトル頻出ワード 上位20（抽出動画 全体 = 本表 + 別掲ノイズ、{len(all_rows)}本）\n\n" + freq_table(freq_all, len(all_rows)))
    L.append(f"\n## タイトル頻出ワード 上位20（ノイズ除外後・日本酒テーマとして有効な動画のみ、{len(main_rows)}本）\n\n" + freq_table(freq_main, len(main_rows)))
    L.append(f"\n## キーワード別 出現本数（タイトルに含む本数）\n\n| 語 | 本表（{len(main_rows)}本） | 全体（{len(all_rows)}本） |\n|---|---|---|\n" + "".join(f"| {t} | {term_count(main_rows, t)} | {term_count(all_rows, t)} |\n" for t in KEY_TERMS))
    L.append("\n## 検索語別の本表該当本数\n\n| 検索語 | 本数 |\n|---|---|\n" + "".join(f"| {k} | {c} |\n" for k, c in kw_hit.most_common()))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("".join(L))
    def rec(r): return {"title": r["title"], "url": r["url"], "channel": r["channel"], "channelId": r.get("channelId"), "subs": r["subs"], "views": r["viewCount"], "ratio": round(r["ratio"], 2), "publishDate": r["publishDate"], "durationSec": r["durationSec_s"], "thumbnail": r["thumb"] if "maxres" in r["thumb"] else None, "thumbnailFallback": r["thumb"], "keywordsHit": r.get("keywordsHit", "")}
    json.dump({"generated": today, "conditions": {"keywords": cfg["keywords"], "extended_to_2y": extended, "min_subs": MIN_SUBS, "min_views": cfg.get("min_views", 1000)},
               "main": [rec(r) for r in main_rows], "noise": [rec(r) for r in noise], "small_channels": [rec(r) for r in small], "ref_1to2y": [rec(r) for r in r2],
               "freq_all_top20": freq_all.most_common(20), "freq_main_top20": freq_main.most_common(20),
               "term_counts": {t: {"main": term_count(main_rows, t), "all": term_count(all_rows, t)} for t in KEY_TERMS}},
              open(re.sub(r"\.md$", ".json", a.out), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[done] main={len(main_rows)} noise={len(noise)} small={len(small)} own={len(own)} extended={extended} -> {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
