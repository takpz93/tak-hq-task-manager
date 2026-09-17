#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自チャンネル分析: 登録者数・全動画台帳（長尺／ショート分離）・直近1年ランキング・直近公開分
使い方: python3 COO/scripts/yt_channel_audit.py --channel UCxxxx --out FILE.md [--since 2026-08-03] [--window-start 2025-09-18 --window-end 2026-09-18] [--prev "2026-08-03 全69本・登録9,670"]
"""
import argparse, csv, json, os, re, sys
from datetime import datetime, timezone, date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import Cache, it_post, walk, text, parse_duration, parse_views, parse_rel_days, parse_subs, parse_en_num, parse_en_date
from yt_reference_dental import clean

def log(*a): print(*a, file=sys.stderr, flush=True)

def lockup_rows(d):
    out = []
    for lk in walk(d, "lockupViewModel"):
        if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO": continue
        s = json.dumps(lk, ensure_ascii=False)
        md = lk.get("metadata", {}).get("lockupMetadataViewModel", {})
        parts = [p.get("text", {}).get("content", "") for row in md.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", []) for p in row.get("metadataParts", [])]
        dur = re.search(r'"text":\s*"(\d+:\d+(?::\d+)?)"', s)
        out.append({"videoId": lk.get("contentId"), "title": md.get("title", {}).get("content", ""),
                    "views_s": next((parse_views(p) for p in parts if "回視聴" in p), None),
                    "relDays_s": next((parse_rel_days(p) for p in parts if "前" in p), None),
                    "durationSec": parse_duration(dur.group(1)) if dur else None, "kind": "長尺"})
    return out

def shorts_rows(d):
    out = []
    for lk in walk(d, "shortsLockupViewModel"):
        vid = next((e.get("videoId") for e in walk(lk, "reelWatchEndpoint")), None)
        acc = lk.get("accessibilityText", "")
        m = re.match(r"(.*), ([\d.,]+(?:万|億)?回視聴) - ", acc)
        out.append({"videoId": vid, "title": m.group(1) if m else acc, "views_s": parse_views(m.group(2)) if m else None, "relDays_s": None, "durationSec": None, "kind": "ショート"})
    return out

def paginate(cid, params, key, parser, cache, max_pages=60):
    d = it_post("browse", {"browseId": cid, "params": params}, cache, f"audit_{cid}_{key}_p1")
    rows = []; page = 1; hdr = d or {}
    while d:
        rows += parser(d)
        tok = None
        for c in walk(d, "continuationItemRenderer"):
            tok = (c.get("continuationEndpoint") or {}).get("continuationCommand", {}).get("token"); break
        if not tok or page >= max_pages: break
        page += 1
        d = it_post("browse", {"continuation": tok}, cache, f"audit_{cid}_{key}_p{page}")
    return hdr, rows

def details(vid, cache):
    body = {"videoId": vid, "context": {"client": {"clientName": "WEB", "clientVersion": "2.20250101.00.00", "hl": "en", "gl": "US"}}}
    d = it_post("next", body, cache, f"nexten_{vid}")
    if not d: return None
    prim = next(walk(d, "videoPrimaryInfoRenderer"), None)
    if not prim: return None
    vc = next(walk(prim, "videoViewCountRenderer"), {}) or {}
    s = json.dumps(d)
    m = re.search(r'like this video along with ([\d,]+) other people', s)
    likes = int(m.group(1).replace(",", "")) if m else None
    comments = None
    for ep in walk(d, "engagementPanelTitleHeaderRenderer"):
        if text(ep.get("title")) == "Comments" and ep.get("contextualInfo"):
            comments = parse_en_num(text(ep.get("contextualInfo"))); break
    if comments is None:
        # 初回応答に件数が無い場合はコメント欄の続きを取得してヘッダーの件数を読む
        toks = []
        for c in walk(d, "continuationItemRenderer"):
            ep = c.get("continuationEndpoint") or {}
            if ep.get("commandMetadata", {}).get("webCommandMetadata", {}).get("apiUrl", "").endswith("/next"):
                t = ep.get("continuationCommand", {}).get("token")
                if t: toks.append(t)
        # コメント欄の続きトークンは "Eg0S..."（動画IDを含む）で始まる。無ければ最初の /next トークン
        tok = next((t for t in toks if t.startswith("Eg")), toks[0] if toks else None)
        if tok:
            d2 = it_post("next", {"continuation": tok, "context": body["context"]}, cache, f"nextcmt_{vid}")
            if d2:
                for h in walk(d2, "commentsHeaderRenderer"):
                    comments = parse_en_num(text(h.get("countText")) or text(h.get("commentsCount"))); break
                if comments is None:
                    s2 = json.dumps(d2)
                    m2 = re.search(r'"commentCount":\s*\{"simpleText":\s*"([\d,.KM]+)"', s2) or re.search(r'"([\d,.KM]+) Comments?"', s2)
                    if m2: comments = parse_en_num(m2.group(1))
                    elif '"commentsHeaderRenderer"' not in s2 and "No comments" in s2: comments = 0
    return {"viewCount": parse_en_num(text(vc.get("viewCount"))), "publishDate": parse_en_date(text(prim.get("dateText"))),
            "likes": likes, "comments": comments, "title_en": text(prim.get("title"))}

def n(x): return f"{x:,}" if isinstance(x, int) else "取得不可"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--since", default="2026-08-03"); ap.add_argument("--window-start", default="2025-09-18"); ap.add_argument("--window-end", default="2026-09-18")
    ap.add_argument("--prev", default="2026-08-03 取得: 全69本・登録9,670人"); ap.add_argument("--handle", default="@watakyu616")
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(__file__), "..", ".cache_yt"))
    a = ap.parse_args(); cache = Cache(a.cache); today = datetime.now(timezone.utc).date()
    # 今回は取得の再現性のため browse キャッシュを使わず毎回取り直す
    for f in os.listdir(cache.d):
        if f.startswith(f"audit_{a.channel}_"): os.remove(os.path.join(cache.d, f))
    hdr, longs = paginate(a.channel, "EgZ2aWRlb3PyBgQKAjoA", "videos", lockup_rows, cache)
    _, shorts = paginate(a.channel, "EgZzaG9ydHPyBgUKA5oBAA==", "shorts", shorts_rows, cache)
    hj = json.dumps(hdr.get("header", {}), ensure_ascii=False)
    m = re.search(r"チャンネル登録者数 ([\d.,]+(?:万|億)?人)", hj); subs = parse_subs(m.group(0)) if m else None
    m2 = re.search(r"([\d,]+) 本の動画", hj); nvid = int(m2.group(1).replace(",", "")) if m2 else None
    name = (hdr.get("header", {}).get("pageHeaderRenderer", {}) or {}).get("pageTitle")
    log(f"[channel] {name} subs={subs} videos={nvid} long={len(longs)} shorts={len(shorts)}")
    allv = [v for v in longs + shorts if v["videoId"]]
    seen = set(); allv = [v for v in allv if not (v["videoId"] in seen or seen.add(v["videoId"]))]
    for i, v in enumerate(allv):
        # 直近公開分は数値が動くので next キャッシュを捨てて取り直す
        if v["relDays_s"] is not None and v["relDays_s"] <= 60:
            p = cache.path(f"nexten_{v['videoId']}")
            if os.path.exists(p): os.remove(p)
        d = details(v["videoId"], cache) or {}
        v.update(d); v["url"] = f"https://www.youtube.com/watch?v={v['videoId']}"
        if v.get("viewCount") is None: v["viewCount"] = v.get("views_s")
        if (i + 1) % 20 == 0: log(f"[details] {i+1}/{len(allv)}")
    # 尺で分離（ショートタブ由来はショート。動画タブ由来でも180秒以下は短尺として別扱い）
    for v in allv:
        if v["kind"] == "長尺" and v["durationSec"] is not None and v["durationSec"] <= 180: v["kind"] = "短尺(180秒以下)"
    longv = sorted([v for v in allv if v["kind"] == "長尺"], key=lambda v: v.get("publishDate") or "", reverse=True)
    shortv = sorted([v for v in allv if v["kind"] != "長尺"], key=lambda v: v.get("publishDate") or "", reverse=True)
    ws, we, since = a.window_start, a.window_end, a.since
    win = [v for v in longv if v.get("publishDate") and ws <= v["publishDate"] <= we and isinstance(v.get("viewCount"), int)]
    avg = sum(v["viewCount"] for v in win) / len(win) if win else 0
    for v in win: v["ratio"] = v["viewCount"] / avg if avg else 0
    rank = sorted(win, key=lambda v: -v["viewCount"])
    recent = [v for v in allv if v.get("publishDate") and v["publishDate"] >= since]
    for v in recent: v["ageDays"] = (today - datetime.strptime(v["publishDate"], "%Y-%m-%d").date()).days
    recent.sort(key=lambda v: v["publishDate"], reverse=True)

    def ledger(rows, dur=True):
        h = "| # | 公開日 | タイトル | 動画URL | 再生数 | 高評価数 | コメント数 |" + (" 動画尺(秒) |" if dur else "") + "\n|---|---|---|---|---|---|---|" + ("---|" if dur else "") + "\n"
        for i, v in enumerate(rows, 1):
            h += f"| {i} | {v.get('publishDate') or '取得不可'} | {clean(v['title'])} | {v['url']} | {n(v.get('viewCount'))} | {n(v.get('likes'))} | {n(v.get('comments'))} |" + (f" {v['durationSec'] if v['durationSec'] is not None else '取得不可'} |" if dur else "") + "\n"
        return h
    L = [f"# 綿久 自チャンネル分析（{today.isoformat()} 取得）\n\n", f"チャンネル: {name}（https://www.youtube.com/{a.handle} ／ {a.channel}）　データ源: YouTube InnerTube（browse / next）\n\n"]
    L.append("## 1. 現在の登録者数・総動画本数\n\n")
    L.append(f"| 項目 | 今回（{today.isoformat()}） | 前回（{a.prev}） |\n|---|---|---|\n| 登録者数 | {n(subs)}人 | — |\n| 総動画本数（チャンネル表示） | {n(nvid)} | — |\n| 取得できた本数 | {len(allv)}（長尺 {len(longv)}／ショート・短尺 {len(shortv)}） | — |\n\n")
    L.append("※ 高評価数は英語UIの「like this video along with N other people」から、コメント数はコメント欄ヘッダーの件数から取得。非公開・0件の場合は「取得不可」。\n\n")
    L.append(f"## 2. 全動画台帳（長尺のみ・公開日の新しい順、{len(longv)}本）\n\n" + ledger(longv))
    L.append(f"\n## 3. ショート・短尺（180秒以下）台帳（{len(shortv)}本、公開日の新しい順。以降の集計から除外）\n\n" + ledger(shortv, dur=True))
    L.append(f"\n## 4. 直近1年（{ws}〜{we}）長尺 再生数ランキング（{len(rank)}本）\n\n")
    L.append(f"直近1年の長尺平均再生数: **{avg:,.0f}回**（{len(win)}本の平均）\n\n| 順位 | 公開日 | タイトル | 再生数 | 対平均倍率 | 高評価数 | コメント数 | 動画尺(秒) | 動画URL |\n|---|---|---|---|---|---|---|---|---|\n")
    for i, v in enumerate(rank, 1):
        L.append(f"| {i} | {v['publishDate']} | {clean(v['title'])} | {n(v['viewCount'])} | {v['ratio']:.2f}倍 | {n(v.get('likes'))} | {n(v.get('comments'))} | {v['durationSec'] if v['durationSec'] is not None else '取得不可'} | {v['url']} |\n")
    L.append(f"\n## 5. {since} 以降に公開された動画（{len(recent)}本、公開日の新しい順）\n\n| # | 公開日 | 経過日数 | 区分 | タイトル | 再生数 | 高評価数 | コメント数 | 動画尺(秒) | 対平均倍率（長尺のみ） | 動画URL |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
    for i, v in enumerate(recent, 1):
        rt = f"{v['ratio']:.2f}倍" if v.get("ratio") else "—"
        L.append(f"| {i} | {v['publishDate']} | {v['ageDays']}日 | {v['kind']} | {clean(v['title'])} | {n(v.get('viewCount'))} | {n(v.get('likes'))} | {n(v.get('comments'))} | {v['durationSec'] if v['durationSec'] is not None else '取得不可'} | {rt} | {v['url']} |\n")
    L.append("\n---\n注記: 再生数・高評価数・コメント数・公開日は取得時点のスナップショット。ショートは尺がチャンネル一覧に表示されないため「取得不可」。\n")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("".join(L))
    with open(re.sub(r"\.md$", ".csv", a.out), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["区分", "公開日", "タイトル", "動画URL", "再生数", "高評価数", "コメント数", "動画尺(秒)", "対平均倍率(直近1年長尺)"])
        for v in longv + shortv: w.writerow([v["kind"], v.get("publishDate"), v["title"], v["url"], v.get("viewCount"), v.get("likes"), v.get("comments"), v["durationSec"], f"{v['ratio']:.2f}" if v.get("ratio") else ""])
    log(f"[done] long={len(longv)} short={len(shortv)} window={len(win)} avg={avg:.0f} recent={len(recent)} -> {a.out}")

if __name__ == "__main__":
    main()
