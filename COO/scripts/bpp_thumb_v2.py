"""BPP（BUDDICA PHOENIX PRO）サムネ v2：上下ベタ置き・赤文字・二重縁・差し込み枠・白矢印。

書き出すもの:
  NN_overlay.png   … 文字だけの透過 PNG（1280×720）
  NN_preview.png   … ダミーの黒グラデ＋差し込み枠＋白矢印＋文字の合成
  parts/inset_frame_top.png / inset_frame_bottom.png … 左上／左下の差し込み枠（透過 1280×720）
  parts/arrow_white_*.png … 注目点を指す白い太矢印（向き違い）
  contact_sheet.png … 5 案一覧（2 行×3 列）

使い方:
  python COO/scripts/bpp_thumb_v2.py --font /path/to/NotoSansCJKjp-Black.otf \
      --out clients/BPP/output/2026-10-14_ランクル250_サムネ案_v2
"""

import argparse
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (232, 25, 44)  # #E8192C

STROKE_BLACK = 15     # 黒の太縁
STROKE_WHITE = 5      # その外側の白の細縁
OUTER = STROKE_BLACK + STROKE_WHITE

# 上段は全幅、下段は右下 10%（x≥1152, y≥648）を避けて x≤1140 で止める
UPPER_X = (4, W - 4)
LOWER_X = (4, 1140)
TEXT_H_GROW = 196     # 文字数が少ない行は、字間が空きすぎないようここまで大きくしてよい
TRACK_MAX = 0.06      # 字間の上限（字の高さに対する比）。超えるなら字を大きくする
TEXT_H_MAX = 172      # 1 行の字面の高さ上限（中段の写真スペースを残すため）
COND_MIN, COND_MAX = 0.60, 0.95  # 長体の範囲

# 差し込み枠（16:9、白枠）。上段・下段の文字と被らない中段の左に置く
INSET_W, INSET_H = 368, 207
INSET_X = 22
INSET_TOP_Y = 226           # 左上：上段の文字（y≤212）の直下
INSET_BOTTOM_Y = 268        # 左下：下段の文字（y≥508）の直上
INSET_BORDER = 8

PATTERNS = [
    dict(no=1, upper="コーティング後", lower="1年でこうなる", inset="top",
         arrow=("down_right", (860, 400))),
    dict(no=2, upper="黒い車の1年後", lower="まさかの鉄粉", inset="bottom",
         arrow=("down_right", (900, 420))),
    dict(no=3, upper="この白い跡は", lower="洗っても消えない", inset="top",
         arrow=("down_left", (840, 410))),
    dict(no=4, upper="コーティング1年", lower="鉄粉が刺さる", inset="bottom",
         arrow=("left", (880, 360))),
    dict(no=5, upper="1年でこの汚れ", lower="黒は誤魔化せない", inset="top",
         arrow=("down_left", (860, 420))),
]


# ---------------------------------------------------------------- 文字

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


def _glyph_mask(text, font_path, size=400, tracking=0.0):
    """文字列の字面マスク。tracking は字間に足す px（size 基準）。"""
    font = ImageFont.truetype(font_path, size)
    pad = size
    adv = sum(font.getlength(c) for c in text) + tracking * (len(text) - 1)
    m = Image.new("L", (int(adv) + pad * 2, size * 2), 0)
    d = ImageDraw.Draw(m)
    x = pad
    for c in text:
        d.text((x, size // 2), c, font=font, fill=255)
        x += font.getlength(c) + tracking
    return m.crop(m.getbbox())


def text_line(text, font_path, fill, x_range, anchor):
    """長体で x_range いっぱいに詰めた 1 行。anchor="top" で最上部、"bottom" で最下部にベタ置き。"""
    m = _glyph_mask(text, font_path)
    target_w = (x_range[1] - x_range[0]) - OUTER * 2
    # 高さ上限で組み、幅に合わせて長体率を決める
    h = TEXT_H_MAX
    cond = target_w / (m.width * h / m.height)
    if cond < COND_MIN:          # 潰れすぎる → 字を小さくする
        cond = COND_MIN
        h = int(target_w / (m.width / m.height * cond))
    elif cond > COND_MAX:        # 文字数が少なく長体が浅い → 長体は上限で止め、残りは字間で埋める
        cond = COND_MAX
        base = m
        for h in range(TEXT_H_MAX, TEXT_H_GROW + 1, 2):   # 字間が空きすぎるなら字を大きくする
            need = target_w / (h / base.height * cond)    # size 400 基準で必要な字面幅
            tracking = max(0.0, (need - base.width) / max(1, len(text) - 1))
            if tracking <= TRACK_MAX * base.height:
                break
        m = _glyph_mask(text, font_path, tracking=tracking)
        h = int(m.height * target_w / (m.width * cond))  # 誤差吸収
    gw = int(m.width * h / m.height * cond)
    g = m.resize((gw, h), Image.LANCZOS)

    tw, th = gw + OUTER * 2, h + OUTER * 2
    glyph = Image.new("L", (tw, th), 0)
    glyph.paste(g, (OUTER, OUTER))
    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    for color, r in ((WHITE, OUTER), (BLACK, STROKE_BLACK)):
        sm = _dilate(glyph, r).filter(ImageFilter.GaussianBlur(0.6))
        layer.paste(Image.new("RGBA", (tw, th), color + (255,)), (0, 0), sm)
    layer.paste(Image.new("RGBA", (tw, th), fill + (255,)), (0, 0), glyph)

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = x_range[0] + ((x_range[1] - x_range[0]) - tw) // 2
    py = 0 if anchor == "top" else H - th
    out.alpha_composite(layer, (px, py))
    return out, (py, py + th), cond


# ---------------------------------------------------------------- パーツ

def inset_frame(pos, y=None):
    x = INSET_X
    if y is None:
        y = INSET_TOP_Y if pos == "top" else INSET_BOTTOM_Y
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((x + 6, y + 8, x + INSET_W + 6, y + INSET_H + 8), fill=(0, 0, 0, 150))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(out).rectangle((x, y, x + INSET_W, y + INSET_H), outline=WHITE + (255,),
                                  width=INSET_BORDER)
    # 枠の内側は透明（ここに別カットを入れる）
    ImageDraw.Draw(out).rectangle((x + INSET_BORDER, y + INSET_BORDER, x + INSET_W - INSET_BORDER,
                                   y + INSET_H - INSET_BORDER), fill=(0, 0, 0, 0))
    return out, (x, y, x + INSET_W, y + INSET_H)


def arrow_part(direction, length=230):
    """白い太矢印（黒縁＋影）。先端が画像の端に来る向きで返す。"""
    s = 4  # スーパーサンプリング
    L, shaft, head_w, head_l = length * s, 46 * s, 116 * s, 92 * s
    pad = 26 * s
    base = Image.new("L", (L + pad * 2, head_w + pad * 2), 0)
    cy = pad + head_w // 2
    pts = [(pad, cy - shaft // 2), (pad + L - head_l, cy - shaft // 2), (pad + L - head_l, cy - head_w // 2),
           (pad + L, cy), (pad + L - head_l, cy + head_w // 2), (pad + L - head_l, cy + shaft // 2),
           (pad, cy + shaft // 2)]
    ImageDraw.Draw(base).polygon(pts, fill=255)
    base = base.resize((base.width // s, base.height // s), Image.LANCZOS)
    angle = {"right": 0, "left": 180, "down_right": -35, "down_left": -145, "up_right": 35, "up_left": 145}[direction]
    bw0, bh0 = base.size
    tip = ((pad + L) / s - bw0 / 2, cy / s - bh0 / 2)   # 回転中心からの先端位置
    base = base.rotate(angle, resample=Image.BICUBIC, expand=True)
    w, h = base.size
    rad = math.radians(angle)
    tx = tip[0] * math.cos(rad) + tip[1] * math.sin(rad) + w / 2
    ty = -tip[0] * math.sin(rad) + tip[1] * math.cos(rad) + h / 2
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow = _dilate(base, 9).filter(ImageFilter.GaussianBlur(6))
    out.paste(Image.new("RGBA", (w, h), (0, 0, 0, 140)), (5, 7), shadow)
    out.paste(Image.new("RGBA", (w, h), BLACK + (255,)), (0, 0), _dilate(base, 7).filter(ImageFilter.GaussianBlur(0.6)))
    out.paste(Image.new("RGBA", (w, h), WHITE + (255,)), (0, 0), base)
    out.info["tip"] = (int(round(tx)), int(round(ty)))
    return out


# ---------------------------------------------------------------- ダミー背景

def dummy_bg(seed):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    v = 10 + 34 * np.exp(-((y - 0.42) ** 2) / 0.05) * (0.45 + 0.55 * x) + rng.normal(0, 1.2, (H, W))
    arr = np.clip(np.stack([v, v, v * 1.05], -1), 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def build(p, font_path):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    up, up_y, up_c = text_line(p["upper"], font_path, WHITE, UPPER_X, "top")
    lo, lo_y, lo_c = text_line(p["lower"], font_path, RED, LOWER_X, "bottom")
    ov.alpha_composite(up)
    ov.alpha_composite(lo)

    fy = up_y[1] + 14 if p["inset"] == "top" else lo_y[0] - 14 - INSET_H
    frame, fbox = inset_frame(p["inset"], fy)
    assert fbox[1] >= up_y[1] and fbox[3] <= lo_y[0], (p["no"], fbox, up_y, lo_y)

    prev = dummy_bg(p["no"])
    d = ImageDraw.Draw(prev)
    d.rectangle(fbox, fill=(58, 58, 64, 255))
    f = ImageFont.truetype(font_path, 26)
    d.text((fbox[0] + 24, fbox[1] + 20), "別カット", font=f, fill=(150, 150, 156))
    prev.alpha_composite(frame)

    direction, tip = p["arrow"]
    ap = arrow_part(direction)
    ox, oy = ap.info["tip"]
    # 注目点の目印（ダミー）
    d.ellipse((tip[0] - 7, tip[1] - 7, tip[0] + 7, tip[1] + 7), outline=(120, 120, 126), width=2)
    prev.alpha_composite(ap, (tip[0] - ox, tip[1] - oy))
    prev.alpha_composite(ov)
    return ov, prev, dict(upper_cond=up_c, lower_cond=lo_c, upper_y=up_y, lower_y=lo_y, inset=fbox)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    parts = os.path.join(a.out, "parts")
    os.makedirs(parts, exist_ok=True)

    for pos in ("top", "bottom"):
        inset_frame(pos)[0].save(os.path.join(parts, f"inset_frame_{pos}.png"))
    for dirn in ("right", "left", "down_right", "down_left", "up_right", "up_left"):
        arrow_part(dirn).save(os.path.join(parts, f"arrow_white_{dirn}.png"))

    previews = []
    for p in PATTERNS:
        ov, prev, info = build(p, a.font)
        ov.save(os.path.join(a.out, f"{p['no']:02d}_overlay.png"))
        prev.convert("RGB").save(os.path.join(a.out, f"{p['no']:02d}_preview.png"))
        previews.append(prev.convert("RGB"))
        print(p["no"], {k: (round(v, 2) if isinstance(v, float) else v) for k, v in info.items()})

    # コンタクトシート 2 行×3 列（6 枠目はパーツ見本）
    tw, th, gap, cap = 560, 315, 20, 40
    sheet = Image.new("RGB", (gap + 3 * (tw + gap), gap + 2 * (th + cap + gap)), (244, 244, 244))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(a.font, 22)
    cells = [(f"案{p['no']}  {p['upper']} ／ {p['lower']}", im) for p, im in zip(PATTERNS, previews)]
    legend = Image.new("RGB", (W, H), (60, 60, 66))
    lg = Image.new("RGBA", (W, H), (60, 60, 66, 255))
    x = 40
    for dirn in ("right", "down_right", "down_left", "left"):
        part = arrow_part(dirn)
        lg.alpha_composite(part, (x, 180 + (0 if dirn in ("right", "left") else -40)))
        x += part.width + 30
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rectangle((40, 440, 40 + INSET_W, 440 + INSET_H), outline=WHITE + (255,), width=INSET_BORDER)
    lg.alpha_composite(fr)
    ImageDraw.Draw(lg).text((40, 60), "パーツ：白い太矢印／差し込み枠（白枠 16:9）", font=ImageFont.truetype(a.font, 44),
                            fill=WHITE)
    legend = lg.convert("RGB")
    cells.append(("パーツ（parts/ フォルダ）", legend))
    for i, (label, im) in enumerate(cells):
        cx = gap + (i % 3) * (tw + gap)
        cy = gap + (i // 3) * (th + cap + gap)
        d.text((cx, cy + 4), label, font=f, fill=(25, 25, 25))
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (cx, cy + cap))
    sheet.save(os.path.join(a.out, "contact_sheet.png"))


if __name__ == "__main__":
    main()
