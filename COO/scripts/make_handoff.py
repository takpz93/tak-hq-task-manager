#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フル版レポート(md/json)から、別エージェントに渡すための圧縮版 md を生成する"""
import json, re, os
OUT = os.path.join(os.path.dirname(__file__), "..", "output")
d = json.load(open(os.path.join(OUT, "youtube_curry_spice_trend.json"), encoding="utf-8"))
src = open(os.path.join(OUT, "youtube_curry_spice_trend.md"), encoding="utf-8").read()
def subs(n): return "非公開" if n is None else (f"{n/10000:.1f}万" if n >= 10000 else f"{n:,}")
def dur(s): return f"{s//60}:{s%60:02d}"
def cell(x): return re.sub(r"\s+", " ", x or "").replace("|", "｜").strip()
def table(rows, lang=False):
    h = "| 倍率 | タイトル | URL | CH名 | 登録者 | 再生数 | 公開日 | 尺 | 型 | ヒットKW |" + (" 言語 |" if lang else "") + "\n|---|---|---|---|---|---|---|---|---|---|" + ("---|" if lang else "") + "\n"
    L = {"ja": "日", "en": "英", "zh": "中", "other": "他"}
    for r in rows:
        h += f"| {r['ratio']:.1f}x | {cell(r['title'])} | {r['url']} | {cell(r['channel'])} | {subs(r['subs'])} | {r['views']:,} | {r['publishDate']} | {dur(r['durationSec'])} | {r['type'][:3]} | {r['keywordsHit']} |" + (f" {L.get(r['lang'], r['lang'])} |" if lang else "") + "\n"
    return h
def section(title):
    m = re.search(r"### " + re.escape(title) + r".*?\n((?:\|.*\n)+)", src); return m.group(1) if m else ""
def cnt(tb, n): return "、".join(f"{l.split('|')[2].strip()}({l.split('|')[3].strip()})" for l in tb.splitlines()[2:][:n])
main = d["main"]; m1 = [r for r in main if r["period"] == "1年以内"]; m2 = [r for r in main if r["period"] != "1年以内"]
out = []
out.append("# YouTube横断「伸びた動画」収集レポート（カレー／スパイス／血糖値・腸活）引き継ぎ版\n")
out.append(f"生成日: {d['generated']}　データ源: YouTube InnerTube（search/next）。フル版: COO/output/youtube_curry_spice_trend.md, .csv, .json\n")
out.append("""
## 抽出条件
- 検索KW 13語（カレー軸: カレー 健康／カレー 血糖値／スパイスカレー 健康／カレー粉／カレールー 比較／インドカレー 健康、スパイス軸: ターメリック 効果／クミン 効果／スパイス 効果 健康／スパイス 腸内環境、血糖値・腸活軸: 血糖値 上げない 食べ方／白米 血糖値 対策／腸活 レシピ）× 5パターン（1年以内×関連順・再生順・新着順、期間なし×関連順・再生順）＋続きページ。参考枠用に英語4語（turmeric benefits / curry health benefits / spices gut health / blood sugar rice）
- 公開1年以内が主枠。1年以内の該当が5本未満のKWは1〜2年前まで補完
- 180秒以下は除外。倍率 = 再生数 ÷ 登録者数。基準: 10万人以上≧1倍／1万〜10万人≧2倍／1万人未満≧3倍
- 追加の前提: 再生数1,000回未満は除外。タイトルにトピック語（カレー／スパイス／粉／食材／血糖値／腸活／米 等）を含まないものは別掲。登録者非公開は判定不可で別掲
- 言語判定: 英語UIで取得した原題に仮名が残れば日本語。海外動画は原題で表示
- 型判定: タイトル・CH名のキーワードで「専門家の解説型」「レシピ・料理型」に二分（レシピ／作り方／常備菜／混ぜるだけ／料理名のみ／料理系CH→料理型、医師／栄養士／解説／研究／効果／血糖値／クリニック系CH→解説型）
""")
out.append("## 収集サマリー\n" + re.search(r"## 収集サマリー\n((?:\|.*\n)+)", src).group(1))
out.append("\n### キーワード別 主枠ヒット数\n" + section("キーワード別 主枠ヒット数"))
out.append(f"\n## 主枠：日本語チャンネル・1年以内（{len(m1)}本、倍率順）\n" + table(m1))
if m2: out.append(f"\n## 主枠補完：日本語・1〜2年（{len(m2)}本）\n" + table(m2))
out.append(f"\n## 参考枠：英語・中国語圏・その他言語（{len(d['foreign'])}本、倍率順）\n" + table(d["foreign"], lang=True))
out.append(f"\n## 別掲：倍率基準クリアだがタイトルにトピック語なし（{len(d['offtopic'])}本、参考）\n" + table(d["offtopic"], lang=True))
out.append("\n## 追加集計：タイトル頻出ワード（主枠 全%d本、出現本数）\n" % len(main))
out.append("- 名詞: " + cnt(section("名詞（上位30）"), 30) + "\n")
out.append("- 数字表現: " + cnt(section("数字表現（上位20）"), 20) + "\n")
out.append("- 【】内: " + cnt(section("【】内ワード（上位20）"), 20) + "\n")
out.append("\n## 追加集計：型別\n" + re.search(r"## 追加集計：「専門家の解説型」vs「レシピ・料理型」\n((?:\|.*\n)+)", src).group(1))
for t in ["専門家の解説型", "レシピ・料理型"]:
    m = re.search(r"### " + t + r"（(\d+)本）の頻出ワード\n\*\*名詞（上位15）\*\*\n\n((?:\|.*\n)+)\n\*\*数字表現（上位10）\*\*\n\n((?:\|.*\n)+)\n\*\*【】内（上位10）\*\*\n\n((?:\|.*\n)+)", src)
    if m: out.append(f"\n### {t}（{m.group(1)}本）\n- 名詞: {cnt(m.group(2), 15)}\n- 数字表現: {cnt(m.group(3), 10)}\n- 【】内: {cnt(m.group(4), 10)}\n")
out.append("\n## 倍率上位30本 サムネ（ファイル名 → URL）\n保存先 COO/output/thumbs_curry/。実行環境から画像ホスト(i.ytimg.com)が遮断され未保存。同フォルダの download_thumbs.sh を手元で実行すると保存される。\n\n")
for l in open(os.path.join(OUT, "thumbs_curry", "thumb_urls.txt"), encoding="utf-8"):
    fn, u = l.rstrip("\n").split("\t"); out.append(f"- {fn} → {u}\n")
if d["hidden_subs"]:
    out.append("\n## 別掲：登録者数非公開（判定不可）\n")
    for r in sorted(d["hidden_subs"], key=lambda r: -r["views"]): out.append(f"- {cell(r['title'])} | {cell(r['channel'])} | {r['views']:,}回 | {r['publishDate']} | {r['url']}\n")
s = "".join(out)
open(os.path.join(OUT, "youtube_curry_spice_trend_handoff.md"), "w", encoding="utf-8").write(s)
print(len(s), "chars,", s.count("\n"), "lines")
