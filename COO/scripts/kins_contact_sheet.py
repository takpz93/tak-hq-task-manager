#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KINS サムネ コンタクトシート生成（ローカル実行用）
使い方: python3 COO/scripts/kins_contact_sheet.py <一覧CSV> <出力ディレクトリ>
  - thumbs/{videoId}.jpg にサムネを保存（maxresdefault → 無ければ hqdefault）
  - CTR降順・公開日順の 5列×8行 グリッド PNG を複数枚出力
"""
import csv, os, sys, io, requests
from PIL import Image, ImageDraw, ImageFont
src, outdir = sys.argv[1], sys.argv[2]; th = os.path.join(outdir, "thumbs"); os.makedirs(th, exist_ok=True)
rows = [r for r in csv.DictReader(open(src, encoding="utf-8-sig"))]
def fetch(vid):
    p = os.path.join(th, f"{vid}.jpg")
    if os.path.exists(p) and os.path.getsize(p) > 1000: return p
    for kind in ("maxresdefault", "hqdefault"):
        r = requests.get(f"https://i.ytimg.com/vi/{vid}/{kind}.jpg", timeout=20)
        if r.status_code == 200 and len(r.content) > 1000:
            open(p, "wb").write(r.content); return p
    return None
try: font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc", 14)
except Exception:
    try: font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 14)
    except Exception: font = ImageFont.load_default()
W, Hh, cols, rws = 320, 180, 5, 8; cap = 26
def sheet(items, prefix):
    for page in range(0, len(items), cols * rws):
        chunk = items[page:page + cols * rws]
        im = Image.new("RGB", (cols * (W + 10) + 10, rws * (Hh + cap + 10) + 10), "white"); dr = ImageDraw.Draw(im)
        for i, r in enumerate(chunk):
            x = 10 + (i % cols) * (W + 10); y = 10 + (i // cols) * (Hh + cap + 10)
            p = fetch(r["videoId"])
            if p:
                t = Image.open(p).convert("RGB"); t.thumbnail((W, Hh)); im.paste(t, (x, y))
            ctr = r["CTR(%)"]; imp = r["インプレッション"]
            dr.text((x, y + Hh + 4), f"{r['順位'] or '-'}｜CTR {ctr}{'%' if ctr not in ('未取得','') else ''}｜インプ {imp}｜再生 {r['再生数(現在)']}｜{r['公開日']}", fill="black", font=font)
        im.save(os.path.join(outdir, f"{prefix}_{page // (cols * rws) + 1:02d}.png")); print("saved", prefix, page // (cols * rws) + 1)
byctr = sorted(rows, key=lambda r: (-(float(r["CTR(%)"]) if r["CTR(%)"] not in ("未取得", "") else -1)))
sheet(byctr, "KINS_サムネ一覧_CTR順"); sheet(sorted(rows, key=lambda r: r["公開日"], reverse=True), "KINS_サムネ一覧_公開日順")
