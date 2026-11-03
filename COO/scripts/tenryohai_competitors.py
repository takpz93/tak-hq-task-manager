#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天領盃 タスクB: 競合チャンネルの直近12か月の動画を取得し JSON に保存（InnerTube browse / next）
使い方: python3 COO/scripts/tenryohai_competitors.py --out FILE.json [--cache DIR] [--days 365]
"""
import argparse, json, os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import Cache, it_post, walk, text, parse_subs
from yt_channel_audit import lockup_rows, details
import re

def log(*a): print(*a, file=sys.stderr, flush=True)

COMPETITORS = [
    ("サケラボちゃんねる", "@sakelabotokyo", "UCEGN4Z0hbYqodLNcgub1agw"),
    ("酒泉洞チャンネル", "@shusendosake", "UCdmtg1-dmbTjqGY93B6Z-TA"),
    ("日本酒王子 近藤悠一", "@nihonshuouji_kondo", "UCwC5E22_AJY_w9cjfRCdHwg"),
    ("CROSSROAD LAB", "@crossroadlab", "UCu0ePEW18Q8DUkdJzuXywYw"),
]

def channel_videos(cid, cache, max_days, max_pages=40):
    d = it_post("browse", {"browseId": cid, "params": "EgZ2aWRlb3PyBgQKAjoA"}, cache, f"comp_{cid}_videos_p1")
    if not d: return None, []
    hdr = json.dumps(d.get("header", {}), ensure_ascii=False)
    md = (d.get("metadata") or {}).get("channelMetadataRenderer") or {}
    m = re.search(r"チャンネル登録者数 ([\d.,]+(?:万|億)?人)", hdr)
    info = {"name": md.get("title") or "", "subs": parse_subs(m.group(0)) if m else None,
            "nvid": int(re.search(r"([\d,]+) 本の動画", hdr).group(1).replace(",", "")) if re.search(r"([\d,]+) 本の動画", hdr) else None}
    rows = []; page = 1
    while d:
        for lk in walk(d, "lockupViewModel"):
            if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO": continue
            src = json.dumps(lk.get("contentImage", {}))
            mm = re.search(r'/vi(?:_webp)?/[^/]+/([a-z0-9_]+)\.(?:jpg|webp)', src)
            for r in lockup_rows({"lockupViewModel": lk}):
                r["thumbKind"] = mm.group(1) if mm else None; rows.append(r)
        # 一覧は新しい順。ページ内の全動画が期間外なら打ち切り
        if rows and all(r["relDays_s"] is not None and r["relDays_s"] > max_days + 60 for r in rows[-30:]): break
        tok = next(((c.get("continuationEndpoint") or {}).get("continuationCommand", {}).get("token") for c in walk(d, "continuationItemRenderer")), None)
        if not tok or page >= max_pages: break
        page += 1
        d = it_post("browse", {"continuation": tok}, cache, f"comp_{cid}_videos_p{page}")
    return info, rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(__file__), "..", ".cache_yt"))
    a = ap.parse_args(); cache = Cache(a.cache); today = datetime.now(timezone.utc).date()
    out = []
    for name, handle, cid in COMPETITORS:
        info, rows = channel_videos(cid, cache, a.days)
        if info is None: log(f"[{name}] 取得失敗"); continue
        log(f"[{name}] subs={info['subs']} listed={len(rows)}")
        vids = []
        for r in rows:
            if not r["videoId"]: continue
            if r["relDays_s"] is not None and r["relDays_s"] > a.days + 60: continue   # 表示の「1年前」は丸めなので余裕を持つ
            d = details(r["videoId"], cache) or {}
            pub = d.get("publishDate")
            if not pub: continue
            age = (today - datetime.strptime(pub, "%Y-%m-%d").date()).days
            if age > a.days: continue
            vids.append({"videoId": r["videoId"], "title": r["title"], "publishDate": pub, "ageDays": age,
                         "durationSec": r["durationSec"], "views": d.get("viewCount") if d.get("viewCount") is not None else r["views_s"],
                         "likes": d.get("likes"), "comments": d.get("comments"), "thumbKind": r["thumbKind"]})
        log(f"[{name}] within {a.days}d: {len(vids)}")
        out.append({"name": info["name"] or name, "label": name, "handle": handle, "channelId": cid, "subs": info["subs"], "nvid": info["nvid"], "videos": vids})
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump({"generated": today.isoformat(), "channels": out}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("[done]", a.out)

if __name__ == "__main__":
    main()
