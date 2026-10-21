#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考チャンネルの通常動画一覧＋字幕（自動生成含む）の取得

- 動画タブを全件たどり、180秒以下を除外
- 公開1年以内を全件。1年以内が --min 本未満なら、2年以内の再生数上位で --min 本まで補う
- 字幕は InnerTube の get_transcript（youtubei.googleapis.com）で取得。取れない動画は transcript=None
- 出力: --out に videos.json（一覧＋字幕セグメント）

使い方:
  python3 COO/scripts/yt_channel_transcripts.py --channel UCxxxx --out DIR [--cache DIR] [--min 10]
"""
import argparse, json, os, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import Cache, it_post, walk, text
from yt_channel_audit import paginate, lockup_rows, details

def log(*a): print(*a, file=sys.stderr, flush=True)

def transcript(vid, cache):
    d = it_post("next", {"videoId": vid}, cache, f"nextja_{vid}")
    if not d: return None
    ep = next(walk(d, "getTranscriptEndpoint"), None)
    if not ep or not ep.get("params"): return None
    t = it_post("get_transcript", {"params": ep["params"]}, cache, f"transcript_{vid}")
    if not t: return None
    segs = []
    for s in walk(t, "transcriptSegmentRenderer"):
        body = text(s.get("snippet")).strip()
        if body:
            segs.append({"t": text(s.get("startTimeText")), "ms": int(s.get("startMs", 0)), "text": body})
    return segs or None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(__file__), "..", ".cache_yt"))
    ap.add_argument("--min", type=int, default=10)
    a = ap.parse_args(); cache = Cache(a.cache); os.makedirs(a.out, exist_ok=True)
    today = datetime.now(timezone.utc).date()
    y1, y2 = str(today - timedelta(days=365)), str(today - timedelta(days=730))

    _, rows = paginate(a.channel, "EgZ2aWRlb3PyBgQKAjoA", "videos", lockup_rows, cache)
    rows = [v for v in rows if v["videoId"] and (v["durationSec"] or 0) > 180]
    log(f"[list] long videos: {len(rows)}")
    for v in rows:
        v.update(details(v["videoId"], cache) or {})
        v["url"] = f"https://www.youtube.com/watch?v={v['videoId']}"
        if v.get("viewCount") is None: v["viewCount"] = v.get("views_s")

    within1 = [v for v in rows if (v.get("publishDate") or "") >= y1]
    if len(within1) >= a.min:
        picked, rule = within1, "公開1年以内の全件"
    else:
        rest = sorted([v for v in rows if y2 <= (v.get("publishDate") or "") < y1], key=lambda v: -(v.get("viewCount") or 0))
        picked = within1 + rest[: a.min - len(within1)]
        rule = f"公開1年以内 {len(within1)} 本＋2年以内の再生数上位 {len(picked) - len(within1)} 本"
    picked.sort(key=lambda v: v.get("publishDate") or "", reverse=True)

    for i, v in enumerate(picked, 1):
        v["transcript"] = transcript(v["videoId"], cache)
        log(f"[{i}/{len(picked)}] {v.get('publishDate')} {v['title'][:40]} -> {len(v['transcript']) if v['transcript'] else '取得不可'}")
    with open(os.path.join(a.out, "videos.json"), "w", encoding="utf-8") as f:
        json.dump({"channel": a.channel, "fetched": str(today), "rule": rule, "total_long": len(rows),
                   "within1y": len(within1), "videos": picked}, f, ensure_ascii=False, indent=1)
    log(f"[done] {rule}")

if __name__ == "__main__":
    main()
