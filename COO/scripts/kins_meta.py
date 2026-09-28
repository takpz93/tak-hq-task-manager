#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KINS 長尺全本のメタデータ（videoId/タイトル/公開日/尺/再生数/サムネURL）を InnerTube から収集して JSON に保存"""
import json, os, re, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import Cache, it_post, walk
from yt_channel_audit import lockup_rows, details
CID = "UCXAU7ks-wPVoFJykHn08zvA"
S = sys.argv[1]; OUT = sys.argv[2]
cache = Cache(S)
for f in os.listdir(cache.d):
    if f.startswith(f"kmeta_{CID}_"): os.remove(os.path.join(cache.d, f))
d = it_post("browse", {"browseId": CID, "params": "EgZ2aWRlb3PyBgQKAjoA"}, cache, f"kmeta_{CID}_p1")
hj = json.dumps(d.get("header", {}), ensure_ascii=False)
subs = re.search(r"チャンネル登録者数 ([^\"]+?人)", hj); nvid = re.search(r"([\d,]+) 本の動画", hj)
vids = []; page = 1
while d:
    for lk in walk(d, "lockupViewModel"):
        if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO": continue
        r = lockup_rows({"lockupViewModel": lk})[0]
        src = json.dumps(lk.get("contentImage", {}))
        m = re.search(r'/vi(?:_webp)?/[^/]+/([a-z0-9_]+)\.(?:jpg|webp)', src); r["thumbKind"] = m.group(1) if m else None
        vids.append(r)
    tok = None
    for c in walk(d, "continuationItemRenderer"):
        tok = (c.get("continuationEndpoint") or {}).get("continuationCommand", {}).get("token"); break
    if not tok: break
    page += 1; d = it_post("browse", {"continuation": tok}, cache, f"kmeta_{CID}_p{page}")
print(f"[list] {len(vids)} videos, subs={subs.group(1) if subs else None}, count={nvid.group(1) if nvid else None}", file=sys.stderr)
longs = [v for v in vids if v["videoId"] and v["durationSec"] and v["durationSec"] > 180]
for i, v in enumerate(longs):
    if v["relDays_s"] is not None and v["relDays_s"] <= 45:
        p = cache.path(f"nexten_{v['videoId']}")
        if os.path.exists(p): os.remove(p)
    v.update(details(v["videoId"], cache) or {})
    if not isinstance(v.get("viewCount"), int): v["viewCount"] = v.get("views_s")
    v["thumb"] = f"https://i.ytimg.com/vi/{v['videoId']}/" + ("maxresdefault.jpg" if v.get("thumbKind") == "hq720" else "hqdefault.jpg")
    v["url"] = f"https://www.youtube.com/watch?v={v['videoId']}"
    if (i + 1) % 25 == 0: print(f"[details] {i+1}/{len(longs)}", file=sys.stderr)
json.dump({"subs": subs.group(1) if subs else None, "count": nvid.group(1) if nvid else None, "n_all": len(vids), "long": longs},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"[done] long={len(longs)} -> {OUT}", file=sys.stderr)
