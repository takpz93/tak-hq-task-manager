#!/usr/bin/env python3
"""加登仙一の日本酒大学 週次レポート & 維持率分析

YouTube Analytics API v2 / Data API v3 / Reporting API から毎週同じ指標を取り、
表だけの Markdown と 維持率 CSV を出力する。解釈・考察は一切書かない。

使い方:
  python3 yt_weekly_report.py                # 通常実行（初回はブラウザ認証）
  python3 yt_weekly_report.py --public-only  # 認証なし。公開情報（動画一覧）のみ
  python3 yt_weekly_report.py --date 2026-09-21  # 実行日を指定（期間はこの前日まで7日）

事前準備:
  1. Google Cloud で OAuth クライアント（デスクトップ）を作り、YouTube Analytics API /
     YouTube Data API v3 / YouTube Reporting API を有効化
  2. client_secret.json を clients/天領盃/credentials/ に置く
  3. pip install -r clients/天領盃/tools/requirements.txt
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

CHANNEL_ID = "UCx8tnZhehtNYsHBHpeHqHOg"
BASE_DIR = Path(__file__).resolve().parents[1]  # clients/天領盃
OUT_DIR = BASE_DIR / "output"
CRED_DIR = BASE_DIR / "credentials"
CLIENT_SECRET = CRED_DIR / "client_secret.json"
TOKEN_FILE = CRED_DIR / "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]
ANOMALY_NOTE = "※視聴回数は 2026-08-27 以降、YouTube側のデータ問題で水増しの可能性（参考値）"
REACH_REPORT_TYPE = "channel_reach_basic_a1"
RETENTION_TARGETS = ["東京の酒屋", "純米大吟醸", "2026秋", "中国地方編", "関西"]
RETENTION_POINTS = [("冒頭30秒", 30), ("1分", 60), ("3分", 180), ("5分", 300), ("10分", 600)]


# ---------------------------------------------------------------- utilities
def fmt_h(minutes: float | None) -> str:
    return "" if minutes is None else f"{minutes / 60:.1f}"


def fmt_pct(x: float | None, digits: int = 1) -> str:
    return "" if x is None else f"{x:.{digits}f}%"


def fmt_int(x: float | None) -> str:
    return "" if x is None else f"{int(round(x)):,}"


def mmss(sec: float) -> str:
    sec = int(round(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


def pct_change(cur: float | None, prev: float | None) -> str:
    if cur is None or prev in (None, 0):
        return ""
    return f"{(cur - prev) / prev * 100:+.1f}%"


def iso_duration_to_sec(s: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    h, mi, se = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + se


def project_type(title: str) -> str:
    if "ランキング" in title:
        return "ランキング"
    if re.search(r"[0-9０-９〇一二三四五六七八九十]+選", title):
        return "◯選"
    return "その他"


def md_table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


# ---------------------------------------------------------------- auth / clients
def get_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not CLIENT_SECRET.exists():
            sys.exit(f"client_secret.json がありません: {CLIENT_SECRET}")
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
        creds = flow.run_local_server(port=0)
        CRED_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


class YT:
    def __init__(self, creds):
        from googleapiclient.discovery import build

        self.analytics = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
        self.data = build("youtube", "v3", credentials=creds, cache_discovery=False)
        self.reporting = build("youtubereporting", "v1", credentials=creds, cache_discovery=False)
        self.creds = creds

    # -- Analytics -------------------------------------------------------
    def query(self, start: date, end: date, metrics: str, dimensions: str | None = None,
              filters: str | None = None, sort: str | None = None, max_results: int | None = None):
        kw = dict(ids=f"channel=={CHANNEL_ID}", startDate=start.isoformat(), endDate=end.isoformat(),
                  metrics=metrics)
        if dimensions:
            kw["dimensions"] = dimensions
        if filters:
            kw["filters"] = filters
        if sort:
            kw["sort"] = sort
        if max_results:
            kw["maxResults"] = max_results
        for attempt in range(4):
            try:
                res = self.analytics.reports().query(**kw).execute()
                break
            except Exception as e:  # quota / transient
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        cols = [c["name"] for c in res.get("columnHeaders", [])]
        return [dict(zip(cols, r)) for r in res.get("rows", [])]

    def totals(self, start: date, end: date, filters: str | None = None) -> dict:
        rows = self.query(start, end,
                          "estimatedMinutesWatched,views,averageViewPercentage,averageViewDuration,"
                          "subscribersGained,subscribersLost", filters=filters)
        return rows[0] if rows else {}

    # -- Data API ---------------------------------------------------------
    def recent_long_videos(self, n: int = 12, extra: int = 20) -> list[dict]:
        uploads = "UU" + CHANNEL_ID[2:]
        ids, token = [], None
        while len(ids) < n + extra:
            res = self.data.playlistItems().list(part="contentDetails", playlistId=uploads,
                                                 maxResults=50, pageToken=token).execute()
            ids += [i["contentDetails"]["videoId"] for i in res.get("items", [])]
            token = res.get("nextPageToken")
            if not token:
                break
        vids = []
        for i in range(0, len(ids), 50):
            res = self.data.videos().list(part="snippet,contentDetails", id=",".join(ids[i:i + 50])).execute()
            for it in res.get("items", []):
                sec = iso_duration_to_sec(it["contentDetails"]["duration"])
                title = it["snippet"]["title"]
                if sec <= 180 or "#shorts" in title.lower():
                    continue
                vids.append({"id": it["id"], "title": title, "sec": sec,
                             "published": datetime.fromisoformat(
                                 it["snippet"]["publishedAt"].replace("Z", "+00:00")).date()})
        vids.sort(key=lambda v: v["published"], reverse=True)
        return vids[:n]

    # -- Reporting API (impressions / CTR) ----------------------------------
    def reach_report_rows(self) -> tuple[list[dict], str]:
        """channel_reach_basic_a1 の最新レポートを取得。列は実行時に判定する。"""
        jobs = self.reporting.jobs().list().execute().get("jobs", [])
        job = next((j for j in jobs if j["reportTypeId"] == REACH_REPORT_TYPE), None)
        if not job:
            job = self.reporting.jobs().create(body={"reportTypeId": REACH_REPORT_TYPE,
                                                     "name": "tenryohai-reach"}).execute()
            return [], f"Reporting API ジョブを新規作成（{job['id']}）。レポートは翌日以降に生成される"
        reports = self.reporting.jobs().reports().list(jobId=job["id"]).execute().get("reports", [])
        if not reports:
            return [], "Reporting API: レポート未生成（ジョブ作成後 1〜2 日待つ）"
        rows: list[dict] = []
        import requests

        self.creds.refresh(__import__("google.auth.transport.requests", fromlist=["Request"]).Request())
        hdr = {"Authorization": f"Bearer {self.creds.token}"}
        for rep in sorted(reports, key=lambda r: r["startTime"])[-60:]:
            r = requests.get(rep["downloadUrl"], headers=hdr, timeout=60)
            r.raise_for_status()
            rows += list(csv.DictReader(io.StringIO(r.text)))
        cols = sorted(rows[0].keys()) if rows else []
        return rows, f"Reporting API 列: {', '.join(cols)}"


def impressions_ctr(rows: list[dict], start: date, end: date, video_id: str | None = None):
    """行にインプレッション列があれば集計。無ければ (None, None)。"""
    if not rows:
        return None, None
    imp_col = next((c for c in rows[0] if "impression" in c.lower() and "click" not in c.lower()), None)
    ctr_col = next((c for c in rows[0] if "click_through" in c.lower() or "ctr" in c.lower()), None)
    if not imp_col:
        return None, None
    imp = clicks = 0.0
    for r in rows:
        d = r.get("date", "")
        if not (start.isoformat().replace("-", "") <= d.replace("-", "") <= end.isoformat().replace("-", "")):
            continue
        if video_id and r.get("video_id") != video_id:
            continue
        try:
            i = float(r.get(imp_col) or 0)
            imp += i
            if ctr_col:
                clicks += i * float(r.get(ctr_col) or 0)
        except ValueError:
            pass
    if imp == 0:
        return None, None
    return imp, (clicks / imp * 100 if ctr_col else None)


# ---------------------------------------------------------------- tasks
def task1_weekly(yt: YT, run_date: date, reach_rows: list[dict]) -> str:
    end = run_date - timedelta(days=1)
    periods = []
    for k in range(4):
        e = end - timedelta(days=7 * k)
        s = e - timedelta(days=6)
        periods.append((["直近7日", "前週", "2週前", "3週前"][k], s, e))
    periods.append(("直近28日", end - timedelta(days=27), end))
    periods.append(("前28日", end - timedelta(days=55), end - timedelta(days=28)))
    data = []
    for label, s, e in periods:
        t = yt.totals(s, e)
        imp, ctr = impressions_ctr(reach_rows, s, e)
        data.append((label, s, e, t, imp, ctr))
    rows = []
    for i, (label, s, e, t, imp, ctr) in enumerate(data):
        mins = t.get("estimatedMinutesWatched")
        views = t.get("views")
        prev = data[i + 1][3].get("estimatedMinutesWatched") if i in (0, 1, 2, 4) else None
        gained, lost = t.get("subscribersGained"), t.get("subscribersLost")
        rows.append([
            f"{label}<br>{s:%m/%d}〜{e:%m/%d}", fmt_h(mins), fmt_int(imp), fmt_pct(ctr),
            fmt_int(imp * ctr / 100) if imp and ctr is not None else "",
            fmt_int(views), f"{mins / views:.2f}" if mins and views else "",
            fmt_pct(t.get("averageViewPercentage")), fmt_int(gained), fmt_int(lost),
            fmt_int((gained or 0) - (lost or 0)) if gained is not None else "",
            pct_change(mins, prev),
        ])
    hdr = ["期間", "総再生時間(h)", "インプレッション", "CTR", "クリック数", "視聴回数(参考)", "分/視聴",
           "平均視聴率", "登録増", "登録減", "純増", "前期間比(再生時間)"]
    return "## 1. 週次サマリー\n\n" + md_table(hdr, rows) + f"\n\n{ANOMALY_NOTE}\n前期間比は総再生時間ベース。直近7日→前週、前週→2週前、2週前→3週前、直近28日→前28日。\n"


def task2_videos(yt: YT, run_date: date, videos: list[dict], reach_rows: list[dict]) -> str:
    end_cap = run_date - timedelta(days=1)
    rows = []
    for v in videos:
        pub = v["published"]
        f = f"video=={v['id']}"
        t7 = yt.totals(pub, min(pub + timedelta(days=6), end_cap), f)
        t28 = yt.totals(pub, min(pub + timedelta(days=27), end_cap), f)
        tall = yt.totals(pub, end_cap, f)
        src = yt.query(pub, end_cap, "views,estimatedMinutesWatched", dimensions="insightTrafficSourceType",
                       filters=f, sort="-views")
        total_v = sum(r["views"] for r in src) or 1
        top3 = " / ".join(f"{r['insightTrafficSourceType']} {r['views'] / total_v * 100:.0f}%" for r in src[:3])
        imp, ctr = impressions_ctr(reach_rows, pub, end_cap, v["id"])
        gained = (tall.get("subscribersGained") or 0) - (tall.get("subscribersLost") or 0)
        hours = (tall.get("estimatedMinutesWatched") or 0) / 60
        rows.append([
            pub.isoformat(), v["title"][:40], mmss(v["sec"]), project_type(v["title"]),
            fmt_h(t7.get("estimatedMinutesWatched")), fmt_h(t28.get("estimatedMinutesWatched")),
            fmt_int(imp), fmt_pct(ctr), fmt_pct(tall.get("averageViewPercentage")), fmt_int(gained),
            f"{gained / hours * 1000:.1f}" if hours else "", top3,
        ])
    hdr = ["公開日", "タイトル", "長さ", "企画タイプ", "7日再生時間(h)", "28日再生時間(h)", "インプレッション",
           "CTR", "平均視聴率", "登録純増", "登録/1000h", "流入元TOP3"]
    return ("## 2. 動画別（直近12本・横動画）\n\n" + md_table(hdr, rows)
            + "\n\n流入元コード: BROWSE=ブラウジング, RELATED_VIDEO=関連動画, YT_SEARCH=YouTube検索, "
              "SUBSCRIBER=登録者フィード, EXT_URL=外部, NOTIFICATION=通知, PLAYLIST=再生リスト, SHORTS=ショートフィード\n"
              "登録/1000h = 公開日〜前日の登録純増 ÷ 総再生時間(h) × 1000。インプレッション・CTRは Reporting API に列がある場合のみ。\n")


def fetch_transcript(video_id: str) -> list[dict]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()
        tr = api.fetch(video_id, languages=["ja"])
        return [{"start": s.start, "dur": s.duration, "text": s.text} for s in tr]
    except Exception:
        pass
    local = BASE_DIR / "scripts" / f"{video_id}.srt"
    if local.exists():
        return parse_srt(local.read_text(encoding="utf-8"))
    return []


def parse_srt(text: str) -> list[dict]:
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().splitlines()
        m = next((re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", l) for l in lines
                  if "-->" in l), None)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        st = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        en = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        body = " ".join(l for l in lines if "-->" not in l and not l.strip().isdigit())
        out.append({"start": st, "dur": en - st, "text": body})
    return out


def text_at(transcript: list[dict], sec: float, width: int = 40) -> str:
    if not transcript:
        return ""
    seg = min(transcript, key=lambda s: abs(s["start"] - sec))
    idx = transcript.index(seg)
    txt = " ".join(s["text"] for s in transcript[max(0, idx - 1): idx + 2])
    return re.sub(r"\s+", " ", txt)[:width]


def task3_retention(yt: YT, run_date: date, videos: list[dict], ret_dir: Path) -> str:
    targets = []
    for key in RETENTION_TARGETS:
        v = next((v for v in videos if key in v["title"]), None)
        if v and v not in targets:
            targets.append(v)
    if len(targets) < 5:
        for v in videos:
            if v not in targets:
                targets.append(v)
            if len(targets) == 5:
                break
    ret_dir.mkdir(parents=True, exist_ok=True)
    out = ["## 3. 維持率カーブ（直近5本）\n"]
    summary_rows, drop_sections = [], []
    for v in targets:
        rows = yt.query(v["published"], run_date - timedelta(days=1),
                        "audienceWatchRatio,relativeRetentionPerformance",
                        dimensions="elapsedVideoTimeRatio", filters=f"video=={v['id']}")
        if not rows:
            drop_sections.append(f"### {v['title'][:40]}\n維持率データなし\n")
            continue
        curve = [(float(r["elapsedVideoTimeRatio"]), float(r["audienceWatchRatio"]),
                  float(r.get("relativeRetentionPerformance") or 0)) for r in rows]
        with open(ret_dir / f"{v['published']}_{v['id']}.csv", "w", newline="", encoding="utf-8-sig") as fp:
            w = csv.writer(fp)
            w.writerow(["ratio", "sec", "mm:ss", "audienceWatchRatio", "relativeRetentionPerformance"])
            for ratio, awr, rrp in curve:
                w.writerow([f"{ratio:.2f}", f"{ratio * v['sec']:.1f}", mmss(ratio * v["sec"]), f"{awr:.4f}", f"{rrp:.4f}"])

        def at(sec: float) -> str:
            ratio = sec / v["sec"]
            if ratio > 1:
                return "-"
            pt = min(curve, key=lambda c: abs(c[0] - ratio))
            return f"{pt[1] * 100:.1f}%"

        summary_rows.append([v["title"][:30], mmss(v["sec"])] + [at(s) for _, s in RETENTION_POINTS]
                            + [at(v["sec"] * 0.5), at(v["sec"] * 0.9)])
        transcript = fetch_transcript(v["id"])
        drops = []
        for (r0, a0, _), (r1, a1, _) in zip(curve, curve[1:]):
            if (a0 - a1) * 100 >= 3:
                sec = r1 * v["sec"]
                drops.append([mmss(r0 * v["sec"]) + "→" + mmss(sec), f"{a0 * 100:.1f}%→{a1 * 100:.1f}%",
                              f"-{(a0 - a1) * 100:.1f}pt", text_at(transcript, sec)])
        sec_md = f"### {v['title'][:40]}（{v['id']}、{mmss(v['sec'])}）\n\n"
        sec_md += md_table(["区間", "維持率", "落差", "その時点の発話（字幕）"], drops) if drops else "3pt以上の落ち込みなし"
        sec_md += "\n" + ("" if transcript else "（字幕取得不可のため発話列は空）\n")
        drop_sections.append(sec_md)
    hdr = ["動画", "長さ"] + [p for p, _ in RETENTION_POINTS] + ["中央(50%)", "終盤(90%)"]
    out.append(md_table(hdr, summary_rows) + "\n")
    out += drop_sections
    return "\n".join(out)


def task4_traffic(yt: YT, run_date: date) -> str:
    end = run_date - timedelta(days=1)
    periods = [("直近28日", end - timedelta(days=27), end), ("前28日", end - timedelta(days=55), end - timedelta(days=28))]
    out = ["## 4. 流入元\n"]
    for label, s, e in periods:
        rows = yt.query(s, e, "estimatedMinutesWatched,views,averageViewPercentage",
                        dimensions="insightTrafficSourceType", sort="-estimatedMinutesWatched")
        total = sum(r["estimatedMinutesWatched"] for r in rows) or 1
        out.append(f"### {label}（{s:%m/%d}〜{e:%m/%d}）\n")
        out.append(md_table(["流入元", "総再生時間(h)", "構成比", "平均視聴率", "視聴回数(参考)"],
                            [[r["insightTrafficSourceType"], fmt_h(r["estimatedMinutesWatched"]),
                              fmt_pct(r["estimatedMinutesWatched"] / total * 100),
                              fmt_pct(r.get("averageViewPercentage")), fmt_int(r["views"])] for r in rows]) + "\n")
        try:
            terms = yt.query(s, e, "views,estimatedMinutesWatched", dimensions="insightTrafficSourceDetail",
                             filters="insightTrafficSourceType==YT_SEARCH", sort="-views", max_results=20)
            out.append(md_table(["検索語", "視聴回数", "総再生時間(h)"],
                                [[r["insightTrafficSourceDetail"], fmt_int(r["views"]),
                                  fmt_h(r["estimatedMinutesWatched"])] for r in terms]) + "\n")
        except Exception as e:  # noqa: BLE001
            out.append(f"検索語TOP20: 取得失敗（{e}）\n")
    out.append(ANOMALY_NOTE + "\n")
    return "\n".join(out)


# ---------------------------------------------------------------- public-only fallback
def public_video_list(n: int = 12) -> list[dict]:
    """認証なしで取れる公開情報（YouTube 内部検索 API）。分析値は含まない。"""
    import requests

    base = "https://youtubei.googleapis.com/youtubei/v1/browse?prettyPrint=false"
    ctx = {"context": {"client": {"clientName": "WEB", "clientVersion": "2.20240101.00.00", "hl": "ja", "gl": "JP"}}}
    body = dict(ctx, browseId=CHANNEL_ID, params="EgZ2aWRlb3PyBgQKAjoA")

    def walk(o, key, acc):
        if isinstance(o, dict):
            if key in o:
                acc.append(o[key])
            for x in o.values():
                walk(x, key, acc)
        elif isinstance(o, list):
            for x in o:
                walk(x, key, acc)

    vids: list[dict] = []
    while len(vids) < n:
        d = requests.post(base, json=body, timeout=40).json()
        lockups: list = []
        walk(d, "lockupViewModel", lockups)
        for L in lockups:
            if L.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO" or L.get("contentId") in {v["id"] for v in vids}:
                continue
            md = L.get("metadata", {}).get("lockupMetadataViewModel", {})
            badges: list = []
            walk(L.get("contentImage", {}), "thumbnailBadgeViewModel", badges)
            length = next((b.get("text") for b in badges if re.fullmatch(r"[\d:]+", b.get("text", ""))), "")
            parts: list = []
            walk(md.get("metadata", {}), "metadataParts", parts)
            texts = [p.get("text", {}).get("content", "") for grp in parts for p in grp]
            vids.append({"id": L["contentId"], "title": md.get("title", {}).get("content", ""), "length": length,
                         "published_rel": next((t for t in texts if "前" in t), ""),
                         "views_txt": next((t for t in texts if "視聴" in t), "")})
        conts: list = []
        walk(d, "continuationItemRenderer", conts)
        tok = next((c.get("continuationEndpoint", {}).get("continuationCommand", {}).get("token") for c in conts
                    if c.get("continuationEndpoint")), None)
        if not tok:
            break
        body = dict(ctx, continuation=tok)
    return vids[:n]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="実行日 YYYY-MM-DD（既定: 今日）")
    ap.add_argument("--public-only", action="store_true")
    ap.add_argument("--out", default=str(OUT_DIR))
    args = ap.parse_args()
    run_date = date.fromisoformat(args.date) if args.date else date.today()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = run_date.strftime("%Y%m%d")

    if args.public_only:
        vids = public_video_list(12)
        print(md_table(["動画ID", "タイトル", "長さ", "公開", "視聴回数(公開値・参考)", "企画タイプ"],
                       [[v["id"], v["title"][:50], v["length"], v["published_rel"], v["views_txt"], project_type(v["title"])]
                        for v in vids]))
        print("\n" + ANOMALY_NOTE)
        return

    yt = YT(get_credentials())
    reach_rows, reach_note = yt.reach_report_rows()
    videos = yt.recent_long_videos(12)
    ret_dir = out_dir / f"維持率_{stamp}"

    sections = [
        f"# 加登仙一の日本酒大学 週次レポート {run_date.isoformat()}\n",
        f"データ取得: Analytics API v2（集計は前日 {run_date - timedelta(days=1)} まで。API側で2〜3日の反映遅れあり）／{reach_note}\n",
        task1_weekly(yt, run_date, reach_rows),
        task2_videos(yt, run_date, videos, reach_rows),
        task3_retention(yt, run_date, videos, ret_dir),
        task4_traffic(yt, run_date),
    ]
    report = "\n".join(sections)
    md_path = out_dir / f"週次レポート_{stamp}.md"
    md_path.write_text(report, encoding="utf-8")

    # 会話貼り付け用の要約（各表の上位行のみ、2000字以内）
    brief = []
    for sec in sections[2:]:
        lines = [l for l in sec.splitlines() if l.startswith("|") or l.startswith("## ") or l.startswith("### ")]
        kept, table_rows = [], 0
        for l in lines:
            if l.startswith("|"):
                table_rows += 1
                if table_rows > 6:  # header + separator + top4
                    continue
            else:
                table_rows = 0
            kept.append(l)
        brief.append("\n".join(kept))
    brief_txt = "\n".join(brief)
    if len(brief_txt) > 2000:
        brief_txt = brief_txt[:1990] + "\n…（省略）"
    print(f"保存: {md_path}\n維持率CSV: {ret_dir}\n\n=== 会話に貼る用 ===\n{brief_txt}")


if __name__ == "__main__":
    main()
