#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""綿久 10/15公開回「羽毛布団、買うなら今？」サムネ3案（A/B/C）＋コンタクトシート生成（Pillow）
レイヤー: 01_bg（背景グラデ）/ 02_guide（写真差し込みガイド・消せる）/ 03_text（文字）→ final に合成
使い方: python3 COO/scripts/watakyu_thumb_umou.py --font <NotoSansCJKjp-Black.otf> --out <dir>
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
YELLOW, WHITE, RED, BLACK = (255, 225, 0, 255), (255, 255, 255, 255), (255, 30, 30, 255), (0, 0, 0, 255)
LEFT = 48                 # 左寄せの基準
TEXT_MAX_W = 820          # 右1/3（x>853）は演者スペースとして空ける
DESIGNS = [  # (ラベル, 上段[(文字, 色)...], 下段[(文字, 色)...])  ※文言は指示どおり1文字も変えない
    ("A", [("10年前の5万円", YELLOW)], [("今の", WHITE), ("10万円", RED)]),
    ("B", [("その「半額」", YELLOW)], [("元から5万円", RED)]),
    ("C", [("買い時を待つな", YELLOW)], [("羽毛は", WHITE), ("時価", RED), ("です", WHITE)]),
]
CAPTION = "業界歴26年・創業177年の老舗寝具店社長"

def fit_font(path, text, max_w, start=170, floor=80):
    for s in range(start, floor, -2):
        f = ImageFont.truetype(path, s)
        if f.getlength(text) <= max_w: return f
    return ImageFont.truetype(path, floor)

def draw_segments(draw, x, y, segs, font, stroke):
    """黒フチを先に全セグメント分描き、その上に色のみを重ねる（セグメント境界でフチが被らない）"""
    cx = x
    for t, _ in segs:
        draw.text((cx, y), t, font=font, fill=BLACK, stroke_width=stroke, stroke_fill=BLACK); cx += font.getlength(t)
    cx = x
    for t, col in segs:
        draw.text((cx, y), t, font=font, fill=col); cx += font.getlength(t)

def background():
    """濃いネイビー→チャコールの斜めグラデ（明度40%前後）"""
    bg = Image.new("RGBA", (W, H))
    px = bg.load()
    c0, c1 = (22, 34, 66), (58, 60, 66)   # navy -> charcoal
    for y in range(H):
        for x in range(W):
            t = (x / W * 0.6 + y / H * 0.4)
            px[x, y] = tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)) + (255,)
    # 左側をわずかに暗くして文字のコントラストを確保
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
    for i in range(0, 900, 4):
        a = int(70 * (1 - i / 900)); sd.rectangle([i, 0, i + 4, H], fill=(0, 0, 0, a))
    return Image.alpha_composite(bg, shade)

def guide(font_path):
    """中央やや右：羽毛布団の実物写真を差し込む位置のガイド（薄い矩形＋破線）。別レイヤーなので消せる"""
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    x0, y0, x1, y1 = 540, 440, 900, 650
    d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255, 28))
    step = 14
    for x in range(x0, x1, step * 2): d.line([x, y0, min(x + step, x1), y0], fill=(255, 255, 255, 120), width=2); d.line([x, y1, min(x + step, x1), y1], fill=(255, 255, 255, 120), width=2)
    for y in range(y0, y1, step * 2): d.line([x0, y, x0, min(y + step, y1)], fill=(255, 255, 255, 120), width=2); d.line([x1, y, x1, min(y + step, y1)], fill=(255, 255, 255, 120), width=2)
    f = ImageFont.truetype(font_path, 22)
    d.text((x0 + 14, y0 + 12), "羽毛布団 写真 差し込み位置", font=f, fill=(255, 255, 255, 150))
    return g

def text_layer(font_path, upper, lower):
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    f_up = fit_font(font_path, "".join(s for s, _ in upper), TEXT_MAX_W, start=150)
    f_lo = fit_font(font_path, "".join(s for s, _ in lower), TEXT_MAX_W, start=170)
    y_up = 70
    draw_segments(d, LEFT, y_up, upper, f_up, stroke=max(8, f_up.size // 12))
    y_lo = y_up + f_up.size + 48
    draw_segments(d, LEFT, y_lo, lower, f_lo, stroke=max(8, f_lo.size // 12))
    f_cap = ImageFont.truetype(font_path, 30)
    d.text((LEFT, H - 72), CAPTION, font=f_cap, fill=WHITE, stroke_width=4, stroke_fill=BLACK)
    return t, f_up.size, f_lo.size

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--font", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bg = background(); gd = guide(a.font)
    bg.save(os.path.join(a.out, "layer_01_bg.png")); gd.save(os.path.join(a.out, "layer_02_guide.png"))
    finals = []
    for label, up, lo in DESIGNS:
        tl, su, sl = text_layer(a.font, up, lo)
        tl.save(os.path.join(a.out, f"{label}_layer_03_text.png"))
        final = Image.alpha_composite(Image.alpha_composite(bg, gd), tl).convert("RGB")
        p = os.path.join(a.out, f"{label}_final.png"); final.save(p); finals.append((label, final))
        print(f"{label}: font upper {su}px / lower {sl}px -> {p}")
    # コンタクトシート（横一列、上にラベル）
    pad, lab_h = 24, 70; tw = W // 2; th = H // 2
    sheet = Image.new("RGB", (pad + (tw + pad) * 3, lab_h + th + pad), (245, 245, 245)); sd = ImageDraw.Draw(sheet)
    f_lab = ImageFont.truetype(a.font, 40)
    for i, (label, im) in enumerate(finals):
        x = pad + (tw + pad) * i
        sd.text((x, 14), f"{label}案", font=f_lab, fill=(20, 20, 20))
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, lab_h))
    p = os.path.join(a.out, "contact_sheet_ABC.png"); sheet.save(p); print("contact:", p)

if __name__ == "__main__": main()
