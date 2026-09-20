#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考チャンネル探索（チャンネル単位）: 検索KW → 候補チャンネル → 概要欄・登録者・直近動画で条件判定 → md
使い方: python3 COO/scripts/yt_channel_finder.py --config CONFIG.json [--cache DIR]
"""
import argparse, json, os, re, sys, statistics
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_trend_collector import Cache, it_post, walk, text, parse_duration, parse_views, parse_rel_days, parse_subs, has_kana
from yt_reference_dental import clean
from yt_channel_audit import details, lockup_rows

def log(*a): print(*a, file=sys.stderr, flush=True)

def search_channels(q, cache):
    d = it_post("search", {"query": q, "params": "EgIQAg=="}, cache, f"chsearch2_{q}")
    out = []
    for c in walk(d or {}, "channelRenderer"):
        out.append((c.get("channelId"), text(c.get("title"))))
    return out

def search_video_channels(q, params, cache, pages=2):
    body = {"query": q}
    if params: body["params"] = params
    d = it_post("search", body, cache, f"search_{q}_{params}_p1")
    out = []
    for page in range(1, pages + 1):
        if not d: break
        for v in walk(d, "videoRenderer"):
            owner = v.get("ownerText") or v.get("longBylineText") or {}
            for r in owner.get("runs", []):
                cid = r.get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId")
                if cid: out.append((cid, text(owner))); break
        tok = next((c.get("token") for c in walk(d, "continuationCommand")), None)
        if not tok or page == pages: break
        d = it_post("search", {"continuation": tok}, cache, f"search_{q}_{params}_p{page+1}")
    return out

def channel_info(cid, cache, pages=2):
    d = it_post("browse", {"browseId": cid, "params": "EgZ2aWRlb3PyBgQKAjoA"}, cache, f"finder_{cid}_videos_p1")
    if not d: return None
    md = (d.get("metadata") or {}).get("channelMetadataRenderer") or {}
    hj = json.dumps(d.get("header", {}), ensure_ascii=False)
    m = re.search(r"チャンネル登録者数 ([\d.,]+(?:万|億)?人)", hj); subs = parse_subs(m.group(0)) if m else None
    m2 = re.search(r"([\d,]+) 本の動画", hj); nvid = int(m2.group(1).replace(",", "")) if m2 else None
    vids = []; page = 1
    while d:
        for lk in walk(d, "lockupViewModel"):
            if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO": continue
            src = json.dumps(lk.get("contentImage", {}))
            mm = re.search(r'/vi(?:_webp)?/[^/]+/([a-z0-9_]+)\.(?:jpg|webp)', src)
            lk_rows = lockup_rows({"lockupViewModel": lk})
            if lk_rows:
                r = lk_rows[0]; r["thumbKind"] = mm.group(1) if mm else None; vids.append(r)
        tok = None
        for c in walk(d, "continuationItemRenderer"):
            tok = (c.get("continuationEndpoint") or {}).get("continuationCommand", {}).get("token"); break
        if not tok or page >= pages: break
        page += 1
        d = it_post("browse", {"continuation": tok}, cache, f"finder_{cid}_videos_p{page}")
    ds = it_post("browse", {"browseId": cid, "params": "EgZzaG9ydHPyBgUKA5oBAA=="}, cache, f"finder_{cid}_shorts_p1")
    n_shorts = len(list(walk(ds or {}, "shortsLockupViewModel")))
    return {"channelId": cid, "name": md.get("title") or "", "description": md.get("description") or "", "url": md.get("vanityChannelUrl") or f"https://www.youtube.com/channel/{cid}",
            "subs": subs, "nvid": nvid, "videos": vids, "n_shorts_p1": n_shorts}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True)
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(__file__), "..", ".cache_yt"))
    a = ap.parse_args(); cfg = json.load(open(a.config, encoding="utf-8")); cache = Cache(a.cache)
    today = datetime.now(timezone.utc).date()
    ev_re = re.compile(cfg["evidence_regex"]); ex_re = re.compile(cfg.get("exclude_regex", "(?!x)x"))
    smin, smax = cfg.get("subs_min", 1000), cfg.get("subs_max", 100000)
    # 1) 候補チャンネル
    cands = {}
    for kw in cfg["keywords"]:
        n0 = len(cands)
        for cid, nm in search_channels(kw, cache): cands.setdefault(cid, {"name": nm, "hits": set()})["hits"].add(kw)
        for params in ["EgIIBQ==", "CAMSAggF", None]:
            for cid, nm in search_video_channels(kw, params, cache): cands.setdefault(cid, {"name": nm, "hits": set()})["hits"].add(kw)
        log(f"[cand] {kw}: +{len(cands)-n0} (total {len(cands)})")
    # 2) チャンネル情報と判定
    kept, rejected = [], []
    for i, (cid, c) in enumerate(cands.items()):
        info = channel_info(cid, cache)
        if not info: rejected.append((c["name"], cid, "取得不可")); continue
        info["hits"] = sorted(c["hits"]); subs = info["subs"]
        longs = [v for v in info["videos"] if v["durationSec"] and v["durationSec"] > 180]
        latest = min([v["relDays_s"] for v in longs if v["relDays_s"] is not None], default=None)
        why = None
        if subs is None: why = "登録者非公開"
        elif subs < smin or subs > smax: why = f"登録者 {subs:,} が範囲外"
        elif not has_kana(info["name"] + " " + " ".join(v["title"] for v in longs[:5])): why = "日本語以外"
        elif len(longs) < 5: why = f"180秒超の動画が{len(longs)}本（主体でない）"
        elif latest is None or latest > 365: why = "直近1年に長尺投稿なし"
        elif ex_re.search(info["name"] + " " + info["description"]): why = "除外語に該当（" + ex_re.search(info["name"] + " " + info["description"]).group(0) + "）"
        else:
            src = info["description"] + "\n" + "\n".join(v["title"] for v in longs[:20])
            m = ev_re.search(info["description"]); mt = [v["title"] for v in longs[:20] if ev_re.search(v["title"])]
            if m: info["evidence"] = "概要欄: …" + info["description"][max(0, m.start()-25):m.end()+25].replace("\n", " ") + "…"
            elif len(mt) >= 2: info["evidence"] = "タイトル: " + " ／ ".join(t[:40] for t in mt[:2])
            else: why = "経営・勤務の根拠がタイトル・概要欄に無い"
        if why: rejected.append((info["name"], cid, why)); continue
        # 直近10本の詳細
        rec = []
        for v in longs[:10]:
            d = details(v["videoId"], cache) or {}
            v.update(d); v["url"] = f"https://www.youtube.com/watch?v={v['videoId']}"
            if not isinstance(v.get("viewCount"), int): v["viewCount"] = v.get("views_s")
            v["ratio"] = (v["viewCount"] / subs) if isinstance(v.get("viewCount"), int) else None
            v["thumb"] = f"https://i.ytimg.com/vi/{v['videoId']}/" + ("maxresdefault.jpg" if v.get("thumbKind") == "hq720" else "hqdefault.jpg")
            rec.append(v)
        rs = [v["ratio"] for v in rec if v["ratio"] is not None]
        info.update({"recent": rec, "avg": sum(rs)/len(rs) if rs else None, "med": statistics.median(rs) if rs else None,
                     "n30": sum(1 for v in longs if v["relDays_s"] is not None and v["relDays_s"] <= 30), "n_long_p": len(longs)})
        kept.append(info)
        if (i + 1) % 25 == 0: log(f"[channels] {i+1}/{len(cands)} kept={len(kept)}")
    kept.sort(key=lambda x: -(x["avg"] or 0))
    log(f"[done] cands={len(cands)} kept={len(kept)} rejected={len(rejected)}")
    # 3) 出力
    def n(x, suf=""): return (f"{x:,}{suf}" if isinstance(x, int) else ("" if x is None else x))
    L = [f"# {cfg['title']}\n\n取得日: {today.isoformat()}　データ源: YouTube InnerTube（search / browse / next）。YouTube Data API はこの環境で利用不可のため代替\n\n"]
    L.append("## 探索・判定条件\n\n")
    L.append(f"- 検索KW（{len(cfg['keywords'])}語）: {' ／ '.join(cfg['keywords'])}。各語でチャンネル検索＋動画検索（1年以内・関連順／再生順／期間なし）を行い、ヒット動画の投稿チャンネルを候補化\n")
    L.append(f"- 登録者 {smin:,}〜{smax:,}人（非公開は除外）／日本語チャンネル／動画タブ直近2ページに180秒超の動画が5本以上／直近1年に長尺投稿あり\n")
    L.append(f"- 経営・勤務の根拠: 概要欄またはタイトル（直近20本中2本以上）に `{cfg['evidence_regex']}` が含まれること。該当箇所を「根拠」列に転記（機械判定。最終確認は要目視）\n")
    L.append("- 倍率 = 再生数 ÷ 登録者数。平均・中央値は直近10本（180秒超）で算出。直近30日の投稿本数は長尺のみ（ショートは日付が取れないため除外）\n")
    L.append("- サムネURL: 一覧にHD版がある動画は maxresdefault、無い動画は hqdefault。hq720 列も併記。実体の取得確認はこの環境では不可\n\n")
    L.append(f"| 項目 | 件数 |\n|---|---|\n| 候補チャンネル | {len(cands)} |\n| 条件クリア | {len(kept)} |\n| 除外 | {len(rejected)} |\n\n")
    L.append("## 1. チャンネル一覧（直近10本の平均倍率 高い順）\n\n| # | チャンネル名 | チャンネルURL | 登録者数 | 総動画本数 | 概要欄（冒頭） | 直近30日投稿(長尺) | 平均倍率 | 中央値倍率 | 根拠 | ヒットKW |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
    for i, c in enumerate(kept, 1):
        L.append(f"| {i} | {clean(c['name'])} | {c['url']} | {n(c['subs'],'人')} | {n(c['nvid'])} | {clean(c['description'])[:120]} | {c['n30']} | {c['avg']:.2f} | {c['med']:.2f} | {clean(c.get('evidence',''))} | {' / '.join(c['hits'])} |\n")
    L.append("\n## 2. 各チャンネルの直近10本（180秒超・新しい順）\n\n")
    for i, c in enumerate(kept, 1):
        L.append(f"### {i}. {clean(c['name'])}（登録 {n(c['subs'],'人')}／平均 {c['avg']:.2f}倍／中央値 {c['med']:.2f}倍）\n\n{c['url']}\n\n概要欄全文: {clean(c['description'])}\n\n")
        L.append("| # | 公開日 | タイトル | 動画URL | サムネ画像URL | サムネURL(hq720) | 再生数 | 尺(秒) | 倍率 |\n|---|---|---|---|---|---|---|---|---|\n")
        for j, v in enumerate(c["recent"], 1):
            rt = f"{v['ratio']:.2f}" if v["ratio"] is not None else ""
            L.append(f"| {j} | {v.get('publishDate') or ''} | {clean(v['title'])} | {v['url']} | {v['thumb']} | https://i.ytimg.com/vi/{v['videoId']}/hq720.jpg | {n(v.get('viewCount'))} | {v['durationSec']} | {rt} |\n")
        L.append("\n")
    L.append("## 3. 除外したチャンネルと理由\n\n| チャンネル名 | チャンネルID | 理由 |\n|---|---|---|\n")
    for nm, cid, why in sorted(rejected, key=lambda x: x[2]): L.append(f"| {clean(nm)} | {cid} | {why} |\n")
    out = cfg["out"]; os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write("".join(L))
    json.dump({"kept": kept, "rejected": rejected}, open(re.sub(r"\.md$", ".json", out), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)

if __name__ == "__main__":
    main()
