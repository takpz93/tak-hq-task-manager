#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千勝会 サムネ文字レイヤー描画（1280x720）
 - 背景レイヤー（bg_*.png）と文字レイヤー（text_*.png, 透過）を別ファイルで出し、合成版（*_thumb_NN.png）を作る
 - 上半分は演者2名（滝口先生・中野先生）の配置スペース。文字は下半分のみ
 - 右下10%（再生時間表示）には文字を置かない
 - 上段: 白・Medium／下段: 黄＋赤縁取り・Black、画面幅80%以上
使い方: python3 chikatsukai_thumb_render.py <config.json>
 config: {"prefix": "8020", "outdir": "...", "bg": [[r,g,b],[r,g,b]], "cards": [{"top": "...", "bottom": "..."}, ...]}
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FONT_BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_MED = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
SAFE_RIGHT = int(W * 0.90)   # 右下10%は空ける（下段・上段ともに右端はここまで）
SAFE_BOTTOM = int(H * 0.90)
MARGIN_L = 40

def font(path, size): return ImageFont.truetype(path, size, index=0)  # index 0 = JP

def background(c1, c2):
    """上→下の縦グラデーション（明度40%前後）"""
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    # 演者スペースの目安（上半分）を薄い破線枠で示す → 背景レイヤーには入れず、ガイドは別ファイル
    return bg

def fit(text, path, max_w, max_h, stroke=0):
    """幅max_w・高さmax_hに収まる最大サイズ"""
    lo, hi = 10, 400
    while lo < hi:
        mid = (lo + hi + 1) // 2
        f = font(path, mid)
        l, t, r, b = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=f, stroke_width=int(mid * stroke))
        if r - l <= max_w and b - t <= max_h: lo = mid
        else: hi = mid - 1
    return lo

def spaced(d, xy, text, f, gap, **kw):
    """1文字ずつ gap px 空けて描く（短い下段を画面幅80%以上に広げるため）"""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, **kw)
        x += d.textlength(ch, font=f) + gap

def spaced_width(d, text, f, gap):
    return sum(d.textlength(ch, font=f) for ch in text) + gap * (len(text) - 1)

def text_layer(top, bottom):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    bw = SAFE_RIGHT - MARGIN_L - 10          # 下段の最大幅（右下10%の手前まで）
    # 下段（主役）: 高さ上限185px、幅が80%未満なら字間で広げる
    bs = fit(bottom, FONT_BLACK, bw, 185, stroke=0.06)
    fb = font(FONT_BLACK, bs); sw = max(6, int(bs * 0.06))
    gap = 0
    need = int(W * 0.80) + 2 * sw
    if spaced_width(d, bottom, fb, 0) + 2 * sw < need and len(bottom) > 1:
        gap = (need - spaced_width(d, bottom, fb, 0) - 2 * sw) / (len(bottom) - 1)
    tw = spaced_width(d, bottom, fb, gap) + 2 * sw
    asc, desc = fb.getmetrics()
    _, t0, _, b0 = d.textbbox((0, 0), bottom, font=fb)
    bx = MARGIN_L + (bw - tw) / 2 + sw
    by = SAFE_BOTTOM - 10 - b0 - sw
    # 上段（細字・白）: 下段の0.36倍以下で明確にサイズ差をつける
    ts = min(fit(top, FONT_MED, bw, 62), int(bs * 0.36))
    ft = font(FONT_MED, ts)
    tl, tt, tr, tb = d.textbbox((0, 0), top, font=ft, stroke_width=3)
    tx = MARGIN_L - tl + (bw - (tr - tl)) // 2
    ty = by + t0 - sw - 14 - tb
    assert ty + tt >= H // 2, "上段が上半分（演者スペース）に食い込んでいる"
    d.text((tx, ty), top, font=ft, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 200))
    # 下段: 外側の暗い縁 → 赤縁取り＋黄文字
    spaced(d, (bx, by), bottom, fb, gap, fill=(0, 0, 0, 0), stroke_width=sw + 5, stroke_fill=(20, 0, 0, 230))
    spaced(d, (bx, by), bottom, fb, gap, fill=(255, 226, 0, 255), stroke_width=sw, stroke_fill=(214, 0, 18, 255))
    box = {"top_size": ts, "bottom_size": bs, "letter_gap": round(gap, 1),
           "bottom_bbox": [round(bx - sw), round(by + t0 - sw), round(bx - sw + tw), round(by + b0 + sw)],
           "bottom_width_ratio": round(tw / W, 3), "top_bbox": [tx + tl, ty + tt, tx + tr, ty + tb]}
    assert box["bottom_bbox"][2] <= SAFE_RIGHT and box["bottom_bbox"][3] <= SAFE_BOTTOM + 2
    return lay, box

def guide_layer():
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    d.rectangle([0, 0, W - 1, H // 2], outline=(255, 255, 255, 120), width=3)
    f = font(FONT_MED, 30)
    d.text((W // 2, H // 4), "演者2名（滝口先生・中野先生）配置エリア", font=f, fill=(255, 255, 255, 150), anchor="mm")
    d.rectangle([SAFE_RIGHT, SAFE_BOTTOM, W - 1, H - 1], fill=(0, 0, 0, 120))
    d.text(((SAFE_RIGHT + W) // 2, (SAFE_BOTTOM + H) // 2), "再生時間", font=font(FONT_MED, 20), fill=(255, 255, 255, 180), anchor="mm")
    return g

def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    out = cfg["outdir"]; pre = cfg["prefix"]
    lay_dir = os.path.join(out, "layers"); os.makedirs(lay_dir, exist_ok=True)
    bg = background(*cfg["bg"]); bg.save(os.path.join(lay_dir, f"{pre}_bg.png"))
    guide = guide_layer(); guide.save(os.path.join(lay_dir, f"{pre}_guide.png"))
    thumbs, info = [], []
    for i, c in enumerate(cfg["cards"], 1):
        lay, box = text_layer(c["top"], c["bottom"])
        lay.save(os.path.join(lay_dir, f"{pre}_text_{i:02d}.png"))
        img = Image.alpha_composite(Image.alpha_composite(bg.convert("RGBA"), guide), lay).convert("RGB")
        p = os.path.join(out, f"{pre}_thumb_{i:02d}.png"); img.save(p)
        thumbs.append(img); info.append({"file": p, **c, **box})
    # コンタクトシート: 横並び（縮小 640x360 ×n）＋ラベル
    sw, sh, pad, lab = 640, 360, 24, 56
    sheet = Image.new("RGB", (pad + len(thumbs) * (sw + pad), sh + pad * 2 + lab), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(thumbs):
        x = pad + i * (sw + pad)
        sheet.paste(im.resize((sw, sh), Image.LANCZOS), (x, pad))
        d.text((x, pad + sh + 12), f"案{i+1}  {cfg['cards'][i]['top']} ／ {cfg['cards'][i]['bottom']}", font=font(FONT_MED, 26), fill=(240, 240, 240))
    sp = os.path.join(out, f"{pre}_contactsheet.png"); sheet.save(sp)
    print(json.dumps({"thumbs": info, "contactsheet": sp}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
