#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""綿久 三浦くん睡眠計測回（悩み回）サムネ4案＋コンタクトシート（Pillow）
羽毛布団回・敷きパッド回の型（watakyu_thumb_umou.py の描画関数）を流用。案ごとに置き場（グラフ／枕／抱き枕）を別レイヤーで持つ。
レイヤー: layer_01_bg / N_layer_02_guide（置き場、消せる）/ N_layer_03_text（文字・状況テロップ）→ N_final
使い方: python3 COO/scripts/watakyu_thumb_miura.py --font <NotoSansCJKjp-Black.otf> --out <dir>
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import watakyu_thumb_umou as base
from watakyu_thumb_umou import W, H, YELLOW, WHITE, RED, BLACK, LEFT, RIGHT_LIMIT, TEXT_MAX_W, CAPTION, background, fit_font, draw_segments, stroke_of, text_bottom

# (番号, 上段, 下段, 状況テロップ(帯), 置き場の種類)  ※文言は確定どおり1文字も変えない
DESIGNS = [
    ("1", [("横向きのつもりが", YELLOW)], [("実は", WHITE), ("うつぶせ", RED)], "朝起きると体が痛い", "graph"),
    ("2", [("夜中に目が覚める", YELLOW)], [("娘が「", WHITE), ("怖い", RED), ("」と", WHITE)], None, "photo"),
    ("3", [("朝、腕がしびれる", YELLOW)], [("実は", WHITE), ("直せる", RED), ("?", WHITE)], None, "pillow"),
    ("4", [("その抱き枕", YELLOW)], [("使い方", WHITE), ("違う", RED), ("?", WHITE)], None, "dakimakura"),
]
GUIDE_TOP = 440
BOX = (540, GUIDE_TOP, 900, 650)   # 置き場（中央やや右、右1/3は美内先生の顔スペースなので侵さない）

def dashed_rect(d, box, alpha=120, step=14):
    x0, y0, x1, y1 = box
    for x in range(x0, x1, step * 2): d.line([x, y0, min(x + step, x1), y0], fill=(255, 255, 255, alpha), width=2); d.line([x, y1, min(x + step, x1), y1], fill=(255, 255, 255, alpha), width=2)
    for y in range(y0, y1, step * 2): d.line([x0, y, x0, min(y + step, y1)], fill=(255, 255, 255, alpha), width=2); d.line([x1, y, x1, min(y + step, y1)], fill=(255, 255, 255, alpha), width=2)

def guide(font_path, kind):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    f = ImageFont.truetype(font_path, 20); f_s = ImageFont.truetype(font_path, 17)
    x0, y0, x1, y1 = BOX
    d.rectangle(BOX, fill=(255, 255, 255, 28)); dashed_rect(d, BOX)
    if kind == "graph":
        d.multiline_text((x0 + 12, y0 + 10), "体の向きデータ グラフ 差し込み位置\n（色分け・活動量計の実測に差し替え）", font=f_s, fill=(255, 255, 255, 170), spacing=4)
        # 置き場の目安として積み上げ棒のダミー（数値は仮。実データのグラフに差し替える）
        bars = [("横向き", 0.35, (90, 170, 255, 150)), ("仰向け", 0.25, (120, 220, 160, 150)), ("うつぶせ", 0.40, (255, 90, 90, 170))]
        bx0, bx1, by = x0 + 20, x1 - 20, y0 + 76; cx = bx0
        for name, frac, col in bars:
            w = int((bx1 - bx0) * frac); d.rectangle([cx, by, cx + w, by + 56], fill=col)
            d.text((cx + 8, by + 16), name, font=f_s, fill=(255, 255, 255, 220)); cx += w
        d.text((bx0, by + 66), "（割合は仮）", font=f_s, fill=(255, 255, 255, 120))
    else:
        lab = {"photo": "実写 差し込み位置\n（三浦くん・寝室など）", "pillow": "枕 実物写真 差し込み位置", "dakimakura": "抱き枕 実物写真（必須）\n「その」が指す現物をここに"}[kind]
        d.multiline_text((x0 + 12, y0 + 10), lab, font=f, fill=(255, 255, 255, 170), spacing=6)
    d.text((RIGHT_LIMIT + 40, 40), "美内先生 顔の位置（右1/3）", font=f_s, fill=(255, 255, 255, 90))
    return g

def text_layer(font_path, upper, lower, band):
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    y_up, gap = 70, 48
    if band:
        # 上の帯：状況テロップ（濃い帯＋白文字・黒フチ）
        f_b = ImageFont.truetype(font_path, 40); bw = int(f_b.getlength(band)) + 56
        d.rounded_rectangle([LEFT - 8, 26, LEFT - 8 + bw, 26 + 64], radius=10, fill=(120, 0, 0, 215))
        d.text((LEFT + 20, 32), band, font=f_b, fill=WHITE, stroke_width=4, stroke_fill=BLACK)
        y_up, gap = 108, 36
    f_up = fit_font(font_path, "".join(s for s, _ in upper), TEXT_MAX_W, start=150)
    draw_segments(d, LEFT, y_up, upper, f_up, stroke=stroke_of(f_up.size))
    y_lo = y_up + f_up.size + gap
    f_lo = fit_font(font_path, "".join(s for s, _ in lower), TEXT_MAX_W, start=170)
    lo_text = "".join(s for s, _ in lower)
    while f_lo.size > 80 and text_bottom(f_lo, lo_text, y_lo) > GUIDE_TOP - 8: f_lo = ImageFont.truetype(font_path, f_lo.size - 2)
    draw_segments(d, LEFT, y_lo, lower, f_lo, stroke=stroke_of(f_lo.size))
    f_cap = ImageFont.truetype(font_path, 30)
    d.text((LEFT, H - 72), CAPTION, font=f_cap, fill=WHITE, stroke_width=4, stroke_fill=BLACK)
    return t, f_up.size, f_lo.size

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--font", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bg = background(); bg.save(os.path.join(a.out, "layer_01_bg.png"))
    finals = []
    for n, up, lo, band, kind in DESIGNS:
        gd = guide(a.font, kind); gd.save(os.path.join(a.out, f"{n}_layer_02_guide.png"))
        tl, su, sl = text_layer(a.font, up, lo, band); tl.save(os.path.join(a.out, f"{n}_layer_03_text.png"))
        final = Image.alpha_composite(Image.alpha_composite(bg, gd), tl).convert("RGB")
        p = os.path.join(a.out, f"{n}_final.png"); final.save(p); finals.append((n, final))
        print(f"{n}: upper {su}px / lower {sl}px, guide={kind} -> {p}")
    # コンタクトシート 2×2（案番号のみ）
    pad, lab_h = 24, 64; tw, th = W // 2, H // 2
    sheet = Image.new("RGB", (pad + (tw + pad) * 2, (lab_h + th + pad) * 2), (245, 245, 245)); sd = ImageDraw.Draw(sheet)
    f_lab = ImageFont.truetype(a.font, 40)
    for i, (n, im) in enumerate(finals):
        x = pad + (tw + pad) * (i % 2); y = (lab_h + th + pad) * (i // 2)
        sd.text((x, y + 12), f"案{n}", font=f_lab, fill=(20, 20, 20)); sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + lab_h))
    p = os.path.join(a.out, "contact_sheet_1234.png"); sheet.save(p); print("contact:", p)

if __name__ == "__main__": main()
