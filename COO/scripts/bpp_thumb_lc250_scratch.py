"""BPP ランクル250（黒・洗車傷を磨く回）サムネ 3 案。

文字の組み方は bpp_thumb_comps.py（2026-10-12 版）と同じ：
上段＝白＋黒縁、下段＝オレンジ＋白縁（外周に黒）、右上に車名、右下 10% は空ける、
中段（y 210〜512）は見せたい部分のため文字を置かない。

書き出し（--out）:
  A.png / B.png / C.png   … 仮背景＋文字の合成
  layers/X_text.png       … 文字（車名・Before/After バッジ・矢印を含む）だけの透過 PNG
  layers/X_bg.png         … 仮背景（黒ボディの洗車傷）
  contact_sheet.png       … 3 案一覧

使い方:
  python COO/scripts/bpp_thumb_lc250_scratch.py --font /path/to/NotoSansCJKjp-Black.otf \
      --out thumbnails/bpp/landcruiser250_scratch_20261025
"""

import argparse
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bpp_thumb_comps import (H, LOWER_BOX, NAVY, ORANGE, RED, UPPER_BOX, W, add_reflection, badge,  # noqa: E402
                             black_paint, car_name_layer, condensed_block, red_arrow)

# 上段は 2026-10-12 版の枠を 3px 上げる（縁取りのにじみが中段 y210 にかからないように）
UPPER_BOX = (UPPER_BOX[0], UPPER_BOX[1] - 3, UPPER_BOX[2], UPPER_BOX[3] - 3)

SHEET_ORDER = ("A", "B", "B2", "C")  # コンタクトシートに並べる順

PATTERNS = [
    dict(label="A", upper="ディーラーコーティング", lower="1年後の黒ランクル", scene="swirl"),
    # B・B2（Tak案で差し替え）：Before/After なし。C と同じ 1 枚の黒ボディ＋洗車傷
    dict(label="B", upper="パール無しの黒", lower="ごまかせない", scene="swirl_macro"),
    dict(label="B2", upper="パール無しの黒", lower="傷はごまかせない", scene="swirl_macro"),
    dict(label="C", upper="どこまで取れる？", lower="黒の洗車傷", scene="swirl_macro"),
    # A の別案（コンタクトシートには入れない）：Before/After にして「磨けば戻る」に寄せる
    dict(label="A_alt", upper="ディーラーコーティング", lower="1年後の黒ランクル", scene="before_after"),
]


# ---------------------------------------------------------------- 仮背景

def add_light(img, center, r, strength=1.0):
    """照明の映り込み（白い光源）。洗車傷はこの周りに同心円状に浮く。"""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = center
    d.ellipse((cx - r, cy - r * 0.42, cx + r, cy + r * 0.42), fill=(255, 255, 255, int(235 * strength)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r * 0.18)))
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - r * 3, cy - r * 1.4, cx + r * 3, cy + r * 1.4),
                                 fill=(200, 205, 215, int(70 * strength)))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(r * 0.9)))


def add_swirls(img, center, rmin, rmax, n, seed, bright=1.0):
    """光源を中心にした細い円弧（スワールマーク）と、ランダムな直線の擦り傷。"""
    rng = random.Random(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = center
    for _ in range(n):
        r = rng.uniform(rmin, rmax)
        start = rng.uniform(0, 360)
        span = rng.uniform(8, 34)
        a = int(rng.uniform(40, 150) * bright * max(0.35, 1 - (r - rmin) / (rmax - rmin + 1)))
        ry = r * rng.uniform(0.55, 0.75)
        d.arc((cx - r, cy - ry, cx + r, cy + ry), start, start + span, fill=(235, 238, 245, a), width=1)
    for _ in range(n // 6):  # 直線の擦り傷
        x, y = rng.uniform(0, W), rng.uniform(150, 560)
        ang = rng.uniform(0, math.pi)
        ln = rng.uniform(20, 90)
        d.line((x, y, x + ln * math.cos(ang), y + ln * math.sin(ang)),
               fill=(220, 224, 232, int(rng.uniform(25, 70) * bright)), width=1)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.35)))


def shade_bands(img):
    """上下の文字帯を少し落とす（2026-10-12 版と同じ処理）。"""
    grad = Image.new("L", (1, H))
    for y in range(H):
        v = int(110 * (1 - y / 210)) if y < 210 else int(150 * (y - 500) / 220) if y > 500 else 0
        grad.putpixel((0, y), v)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    shade.putalpha(grad.resize((W, H)))
    img.alpha_composite(shade)


def scratched(seed, center=(760, 360), light_r=70, rmin=60, rmax=640, n=2600, bright=1.0):
    img = black_paint(seed=seed)
    add_light(img, center, light_r)
    add_swirls(img, center, rmin, rmax, n, seed, bright)
    return img


def scene(name):
    if name == "swirl":
        # 「全面ボロボロ」に見せない：傷は細かく控えめ、光源の艶を大きく
        # 傷の中心を下げ、上段の直下（y200〜300）は傷を薄くする
        img = scratched(11, center=(760, 420), light_r=95, rmin=70, rmax=560, n=1500, bright=0.7)
    elif name == "swirl_macro":
        img = scratched(13, center=(700, 350), light_r=110, rmin=80, rmax=520, n=4200, bright=1.35)
    elif name == "before_after":
        left = scratched(12, center=(320, 360), light_r=60, rmin=50, rmax=420, n=2400)
        right = black_paint(seed=14, glossy=True)
        add_light(right, (960, 360), 60)
        add_reflection(right, (W // 2, 240, W, 480))
        img = Image.new("RGBA", (W, H))
        img.paste(left.crop((0, 0, W // 2, H)), (0, 0))
        img.paste(right.crop((W // 2, 0, W, H)), (W // 2, 0))
        ImageDraw.Draw(img).line((W // 2, 0, W // 2, H), fill=(255, 255, 255, 255), width=6)
    else:
        raise ValueError(name)
    shade_bands(img)
    return img


# ---------------------------------------------------------------- 文字レイヤー

def text_layer(p, font_path):
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if p["scene"] == "before_after":
        badge(out, font_path, "Before", (34, 440), NAVY)
        aw = badge(Image.new("RGBA", (W, H)), font_path, "After", (0, 0), RED)  # 幅だけ測る
        badge(out, font_path, "After", (1240 - aw, 440), RED)
        red_arrow(out, W // 2, 362)
    out.alpha_composite(car_name_layer(font_path))
    out.alpha_composite(condensed_block(p["upper"], font_path, UPPER_BOX, (255, 255, 255),
                                        [((0, 0, 0), 13)], grow=14))
    out.alpha_composite(condensed_block(p["lower"], font_path, LOWER_BOX, ORANGE,
                                        [((0, 0, 0), 17), ((255, 255, 255), 12)],
                                        grow=0, anchor="bottom"))  # 中段（y≤512）へ伸ばさない
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "layers"), exist_ok=True)

    items = []
    for p in PATTERNS:
        bg = scene(p["scene"])
        txt = text_layer(p, a.font)
        comp = bg.copy()
        comp.alpha_composite(txt)
        comp = comp.convert("RGB")
        comp.save(os.path.join(a.out, f"{p['label']}.png"))
        txt.save(os.path.join(a.out, "layers", f"{p['label']}_text.png"))
        bg.convert("RGB").save(os.path.join(a.out, "layers", f"{p['label']}_bg.png"))
        alpha = txt.getchannel("A")
        zone = alpha.crop((int(W * 0.9), int(H * 0.9), W, H)).getextrema()
        mid = alpha.crop((0, 212, W, 512)).getbbox()
        print(p["label"], "badge_zone_alpha", zone, "text_in_mid_band_bbox", mid)
        if p["label"] in SHEET_ORDER:
            items.append((p, comp))

    items.sort(key=lambda it: SHEET_ORDER.index(it[0]["label"]))
    tw, th, gap, cap = 560, 315, 24, 44
    sheet = Image.new("RGB", (gap + len(items) * (tw + gap), 70 + th + cap + gap), (244, 244, 244))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 18), "BPP ランクル250（黒）洗車傷の回｜サムネ4案（仮背景）",
           font=ImageFont.truetype(a.font, 30), fill=(20, 20, 20))
    f = ImageFont.truetype(a.font, 22)
    for i, (p, img) in enumerate(items):
        cx = gap + i * (tw + gap)
        d.text((cx, 70), f"{p['label']}  {p['upper']} ／ {p['lower']}", font=f, fill=(30, 30, 30))
        sheet.paste(img.resize((tw, th), Image.LANCZOS), (cx, 70 + cap))
    sheet.save(os.path.join(a.out, "contact_sheet.png"))


if __name__ == "__main__":
    main()
