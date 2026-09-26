#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""③ テーマ別レポートの統合 と ④ タイトル頻出ワード集計（③の母集団のみ）"""
import json, glob, os, re, sys, statistics, unicodedata
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_reference_dental import clean, fmt_subs, scale
from yt_trend_collector import STOP

TODAY = date.today().isoformat()
OUT = "clients/KINS/output"
themes = sorted(glob.glob(f"{OUT}/themes/config_*.json"))

def dur(s): return f"{s//60}:{s%60:02d}" if isinstance(s, int) else ""

L3 = [f"# KINS 参考動画 8テーマ横断（{TODAY}）\n\n対象外チャンネル: 【下川先生】の菌ケア大学（UCXAU7ks-wPVoFJykHn08zvA）は除外　データ源: YouTube InnerTube（search / next）\n\n"]
L3.append("条件: 公開1年以内（1年以内で15本未満のテーマは最大2年まで拡張し公開日で判別）／180秒超のみ／倍率 = 再生数÷登録者数 が 大規模(10万人以上)1倍・中規模(1万〜10万)2倍・小規模(1万未満)3倍 以上／再生数1,000回未満は除外／各テーマ最大15本（倍率順）／サムネURLは一覧にHD版がある動画は maxresdefault、無ければ hqdefault。\n\n")
L4 = [f"# KINS タイトル頻出ワード（{TODAY}）\n\n母集団: `KINS_参考動画_8テーマ_20260926.md` に掲載した動画のみ（テーマごと）。名詞・複合語を形態素解析（janome）で切り出し、出現2本以上のみ掲載。出現1本のワードはエビデンスなしとして除外。\n\n"]
from janome.tokenizer import Tokenizer
tk = Tokenizer()
COMP = sorted(["血糖値スパイク", "血糖値", "HbA1c", "糖尿病", "食べ方", "食べる順番", "食後", "眠気", "口臭", "マウスウォッシュ", "歯周病", "歯磨き", "グルテンフリー", "グルテン", "米粉パン", "米粉", "小麦", "小麦粉", "発酵食品", "食べ合わせ", "ヨーグルト", "納豆", "味噌", "キムチ", "コンビニ", "セブンイレブン", "セブン", "ローソン", "ファミマ", "添加物", "食品添加物", "腸活", "腸内環境", "腸内細菌", "サプリ", "サプリメント", "整腸剤", "乳酸菌", "ビフィズス菌", "酪酸菌", "ドラッグストア", "冷え性", "冷え", "温活", "体温", "血流", "自律神経", "乳化剤", "人工甘味料", "甘味料", "アスパルテーム", "保存料", "着色料", "管理栄養士", "栄養士", "医師", "専門医", "内科医", "薬剤師", "現役", "徹底解説", "解説", "おすすめ", "ランキング", "TOP5", "5選", "3選", "10選", "7選", "危険", "危ない", "衝撃", "本当", "真実", "理由", "原因", "対策", "改善", "方法", "習慣", "選び方", "買ってはいけない", "食べてはいけない", "知らない", "9割", "保存版", "最強", "最新", "市販", "効果"], key=len, reverse=True)
COMP_RE = re.compile("|".join(re.escape(c) for c in COMP))
def words(title):
    t = unicodedata.normalize("NFKC", title); seen = set(COMP_RE.findall(t)); rest = COMP_RE.sub(" ", t)
    for w in tk.tokenize(rest):
        pos = w.part_of_speech.split(",")
        if pos[0] != "名詞" or pos[1] in ("数", "非自立", "接尾", "代名詞"): continue
        s = w.surface
        if len(s) < 2 or s in STOP or re.fullmatch(r"[\d\W_]+", s): continue
        seen.add(s)
    return seen

for cf in themes:
    cfg = json.load(open(cf, encoding="utf-8")); key = os.path.basename(cf)[7:-5]
    jp = cfg["out"][:-3] + ".json"
    d = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else {"final": []}
    rows = d["final"]; ext = any(r["ageDays"] > 365 for r in rows)
    L3.append(f"## テーマ{key}（検索語: {' / '.join(cfg['keywords'])}）\n\n")
    L3.append(f"該当 {len(rows)}本" + ("（1年以内が15本未満のため最大2年まで拡張。公開日で判別）" if ext else "") + "\n\n")
    if not rows: L3.append("**0本**（条件を満たす動画なし。条件は緩めていない）\n\n"); continue
    L3.append("| # | タイトル | チャンネル名 | 登録者数 | 再生数 | 倍率 | 公開日 | 尺 | URL | サムネURL | サムネURL(hq720) |\n|---|---|---|---:|---:|---:|---|---:|---|---|---|\n")
    for i, r in enumerate(rows, 1):
        L3.append(f"| {i} | {clean(r['title'])} | {clean(r['channel'])} | {fmt_subs(r['subs'])} | {r['viewCount']:,} | {r['ratio']:.2f} | {r['publishDate']} | {dur(r['durationSec_s'])} | {r['url']} | {r['thumb']} | https://i.ytimg.com/vi/{r['videoId']}/hq720.jpg |\n")
    L3.append("\n")
    # ④
    n = len(rows); idx = {}
    for r in rows:
        for w in words(r["title"]): idx.setdefault(w, []).append(r)
    items = [(w, rs) for w, rs in idx.items() if len(rs) >= 2]
    items.sort(key=lambda x: (-len(x[1]), -statistics.median([r["ratio"] for r in x[1]])))
    L4.append(f"## テーマ{key}（母数 {n}本）\n\n")
    if not items: L4.append("出現2本以上のワードなし\n\n"); continue
    L4.append("| ワード | 出現本数 | 母数 | 出現率 | そのワードを含む動画の倍率（中央値） | 最高倍率の動画 |\n|---|---:|---:|---:|---:|---|\n")
    for w, rs in items:
        top = max(rs, key=lambda r: r["ratio"])
        L4.append(f"| {w} | {len(rs)} | {n} | {len(rs)/n*100:.0f}% | {statistics.median([r['ratio'] for r in rs]):.2f} | {clean(top['title'])[:50]}（{top['ratio']:.2f}倍） |\n")
    L4.append("\n")
open(f"{OUT}/KINS_参考動画_8テーマ_20260926.md", "w", encoding="utf-8").write("".join(L3))
open(f"{OUT}/KINS_頻出ワード_20260926.md", "w", encoding="utf-8").write("".join(L4))
print("assembled")
