#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KINS（【下川先生】の菌ケア大学）向け YouTube Analytics API 取得スクリプト（依頼1〜4 + 突き合わせ）

出力（--out-dir、既定 clients/KINS/output）:
  kins_conv28d_YYYYMMDD.csv         依頼1 長尺（181秒以上）: 公開後28日ウィンドウの動画別実績（convRate 降順）
  kins_conv28d_shorts_YYYYMMDD.csv  依頼1 ショート（180秒以下）: 同上
  kins_conv28d_notyet_YYYYMMDD.csv  依頼1 公開後28日未達（videoId・公開日のみ）
  kins_retention_YYYYMMDD.csv       依頼2 視聴者維持率カーブ（videoId ごとの elapsedVideoTimeRatio, audienceWatchRatio）
  kins_traffic_YYYYMMDD.csv         依頼3 動画別トラフィックソース内訳（直近28日）
  kins_traffic_endscreen_YYYYMMDD.csv 依頼3 END_SCREEN 流入が 0/極小の動画一覧
  kins_cards_YYYYMMDD.csv           依頼4 カード／終了画面（annotation）指標（直近28日・動画別）
  kins_reconcile_YYYYMMDD.csv       Studio 実測との突き合わせ用（チャンネル合計）
  kins_run_YYYYMMDD.log             実行ログ（失敗した metrics など）

認証（どれか）:
  1) --token  : 認可済みユーザー JSON（refresh_token 入り）。ローカルで一度作れば別マシンに持ち込める
  2) --credentials : OAuth クライアント (credentials.json)。ブラウザで認可して --token に保存
  3) --device : ブラウザの無い環境向け。OAuth クライアント（種類「テレビと制限付き入力デバイス」）の
                credentials.json か環境変数 YT_CLIENT_ID / YT_CLIENT_SECRET を使い、表示された URL と
                コードをスマホ等で承認する。取得したトークンは --token に保存
  4) 環境変数 YT_ACCESS_TOKEN : アクセストークン直指定（OAuth Playground 等。約1時間で失効）
  必要スコープ: yt-analytics.readonly, youtube.readonly

使い方:
  python3 COO/scripts/kins_yt_analytics.py --token yt_token.json
  python3 COO/scripts/kins_yt_analytics.py --credentials credentials.json --token yt_token.json
  python3 COO/scripts/kins_yt_analytics.py --token yt_token.json --videos-csv clients/KINS/output/kins_videos_20260920.csv

注意:
  - Analytics API の日付は太平洋時間（PT）基準。公開日は Data API の publishedAt(UTC) を PT に変換して startDate にする
    （JST 表示の公開日とは 1 日ずれることがある。CSV には publishedAt(UTC) と publishedAt_JST / startDate(PT) を併記）
  - API が返さない値は空欄のまま（0 埋めしない）
  - impressions / impressionClickThroughRate は Analytics API v2 で公開されていない可能性が高い。取れなければ空欄 + ログに記録
"""
import argparse, csv, json, os, re, sys, time
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

CHANNEL = "UCXAU7ks-wPVoFJykHn08zvA"
ANALYTICS = "https://youtubeanalytics.googleapis.com/v2/reports"
DATA_API = "https://www.googleapis.com/youtube/v3"
SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly", "https://www.googleapis.com/auth/youtube.readonly"]
PT, JST = ZoneInfo("America/Los_Angeles"), ZoneInfo("Asia/Tokyo")
SHORT_MAX_SEC = 180
WINDOW_DAYS = 28

# 依頼2: タイトル検索語（部分一致・空白/記号無視）→ videoId を特定する
RETENTION_TARGETS = [
    ("高転換", "超有料級", "7年ぶりに", "コストコ"),
    ("高転換", "トレーニー必見", "筋トレで老けます"),
    ("高転換", "毎日食べてます", "1日のフル食"),
    ("低転換", "キムチ腸活", "10商品を格付け"),
    ("低転換", "コストコ爆買い", "ヘトヘトのカメラマン"),
    ("低転換", "衝撃", "腸に最悪だと思っていたカレー"),
]

# 突き合わせ用（Studio 実測の期間）
RECONCILE_PERIODS = [
    ("直近7日 9/13–9/19", "2026-09-13", "2026-09-19"),
    ("前週 9/6–9/12", "2026-09-06", "2026-09-12"),
    ("直近28日 8/23–9/19", "2026-08-23", "2026-09-19"),
    ("前28日 7/26–8/22", "2026-07-26", "2026-08-22"),
    ("90日 6/22–9/19", "2026-06-22", "2026-09-19"),
]

LOG_LINES = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, file=sys.stderr, flush=True); LOG_LINES.append(s)


# ---------------- 認証 ----------------
def load_client(credentials_file):
    """OAuth クライアントの client_id / client_secret。credentials.json（installed / web / 直下）か環境変数から"""
    if credentials_file and os.path.isfile(credentials_file):
        d = json.load(open(credentials_file, encoding="utf-8"))
        d = d.get("installed") or d.get("web") or d
        if d.get("client_id"): return d["client_id"], d.get("client_secret", "")
    if os.environ.get("YT_CLIENT_ID"):
        return os.environ["YT_CLIENT_ID"], os.environ.get("YT_CLIENT_SECRET", "")
    return None, None


def device_flow(client_id, client_secret):
    """OAuth 2.0 限定入力デバイス向けフロー。ユーザーが別端末で URL + コードを承認するのを待つ"""
    r = requests.post("https://oauth2.googleapis.com/device/code", data={"client_id": client_id, "scope": " ".join(SCOPES)}, timeout=30)
    if r.status_code != 200:
        sys.exit(f"device/code 失敗 HTTP {r.status_code}: {r.text[:300]}（OAuth クライアントの種類は「テレビと制限付き入力デバイス」が必要）")
    d = r.json()
    print("\n==== 認可が必要です ====", file=sys.stderr)
    print(f"  1) ブラウザで開く: {d.get('verification_url')}", file=sys.stderr)
    print(f"  2) コードを入力: {d.get('user_code')}", file=sys.stderr)
    print(f"  ({d.get('expires_in', 1800) // 60} 分以内。チャンネル所有者のアカウントで承認)\n", file=sys.stderr)
    interval, deadline = int(d.get("interval", 5)), time.time() + int(d.get("expires_in", 1800))
    while time.time() < deadline:
        time.sleep(interval)
        t = requests.post("https://oauth2.googleapis.com/token", data={"client_id": client_id, "client_secret": client_secret, "device_code": d["device_code"],
                                                                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"}, timeout=30)
        j = t.json()
        if t.status_code == 200 and j.get("access_token"):
            log("[auth] デバイス認可 完了")
            return {"token": j["access_token"], "refresh_token": j.get("refresh_token"), "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": client_id, "client_secret": client_secret, "scopes": SCOPES, "universe_domain": "googleapis.com"}
        err = j.get("error")
        if err == "slow_down": interval += 5
        elif err in ("authorization_pending", None): continue
        else: sys.exit(f"デバイス認可 失敗: {err} {j.get('error_description', '')}")
    sys.exit("デバイス認可 期限切れ。もう一度実行してください")


class Auth:
    """認可済みユーザー JSON（token / refresh_token / client_id / client_secret）を扱う。更新は HTTP 直叩きで google-auth 非依存"""
    def __init__(self, token_file=None, credentials_file=None, device=False):
        self.access_token = os.environ.get("YT_ACCESS_TOKEN")
        self.info, self.token_file, self.expires_at = None, token_file, 0
        if self.access_token:
            log("[auth] YT_ACCESS_TOKEN を使用"); return
        if token_file and os.path.isfile(token_file):
            self.info = json.load(open(token_file, encoding="utf-8"))
            self.refresh()
        if not self.access_token:
            cid, csec = load_client(credentials_file)
            if device:
                if not cid: sys.exit("--device には credentials.json か YT_CLIENT_ID / YT_CLIENT_SECRET が必要です")
                self.info = device_flow(cid, csec)
            else:
                if not credentials_file or not os.path.isfile(credentials_file):
                    sys.exit("認証情報がありません。--token（認可済み JSON）、--credentials（OAuth クライアント）+ ブラウザ、--device、または YT_ACCESS_TOKEN を指定してください")
                from google_auth_oauthlib.flow import InstalledAppFlow
                creds = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES).run_local_server(port=0)
                self.info = json.loads(creds.to_json())
            self.access_token, self.expires_at = self.info.get("token"), time.time() + 3300
            self.save()

    def refresh(self):
        if not self.info or not self.info.get("refresh_token"): return
        r = requests.post(self.info.get("token_uri", "https://oauth2.googleapis.com/token"),
                          data={"client_id": self.info["client_id"], "client_secret": self.info.get("client_secret", ""),
                                "refresh_token": self.info["refresh_token"], "grant_type": "refresh_token"}, timeout=30)
        if r.status_code != 200:
            sys.exit(f"トークン更新に失敗 HTTP {r.status_code}: {r.text[:300]}")
        j = r.json(); self.access_token = j["access_token"]; self.info["token"] = j["access_token"]
        self.expires_at = time.time() + int(j.get("expires_in", 3600)) - 120
        self.save(); log("[auth] トークン更新")

    def save(self):
        if self.token_file and self.info:
            with open(self.token_file, "w", encoding="utf-8") as f: json.dump(self.info, f, ensure_ascii=False, indent=1)
            log(f"[auth] token を保存: {self.token_file}")

    def headers(self):
        if self.info and self.info.get("refresh_token") and time.time() >= self.expires_at: self.refresh()
        return {"Authorization": f"Bearer {self.access_token}"}


# ---------------- API 呼び出し ----------------
class Api:
    def __init__(self, auth, sleep=0.15):
        self.auth, self.sleep, self.calls = auth, sleep, 0

    def _get(self, url, params):
        for attempt in range(5):
            self.calls += 1
            r = requests.get(url, params=params, headers=self.auth.headers(), timeout=60)
            if r.status_code == 200:
                time.sleep(self.sleep); return r.json(), None
            if r.status_code in (429, 500, 502, 503) and attempt < 4:
                time.sleep(2 ** attempt); continue
            try: msg = r.json().get("error", {}).get("message", r.text[:300])
            except Exception: msg = r.text[:300]
            return None, f"HTTP {r.status_code}: {msg}"
        return None, "retry exhausted"

    def query(self, start, end, metrics, dimensions=None, filters=None, sort=None, max_results=None):
        p = {"ids": f"channel=={CHANNEL}", "startDate": start, "endDate": end, "metrics": ",".join(metrics)}
        if dimensions: p["dimensions"] = ",".join(dimensions)
        if filters: p["filters"] = filters
        if sort: p["sort"] = sort
        if max_results: p["maxResults"] = max_results
        d, err = self._get(ANALYTICS, p)
        if err:
            log(f"[analytics] FAIL {p} -> {err}"); return None, err
        cols = [c["name"] for c in d.get("columnHeaders", [])]
        rows = [dict(zip(cols, r)) for r in d.get("rows", [])]
        return rows, None

    def query_metric_groups(self, start, end, groups, **kw):
        """metrics を複数グループに分けて順に取得し、失敗したグループは空欄扱い。戻り値: key -> {metric: value}"""
        merged, failed = {}, []
        for metrics in groups:
            rows, err = self.query(start, end, metrics, **kw)
            if err:
                # グループ内の 1 metric ずつ再試行（未対応 metric の切り分け）
                for m in metrics:
                    rows1, err1 = self.query(start, end, [m], **kw)
                    if err1: failed.append(m); continue
                    for r in rows1: merged.setdefault(self._key(r, kw.get("dimensions")), {}).update(r)
                continue
            for r in rows: merged.setdefault(self._key(r, kw.get("dimensions")), {}).update(r)
        return merged, failed

    @staticmethod
    def _key(row, dims):
        return tuple(row.get(d) for d in (dims or [])) if dims else ()

    def data(self, path, **params):
        d, err = self._get(f"{DATA_API}/{path}", params)
        if err: log(f"[data] FAIL {path} {params} -> {err}")
        return d


# ---------------- 動画一覧 ----------------
def iso_duration_sec(s):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m: return None
    d, h, mi, se = (int(x) if x else 0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se

def list_videos_data_api(api):
    ch = api.data("channels", part="contentDetails", id=CHANNEL)
    if not ch or not ch.get("items"): return None
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while True:
        p = {"part": "contentDetails", "playlistId": uploads, "maxResults": 50}
        if tok: p["pageToken"] = tok
        d = api.data("playlistItems", **p)
        if not d: return None
        ids += [it["contentDetails"]["videoId"] for it in d.get("items", [])]
        tok = d.get("nextPageToken")
        if not tok: break
    out = []
    for i in range(0, len(ids), 50):
        d = api.data("videos", part="snippet,contentDetails,status", id=",".join(ids[i:i + 50]), maxResults=50)
        if not d: return None
        for v in d.get("items", []):
            pub = v["snippet"]["publishedAt"]
            out.append({"videoId": v["id"], "title": v["snippet"]["title"], "publishedAt": pub,
                        "durationSec": iso_duration_sec(v["contentDetails"].get("duration")),
                        "privacy": v.get("status", {}).get("privacyStatus")})
    log(f"[videos] Data API: {len(out)}本")
    return out

def list_videos_csv(path):
    """yt_channel_audit.py の CSV（区分, 公開日, タイトル, 動画URL, ..., 動画尺(秒)）を読む。公開日は JST 日付のみ（時刻不明）"""
    out = []
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            m = re.search(r"v=([\w-]+)", r.get("動画URL", ""))
            if not m or not r.get("公開日"): continue
            dur = r.get("動画尺(秒)")
            out.append({"videoId": m.group(1), "title": r.get("タイトル", ""), "publishedAt": r["公開日"] + "T00:00:00+09:00",
                        "durationSec": int(dur) if dur and dur.isdigit() else None, "privacy": "", "kind_hint": r.get("区分", "")})
    log(f"[videos] CSV: {len(out)}本 ({path})")
    return out

def to_dates(published_at):
    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    return dt.astimezone(PT).date(), dt.astimezone(JST).date()


# ---------------- 依頼1 ----------------
def pct(v, nd=1):
    return "" if v in (None, "") else f"{float(v):.{nd}f}"

def conv_rate(gained, views):
    try:
        g, v = float(gained), float(views)
        return f"{g / v * 100:.3f}%" if v > 0 else ""
    except (TypeError, ValueError): return ""

def run_conv28d(api, videos, since, today_pt, lag_days, out_dir, tag):
    base_metrics = ["views", "estimatedMinutesWatched", "averageViewDuration", "averageViewPercentage", "subscribersGained", "subscribersLost"]
    imp_metrics = ["impressions", "impressionClickThroughRate"]
    longs, shorts, notyet = [], [], []
    imp_failed_all = True
    targets = [v for v in videos if to_dates(v["publishedAt"])[1] >= since or to_dates(v["publishedAt"])[0] >= since]
    log(f"[conv28d] 対象 {len(targets)}本（公開日 {since} 以降）")
    for i, v in enumerate(targets, 1):
        pt_day, jst_day = to_dates(v["publishedAt"])
        start, end = pt_day, pt_day + timedelta(days=WINDOW_DAYS - 1)
        row = {"videoId": v["videoId"], "title": v["title"], "publishedAt": v["publishedAt"], "publishedAt_JST": jst_day.isoformat(),
               "startDate_PT": start.isoformat(), "endDate_PT": end.isoformat(), "durationSec": v.get("durationSec", "")}
        if end + timedelta(days=lag_days) > today_pt:
            notyet.append({"videoId": v["videoId"], "title": v["title"], "publishedAt": v["publishedAt"], "publishedAt_JST": jst_day.isoformat(),
                           "durationSec": v.get("durationSec", ""), "window_end_PT": end.isoformat()}); continue
        merged, failed = api.query_metric_groups(start.isoformat(), end.isoformat(), [base_metrics, imp_metrics],
                                                 dimensions=["video"], filters=f"video=={v['videoId']}")
        m = merged.get((v["videoId"],), {})
        if "impressions" in m: imp_failed_all = False
        row.update({"views": m.get("views", ""), "subscribersGained": m.get("subscribersGained", ""), "subscribersLost": m.get("subscribersLost", ""),
                    "convRate": conv_rate(m.get("subscribersGained"), m.get("views")),
                    "avgViewPct": pct(m.get("averageViewPercentage")), "avgViewSec": pct(m.get("averageViewDuration"), 0),
                    "estimatedMinutesWatched": m.get("estimatedMinutesWatched", ""),
                    "impressions": m.get("impressions", ""), "ctr": pct(m.get("impressionClickThroughRate"), 2),
                    "failedMetrics": ";".join(failed)})
        dur = v.get("durationSec")
        is_short = (dur is not None and dur <= SHORT_MAX_SEC) or (dur is None and "ショート" in v.get("kind_hint", ""))
        (shorts if is_short else longs).append(row)
        if i % 10 == 0: log(f"[conv28d] {i}/{len(targets)}")
    if imp_failed_all: log("[conv28d] impressions / impressionClickThroughRate は取得できず（Analytics API 非対応の可能性）。列は空欄")
    def keyf(r):
        try: return float(r["convRate"].rstrip("%"))
        except ValueError: return -1
    cols = ["videoId", "title", "publishedAt", "publishedAt_JST", "startDate_PT", "endDate_PT", "durationSec", "views", "subscribersGained",
            "subscribersLost", "convRate", "avgViewPct", "avgViewSec", "estimatedMinutesWatched", "impressions", "ctr", "failedMetrics"]
    write_csv(os.path.join(out_dir, f"kins_conv28d_{tag}.csv"), cols, sorted(longs, key=keyf, reverse=True))
    write_csv(os.path.join(out_dir, f"kins_conv28d_shorts_{tag}.csv"), cols, sorted(shorts, key=keyf, reverse=True))
    write_csv(os.path.join(out_dir, f"kins_conv28d_notyet_{tag}.csv"),
              ["videoId", "title", "publishedAt", "publishedAt_JST", "durationSec", "window_end_PT"], sorted(notyet, key=lambda r: r["publishedAt"]))
    log(f"[conv28d] 長尺 {len(longs)} / ショート {len(shorts)} / 未達 {len(notyet)}")
    return longs


# ---------------- 依頼2 ----------------
def norm(s): return re.sub(r"[\s　「」『』【】\[\]（）()、。,.!！?？…・:：\-ー〜~\"'“”]", "", s or "")

def resolve_retention_targets(videos, overrides):
    found = []
    for grp, *keys in RETENTION_TARGETS:
        label = " / ".join(keys)
        if label in overrides:
            vid = overrides[label]; v = next((x for x in videos if x["videoId"] == vid), {"videoId": vid, "title": "", "publishedAt": ""})
            found.append((grp, label, v)); continue
        hits = [v for v in videos if all(norm(k) in norm(v["title"]) for k in keys)]
        if len(hits) != 1:
            hits2 = [v for v in videos if norm(keys[-1]) in norm(v["title"])]
            hits = hits2 if len(hits2) == 1 else hits
        if len(hits) == 1: found.append((grp, label, hits[0]))
        else: log(f"[retention] 特定できず ({len(hits)}件): {label} -> {[h['videoId'] for h in hits]}")
    return found

def run_retention(api, videos, overrides, out_dir, tag, today_pt):
    rows_out = []
    for grp, label, v in resolve_retention_targets(videos, overrides):
        if not v.get("publishedAt"):
            log(f"[retention] 公開日不明のためスキップ: {v['videoId']}"); continue
        pt_day = to_dates(v["publishedAt"])[0]
        start, end = pt_day, min(pt_day + timedelta(days=WINDOW_DAYS - 1), today_pt)
        rows, err = api.query(start.isoformat(), end.isoformat(), ["audienceWatchRatio", "relativeRetentionPerformance"],
                              dimensions=["elapsedVideoTimeRatio"], filters=f"video=={v['videoId']}")
        if err:
            rows, err = api.query(start.isoformat(), end.isoformat(), ["audienceWatchRatio"], dimensions=["elapsedVideoTimeRatio"], filters=f"video=={v['videoId']}")
        log(f"[retention] {grp} {v['videoId']} {v['title'][:30]} -> {len(rows or [])}点")
        for r in rows or []:
            rows_out.append({"group": grp, "videoId": v["videoId"], "title": v["title"], "startDate_PT": start.isoformat(), "endDate_PT": end.isoformat(),
                             "elapsedVideoTimeRatio": r.get("elapsedVideoTimeRatio", ""), "audienceWatchRatio": r.get("audienceWatchRatio", ""),
                             "relativeRetentionPerformance": r.get("relativeRetentionPerformance", "")})
    write_csv(os.path.join(out_dir, f"kins_retention_{tag}.csv"),
              ["group", "videoId", "title", "startDate_PT", "endDate_PT", "elapsedVideoTimeRatio", "audienceWatchRatio", "relativeRetentionPerformance"], rows_out)


# ---------------- 依頼3 ----------------
def run_traffic(api, videos, start, end, top_n, out_dir, tag, endscreen_max):
    title = {v["videoId"]: v["title"] for v in videos}
    metrics = ["views", "subscribersGained", "averageViewPercentage"]
    rows, err = api.query(start, end, metrics, dimensions=["video", "insightTrafficSourceType"], sort="-views", max_results=200)
    per_video = {}
    if err:
        log("[traffic] video×insightTrafficSourceType の同時指定は不可 → 上位動画ごとに insightTrafficSourceType を取得")
        top, err2 = api.query(start, end, ["views", "subscribersGained", "averageViewPercentage"], dimensions=["video"], sort="-views", max_results=top_n)
        if err2: log("[traffic] 上位動画の取得に失敗"); top = []
        rows = []
        for t in top:
            vid = t["video"]
            per_video[vid] = t
            r2, e2 = api.query(start, end, metrics, dimensions=["insightTrafficSourceType"], filters=f"video=={vid}", sort="-views")
            if e2:
                r2, e2 = api.query(start, end, ["views"], dimensions=["insightTrafficSourceType"], filters=f"video=={vid}", sort="-views")
            for r in r2 or []: rows.append({"video": vid, **r})
    else:
        for r in rows:
            pv = per_video.setdefault(r["video"], {"views": 0})
            pv["views"] = pv.get("views", 0) + (r.get("views") or 0)
        keep = set(sorted(per_video, key=lambda k: -per_video[k]["views"])[:top_n])
        rows = [r for r in rows if r["video"] in keep]
    out = [{"videoId": r["video"], "title": title.get(r["video"], ""), "insightTrafficSourceType": r.get("insightTrafficSourceType", ""),
            "views": r.get("views", ""), "subscribersGained": r.get("subscribersGained", ""), "averageViewPercentage": pct(r.get("averageViewPercentage"))} for r in rows]
    out.sort(key=lambda r: (-(per_video.get(r["videoId"], {}).get("views") or 0), r["videoId"], -(float(r["views"]) if r["views"] != "" else 0)))
    write_csv(os.path.join(out_dir, f"kins_traffic_{tag}.csv"), ["videoId", "title", "insightTrafficSourceType", "views", "subscribersGained", "averageViewPercentage"], out)
    # END_SCREEN 流入（= 他動画の終了画面からこの動画への流入）が 0 / 極小の動画
    es = {}
    for r in out:
        es.setdefault(r["videoId"], {"videoId": r["videoId"], "title": r["title"], "totalViews": per_video.get(r["videoId"], {}).get("views", ""), "endScreenViews": ""})
        if r["insightTrafficSourceType"] == "END_SCREEN": es[r["videoId"]]["endScreenViews"] = r["views"]
    flagged = []
    for e in es.values():
        v = e["endScreenViews"]
        if v == "" or float(v) <= endscreen_max:
            e["endScreenViews_note"] = "行なし(0)" if v == "" else ""
            flagged.append(e)
    flagged.sort(key=lambda e: -(float(e["totalViews"]) if e["totalViews"] != "" else 0))
    write_csv(os.path.join(out_dir, f"kins_traffic_endscreen_{tag}.csv"), ["videoId", "title", "totalViews", "endScreenViews", "endScreenViews_note"], flagged)
    log(f"[traffic] {len(es)}本 / END_SCREEN<= {endscreen_max}: {len(flagged)}本")


# ---------------- 依頼4 ----------------
def run_cards(api, videos, start, end, out_dir, tag):
    title = {v["videoId"]: v["title"] for v in videos}
    groups = [["views"], ["cardImpressions", "cardClicks", "cardClickRate"], ["annotationImpressions", "annotationClicks", "annotationClickThroughRate"]]
    merged, failed = api.query_metric_groups(start, end, groups, dimensions=["video"], sort="-views", max_results=200)
    if failed: log(f"[cards] 取得できなかった metrics: {failed}")
    cols = ["videoId", "title", "views", "cardImpressions", "cardClicks", "cardClickRate", "annotationImpressions", "annotationClicks", "annotationClickThroughRate"]
    out = []
    for (vid,), m in merged.items():
        out.append({"videoId": vid, "title": title.get(vid, ""), **{c: m.get(c, "") for c in cols[2:]}})
    out.sort(key=lambda r: -(float(r["views"]) if r["views"] != "" else 0))
    write_csv(os.path.join(out_dir, f"kins_cards_{tag}.csv"), cols, out)
    with open(os.path.join(out_dir, f"kins_cards_{tag}.csv"), "a", encoding="utf-8-sig") as f:
        if failed: f.write(f"# 取得不可 metrics: {';'.join(failed)}\n")


# ---------------- 突き合わせ ----------------
def run_reconcile(api, out_dir, tag):
    out = []
    for label, s, e in RECONCILE_PERIODS:
        merged, failed = api.query_metric_groups(s, e, [["views", "subscribersGained", "subscribersLost", "averageViewPercentage"], ["impressions", "impressionClickThroughRate"]])
        m = merged.get((), {})
        out.append({"period": label, "startDate_PT": s, "endDate_PT": e, "views": m.get("views", ""), "subscribersGained": m.get("subscribersGained", ""),
                    "subscribersLost": m.get("subscribersLost", ""), "averageViewPercentage": pct(m.get("averageViewPercentage")),
                    "impressions": m.get("impressions", ""), "ctr": pct(m.get("impressionClickThroughRate"), 2)})
    # JST→PT ずれ確認用: 1 日前倒し
    for label, s, e in RECONCILE_PERIODS[:3]:
        s2 = (date.fromisoformat(s) - timedelta(days=1)).isoformat(); e2 = (date.fromisoformat(e) - timedelta(days=1)).isoformat()
        merged, _ = api.query_metric_groups(s2, e2, [["views", "subscribersGained", "subscribersLost", "averageViewPercentage"]])
        m = merged.get((), {})
        out.append({"period": label + "（PT 1日前倒し）", "startDate_PT": s2, "endDate_PT": e2, "views": m.get("views", ""), "subscribersGained": m.get("subscribersGained", ""),
                    "subscribersLost": m.get("subscribersLost", ""), "averageViewPercentage": pct(m.get("averageViewPercentage")), "impressions": "", "ctr": ""})
    write_csv(os.path.join(out_dir, f"kins_reconcile_{tag}.csv"), ["period", "startDate_PT", "endDate_PT", "views", "subscribersGained", "subscribersLost", "averageViewPercentage", "impressions", "ctr"], out)


def write_csv(path, cols, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    log(f"[write] {path} ({len(rows)}行)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--token", default="yt_token.json", help="認可済みユーザー JSON（無ければ --credentials で作成して保存）")
    ap.add_argument("--credentials", default="credentials.json", help="OAuth クライアント JSON")
    ap.add_argument("--device", action="store_true", help="ブラウザ無し環境向け: デバイスコード方式で認可（URL とコードを表示して待つ）")
    ap.add_argument("--videos-csv", help="Data API の代わりに yt_channel_audit.py の CSV から動画一覧を読む")
    ap.add_argument("--out-dir", default=os.path.join(os.path.dirname(__file__), "..", "..", "clients", "KINS", "output"))
    ap.add_argument("--tag", default=datetime.now(JST).strftime("%Y%m%d"))
    ap.add_argument("--since", default="2025-09-20", help="依頼1 対象の公開日下限")
    ap.add_argument("--lag-days", type=int, default=2, help="Analytics 反映遅れ。公開日+27日+lag が今日(PT)を超える動画は未達扱い")
    ap.add_argument("--traffic-start", default="2026-08-23"); ap.add_argument("--traffic-end", default="2026-09-19")
    ap.add_argument("--traffic-top", type=int, default=20); ap.add_argument("--endscreen-max", type=float, default=5, help="END_SCREEN 流入がこの回数以下なら一覧に載せる")
    ap.add_argument("--retention-id", action="append", default=[], help='"検索語ラベル=videoId" で依頼2の特定を上書き')
    ap.add_argument("--only", default="1,2,3,4,r", help="実行する依頼（例: 1,2）。r=突き合わせ")
    a = ap.parse_args()
    out_dir = os.path.abspath(a.out_dir); os.makedirs(out_dir, exist_ok=True)
    only = set(a.only.split(","))
    today_pt = datetime.now(PT).date()
    api = Api(Auth(a.token, a.credentials, a.device))

    videos = list_videos_csv(a.videos_csv) if a.videos_csv else list_videos_data_api(api)
    if videos is None: sys.exit("動画一覧を取得できませんでした（youtube.readonly スコープ、または --videos-csv を確認）")
    write_csv(os.path.join(out_dir, f"kins_videos_{a.tag}.csv"), ["videoId", "title", "publishedAt", "durationSec", "privacy"], sorted(videos, key=lambda v: v["publishedAt"], reverse=True))

    if "1" in only: run_conv28d(api, videos, date.fromisoformat(a.since), today_pt, a.lag_days, out_dir, a.tag)
    if "2" in only: run_retention(api, videos, dict(x.split("=", 1) for x in a.retention_id), out_dir, a.tag, today_pt)
    if "3" in only: run_traffic(api, videos, a.traffic_start, a.traffic_end, a.traffic_top, out_dir, a.tag, a.endscreen_max)
    if "4" in only: run_cards(api, videos, a.traffic_start, a.traffic_end, out_dir, a.tag)
    if "r" in only: run_reconcile(api, out_dir, a.tag)
    log(f"[done] API calls: {api.calls}")
    with open(os.path.join(out_dir, f"kins_run_{a.tag}.log"), "w", encoding="utf-8") as f: f.write("\n".join(LOG_LINES) + "\n")


if __name__ == "__main__":
    main()
