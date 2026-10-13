#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""綿久 10/15公開回「羽毛布団、買うなら今？」サムネ3案（A/B/C）＋コンタクトシート生成（Pillow）
レイヤー: 01_bg（背景グラデ）/ 02_guide（写真差し込みガイド・消せる）/ 03_text（文字）→ final に合成
使い方: python3 COO/scripts/watakyu_thumb_umou.py --font <NotoSansCJKjp-Black.otf> --out <dir> [--variant v1|v2]
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
YELLOW, WHITE, RED, BLACK = (255, 225, 0, 255), (255, 255, 255, 255), (255, 30, 30, 255), (0, 0, 0, 255)
LEFT = 48                 # 左寄せの基準
RIGHT_LIMIT = 853         # 右1/3（x>=853）は演者スペースとして空ける
TEXT_MAX_W = RIGHT_LIMIT - 48  # フチ込みの最大描画幅
GUIDE_TOP = 440           # 写真ガイドの上辺（文字はこの上に収める）
DESIGNS = [  # (ラベル, 上段[(文字, 色)...], 下段[(文字, 色)...])  ※文言は指示どおり1文字も変えない
    ("A", [("10年前の5万円", YELLOW)], [("今の", WHITE), ("10万円", RED)]),
    ("B", [("その「半額」", YELLOW)], [("元から5万円", RED)]),
    ("C", [("買い時を待つな", YELLOW)], [("羽毛は", WHITE), ("時価", RED), ("です", WHITE)]),
]
# v2（差し戻し後）: 1行目で商品を言い切り、2行目で結論。(ラベル, 上段, 下段, 写真ガイド枚数)  ※文言は指示どおり1文字も変えない
DESIGNS_V2 = [
    ("A", [("羽毛布団の", YELLOW)], [("半額は", WHITE), ("疑え", RED)], 1),
    ("B", [("昔5万の羽毛布団", YELLOW)], [("今は", WHITE), ("10万", RED), ("です", WHITE)], 1),
    ("C", [("同じ羽毛布団", YELLOW)], [("なぜ値段が", WHITE), ("倍", RED)], 2),
]
CAPTION = "業界歴26年・創業177年の老舗寝具店社長"

def stroke_of(size): return max(8, size // 12)

def fit_font(path, text, max_w, start=170, floor=80):
    """黒フチ込みの実描画幅が max_w に収まる最大サイズ"""
    for sz in range(start, floor, -2):
        f = ImageFont.truetype(path, sz)
        if f.getlength(text) + 2 * stroke_of(sz) <= max_w: return f
    return ImageFont.truetype(path, floor)

def text_bottom(f, text, y):
    """フチ込みで文字が実際に占める下端 y"""
    return y + f.getbbox(text, stroke_width=stroke_of(f.size))[3]

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

def guide(font_path, n=1):
    """中央やや右：羽毛布団の実物写真を差し込む位置のガイド（薄い矩形＋破線）。n=2 で横並び2枚。別レイヤーなので消せる"""
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    rects = [(540, GUIDE_TOP, 900, 650)] if n == 1 else [(470, GUIDE_TOP, 680, 650), (700, GUIDE_TOP, 910, 650)]
    f = ImageFont.truetype(font_path, 22 if n == 1 else 18)
    for i, (x0, y0, x1, y1) in enumerate(rects, 1):
        d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255, 28))
        step = 14
        for x in range(x0, x1, step * 2): d.line([x, y0, min(x + step, x1), y0], fill=(255, 255, 255, 120), width=2); d.line([x, y1, min(x + step, x1), y1], fill=(255, 255, 255, 120), width=2)
        for y in range(y0, y1, step * 2): d.line([x0, y, x0, min(y + step, y1)], fill=(255, 255, 255, 120), width=2); d.line([x1, y, x1, min(y + step, y1)], fill=(255, 255, 255, 120), width=2)
        lab = "羽毛布団 写真 差し込み位置" if n == 1 else f"羽毛布団 写真{i}"
        d.text((x0 + 14, y0 + 12), lab, font=f, fill=(255, 255, 255, 150))
    return g

def text_layer(font_path, upper, lower):
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    f_up = fit_font(font_path, "".join(s for s, _ in upper), TEXT_MAX_W, start=150)
    f_lo = fit_font(font_path, "".join(s for s, _ in lower), TEXT_MAX_W, start=170)
    y_up = 70
    draw_segments(d, LEFT, y_up, upper, f_up, stroke=stroke_of(f_up.size))
    y_lo = y_up + f_up.size + 48
    # 下段の底（フチ・ディセンダ込み）が写真ガイド上辺に掛からないよう、実測で収まるまで縮める
    lo_text = "".join(s for s, _ in lower)
    while f_lo.size > 80 and text_bottom(f_lo, lo_text, y_lo) > GUIDE_TOP - 8: f_lo = ImageFont.truetype(font_path, f_lo.size - 2)
    draw_segments(d, LEFT, y_lo, lower, f_lo, stroke=stroke_of(f_lo.size))
    f_cap = ImageFont.truetype(font_path, 30)
    d.text((LEFT, H - 72), CAPTION, font=f_cap, fill=WHITE, stroke_width=4, stroke_fill=BLACK)
    return t, f_up.size, f_lo.size

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--font", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--variant", choices=["v1", "v2"], default="v1", help="v1=初版文言, v2=差し戻し後の文言（ファイル名に _v2）")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    designs = [(l, u, lo, 1) for l, u, lo in DESIGNS] if a.variant == "v1" else DESIGNS_V2
    sfx = "" if a.variant == "v1" else "_v2"
    bg = background(); bg.save(os.path.join(a.out, f"layer_01_bg{sfx}.png"))
    guides = {}
    finals = []
    for label, up, lo, n in designs:
        if n not in guides:
            guides[n] = guide(a.font, n); guides[n].save(os.path.join(a.out, f"layer_02_guide{sfx}_{n}photo.png"))
        tl, su, sl = text_layer(a.font, up, lo)
        tl.save(os.path.join(a.out, f"{label}_layer_03_text{sfx}.png"))
        final = Image.alpha_composite(Image.alpha_composite(bg, guides[n]), tl).convert("RGB")
        p = os.path.join(a.out, f"{label}_final{sfx}.png"); final.save(p); finals.append((label, final))
        print(f"{label}: font upper {su}px / lower {sl}px, guide x{n} -> {p}")
    # コンタクトシート（横一列、上にラベル）
    pad, lab_h = 24, 70; tw = W // 2; th = H // 2
    sheet = Image.new("RGB", (pad + (tw + pad) * 3, lab_h + th + pad), (245, 245, 245)); sd = ImageDraw.Draw(sheet)
    f_lab = ImageFont.truetype(a.font, 40)
    for i, (label, im) in enumerate(finals):
        x = pad + (tw + pad) * i
        sd.text((x, 14), f"{label}案", font=f_lab, fill=(20, 20, 20))
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, lab_h))
    p = os.path.join(a.out, f"contact_sheet_ABC{sfx}.png"); sheet.save(p); print("contact:", p)

if __name__ == "__main__": main()
