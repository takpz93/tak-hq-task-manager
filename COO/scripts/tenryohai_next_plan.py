#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天領盃 次回企画の材料: タスクA〜D の md を生成し、会話貼り付け用の要約を stdout に出す
入力:
  --own-csv   yt_channel_audit.py の CSV（自ch）
  --comp-json tenryohai_competitors.py の JSON（競合）
  --search-json yt_reference_search.py の JSON（横断検索）
使い方: python3 COO/scripts/tenryohai_next_plan.py --own-csv A.csv --comp-json B.json --search-json C.json --out-dir clients/天領盃/output --tag 20260929
"""
import argparse, csv, json, os, re, sys, unicodedata
from collections import Counter
from datetime import date, datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import STOP

def log(*a): print(*a, file=sys.stderr, flush=True)
def clean(x): return re.sub(r"\s+", " ", x or "").replace("|", "｜").strip()
def n(x): return f"{x:,}" if isinstance(x, (int, float)) and not isinstance(x, bool) else ("" if x is None else str(x))
def dur(s): return f"{s//60}:{s%60:02d}" if isinstance(s, int) else ""
def subs_s(x): return "" if x is None else (f"{x/10000:.1f}万人" if x >= 10000 else f"{x:,}人")
def scale(subs): return "大規模" if subs >= 100000 else ("中規模" if subs >= 10000 else "小規模")
def grade(ratio, subs):
    g1, g2 = (1.0, 0.5) if subs >= 100000 else ((2.0, 1.0) if subs >= 10000 else (3.0, 1.0))
    return "G1" if ratio >= g1 else ("G2" if ratio >= g2 else "")

# ---- 企画タイプ（判定順: ランキング → ◯選 → 酒屋 → その他。該当タグは全て「タグ」列に列挙）----
TYPE_RULES = [("ランキング", r"ランキング|TOP\s*\d+|トップ\s*\d+|ベスト\s*\d+"), ("◯選", r"[0-9０-９一二三四五六七八九十]+\s*(?:選|本|つ|銘柄|店舗)"), ("酒屋", r"酒屋|特約店|酒販店")]
def plan_type(title):
    t = unicodedata.normalize("NFKC", title)
    tags = [lab for lab, rx in TYPE_RULES if re.search(rx, t, re.I)]
    return (tags[0] if tags else "その他"), ",".join(tags)

# ---- 既出チェック用の語彙（タイトルから抽出）----
VOCAB = {
    "味わい": ["甘口", "辛口", "淡麗", "濃醇", "甘旨", "甘酸っぱい", "フルーティ", "酸", "ドライ", "スッキリ", "飲みやす", "低アルコール", "スパークリング", "にごり", "熱燗", "ぬる燗", "燗", "冷酒", "生酒", "無濾過", "原酒", "ひやおろし", "新酒", "しぼりたて", "旨い", "旨", "クセ"],
    "種別": ["純米大吟醸", "純米吟醸", "純米酒", "大吟醸", "吟醸", "本醸造", "純米"],
    "価格帯": ["コスパ", "安くて", "安い", "1000円", "2000円", "3000円", "5000円", "1万円", "高級", "プレミアム", "物価高騰", "一升瓶", "価格"],
    "地方": ["四国", "東北", "中部", "関西", "中国地方", "関東", "九州", "北陸", "北海道", "全国", "新潟", "東京", "大阪", "福島", "茨城", "高知", "佐渡", "山形", "秋田", "広島", "京都", "兵庫", "奈良", "三重", "長野", "石川", "富山", "福井", "静岡", "愛知", "岐阜", "栃木", "群馬", "埼玉", "千葉", "神奈川", "山梨", "岩手", "宮城", "青森", "岡山", "山口", "鳥取", "島根", "香川", "愛媛", "徳島", "福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄", "滋賀", "和歌山"],
    "季節": ["春", "夏酒", "夏", "秋", "冬", "年末", "正月", "花見", "お盆", "ひやおろし", "新酒", "2025年", "2026年", "2025", "2026"],
    "銘柄": ["鍋島", "赤武", "而今", "みむろ杉", "播州一献", "雅楽代", "紀土", "あたごのまつ", "雨後の月", "一白水成", "風の森", "天領盃", "獺祭", "十四代", "新政", "花陽浴", "田酒", "飛露喜", "九平次", "東洋美人", "くどき上手", "写楽", "寫樂", "仙禽", "産土", "光栄菊", "楽器正宗", "伯楽星", "宮寒梅", "陸奥八仙", "豊盃", "久保田", "八海山", "越乃寒梅", "黒龍", "梵", "天狗舞", "手取川", "磯自慢", "開運", "出羽桜", "上喜元", "栄光冨士", "楯野川", "大七", "奈良萬", "会津娘", "廣戸川", "天明", "澤屋まつもと", "松の司", "七本槍", "白隠正宗", "荷札酒", "高千代", "村祐", "菱湖", "山間", "鶴齢", "〆張鶴", "尾瀬の雪どけ", "山和", "阿部", "あべ", "翠玉", "鳳凰美田", "作"],
    "イベント・場": ["酒の陣", "サケコンペ", "SAKE COMPETITION", "SAKETIME", "特約店", "酒屋", "酒販店", "飲食店", "居酒屋", "コンビニ", "スーパー"],
    "対象": ["初心者", "はじめて", "お酒が苦手", "日本酒好き", "プロ", "蔵元", "杜氏"],
}
def extract_vocab(title):
    t = unicodedata.normalize("NFKC", title)
    found = {}
    for cat, words in VOCAB.items():
        hits = []
        for w in words:
            if w == "作":
                if re.search(r"(?<=[・/、,])作(?=[・/、,…])", t): hits.append(w)
            elif w == "燗" and ("熱燗" in hits or "ぬる燗" in hits): continue
            elif w == "純米" and any(h.startswith("純米") for h in hits): continue
            elif w == "吟醸" and any("吟醸" in h for h in hits): continue
            elif w == "旨" and "旨い" in hits: continue
            elif w == "夏" and "夏酒" in hits: continue
            elif w == "2025" and "2025年" in hits: continue
            elif w == "2026" and "2026年" in hits: continue
            elif w == "酸" and "甘酸っぱい" in hits: continue
            elif w in t: hits.append(w)
        if hits: found[cat] = hits
    return found

# ---- 形態素解析（タスクD）----
COMPOUNDS = sorted(set(["純米大吟醸", "大吟醸", "純米吟醸", "純米酒", "純米", "吟醸", "日本酒", "精米歩合", "蔵元", "酒蔵", "酒屋", "酒販店", "特約店", "飲み比べ", "利き酒", "唎酒師", "晩酌", "家飲み", "銘柄", "コスパ", "ランキング", "おすすめ", "オススメ", "居酒屋", "酒米", "杜氏", "限定", "生酒", "無濾過", "生原酒", "ひやおろし", "新酒", "初心者", "ソムリエ", "選び方", "フルーティ", "フルーティー", "甘口", "辛口", "淡麗", "濃醇", "にごり", "燗酒", "熱燗", "ぬる燗", "冷酒", "夏酒", "秋酒", "しぼりたて", "低アルコール", "スパークリング", "飲みやす", "徹底解説", "徹底比較", "本音", "ガチ", "厳選", "激旨", "最強", "最新", "トレンド", "失敗しない", "飲まなきゃ損", "コンビニ", "スーパー", "ウイスキー", "ハイボール", "ワイン", "焼酎", "ビール", "酒の陣", "サケコンペ", "SAKETIME"] + sum(VOCAB.values(), [])), key=len, reverse=True)
COMPOUND_RE = re.compile("|".join(re.escape(c) for c in COMPOUNDS if c != "作"))

def word_freq(titles):
    from janome.tokenizer import Tokenizer
    tk = Tokenizer(); cnt = Counter()
    for t in titles:
        t = unicodedata.normalize("NFKC", t)
        body = re.sub(r"【[^】]*】", lambda m: " " + m.group(0)[1:-1] + " ", t)
        seen = set(COMPOUND_RE.findall(body)); body = COMPOUND_RE.sub(" ", body)
        for w in tk.tokenize(body):
            pos = w.part_of_speech.split(",")
            if pos[0] != "名詞" or pos[1] in ("数", "非自立", "接尾", "代名詞"): continue
            s = w.surface
            if len(s) < 2 or s in STOP or re.fullmatch(r"[\d\W_]+", s): continue
            seen.add(s)
        for s in seen: cnt[s] += 1
    return cnt

def freq_table(cnt, total, top=30):
    h = f"| 順位 | 語 | 出現本数（/{total}本） |\n|---|---|---|\n"
    return h + "".join(f"| {i} | {w} | {c} |\n" for i, (w, c) in enumerate(cnt.most_common(top), 1))

# ---- タスクA ----
def task_a(own_csv, since, today, out_dir, tag):
    rows = []
    for r in csv.DictReader(open(own_csv, encoding="utf-8-sig")):
        m = re.search(r"v=([\w-]+)", r["動画URL"]); d = r["動画尺(秒)"]
        rows.append({"kind": r["区分"], "publishDate": r["公開日"], "title": r["タイトル"], "videoId": m.group(1) if m else "",
                     "durationSec": int(d) if d.isdigit() else None, "views": int(r["再生数"]) if r["再生数"].isdigit() else None,
                     "likes": int(r["高評価数"]) if r["高評価数"].isdigit() else None, "comments": int(r["コメント数"]) if r["コメント数"].isdigit() else None,
                     "ratio": float(r["対平均倍率(直近1年長尺)"]) if r["対平均倍率(直近1年長尺)"] else None})
    older = [r for r in rows if r["publishDate"] < since]
    rows = [r for r in rows if r["publishDate"] >= since]
    longs = [r for r in rows if r["durationSec"] is not None and r["durationSec"] > 180]
    shorts = [r for r in rows if r not in longs]
    avg = sum(r["views"] for r in longs if r["views"]) / max(1, len([r for r in longs if r["views"]]))
    for r in longs: r["ratio"] = r["views"] / avg if r["views"] else None
    for r in rows:
        r["type"], r["tags"] = plan_type(r["title"]); r["vocab"] = extract_vocab(r["title"])
    longs.sort(key=lambda r: r["publishDate"], reverse=True)
    def table(rs, ratio=True):
        h = "| 公開日 | タイトル | 動画ID | 長さ | 視聴回数 | 高評価 | コメント数 |" + (" 対平均倍率 |" if ratio else "") + " 企画タイプ | 該当タグ |\n|---|---|---|---|---|---|---|" + ("---|" if ratio else "") + "---|---|\n"
        for r in rs:
            h += f"| {r['publishDate']} | {clean(r['title'])} | {r['videoId']} | {dur(r['durationSec'])} | {n(r['views'])} | {n(r['likes'])} | {n(r['comments'])} |" + (f" {r['ratio']:.2f} |" if ratio and r['ratio'] is not None else (" |" if ratio else "")) + f" {r['type']} | {r['tags']} |\n"
        return h
    tc = Counter(r["type"] for r in longs)
    L = [f"# 自ch全動画（加登仙一の日本酒大学・直近12か月）\n\n取得日: {today}　対象: 公開日 {since} 以降　データ源: YouTube InnerTube（browse / next。Data API と同じ公開値。API キーが無いため代替）\n\n"]
    L.append(f"- 長尺（181秒以上）{len(longs)}本／ショート（180秒以下）{len(shorts)}本／12か月より前で除外 {len(older)}本\n- 対平均倍率 = 視聴回数 ÷ 期間内ロング平均（{avg:,.0f}回、{len(longs)}本）\n- 企画タイプ判定順: ランキング → ◯選 → 酒屋 → その他（複数該当は「該当タグ」列に列挙）\n- 企画タイプ内訳: " + "／".join(f"{k} {v}本" for k, v in tc.most_common()) + "\n\n")
    L.append(f"## 長尺（{len(longs)}本、公開日の新しい順）\n\n" + table(longs))
    L.append(f"\n## ショート（180秒以下、{len(shorts)}本）\n\n" + (table(shorts, ratio=False) if shorts else "該当なし\n"))
    # 企画タイプ別 平均
    L.append("\n## 企画タイプ別（長尺）\n\n| 企画タイプ | 本数 | 平均視聴回数 | 平均倍率 | 最大倍率 |\n|---|---|---|---|---|\n")
    for t, _ in tc.most_common():
        rs = [r for r in longs if r["type"] == t and r["views"]]
        L.append(f"| {t} | {len(rs)} | {sum(r['views'] for r in rs)/len(rs):,.0f} | {sum(r['ratio'] for r in rs)/len(rs):.2f} | {max(r['ratio'] for r in rs):.2f} |\n")
    # 既出キーワード
    L.append("\n## 既出チェック用: タイトル中の語（味わい・種別・価格帯・地方・季節・銘柄・イベント・対象）\n\n### 語ごとの出現本数と該当動画\n\n")
    for cat in VOCAB:
        cnt = Counter(); where = {}
        for r in longs:
            for w in r["vocab"].get(cat, []): cnt[w] += 1; where.setdefault(w, []).append(r)
        if not cnt: L.append(f"#### {cat}\n\n該当なし\n\n"); continue
        L.append(f"#### {cat}\n\n| 語 | 本数 | 該当動画（公開日 / 倍率） |\n|---|---|---|\n")
        for w, c in cnt.most_common():
            L.append(f"| {w} | {c} | " + "、".join(f"{r['publishDate']}({r['ratio']:.2f})" if r['ratio'] is not None else r['publishDate'] for r in where[w]) + " |\n")
        L.append("\n")
    L.append("### 動画ごとの抽出語\n\n| 公開日 | タイトル | 味わい | 種別 | 価格帯 | 地方 | 季節 | 銘柄 | イベント・場 | 対象 |\n|---|---|---|---|---|---|---|---|---|---|\n")
    for r in longs:
        L.append(f"| {r['publishDate']} | {clean(r['title'])} |" + "".join(f" {'、'.join(r['vocab'].get(c, []))} |" for c in VOCAB) + "\n")
    if older: L.append(f"\n## 参考: 12か月より前（除外、{len(older)}本）\n\n" + "".join(f"- {r['publishDate']} {clean(r['title'])} ({r['videoId']}, {dur(r['durationSec'])}, {n(r['views'])}回)\n" for r in older))
    open(os.path.join(out_dir, f"自ch全動画_{tag}.md"), "w", encoding="utf-8").write("".join(L))
    return longs, shorts, avg, older

# ---- タスクB ----
def task_b(comp_json, today, out_dir, tag):
    d = json.load(open(comp_json, encoding="utf-8"))
    hits = []; summary = []
    for ch in d["channels"]:
        subs = ch["subs"]; vids = [v for v in ch["videos"] if v["durationSec"] is not None and v["durationSec"] > 180]
        shorts = len(ch["videos"]) - len(vids)
        rows = []
        for v in vids:
            if not v["views"] or not subs: continue
            ratio = v["views"] / subs; g = grade(ratio, subs)
            rec = {"channel": ch["name"] or ch["label"], "handle": ch["handle"], "subs": subs, "publishDate": v["publishDate"], "title": v["title"], "videoId": v["videoId"],
                   "url": f"https://www.youtube.com/watch?v={v['videoId']}", "durationSec": v["durationSec"], "views": v["views"], "ratio": ratio, "grade": g,
                   "thumb": f"https://i.ytimg.com/vi/{v['videoId']}/maxresdefault.jpg" if (v.get("thumbKind") or "").startswith(("maxres", "hq720")) else f"https://i.ytimg.com/vi/{v['videoId']}/hqdefault.jpg"}
            rows.append(rec)
            if g: hits.append(rec)
        rows.sort(key=lambda r: -r["ratio"])
        summary.append({"channel": ch["name"] or ch["label"], "handle": ch["handle"], "subs": subs, "scale": scale(subs) if subs else "", "n12": len(vids), "shorts": shorts,
                        "g1": sum(1 for r in rows if r["grade"] == "G1"), "g2": sum(1 for r in rows if r["grade"] == "G2"),
                        "avg": sum(r["views"] for r in rows) / len(rows) if rows else 0, "median": sorted(r["views"] for r in rows)[len(rows)//2] if rows else 0, "rows": rows})
    hits.sort(key=lambda r: (r["channel"], -r["ratio"]))
    def table(rs):
        h = "| チャンネル名 | 登録者数 | 公開日 | タイトル | URL | 長さ | 視聴回数 | 倍率 | G1/G2 | サムネイルURL |\n|---|---|---|---|---|---|---|---|---|---|\n"
        return h + "".join(f"| {clean(r['channel'])} | {subs_s(r['subs'])} | {r['publishDate']} | {clean(r['title'])} | {r['url']} | {dur(r['durationSec'])} | {n(r['views'])} | {r['ratio']:.2f} | {r['grade']} | {r['thumb']} |\n" for r in rs)
    L = [f"# 競合ヒット（跳ねた動画・直近12か月）\n\n取得日: {today}　データ源: YouTube InnerTube（browse / next）\n\n- 倍率 = 視聴回数 ÷ チャンネル登録者数（登録者数は取得時点）\n- 大規模(10万人以上): G1≧1倍／G2 0.5〜1倍　中規模(1万〜10万人): G1≧2倍／G2 1〜2倍　小規模(1万人未満): G1≧3倍／G2 1〜3倍\n- 180秒以下は除外。サムネURLは一覧のサムネが HD なら maxresdefault、無ければ hqdefault\n\n"]
    L.append("## チャンネル別サマリ\n\n| チャンネル名 | ハンドル | 登録者数 | 規模帯 | 12か月の長尺本数 | 除外ショート | G1 | G2 | 平均視聴回数 | 中央値 |\n|---|---|---|---|---|---|---|---|---|---|\n")
    for s in summary: L.append(f"| {clean(s['channel'])} | {s['handle']} | {subs_s(s['subs'])} | {s['scale']} | {s['n12']} | {s['shorts']} | {s['g1']} | {s['g2']} | {s['avg']:,.0f} | {s['median']:,} |\n")
    L.append(f"\n## G1/G2 該当（{len(hits)}本、チャンネル別・倍率順）\n\n" + (table(hits) if hits else "該当なし\n"))
    for s in summary:
        L.append(f"\n## 全動画: {clean(s['channel'])}（{s['n12']}本、倍率順）\n\n" + (table(s["rows"]) if s["rows"] else "該当なし\n"))
    open(os.path.join(out_dir, f"競合ヒット_{tag}.md"), "w", encoding="utf-8").write("".join(L))
    return hits, summary

# ---- タスクC（yt_reference_search.py の JSON を指定列順で再整形）----
def task_c(search_json, cfg, today, out_dir, tag):
    d = json.load(open(search_json, encoding="utf-8"))
    rows = [r for r in d["final"] if r["ageDays"] <= 365]
    rows.sort(key=lambda r: -r["ratio"])
    def table(rs):
        h = "| # | タイトル | チャンネル名 | 登録者数 | 規模帯 | 公開日 | URL | 視聴回数 | 倍率 | 長さ | サムネイルURL | ヒット検索語 |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        return h + "".join(f"| {i} | {clean(r['title'])} | {clean(r['channel'])} | {subs_s(r['subs'])} | {scale(r['subs'])} | {r['publishDate']} | {r['url']} | {n(r['viewCount'])} | {r['ratio']:.2f} | {dur(r['durationSec_s'])} | {r['thumb']} | {r.get('keywordsHit','')} |\n" for i, r in enumerate(rs, 1))
    L = [f"# 横断検索ヒット（伸びた日本酒動画・直近1年）\n\n取得日: {today}　データ源: YouTube InnerTube（search / next）\n\n"]
    L.append(f"- 検索語（{len(cfg['keywords'])}語）: {' ／ '.join(cfg['keywords'])}\n- 各語につき 関連順・再生順・新着順×1年以内 ＋ 期間指定なし×関連順・再生順、続きページ込み\n- 公開1年以内／180秒超のみ（ショート専用枠は除外。横動画判定は尺による）／日本語チャンネルのみ／再生数{cfg.get('min_views',1000):,}回未満は除外\n- 倍率 = 再生数 ÷ 登録者数。大規模(10万人以上)≧1倍／中規模(1万〜10万人)≧2倍／小規模(1万人未満)≧3倍\n- タイトルにテーマ語を含まない検索ノイズ {len(d.get('offtopic', []))}本、日本語以外 {len(d.get('foreign', []))}本、登録者非公開 {len(d.get('hidden', []))}本は除外\n- サムネURL: 検索結果に HD 版がある動画は maxresdefault、無い動画は hqdefault\n\n")
    L.append(f"## 抽出結果（{len(rows)}本、倍率順）\n\n" + (table(rows) if rows else "該当なし\n"))
    kw = Counter(); [kw.update(r.get("keywordsHit", "").split(" / ")) for r in rows]
    L.append("\n## 検索語別の該当本数\n\n| 検索語 | 本数 |\n|---|---|\n" + "".join(f"| {k} | {c} |\n" for k, c in kw.most_common()))
    open(os.path.join(out_dir, f"横断検索ヒット_{tag}.md"), "w", encoding="utf-8").write("".join(L))
    return rows

# ---- タスクD ----
def task_d(b_rows, c_rows, today, out_dir, tag):
    items = [("B", r["title"]) for r in b_rows] + [("C", r["title"]) for r in c_rows]
    seen = set(); uniq = []
    for src, t in items:
        k = unicodedata.normalize("NFKC", t)
        if k in seen: continue
        seen.add(k); uniq.append((src, t, plan_type(t)[0]))
    groups = {"全体": [t for _, t, _ in uniq], "ランキング系": [t for _, t, ty in uniq if ty == "ランキング"], "◯選系": [t for _, t, ty in uniq if ty == "◯選"], "その他（酒屋含む）": [t for _, t, ty in uniq if ty not in ("ランキング", "◯選")]}
    L = [f"# タイトル頻出ワード（競合ヒット + 横断検索ヒット）\n\n取得日: {today}　対象: 競合ヒット {len(b_rows)}本 + 横断検索ヒット {len(c_rows)}本（重複除外後 {len(uniq)}本）\n\n- 形態素解析: janome（名詞のみ。数・接尾・代名詞・1文字語を除外）。日本酒ドメインの複合語は最長一致で先に切り出し\n- 出現本数 = その語を含む動画の本数（1本で複数回出ても1）\n- 分類: ランキング系 = タイトルに「ランキング／TOP◯／ベスト◯」、◯選系 = 「◯選／◯本／◯つ／◯銘柄」（ランキング系を優先）\n\n"]
    for g, titles in groups.items():
        L.append(f"## {g}（{len(titles)}本）TOP30\n\n" + (freq_table(word_freq(titles), len(titles)) if titles else "該当なし\n") + "\n")
    open(os.path.join(out_dir, f"頻出ワード_{tag}.md"), "w", encoding="utf-8").write("".join(L))
    return {g: (word_freq(t), len(t)) for g, t in groups.items()}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--own-csv"); ap.add_argument("--comp-json"); ap.add_argument("--search-json"); ap.add_argument("--search-config")
    ap.add_argument("--out-dir", default="clients/天領盃/output"); ap.add_argument("--tag", default=datetime.now().strftime("%Y%m%d"))
    ap.add_argument("--since", default=(date.today() - timedelta(days=365)).isoformat())
    a = ap.parse_args(); today = date.today().isoformat(); os.makedirs(a.out_dir, exist_ok=True)
    S = []
    if a.own_csv:
        longs, shorts, avg, older = task_a(a.own_csv, a.since, today, a.out_dir, a.tag)
        top = sorted(longs, key=lambda r: -(r["ratio"] or 0))[:15]
        S.append(f"■ 自ch（直近12か月 長尺{len(longs)}本・ショート{len(shorts)}本・平均{avg:,.0f}回）倍率TOP15\n" + "\n".join(f"{r['ratio']:.2f}x {r['views']:,} {r['publishDate']} [{r['type']}] {r['title'][:38]}" for r in top))
    b_hits = []
    if a.comp_json and os.path.exists(a.comp_json):
        b_hits, summ = task_b(a.comp_json, today, a.out_dir, a.tag)
        S.append("■ 競合サマリ\n" + "\n".join(f"{s['channel'][:12]} {subs_s(s['subs'])} 長尺{s['n12']}本 G1:{s['g1']} G2:{s['g2']} 中央値{s['median']:,}" for s in summ))
        S.append("■ 競合G1/G2 倍率TOP15\n" + "\n".join(f"{r['ratio']:.2f}x {r['grade']} {r['views']:,} {r['publishDate']} {r['channel'][:8]} {r['title'][:34]}" for r in sorted(b_hits, key=lambda r: -r["ratio"])[:15]))
    c_rows = []
    if a.search_json and os.path.exists(a.search_json):
        cfg = json.load(open(a.search_config, encoding="utf-8")) if a.search_config else {"keywords": [], "min_views": 1000}
        c_rows = task_c(a.search_json, cfg, today, a.out_dir, a.tag)
        S.append(f"■ 横断検索ヒット（{len(c_rows)}本）倍率TOP15\n" + "\n".join(f"{r['ratio']:.2f}x {r['viewCount']:,} {subs_s(r['subs'])} {r['publishDate']} {r['channel'][:8]} {r['title'][:34]}" for r in c_rows[:15]))
    if b_hits or c_rows:
        fq = task_d(b_hits, c_rows, today, a.out_dir, a.tag)
        for g in ("ランキング系", "◯選系"):
            cnt, tot = fq[g]
            S.append(f"■ 頻出ワード {g}（{tot}本）TOP15\n" + "、".join(f"{w}{c}" for w, c in cnt.most_common(15)))
    out = "\n\n".join(S)
    print(out[:3000])
    log(f"[summary] {len(out)}字")

if __name__ == "__main__":
    main()
