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
 強調: 文言中の [ ] で囲んだ部分を強調色で描く（例 "[何分]で終わってる？"）。括弧は描画しない
   上段の強調 = 黄・Black・赤縁／下段の強調 = 赤・Black・白縁（通常の下段は黄・赤縁）
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

def parse(text):
    """'[強調]通常' → [(文字, 強調か)]"""
    out, emph = [], False
    for ch in text:
        if ch == "[": emph = True
        elif ch == "]": emph = False
        else: out.append((ch, emph))
    return out

def plain(text): return text.replace("[", "").replace("]", "")

RED, YELLOW, WHITE, DARK = (214, 0, 18, 255), (255, 226, 0, 255), (255, 255, 255, 255), (20, 0, 0, 230)

def draw_chars(d, x, base, chars, fonts, gap, styles):
    """1文字ずつベースライン揃えで描く。styles[emph] = (font_key, fill, stroke_w, stroke_fill, outer_w)"""
    # 外側の暗い縁を先に全文字ぶん描いてから本体を重ねる（隣の文字の縁が本体に被らないように）
    for layer in ("outer", "body"):
        cx = x
        for ch, emph in chars:
            fk, fill, sw, sf, ow = styles[emph]
            f = fonts[fk]
            if layer == "outer" and ow:
                d.text((cx, base), ch, font=f, fill=(0, 0, 0, 0), stroke_width=sw + ow, stroke_fill=DARK, anchor="ls")
            if layer == "body":
                d.text((cx, base), ch, font=f, fill=fill, stroke_width=sw, stroke_fill=sf, anchor="ls")
            cx += d.textlength(ch, font=f) + gap

def chars_width(d, chars, fonts, styles, gap):
    return sum(d.textlength(ch, font=fonts[styles[e][0]]) for ch, e in chars) + gap * (len(chars) - 1)

def text_layer(top, bottom):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    bw = SAFE_RIGHT - MARGIN_L - 10          # 文字の最大幅（右下10%の手前まで）
    # 下段（主役）: 高さ上限175px、幅が80%未満なら字間で広げる
    bs = fit(plain(bottom), FONT_BLACK, bw, 175, stroke=0.06)
    sw = max(6, int(bs * 0.06))
    bf = {"B": font(FONT_BLACK, bs)}
    bstyle = {False: ("B", YELLOW, sw, RED, 5), True: ("B", RED, sw, WHITE, 5)}
    bch = parse(bottom)
    gap = 0
    need = int(W * 0.80) + 2 * sw
    w0 = chars_width(d, bch, bf, bstyle, 0)
    if w0 + 2 * sw < need and len(bch) > 1:
        gap = (need - w0 - 2 * sw) / (len(bch) - 1)
    tw = chars_width(d, bch, bf, bstyle, gap) + 2 * sw
    asc, desc = bf["B"].getmetrics()
    bx = MARGIN_L + (bw - tw) / 2 + sw
    base_b = SAFE_BOTTOM - 10 - sw - int(desc * 0.55)
    _, gt, _, gb = d.textbbox((0, base_b), "定", font=bf["B"], anchor="ls")
    # 上段: 白・Medium（強調は黄・Black）。下段の0.5倍・最低60px・高さ上限80px
    tp = plain(top)
    ts = min(fit(tp, FONT_BLACK, bw, 80), max(int(bs * 0.5), 60))
    while True:   # 上半分（演者スペース）に入らないサイズまで下げる
        tsw = max(3, int(ts * 0.06))
        tf = {"M": font(FONT_MED, ts), "B": font(FONT_BLACK, ts)}
        _, tt, _, tb = d.textbbox((0, 0), "定", font=tf["B"], anchor="ls")
        base_t = gt - sw - 5 - 16 - tb             # 下段の上端（縁込み）から16px空ける
        top_y = base_t + tt - tsw - 3
        if top_y >= H // 2 + 4 or ts <= 40: break
        ts -= 2
    tstyle = {False: ("M", WHITE, 3, (0, 0, 0, 200), 0), True: ("B", YELLOW, tsw, RED, 3)}
    tch = parse(top)
    ttw = chars_width(d, tch, tf, tstyle, 0)
    tx = MARGIN_L + (bw - ttw) / 2
    assert top_y >= H // 2, f"上段が上半分（演者スペース）に食い込んでいる: {top_y}"
    draw_chars(d, tx, base_t, tch, tf, 0, tstyle)
    draw_chars(d, bx, base_b, bch, bf, gap, bstyle)
    bb = lay.getbbox()
    box = {"top_size": ts, "bottom_size": bs, "letter_gap": round(gap, 1),
           "bottom_width_ratio": round(tw / W, 3), "text_bbox": list(bb)}
    assert bb[2] <= SAFE_RIGHT and bb[3] <= SAFE_BOTTOM and bb[1] >= H // 2, f"安全域はみ出し: {bb}"
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
        d.text((x, pad + sh + 12), f"案{i+1}  {plain(cfg['cards'][i]['top'])} ／ {plain(cfg['cards'][i]['bottom'])}", font=font(FONT_MED, 26), fill=(240, 240, 240))
    sp = os.path.join(out, f"{pre}_contactsheet.png"); sheet.save(sp)
    print(json.dumps({"thumbs": info, "contactsheet": sp}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
