#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube横断「伸びた動画」収集ツール（カレー／スパイス／血糖値・腸活）

- YouTube InnerTube (youtubei.googleapis.com) を使い、APIキー不要で
  検索・再生数・公開日・尺・チャンネル登録者数を取得する
- 規模帯別倍率（再生数÷登録者数）で「伸びた動画」を抽出
- md レポート、CSV、JSON、サムネ一覧を COO/output/ に出力

使い方:
  python3 COO/scripts/yt_trend_collector.py [--cache DIR] [--out DIR]
"""
import argparse, json, os, re, sys, time, unicodedata, subprocess
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import requests

# InnerTube 公開クライアントキー（YouTube Web フロントエンドに埋め込まれている公開値）
INNERTUBE_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
INNERTUBE = "https://youtubei.googleapis.com/youtubei/v1/"
CTX = {"context": {"client": {"clientName": "WEB", "clientVersion": "2.20250101.00.00", "hl": "ja", "gl": "JP"}}}

KEYWORDS = {
    "カレー軸": ["カレー 健康", "カレー 血糖値", "スパイスカレー 健康", "カレー粉", "カレールー 比較", "インドカレー 健康"],
    "スパイス軸": ["ターメリック 効果", "クミン 効果", "スパイス 効果 健康", "スパイス 腸内環境"],
    "血糖値・腸活軸": ["血糖値 上げない 食べ方", "白米 血糖値 対策", "腸活 レシピ"],
}
# 参考枠（英語圏）: 日本語検索に混ざる海外動画に加え、少量の英語クエリで補完
KEYWORDS_REF = {"参考枠(英語)": ["turmeric benefits", "curry health benefits", "spices gut health", "blood sugar rice"]}

# 検索フィルタ (sp パラメータ)
PARAMS = [
    ("1年以内/関連順", "EgIIBQ%3D%3D", 3),
    ("1年以内/再生順", "CAMSAggF", 3),
    ("1年以内/新着順", "CAISAggF", 2),
    ("期間なし/関連順", None, 2),
    ("期間なし/再生順", "CAM%3D", 2),
]

MIN_VIEWS = 1000           # ノイズ除去（登録者数が極小のチャンネルの数十回再生などを除外）
MAX_AGE_DAYS = 730         # 最大2年
PRIMARY_AGE_DAYS = 365     # 主枠は1年以内
MIN_DURATION = 181         # 180秒以下は除外
FEW_HITS = 5               # 1年以内の該当が5本未満なら2年まで補完
TOP_THUMBS = 30

def log(*a):
    print(*a, file=sys.stderr, flush=True)

class Cache:
    def __init__(self, d):
        self.d = d; os.makedirs(d, exist_ok=True)
    def path(self, k): return os.path.join(self.d, re.sub(r'[^A-Za-z0-9_.-]', '_', k) + ".json")
    def get(self, k):
        p = self.path(k)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f: return json.load(f)
    def put(self, k, v):
        with open(self.path(k), "w", encoding="utf-8") as f: json.dump(v, f, ensure_ascii=False)

SESSION = requests.Session()
VERIFY = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE") or True

def it_post(endpoint, body, cache, key):
    c = cache.get(key)
    if c is not None: return c
    payload = dict(CTX); payload.update(body)
    for attempt in range(4):
        try:
            r = SESSION.post(INNERTUBE + endpoint, params={"key": INNERTUBE_KEY, "prettyPrint": "false"},
                             json=payload, timeout=40, verify=VERIFY,
                             headers={"User-Agent": "Mozilla/5.0", "X-YouTube-Client-Name": "1", "X-YouTube-Client-Version": "2.20250101.00.00"})
            if r.status_code == 200:
                d = r.json(); cache.put(key, d); time.sleep(0.25); return d
            log(f"  HTTP {r.status_code} on {endpoint} (attempt {attempt+1})")
        except Exception as e:
            log(f"  error on {endpoint}: {e} (attempt {attempt+1})")
        time.sleep(2 * (attempt + 1))
    return None

# ---------- パース ----------
def walk(o, key):
    if isinstance(o, dict):
        if key in o: yield o[key]
        for v in o.values(): yield from walk(v, key)
    elif isinstance(o, list):
        for v in o: yield from walk(v, key)

def text(o):
    if not o: return ""
    if "simpleText" in o: return o["simpleText"]
    if "runs" in o: return "".join(r.get("text", "") for r in o["runs"])
    return ""

def parse_duration(s):
    if not s: return None
    p = [int(x) for x in re.findall(r"\d+", s)]
    if not p: return None
    sec = 0
    for x in p: sec = sec * 60 + x
    return sec

def parse_views(s):
    if not s: return None
    s = unicodedata.normalize("NFKC", s)
    m = re.search(r"([\d,.]+)\s*(万|億)?", s)
    if not m: return None
    n = float(m.group(1).replace(",", ""))
    if m.group(2) == "万": n *= 10000
    if m.group(2) == "億": n *= 100000000
    return int(n)

def parse_rel_days(s):
    if not s: return None
    s = unicodedata.normalize("NFKC", s)
    m = re.search(r"(\d+)\s*(年|か月|ヶ月|週間|日|時間|分|秒)", s)
    if not m: return None
    n = int(m.group(1)); u = m.group(2)
    return {"年": 365, "か月": 30, "ヶ月": 30, "週間": 7, "日": 1}.get(u, 0) * n

def parse_subs(s):
    if not s: return None
    s = unicodedata.normalize("NFKC", s)
    m = re.search(r"([\d,.]+)\s*(万|億)?\s*人", s)
    if not m: return None
    n = float(m.group(1).replace(",", ""))
    if m.group(2) == "万": n *= 10000
    if m.group(2) == "億": n *= 100000000
    return int(n)

def search_videos(query, params, pages, cache):
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
            ch_id = None; ch_url = None
            for r in owner.get("runs", []):
                ep = r.get("navigationEndpoint", {})
                ch_id = ep.get("browseEndpoint", {}).get("browseId")
                ch_url = ep.get("browseEndpoint", {}).get("canonicalBaseUrl")
                if ch_id: break
            out.append({
                "videoId": vid,
                "title": text(v.get("title")),
                "channel": text(owner),
                "channelId": ch_id, "channelUrl": ch_url,
                "durationSec_s": parse_duration(text(v.get("lengthText"))),
                "views_s": parse_views(text(v.get("viewCountText"))),
                "relDays_s": parse_rel_days(text(v.get("publishedTimeText"))),
            })
        tok = None
        for c in walk(d, "continuationCommand"):
            tok = c.get("token"); break
        if not tok or page == pages: break
        d = it_post("search", {"continuation": tok}, cache, f"search_{query}_{params}_p{page+1}")
    return out

def video_details(vid, cache):
    d = it_post("player", {"videoId": vid}, cache, f"player_{vid}")
    if not d: return None
    vd = d.get("videoDetails") or {}
    mf = (d.get("microformat") or {}).get("playerMicroformatRenderer") or {}
    if not vd.get("videoId"): return None
    return {
        "title": vd.get("title"), "lengthSeconds": int(vd.get("lengthSeconds") or 0),
        "viewCount": int(vd.get("viewCount") or 0), "author": vd.get("author"),
        "channelId": vd.get("channelId"), "publishDate": (mf.get("publishDate") or mf.get("uploadDate") or "")[:10],
        "category": mf.get("category"), "isLive": bool(vd.get("isLiveContent")),
        "keywords": vd.get("keywords") or [],
    }

def channel_subs(vid, cache):
    d = it_post("next", {"videoId": vid}, cache, f"next_{vid}")
    if not d: return None, None
    subs = None; handle = None
    for o in walk(d, "videoOwnerRenderer"):
        subs = parse_subs(text(o.get("subscriberCountText")))
        for r in (o.get("title") or {}).get("runs", []):
            handle = r.get("navigationEndpoint", {}).get("browseEndpoint", {}).get("canonicalBaseUrl")
        break
    return subs, handle

# ---------- 判定 ----------
def lang_of(*texts):
    s = "".join(t or "" for t in texts)
    if re.search(r"[぀-ヿ]", s): return "ja"
    if re.search(r"[一-鿿]", s): return "zh"
    return "en"

def threshold(subs):
    if subs >= 100000: return 1.0
    if subs >= 10000: return 2.0
    return 3.0

RECIPE_KW = ["レシピ", "作り方", "作る", "作れ", "作っ", "料理", "簡単", "材料", "献立", "ごはん", "ご飯", "晩", "弁当", "炊", "煮込", "焼", "炒", "手作り", "本格", "時短", "混ぜ", "丼", "スープ", "おかず", "ランチ", "ディナー", "recipe", "cook", "how to make", "homemade", "美味", "おいしい", "うまい", "絶品", "食べる", "作り置き", "キッチン", "kitchen", "chef", "シェフ", "食堂", "飯"]
EXPERT_KW = ["医師", "医者", "医学", "内科", "専門医", "教授", "博士", "薬剤師", "管理栄養士", "栄養士", "栄養学", "解説", "研究", "論文", "効果", "効能", "血糖値", "腸内", "健康", "寿命", "病", "予防", "危険", "リスク", "科学", "メカニズム", "理由", "真実", "衝撃", "実は", "doctor", "dr.", "dr ", "md", "science", "study", "research", "benefit", "health", "nutrition", "dietitian", "physician", "professor", "がん", "癌", "糖尿", "ダイエット", "痩せ", "老化", "認知症", "免疫", "炎症", "アンチエイジング", "栄養", "成分", "比較", "選び方", "ランキング", "レビュー"]

def classify(title, channel, category, keywords):
    t = (title or "").lower(); c = (channel or "").lower(); k = " ".join(keywords).lower()
    r = sum(2 for w in RECIPE_KW if w in t) + sum(1 for w in RECIPE_KW if w in c) + sum(0.5 for w in RECIPE_KW if w in k)
    e = sum(2 for w in EXPERT_KW if w in t) + sum(1 for w in EXPERT_KW if w in c) + sum(0.5 for w in EXPERT_KW if w in k)
    if category == "Howto & Style": r += 1.5
    if category in ("Education", "Science & Technology"): e += 1.5
    if r > e: return "レシピ・料理型"
    if e > r: return "専門家の解説型"
    return "レシピ・料理型" if category == "Howto & Style" else "専門家の解説型"

# ---------- 集計 ----------
STOP = set("こと もの ため さん ここ これ それ あれ さ 方 的 化 用 中 人 私 僕 今 分 年 月 日 回 本 つ 個 位 時 上 下 前 後 目 気 何 系 全 超 感 的 内 外 話 版 編 件 種 等 みんな みたい よう そう ない".split())

def word_stats(items):
    from janome.tokenizer import Tokenizer
    tk = Tokenizer()
    nouns = Counter(); nums = Counter(); brackets = Counter()
    for it in items:
        title = unicodedata.normalize("NFKC", it["title"])
        # 【】内
        bs = set(b.strip() for b in re.findall(r"【([^】]*)】", title) if b.strip())
        for b in bs: brackets[b] += 1
        # 数字表現
        ns = set(m.strip() for m in re.findall(r"\d+(?:[.,]\d+)?\s*(?:kcal|kg|mg|g|ml|cc|分|秒|時間|日間|日|週間|か月|ヶ月|年間|年|歳|代|円|倍|%|種|選|個|本|杯|食|人|回|割|位|つ|品|kcal|km|cm|mm|g|L|l|万|千|億|割減|kg減|周年|時|号|等分|の|つ|項目|ステップ|STEP|step)?", title, flags=re.I))
        ns = set(n for n in ns if re.search(r"\d", n))
        for n in ns: nums[n] += 1
        # 名詞
        seen = set()
        for w in tk.tokenize(re.sub(r"【[^】]*】", " ", title)):
            pos = w.part_of_speech.split(",")
            if pos[0] != "名詞" or pos[1] in ("数", "非自立", "接尾", "代名詞"): continue
            s = w.surface
            if len(s) < 2 or s in STOP or re.fullmatch(r"[\d\W_]+", s): continue
            seen.add(s)
        for s in seen: nouns[s] += 1
    return nouns, nums, brackets

def fmt_n(n):
    return f"{n:,}" if isinstance(n, int) else "-"

def fmt_subs(n):
    if n is None: return "非公開"
    if n >= 10000: return f"{n/10000:.1f}万人"
    return f"{n:,}人"

def safe_name(s, n=30):
    s = re.sub(r'[\\/:*?"<>|\s]+', "_", s or "")
    return s[:n].strip("_") or "ch"

def md_table(rows):
    h = "| # | タイトル | CH名 | 登録者数 | 再生数 | 倍率 | 公開日 | 尺 | 型 | KW | サムネ |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
    out = []
    for i, r in enumerate(rows, 1):
        t = r["title"].replace("|", "｜")
        out.append(f"| {i} | [{t}]({r['url']}) | {r['channel'].replace('|','｜')} | {fmt_subs(r['subs'])} | {fmt_n(r['views'])} | **{r['ratio']:.1f}x** | {r['publishDate']} | {r['durationSec']//60}:{r['durationSec']%60:02d} | {r['type']} | {r['keywordsHit']} | [img]({r['thumb']}) |")
    return h + "\n".join(out) + "\n"

def counter_table(cnt, label, top=30):
    h = f"| 順位 | {label} | 出現本数 |\n|---|---|---|\n"
    return h + "\n".join(f"| {i} | {w} | {c} |" for i, (w, c) in enumerate(cnt.most_common(top), 1)) + "\n"

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(__file__), "..", ".cache_yt"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "output"))
    ap.add_argument("--no-thumbs", action="store_true")
    a = ap.parse_args()
    cache = Cache(a.cache)
    os.makedirs(a.out, exist_ok=True)
    thumb_dir = os.path.join(a.out, "thumbs_curry"); os.makedirs(thumb_dir, exist_ok=True)
    today = datetime.now(timezone.utc).date()

    # 1) 検索
    cands = {}  # videoId -> record
    hits = defaultdict(set)  # videoId -> set(keyword)
    all_kw = [(axis, kw, False) for axis, kws in KEYWORDS.items() for kw in kws] + \
             [(axis, kw, True) for axis, kws in KEYWORDS_REF.items() for kw in kws]
    for axis, kw, is_ref in all_kw:
        n0 = len(cands)
        for label, params, pages in PARAMS:
            for v in search_videos(kw, params, pages, cache):
                hits[v["videoId"]].add(kw)
                if v["videoId"] not in cands:
                    v["axis"] = axis; v["isRef"] = is_ref
                    cands[v["videoId"]] = v
        log(f"[search] {kw}: +{len(cands)-n0} (total {len(cands)})")

    # 2) 事前フィルタ（検索結果ベース）→ 詳細取得
    pre = []
    for vid, v in cands.items():
        if v["durationSec_s"] is not None and v["durationSec_s"] < MIN_DURATION: continue
        if v["relDays_s"] is not None and v["relDays_s"] > MAX_AGE_DAYS: continue
        if v["views_s"] is not None and v["views_s"] < MIN_VIEWS: continue
        pre.append(vid)
    log(f"[prefilter] {len(pre)} / {len(cands)}")

    detailed = []
    for i, vid in enumerate(pre):
        v = cands[vid]
        d = video_details(vid, cache)
        if d is None:
            # player が取れない場合は検索結果の値で近似
            if v["durationSec_s"] is None or v["views_s"] is None or v["relDays_s"] is None: continue
            d = {"title": v["title"], "lengthSeconds": v["durationSec_s"], "viewCount": v["views_s"],
                 "author": v["channel"], "channelId": v["channelId"],
                 "publishDate": (today - timedelta(days=v["relDays_s"])).isoformat() + "(approx)",
                 "category": None, "isLive": False, "keywords": []}
        if d["lengthSeconds"] < MIN_DURATION or d["viewCount"] < MIN_VIEWS or not d["publishDate"]: continue
        try:
            age = (today - datetime.strptime(d["publishDate"][:10], "%Y-%m-%d").date()).days
        except Exception:
            continue
        if age > MAX_AGE_DAYS: continue
        v.update(d); v["ageDays"] = age
        detailed.append(v)
        if (i + 1) % 50 == 0: log(f"[details] {i+1}/{len(pre)}")
    log(f"[details] kept {len(detailed)}")

    # 3) 登録者数（チャンネル単位でキャッシュ）
    subs_by_ch = {}
    for v in detailed:
        ch = v.get("channelId") or v["channel"]
        if ch not in subs_by_ch:
            s, handle = channel_subs(v["videoId"], cache)
            subs_by_ch[ch] = (s, handle)
        v["subs"], v["handle"] = subs_by_ch[ch]
    log(f"[subs] channels: {len(subs_by_ch)}")

    # 4) 倍率判定・整形
    rows = []; hidden = []
    for v in detailed:
        title = v.get("title") or cands[v["videoId"]]["title"]
        channel = v.get("author") or v["channel"]
        rec = {
            "videoId": v["videoId"], "title": title, "url": f"https://www.youtube.com/watch?v={v['videoId']}",
            "channel": channel, "channelId": v.get("channelId"), "handle": v.get("handle") or v.get("channelUrl"),
            "subs": v["subs"], "views": v["viewCount"], "publishDate": v["publishDate"][:10],
            "durationSec": v["lengthSeconds"], "ageDays": v["ageDays"], "category": v.get("category"),
            "thumb": f"https://i.ytimg.com/vi/{v['videoId']}/maxresdefault.jpg",
            "lang": lang_of(title, channel), "axis": v["axis"], "isRef": v["isRef"],
            "keywordsHit": " / ".join(sorted(hits[v["videoId"]])),
            "type": classify(title, channel, v.get("category"), v.get("keywords") or []),
        }
        if rec["subs"] is None or rec["subs"] == 0:
            hidden.append(rec); continue
        rec["ratio"] = rec["views"] / rec["subs"]
        rec["threshold"] = threshold(rec["subs"])
        if rec["ratio"] >= rec["threshold"]:
            rows.append(rec)
    rows.sort(key=lambda r: -r["ratio"])
    log(f"[select] passed {len(rows)}, hidden-subs {len(hidden)}")

    ja_1y = [r for r in rows if r["lang"] == "ja" and r["ageDays"] <= PRIMARY_AGE_DAYS]
    ja_2y = [r for r in rows if r["lang"] == "ja" and r["ageDays"] > PRIMARY_AGE_DAYS]
    foreign = [r for r in rows if r["lang"] != "ja"]

    # 1年以内の該当が少ないキーワードは2年まで補完
    kw_1y = Counter(); [kw_1y.update(r["keywordsHit"].split(" / ")) for r in ja_1y]
    all_jp_kws = [kw for kws in KEYWORDS.values() for kw in kws]
    few = [kw for kw in all_jp_kws if kw_1y[kw] < FEW_HITS]
    ja_supp = [r for r in ja_2y if any(kw in r["keywordsHit"].split(" / ") for kw in few)]

    main_rows = ja_1y + ja_supp
    for r in main_rows: r["period"] = "1年以内" if r["ageDays"] <= PRIMARY_AGE_DAYS else "1〜2年(補完)"

    # 5) 集計
    nouns, nums, brackets = word_stats(main_rows)
    by_type = defaultdict(list)
    for r in main_rows: by_type[r["type"]].append(r)
    type_stats = {}
    for t, rs in by_type.items():
        n, nu, b = word_stats(rs)
        type_stats[t] = {"n": len(rs), "nouns": n, "nums": nu, "brackets": b,
                         "views": sum(r["views"] for r in rs), "ratio_med": sorted(r["ratio"] for r in rs)[len(rs)//2] if rs else 0,
                         "ratio_avg": sum(r["ratio"] for r in rs)/len(rs) if rs else 0}

    # 6) サムネ（倍率上位30本）
    top = main_rows[:TOP_THUMBS]
    thumb_list = []; ok = 0; fail = 0
    for r in top:
        fn = f"{r['ratio']:.1f}_{safe_name(r['channel'])}_{r['videoId']}.jpg"
        r["thumbFile"] = fn
        thumb_list.append((fn, r["thumb"]))
        if a.no_thumbs: continue
        p = os.path.join(thumb_dir, fn)
        if os.path.exists(p) and os.path.getsize(p) > 0: ok += 1; continue
        try:
            rr = SESSION.get(r["thumb"], timeout=30, verify=VERIFY)
            if rr.status_code == 200 and rr.headers.get("content-type", "").startswith("image"):
                open(p, "wb").write(rr.content); ok += 1
            else:
                rr = SESSION.get(r["thumb"].replace("maxresdefault", "hqdefault"), timeout=30, verify=VERIFY)
                if rr.status_code == 200 and rr.headers.get("content-type", "").startswith("image"):
                    open(p, "wb").write(rr.content); ok += 1
                else: fail += 1
        except Exception as e:
            fail += 1
    with open(os.path.join(thumb_dir, "thumb_urls.txt"), "w", encoding="utf-8") as f:
        for fn, u in thumb_list: f.write(f"{fn}\t{u}\n")
    with open(os.path.join(thumb_dir, "download_thumbs.sh"), "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n# 倍率上位30本のサムネ(maxresdefault)をこのディレクトリに保存する\ncd \"$(dirname \"$0\")\"\nwhile IFS=$'\\t' read -r fn url; do\n  [ -s \"$fn\" ] && continue\n  curl -sSL -o \"$fn\" \"$url\" || curl -sSL -o \"$fn\" \"${url/maxresdefault/hqdefault}\"\n  echo \"saved $fn\"\ndone < thumb_urls.txt\n")
    os.chmod(os.path.join(thumb_dir, "download_thumbs.sh"), 0o755)
    log(f"[thumbs] ok {ok}, fail {fail}")

    # 7) 出力
    json.dump({"generated": today.isoformat(), "main": main_rows, "foreign": foreign, "hidden_subs": hidden,
               "candidates": len(cands), "prefiltered": len(pre), "detailed": len(detailed)},
              open(os.path.join(a.out, "youtube_curry_spice_trend.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    import csv
    with open(os.path.join(a.out, "youtube_curry_spice_trend.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["区分", "タイトル", "URL", "CH名", "登録者数", "再生数", "倍率", "公開日", "尺(秒)", "型", "ヒットKW", "軸", "期間", "言語", "サムネURL"])
        for r in main_rows + foreign:
            w.writerow(["参考枠" if r["lang"] != "ja" else "主枠", r["title"], r["url"], r["channel"], r["subs"], r["views"], f"{r['ratio']:.2f}", r["publishDate"], r["durationSec"], r["type"], r["keywordsHit"], r["axis"], r.get("period", "-"), r["lang"], r["thumb"]])

    # md
    L = []
    L.append(f"# YouTube横断「伸びた動画」収集レポート（カレー／スパイス／血糖値・腸活）\n")
    L.append(f"生成日: {today.isoformat()}　｜　データ源: YouTube InnerTube（検索・動画詳細・チャンネル情報）\n")
    L.append("## 抽出条件\n")
    L.append(f"- 検索キーワード: 13語（カレー軸6／スパイス軸4／血糖値・腸活軸3）× 5パターン（1年以内×関連順・再生順・新着順、期間指定なし×関連順・再生順）＋続きページ\n"
             f"- 公開1年以内を主枠。1年以内の該当が{FEW_HITS}本未満のキーワードは1〜2年前まで補完（「1〜2年(補完)」と表示）\n"
             f"- 180秒以下（ショート）は除外。ライブ配信アーカイブは含む\n"
             f"- 倍率 = 再生数 ÷ チャンネル登録者数。規模帯別基準: 10万人以上≧1倍／1万〜10万人≧2倍／1万人未満≧3倍\n"
             f"- ノイズ除去のため再生数{MIN_VIEWS:,}回未満は除外（追加の前提。極小チャンネルの数十回再生で倍率が跳ねるのを防ぐ）\n"
             f"- 登録者数非公開のチャンネルは倍率が算出できないため別掲\n"
             f"- 日本語チャンネルを主枠、英語・中国語圏は参考枠として別立て（タイトル・CH名の文字種で判定）\n")
    L.append("## 収集サマリー\n")
    L.append(f"| 項目 | 件数 |\n|---|---|\n| 検索でヒットしたユニーク動画 | {len(cands)} |\n| 事前フィルタ通過（尺・期間・再生数） | {len(pre)} |\n| 詳細取得後に条件内 | {len(detailed)} |\n| 倍率基準クリア（全言語） | {len(rows)} |\n| **主枠（日本語・1年以内）** | **{len(ja_1y)}** |\n| 主枠補完（日本語・1〜2年） | {len(ja_supp)} |\n| 参考枠（英語・中国語圏） | {len(foreign)} |\n| 登録者数非公開で判定不可 | {len(hidden)} |\n")
    L.append("### キーワード別 主枠ヒット数（1年以内）\n")
    L.append("| 軸 | キーワード | 1年以内 | 補完(1〜2年) |\n|---|---|---|---|\n")
    kw_supp = Counter(); [kw_supp.update(r["keywordsHit"].split(" / ")) for r in ja_supp]
    for axis, kws in KEYWORDS.items():
        for kw in kws:
            L.append(f"| {axis} | {kw} | {kw_1y[kw]} | {kw_supp[kw] if kw in few else '-'} |\n")
    L.append("\n（同一動画が複数キーワードにヒットした場合は各キーワードで計上）\n")

    L.append("\n## 主枠：日本語チャンネル（倍率順）\n")
    L.append("### 1年以内\n")
    L.append(md_table(ja_1y) if ja_1y else "該当なし\n")
    if ja_supp:
        L.append(f"\n### 1〜2年（補完枠：1年以内の該当が{FEW_HITS}本未満だったキーワード → {', '.join(few)}）\n")
        L.append(md_table(ja_supp))

    L.append("\n## 参考枠：英語・中国語圏チャンネル（倍率順）\n")
    L.append(md_table(foreign) if foreign else "該当なし\n")

    L.append("\n## 追加集計：タイトル頻出ワード（主枠 全{}本）\n".format(len(main_rows)))
    L.append("### 名詞（上位30）\n"); L.append(counter_table(nouns, "名詞", 30))
    L.append("\n### 数字表現（上位20）\n"); L.append(counter_table(nums, "数字表現", 20))
    L.append("\n### 【】内ワード（上位20）\n"); L.append(counter_table(brackets, "【】内", 20))

    L.append("\n## 追加集計：「専門家の解説型」vs「レシピ・料理型」\n")
    L.append("| 型 | 本数 | 合計再生数 | 倍率中央値 | 倍率平均 |\n|---|---|---|---|---|\n")
    for t in ["専門家の解説型", "レシピ・料理型"]:
        s = type_stats.get(t)
        if s: L.append(f"| {t} | {s['n']} | {s['views']:,} | {s['ratio_med']:.1f}x | {s['ratio_avg']:.1f}x |\n")
        else: L.append(f"| {t} | 0 | - | - | - |\n")
    L.append("\n（判定はタイトル・CH名・動画カテゴリのキーワードによる自動分類。レシピ／作り方／料理／簡単／材料 等→料理型、医師／管理栄養士／解説／研究／効果／血糖値 等→解説型）\n")
    for t in ["専門家の解説型", "レシピ・料理型"]:
        s = type_stats.get(t)
        if not s: continue
        L.append(f"\n### {t}（{s['n']}本）の頻出ワード\n")
        L.append("**名詞（上位15）**\n\n" + counter_table(s["nouns"], "名詞", 15))
        L.append("\n**数字表現（上位10）**\n\n" + counter_table(s["nums"], "数字表現", 10))
        L.append("\n**【】内（上位10）**\n\n" + counter_table(s["brackets"], "【】内", 10))
        L.append(f"\n**{t} 一覧（倍率順）**\n\n" + md_table(by_type[t]))

    L.append("\n## 倍率上位30本 サムネ画像\n")
    L.append(f"保存先: `COO/output/thumbs_curry/`　ファイル名: `{{倍率}}_{{チャンネル名}}_{{動画ID}}.jpg`\n\n")
    if fail and not ok:
        L.append(f"> ⚠️ この実行環境からは画像ホスト（i.ytimg.com）への接続が遮断されており、画像本体は保存できませんでした。`COO/output/thumbs_curry/download_thumbs.sh` を手元で実行すると同じファイル名で保存されます（URL一覧は `thumb_urls.txt`）。\n\n")
    L.append("| # | ファイル名 | サムネURL |\n|---|---|---|\n")
    for i, (fn, u) in enumerate(thumb_list, 1): L.append(f"| {i} | {fn} | {u} |\n")

    if hidden:
        L.append("\n## 別掲：登録者数非公開のため倍率判定不可（条件内・再生数順）\n")
        hidden.sort(key=lambda r: -r["views"])
        L.append("| # | タイトル | CH名 | 再生数 | 公開日 | 尺 |\n|---|---|---|---|---|---|\n")
        for i, r in enumerate(hidden[:30], 1):
            L.append(f"| {i} | [{r['title'].replace('|','｜')}]({r['url']}) | {r['channel']} | {r['views']:,} | {r['publishDate']} | {r['durationSec']//60}:{r['durationSec']%60:02d} |\n")

    L.append("\n---\n付随ファイル: `youtube_curry_spice_trend.csv`（全行）, `youtube_curry_spice_trend.json`（生データ）, `COO/scripts/yt_trend_collector.py`（再実行用）\n")
    with open(os.path.join(a.out, "youtube_curry_spice_trend.md"), "w", encoding="utf-8") as f: f.write("".join(L))
    log("[done]")

if __name__ == "__main__":
    main()
