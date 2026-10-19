#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""綿久 冬のあったか敷きパッド2026（ニトリ／無印／西川 比較）サムネ3案＋コンタクトシート（Pillow）
10/15羽毛布団回の型（watakyu_thumb_umou.py の描画関数）を流用し、ロゴ3社横並び＋敷きパッド写真3枚のガイドを追加。
レイヤー: 01_bg / 02_guide（ロゴ・写真の置き場、消せる）/ 03_text → final
使い方: python3 COO/scripts/watakyu_thumb_shikipad.py --font <NotoSansCJKjp-Black.otf> --out <dir>
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import watakyu_thumb_umou as base
from watakyu_thumb_umou import W, H, YELLOW, WHITE, RED, BLACK, LEFT, RIGHT_LIMIT, background, text_layer

base.GUIDE_TOP = 412   # 文字はロゴ行（y=420〜）の上に収める
BRANDS = ["ニトリ", "無印良品", "西川"]
LOGO_Y, LOGO_H = 420, 56          # ロゴ行（3社同じ大きさで横並び）
PHOTO_Y, PHOTO_H = 486, 150       # 敷きパッド実物写真3枚（ロゴの直下、同じ列幅）
COL_W, GAP = 232, 16              # 3列 = 48 + 232*3 + 16*2 = 776 < 853（右1/3は演者スペース）
DESIGNS = [  # (ラベル, 上段, 下段)  ※文言は指示どおり1文字も変えない
    ("1", [("冬の敷きパッド", YELLOW)], [("暖かさで", WHITE), ("選ぶな", RED)]),
    ("2", [("冬の敷きパッド", YELLOW)], [("正解", RED), ("はどれ？", WHITE)]),
    ("3", [("夜中に暑い？", YELLOW)], [("敷きパッド", RED), ("かも", WHITE)]),
]

def dashed_rect(d, box, alpha=120, step=12):
    x0, y0, x1, y1 = box
    for x in range(x0, x1, step * 2): d.line([x, y0, min(x + step, x1), y0], fill=(255, 255, 255, alpha), width=2); d.line([x, y1, min(x + step, x1), y1], fill=(255, 255, 255, alpha), width=2)
    for y in range(y0, y1, step * 2): d.line([x0, y, x0, min(y + step, y1)], fill=(255, 255, 255, alpha), width=2); d.line([x1, y, x1, min(y + step, y1)], fill=(255, 255, 255, alpha), width=2)

def guide(font_path):
    """ロゴ3社（同サイズ横並び）＋ 敷きパッド写真3枚の置き場。別レイヤーなので消せる"""
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    f_logo = ImageFont.truetype(font_path, 30); f_lab = ImageFont.truetype(font_path, 18)
    for i, name in enumerate(BRANDS):
        x0 = LEFT + i * (COL_W + GAP); x1 = x0 + COL_W
        # ロゴ枠（白地・薄い）：実ロゴをここに同じ大きさで差し込む
        d.rounded_rectangle([x0, LOGO_Y, x1, LOGO_Y + LOGO_H], radius=8, fill=(255, 255, 255, 46))
        dashed_rect(d, (x0, LOGO_Y, x1, LOGO_Y + LOGO_H))
        tw = f_logo.getlength(name); d.text((x0 + (COL_W - tw) / 2, LOGO_Y + 9), name, font=f_logo, fill=(255, 255, 255, 190))
        # 写真枠
        d.rectangle([x0, PHOTO_Y, x1, PHOTO_Y + PHOTO_H], fill=(255, 255, 255, 28))
        dashed_rect(d, (x0, PHOTO_Y, x1, PHOTO_Y + PHOTO_H))
        d.text((x0 + 10, PHOTO_Y + 8), f"{name} 敷きパッド 実物写真", font=f_lab, fill=(255, 255, 255, 150))
    # 演者スペースの目安（右1/3）
    d.text((RIGHT_LIMIT + 40, 40), "美内先生 顔の位置（右1/3）", font=f_lab, fill=(255, 255, 255, 90))
    return g

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
    pad, lab_h = 24, 70; tw = W // 2; th = H // 2
    sheet = Image.new("RGB", (pad + (tw + pad) * 3, lab_h + th + pad), (245, 245, 245)); sd = ImageDraw.Draw(sheet)
    f_lab = ImageFont.truetype(a.font, 40)
    for i, (label, im) in enumerate(finals):
        x = pad + (tw + pad) * i
        sd.text((x, 14), f"案{label}" + ("（第一候補）" if label == "1" else ""), font=f_lab, fill=(20, 20, 20))
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, lab_h))
    p = os.path.join(a.out, "contact_sheet_123.png"); sheet.save(p); print("contact:", p)

if __name__ == "__main__": main()
