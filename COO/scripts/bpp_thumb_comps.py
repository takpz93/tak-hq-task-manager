"""BPP（BUDDICA PHOENIX PRO）サムネ案のレイアウトカンプ生成。

各案について 3 種類の PNG を書き出す:
  NN_comp.png     … 模擬画（画カット指定のイメージ）＋文字を合成したカンプ
  NN_overlay.png  … 文字・バッジ・矢印だけの透過 PNG（実フレームに重ねて使う）
  NN_guide.png    … カンプに被写体ゾーン・再生時間バッジ域の点線を重ねた確認用
加えて contact_sheet.png（9 案一覧）。

使い方:
  python COO/scripts/bpp_thumb_comps.py --font /path/to/NotoSansCJKjp-Black.otf \
      --out clients/BPP/output/2026-10-12_ランクル250_サムネ案
"""

import argparse
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
ORANGE = (240, 128, 48)
NAVY = (22, 40, 92)
RED = (214, 28, 36)
CAR_NAME = "トヨタ ランドクルーザー250"

# レイアウト（px）
UPPER_BOX = (28, 54, 1252, 200)      # 上段: 白文字＋黒縁
LOWER_BOX = (22, 520, 1140, 702)     # 下段: オレンジ＋白縁。右下 10% を避けて x≤1140
SUBJECT_ZONE = (0, 210, W, 512)      # 見せたい部分（文字を置かない）
DURATION_ZONE = (int(W * 0.9), int(H * 0.9), W, H)  # 再生時間バッジ域

MIN_CONDENSE = 0.62   # 長体の下限（これ以上潰すなら文字サイズを下げる）
MAX_CONDENSE = 0.92   # 長体の上限（最低でもこれだけはかける）

PATTERNS = [
    dict(no=1, upper="コーティングしたのに", lower="1年でこうなる", scene="purple_side"),
    dict(no=2, upper="洗っても消えない", lower="黒は隠せない", scene="spots_wide"),
    dict(no=3, upper="1年前にコーティング", lower="なのに鉄粉だらけ", scene="purple_dense"),
    dict(no=4, upper="塗って終わりじゃない", lower="1年後の黒ランクル", scene="full_with_inset"),
    dict(no=5, upper="この白い跡、何？", lower="洗っても落ちません", scene="spots_macro"),
    dict(no=6, upper="1年でこんなに汚れる", lower="黒のランクル250", scene="purple_rear"),
    dict(no=7, upper="コーティング済みの車", lower="鉄粉が刺さってた", scene="purple_macro"),
    dict(no=8, upper="黒は1年でこうなる", lower="落とせるのはプロだけ", scene="before_after"),
    dict(no=9, upper="映り込みが戻った", lower="黒本来の深み", scene="reflection"),
]


# ---------------------------------------------------------------- 文字描画

def _dilate(mask, r):
    """円形カーネルで alpha マスクを膨張させる（縁取り用）。"""
    a = np.asarray(mask, dtype=np.uint8)
    out = a.copy()
    h, w = a.shape
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r:
                continue
            ys, yd = (slice(dy, h), slice(0, h - dy)) if dy >= 0 else (slice(0, h + dy), slice(-dy, h))
            xs, xd = (slice(dx, w), slice(0, w - dx)) if dx >= 0 else (slice(0, w + dx), slice(-dx, w))
            np.maximum(out[ys, xs], a[yd, xd], out=out[ys, xs])
    return Image.fromarray(out)


def _text_mask(text, font_path, size):
    font = ImageFont.truetype(font_path, size)
    l, t, r, b = font.getbbox(text)
    pad = 4
    m = Image.new("L", (r - l + pad * 2, b - t + pad * 2), 0)
    ImageDraw.Draw(m).text((pad - l, pad - t), text, font=font, fill=255)
    return m


def condensed_block(text, font_path, box, fill, strokes, grow=0, anchor="top"):
    """box 内に長体をかけて幅いっぱいに詰めた文字レイヤー（RGBA, W×H）を返す。

    strokes: [(color, radius), ...] 外側から順に。
    grow: 文字数が少なく幅が余るとき、box を高さ方向に何 px まで広げてよいか。
    anchor: 広げるときに固定する辺（"top" は下へ、"bottom" は上へ伸びる）。
    """
    x0, y0, x1, y1 = box
    max_r = max(r for _, r in strokes)
    bw, bh = (x1 - x0) - max_r * 2, (y1 - y0) - max_r * 2

    # 長体上限でも幅が余るなら、grow の範囲で文字を大きくして幅を埋める
    m = _text_mask(text, font_path, int(bh * 1.25))
    m_w = m.width * (bh / m.height) * MAX_CONDENSE
    if m_w < bw and grow:
        add = min(grow, int(bh * bw / m_w) - bh)
        bh += add
        if anchor == "bottom":
            y0 -= add
        else:
            y1 += add

    size = int(bh * 1.25)
    while True:
        m = _text_mask(text, font_path, size)
        scale_h = bh / m.height
        if scale_h < 1:
            size = int(size * scale_h)
            continue
        cond = bw / m.width
        if cond < MIN_CONDENSE:
            size = int(size * cond / MIN_CONDENSE) - 1
            continue
        cond = min(cond, MAX_CONDENSE)
        break
    m = m.resize((max(1, int(m.width * cond)), m.height), Image.LANCZOS)

    tw, th = m.width + max_r * 2, m.height + max_r * 2
    glyph = Image.new("L", (tw, th), 0)
    glyph.paste(m, (max_r, max_r))

    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    for color, r in strokes:  # 外側の縁から重ねる
        sm = _dilate(glyph, r).filter(ImageFilter.GaussianBlur(0.6))
        layer.paste(Image.new("RGBA", (tw, th), color + (255,)), (0, 0), sm)
    layer.paste(Image.new("RGBA", (tw, th), fill + (255,)), (0, 0), glyph)

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = x0
    py = y0 + ((y1 - y0) - th) // 2
    out.alpha_composite(layer, (px, py))
    return out


def car_name_layer(font_path):
    font = ImageFont.truetype(font_path, 26)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    l, t, r, b = font.getbbox(CAR_NAME)
    d.text((W - 26 - (r - l) - l, 14 - t), CAR_NAME, font=font, fill=(255, 255, 255),
           stroke_width=4, stroke_fill=(0, 0, 0))
    return out


def badge(out, font_path, text, xy, bg):
    font = ImageFont.truetype(font_path, 34)
    d = ImageDraw.Draw(out)
    l, t, r, b = font.getbbox(text)
    x, y = xy
    bw, bh = (r - l) + 40, 58
    d.rounded_rectangle((x + 3, y + 4, x + bw + 3, y + bh + 4), 8, fill=(0, 0, 0, 120))
    d.rounded_rectangle((x, y, x + bw, y + bh), 8, fill=bg + (255,), outline=(255, 255, 255, 255), width=3)
    d.text((x + 20 - l, y + (bh - (b - t)) // 2 - t), text, font=font, fill=(255, 255, 255))
    return bw


def red_arrow(out, cx, cy):
    d = ImageDraw.Draw(out)
    pts = [(cx - 52, cy - 22), (cx + 6, cy - 22), (cx + 6, cy - 50), (cx + 62, cy),
           (cx + 6, cy + 50), (cx + 6, cy + 22), (cx - 52, cy + 22)]
    d.polygon([(x + 3, y + 5) for x, y in pts], fill=(0, 0, 0, 130))
    d.polygon(pts, fill=RED + (255,), outline=(255, 255, 255, 255), width=4)


# ---------------------------------------------------------------- 模擬画

def black_paint(w=W, h=H, seed=0, glossy=False):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    base = 14 + 22 * np.exp(-((y - 0.35) ** 2) / 0.02) * (0.6 + 0.4 * x)
    if not glossy:
        base = base + rng.normal(0, 2.2, (h, w))  # くすみ
    arr = np.clip(np.stack([base, base, base * 1.06], -1), 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def add_purple(img, region, n, seed, macro=False):
    rng = random.Random(seed)
    x0, y0, x1, y1 = region
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        hue = rng.choice([(150, 40, 190), (120, 30, 170), (175, 60, 205), (95, 25, 140)])
        a = rng.randint(120, 230)
        if macro:
            r = rng.uniform(3, 9)
            d.ellipse((x - r * 2.6, y - r * 2.6, x + r * 2.6, y + r * 2.6), fill=hue + (60,))
            d.ellipse((x - r, y - r, x + r, y + r), fill=hue + (a,))
            d.line((x, y, x + rng.uniform(-2, 2), y + rng.uniform(20, 90)), fill=hue + (a // 2,),
                   width=max(2, int(r * 0.8)))
        else:
            length = rng.uniform(30, 220)
            wdt = rng.randint(2, 7)
            d.line((x, y, x + rng.uniform(-3, 3), y + length), fill=hue + (a,), width=wdt)
            d.ellipse((x - wdt, y + length - wdt, x + wdt, y + length + wdt * 1.6), fill=hue + (a,))
    lay = lay.filter(ImageFilter.GaussianBlur(1.6 if macro else 1.1))
    img.alpha_composite(lay)


def add_spots(img, region, n, seed, rmin=8, rmax=34):
    rng = random.Random(seed)
    x0, y0, x1, y1 = region
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.uniform(rmin, rmax)
        e = rng.uniform(0.75, 1.0)
        a = rng.randint(130, 230)
        wd = max(2, int(r / 9))
        d.ellipse((x - r, y - r * e, x + r, y + r * e), fill=(220, 220, 225, 18),
                  outline=(235, 235, 240, a), width=wd)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.9)))


def add_reflection(img, region, seed=0, strong=True):
    x0, y0, x1, y1 = region
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # 天井照明の映り込み（パースのついた蛍光灯）
    for i, yy in enumerate(np.linspace(y0 + 20, y1 - 30, 4)):
        skew = 60 + i * 30
        th = 10 + i * 4
        d.polygon([(x0 + 80 + i * 40, yy), (x1 - 120 - i * 30, yy - 18),
                   (x1 - 120 - i * 30 + skew * 0.1, yy - 18 + th), (x0 + 80 + i * 40, yy + th)],
                  fill=(255, 255, 255, 255 if strong else 110))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.8 if strong else 6)))
    glow = lay.filter(ImageFilter.GaussianBlur(14))
    glow.putalpha(glow.getchannel("A").point(lambda v: v // 3))
    img.alpha_composite(glow)


def land_cruiser_silhouette(seed=4):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    arr = np.zeros((H, W, 3), np.uint8)
    yy = np.linspace(0, 1, H)[:, None]
    arr[...] = (np.clip(150 - 70 * yy, 0, 255)).astype(np.uint8)[..., None]  # 施工ブースの壁〜床
    img = Image.fromarray(arr, "RGB").convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle((0, 470, W, H), fill=(98, 98, 102))
    # ボクシーな SUV（斜め前 45°）
    body = [(120, 300), (190, 230), (300, 222), (360, 160), (720, 150), (800, 222),
            (860, 236), (880, 330), (870, 440), (140, 450), (110, 380)]
    d.polygon(body, fill=(18, 18, 20))
    d.polygon([(380, 172), (700, 164), (760, 222), (340, 228)], fill=(48, 52, 60))  # ガラス
    d.polygon([(800, 230), (860, 244), (868, 330), (806, 318)], fill=(30, 30, 34))   # フロント面
    d.rectangle((812, 262, 862, 280), fill=(160, 160, 165))                           # グリル
    for cx in (270, 720):
        d.ellipse((cx - 72, 380, cx + 72, 524), fill=(8, 8, 8))
        d.ellipse((cx - 40, 412, cx + 40, 492), fill=(70, 70, 74))
    add_spots(img, (180, 240, 820, 430), 60, seed, rmin=4, rmax=10)
    return img


def inset_circle(img, src, center, r):
    mask = Image.new("L", (r * 2, r * 2), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, r * 2 - 1, r * 2 - 1), fill=255)
    crop = src.crop((center[0] - r, center[1] - r, center[0] + r, center[1] + r))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((center[0] - r + 5, center[1] - r + 7, center[0] + r + 5,
                                    center[1] + r + 7), fill=(0, 0, 0, 140))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)))
    img.paste(crop, (center[0] - r, center[1] - r), mask)
    ImageDraw.Draw(img).ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r),
                                outline=(255, 255, 255, 255), width=7)


def scene(name, font_path):
    if name == "purple_side":
        img = black_paint(seed=1)
        add_purple(img, (60, 170, 1220, 520), 260, 1)
    elif name == "purple_dense":
        img = black_paint(seed=3)
        add_purple(img, (0, 140, W, 560), 620, 3)
    elif name == "purple_macro":
        img = black_paint(seed=7)
        add_purple(img, (80, 200, 1200, 470), 70, 7, macro=True)
    elif name == "purple_rear":
        img = black_paint(seed=6)
        f = ImageFont.truetype(font_path, 54)
        d = ImageDraw.Draw(img)
        d.text((380, 232), "L A N D  C R U I S E R", font=f, fill=(150, 150, 158))
        add_purple(img, (60, 300, 1220, 520), 300, 6)
    elif name == "spots_wide":
        img = black_paint(seed=2)
        add_spots(img, (40, 210, 1240, 510), 140, 2)
    elif name == "spots_macro":
        img = black_paint(seed=5)
        add_spots(img, (60, 215, 1220, 505), 26, 5, rmin=26, rmax=58)
        add_spots(img, (590, 300, 690, 410), 1, 55, rmin=46, rmax=48)
        d = ImageDraw.Draw(img)
        d.ellipse((560, 270, 720, 440), outline=RED + (255,), width=9)
    elif name == "full_with_inset":
        img = land_cruiser_silhouette()
        src = black_paint(seed=40)
        add_spots(src, (0, 0, W, H), 300, 40, rmin=10, rmax=26)
        inset_circle(img, src, (1060, 360), 138)
    elif name == "before_after":
        left = black_paint(seed=8)
        add_spots(left, (0, 200, W, 520), 150, 8)
        right = black_paint(seed=9, glossy=True)
        add_reflection(right, (0, 220, W, 500))
        img = Image.new("RGBA", (W, H))
        img.paste(left.crop((0, 0, W // 2, H)), (0, 0))
        img.paste(right.crop((W // 2, 0, W, H)), (W // 2, 0))
        ImageDraw.Draw(img).line((W // 2, 0, W // 2, H), fill=(255, 255, 255, 255), width=6)
    elif name == "reflection":
        img = black_paint(seed=10, glossy=True)
        add_reflection(img, (40, 225, 1240, 500))
    else:
        raise ValueError(name)
    # 上下の文字が乗る帯を少し落として可読性を上げる（実写でも同じ処理を推奨）
    grad = Image.new("L", (1, H))
    for y in range(H):
        v = 0
        if y < 210:
            v = int(110 * (1 - y / 210))
        elif y > 500:
            v = int(150 * (y - 500) / 220)
        grad.putpixel((0, y), v)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    shade.putalpha(grad.resize((W, H)))
    img.alpha_composite(shade)
    return img


# ---------------------------------------------------------------- 合成

def overlay(p, font_path):
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if p["scene"] == "before_after":
        badge(out, font_path, "Before", (34, 440), NAVY)
        aw = badge(out, font_path, "After", (0, -999), RED)  # 幅だけ測る
        badge(out, font_path, "After", (1240 - aw, 440), RED)
        red_arrow(out, W // 2, 362)
    out.alpha_composite(car_name_layer(font_path))
    out.alpha_composite(condensed_block(p["upper"], font_path, UPPER_BOX, (255, 255, 255),
                                        [((0, 0, 0), 13)], grow=14))
    out.alpha_composite(condensed_block(p["lower"], font_path, LOWER_BOX, ORANGE,
                                        [((0, 0, 0), 17), ((255, 255, 255), 12)],
                                        grow=60, anchor="bottom"))
    return out


def dashed_rect(d, box, color, dash=14, width=3):
    x0, y0, x1, y1 = box
    for x in range(x0, x1, dash * 2):
        d.line((x, y0, min(x + dash, x1), y0), fill=color, width=width)
        d.line((x, y1 - 1, min(x + dash, x1), y1 - 1), fill=color, width=width)
    for y in range(y0, y1, dash * 2):
        d.line((x0, y, x0, min(y + dash, y1)), fill=color, width=width)
        d.line((x1 - 1, y, x1 - 1, min(y + dash, y1)), fill=color, width=width)


def guide(comp, font_path):
    g = comp.copy()
    d = ImageDraw.Draw(g)
    dashed_rect(d, SUBJECT_ZONE, (0, 255, 160, 255))
    dashed_rect(d, DURATION_ZONE, (255, 60, 60, 255))
    f = ImageFont.truetype(font_path, 18)
    d.text((12, SUBJECT_ZONE[1] + 8), "被写体ゾーン（文字を置かない）", font=f, fill=(0, 255, 160))
    d.text((DURATION_ZONE[0] + 6, DURATION_ZONE[1] + 8), "再生時間", font=f, fill=(255, 90, 90))
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    comps = []
    for p in PATTERNS:
        ov = overlay(p, a.font)
        comp = scene(p["scene"], a.font)
        comp.alpha_composite(ov)
        base = os.path.join(a.out, f"{p['no']:02d}")
        comp.convert("RGB").save(base + "_comp.png")
        ov.save(base + "_overlay.png")
        guide(comp, a.font).convert("RGB").save(base + "_guide.png")
        comps.append(comp.convert("RGB"))

    tw, th, gap = 640, 360, 16
    sheet = Image.new("RGB", (tw * 3 + gap * 4, (th + 44) * 3 + gap * 2), (245, 245, 245))
    f = ImageFont.truetype(a.font, 24)
    d = ImageDraw.Draw(sheet)
    for i, (p, c) in enumerate(zip(PATTERNS, comps)):
        cx, cy = gap + (i % 3) * (tw + gap), gap + (i // 3) * (th + 44 + gap // 2)
        d.text((cx, cy), f"案{p['no']}  {p['upper']} ／ {p['lower']}", font=f, fill=(30, 30, 30))
        sheet.paste(c.resize((tw, th), Image.LANCZOS), (cx, cy + 36))
    sheet.save(os.path.join(a.out, "contact_sheet.png"))


if __name__ == "__main__":
    main()
