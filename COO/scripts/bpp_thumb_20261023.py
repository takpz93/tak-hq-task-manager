"""BPP サムネ案（2026-10-23 公開分：クラウン／ディフェンダー）。

文字は上側にまとめ（上段＝白・大、下段＝オレンジ）、画面中央〜下は見せたい部分のために空ける。
背景は実写に差し替える前提の仮背景（明度 40% 前後）。

書き出し（--out ごと）:
  A.png / B.png / C.png      … 仮背景＋文字の合成
  layers/X_text.png          … 文字だけの透過 PNG
  layers/X_bg.png            … 仮背景
  contact_sheet.png          … 3 案一覧

使い方:
  python COO/scripts/bpp_thumb_20261023.py --font /path/to/NotoSansCJKjp-Black.otf --root thumbnails/bpp
"""

import argparse
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (240, 128, 48)

STROKE = 14            # 黒の縁取り
SHADOW_OFF = (6, 8)    # ドロップシャドウ
SHADOW_BLUR = 10

UPPER = dict(y=10, h=150, x=(24, W - 24))   # 上段：いちばん強いフック
LOWER = dict(gap=8, h=104, x=(24, W - 24))  # 下段：上段の直下
COND_MIN, COND_MAX = 0.60, 0.95
TEXT_BOTTOM_LIMIT = 340  # 文字はここより上に収める（中央〜下は見せたい部分）

JOBS = {
    "crown_20261023": dict(
        bg=dict(base=(96, 98, 104), seed=21),
        patterns=[("A", "毎週洗っても白い", "クラウンのグリル"),
                  ("B", "くもりは磨ける？", "クラウンマーク"),
                  ("C", "上だけ黄ばむ", "ヘッドライト")]),
    "defender_20261023": dict(
        bg=dict(base=(102, 103, 104), seed=7),
        patterns=[("A", "ツヤが消えた", "ディフェンダー"),
                  ("B", "洗っても戻らない", "20年車のくすみ"),
                  ("C", "プロの私物車", "くすみは取れる？")]),
}


def _dilate(mask, r):
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


def _glyph_mask(text, font_path, size=400):
    font = ImageFont.truetype(font_path, size)
    l, t, r, b = font.getbbox(text)
    m = Image.new("L", (r - l + 8, b - t + 8), 0)
    ImageDraw.Draw(m).text((4 - l, 4 - t), text, font=font, fill=255)
    return m.crop(m.getbbox())


def text_line(text, font_path, fill, x_range, y, h_max):
    """長体をかけて x_range に収めた 1 行（黒縁＋影）を (layer, bottom_y) で返す。

    幅に余裕があれば長体 COND_MAX・高さ h_max で左寄せ、足りなければ長体を深くし、
    それでも入らなければ字を小さくする。
    """
    m = _glyph_mask(text, font_path)
    avail = (x_range[1] - x_range[0]) - STROKE * 2
    h = h_max
    cond = min(COND_MAX, avail / (m.width * h / m.height))
    if cond < COND_MIN:
        cond = COND_MIN
        h = int(avail / (m.width / m.height * cond))
    g = m.resize((int(m.width * h / m.height * cond), h), Image.LANCZOS)

    pad = STROKE + SHADOW_BLUR * 2
    tw, th = g.width + pad * 2, h + pad * 2
    glyph = Image.new("L", (tw, th), 0)
    glyph.paste(g, (pad, pad))
    edge = _dilate(glyph, STROKE).filter(ImageFilter.GaussianBlur(0.7))

    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    shadow = Image.new("L", (tw, th), 0)
    shadow.paste(edge, SHADOW_OFF)
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR)).point(lambda v: int(v * 0.75))
    layer.paste(Image.new("RGBA", (tw, th), BLACK + (255,)), (0, 0), shadow)
    layer.paste(Image.new("RGBA", (tw, th), BLACK + (255,)), (0, 0), edge)
    layer.paste(Image.new("RGBA", (tw, th), fill + (255,)), (0, 0), glyph)

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(layer, (x_range[0] - pad + STROKE, y - pad + STROKE))
    return out, y + h + STROKE * 2


def text_layer(upper, lower, font_path):
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    up, up_bottom = text_line(upper, font_path, WHITE, UPPER["x"], UPPER["y"], UPPER["h"])
    lo, lo_bottom = text_line(lower, font_path, ORANGE, LOWER["x"], up_bottom + LOWER["gap"], LOWER["h"])
    assert lo_bottom <= TEXT_BOTTOM_LIMIT, (upper, lower, lo_bottom)
    out.alpha_composite(lo)
    out.alpha_composite(up)
    return out, lo_bottom


def background(base, seed):
    """仮背景：平均明度 40% 前後。中央〜下にボディの映り込みを想定した明るい帯を入れる。"""
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    shade = 0.80 + 0.20 * (1 - y)                                   # 上がやや明るい壁、下へ落ちる
    band = 0.45 * np.exp(-((y - 0.66) ** 2) / 0.012) * (0.55 + 0.45 * np.sin(np.pi * x))  # 映り込みの帯
    v = shade + band
    v = v / v.mean()                                                 # 平均を base に合わせる
    arr = np.stack([v * c for c in base], -1) + rng.normal(0, 1.5, (H, W, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def luminance(img):
    a = np.asarray(img.convert("RGB"), dtype=float) / 255
    return float((0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]).mean())


def contact_sheet(items, font_path, title):
    tw, th, gap, cap = 640, 360, 24, 44
    sheet = Image.new("RGB", (gap + 3 * (tw + gap), 70 + th + cap + gap), (244, 244, 244))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 18), title, font=ImageFont.truetype(font_path, 30), fill=(20, 20, 20))
    f = ImageFont.truetype(font_path, 22)
    for i, (label, upper, lower, img) in enumerate(items):
        cx = gap + i * (tw + gap)
        d.text((cx, 70), f"{label}  {upper} ／ {lower}", font=f, fill=(30, 30, 30))
        sheet.paste(img.resize((tw, th), Image.LANCZOS), (cx, 70 + cap))
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True)
    ap.add_argument("--root", required=True)
    a = ap.parse_args()
    for job, cfg in JOBS.items():
        out = os.path.join(a.root, job)
        os.makedirs(os.path.join(out, "layers"), exist_ok=True)
        bg = background(**cfg["bg"])
        items = []
        for label, upper, lower in cfg["patterns"]:
            txt, bottom = text_layer(upper, lower, a.font)
            comp = bg.convert("RGBA")
            comp.alpha_composite(txt)
            comp = comp.convert("RGB")
            comp.save(os.path.join(out, f"{label}.png"))
            txt.save(os.path.join(out, "layers", f"{label}_text.png"))
            bg.save(os.path.join(out, "layers", f"{label}_bg.png"))
            zone = txt.getchannel("A").crop((int(W * 0.9), int(H * 0.9), W, H)).getextrema()
            print(job, label, f"text_bottom={bottom}", f"bg_luminance={luminance(bg):.2f}", f"badge_zone_alpha={zone}")
            items.append((label, upper, lower, comp))
        name = "クラウン アスリート（210系・黒）" if job.startswith("crown") else "ディフェンダー（シルバー）"
        contact_sheet(items, a.font, f"BPP {name}｜サムネ3案（仮背景）").save(os.path.join(out, "contact_sheet.png"))


if __name__ == "__main__":
    main()
