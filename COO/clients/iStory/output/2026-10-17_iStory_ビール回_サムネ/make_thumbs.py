#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iStory（のりさん / 居酒屋店長日誌）10/17公開 ビール回 サムネ生成
使い方: python3 make_thumbs.py [--font /path/to/NotoSansCJKjp-Black.otf]

構造（文字だけ差し替えられるようにレイヤー分離）:
  layers/background.png  … 背景レイヤー（3案共通、明度40%前後）
  layers/text_X.png      … 文字レイヤー（透過PNG）
  thumb_X.png            … 背景 + 文字 を合成した完成品
  contact_sheet.png      … 3案の比較用
文言を変えるときは COPY だけ書き換えて再実行する。
"""
import argparse, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 720

# ---- 文言（確定3案。改行しない） ----
COPY = {
    "A": ("酒税下がっても", "ビールは高い"),
    "B": ("減税分は", "客に返りません"),
    "C": ("ビール700円", "高くありません"),
}

# ---- レイアウト規則 ----
TEXT_LEFT = 56                       # 左余白
TEXT_RIGHT = int(W * 2 / 3) - 40     # 右1/3は演者合成用に空ける
NO_TEXT_ZONES = [
    (int(W * 2 / 3), 0, W, H),                         # 右1/3（演者）
    (int(W * 0.80), int(H * 0.80), W, H),              # 右下（再生時間表示）
]
BOTTOM_LIMIT = int(H * 0.90)         # 下端10%にも文字を置かない
LOWER_MAX, UPPER_MAX = 170, 104      # 下段 > 上段 を保証する上限サイズ
UPPER_RATIO = 0.62                   # 上段は下段の62%以下
GAP = 18                             # 行間

# ---- 文字色: 塗り + 白フチ + 濃い縁取り ----
UPPER_STYLE = dict(fill=(40, 22, 8), white=7, dark=15, dark_color=(20, 10, 2))
LOWER_STYLE = dict(fill=(232, 20, 26), white=9, dark=19, dark_color=(25, 8, 4))

TARGET_LUMA = 0.40                   # 背景の平均明度

FONT_CANDIDATES = [
    os.environ.get("THUMB_FONT", ""),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Black.otf",
    os.path.expanduser("~/Library/Fonts/NotoSansCJKjp-Black.otf"),
    "/Library/Fonts/NotoSansCJKjp-Black.otf",
    "/tmp/claude-0/fonts/NotoSansCJKjp-Black.otf",
    os.path.join(HERE, "NotoSansCJKjp-Black.otf"),
]


def find_font(path):
    for p in ([path] if path else []) + FONT_CANDIDATES:
        if p and os.path.exists(p):
            f = ImageFont.truetype(p, 40)
            if f.getname()[1] != "Black":
                raise SystemExit(f"Black ウェイトではありません: {p} {f.getname()}")
            return p
    raise SystemExit("Noto Sans CJK JP Black が見つかりません。--font で指定してください")


# ---------------- 背景レイヤー ----------------
def make_background(seed=17):
    """琥珀色の居酒屋の灯り（ボケ）＋ビアグラスの泡のイメージ。写真差し替え前提の汎用背景"""
    rng = random.Random(seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # ベース: 左上が少し明るい暖色グラデ
    t = np.clip((x / W) * 0.55 + (y / H) * 0.45, 0, 1)[..., None]
    top = np.array([150, 92, 30], np.float32)
    bot = np.array([45, 22, 8], np.float32)
    img = top * (1 - t) + bot * t
    # ボケ（提灯・照明）
    bokeh = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(bokeh)
    for _ in range(46):
        r = rng.randint(18, 90)
        cx, cy = rng.randint(-40, W + 40), rng.randint(-40, H + 40)
        c = rng.choice([(255, 190, 80), (255, 150, 50), (255, 220, 140), (230, 110, 40)])
        k = rng.uniform(0.25, 0.7)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(int(v * k) for v in c))
    bokeh = np.asarray(bokeh.filter(ImageFilter.GaussianBlur(14)), np.float32)
    img = img + bokeh * 0.75
    # 泡のような細かい粒（下側）
    foam = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(foam)
    for _ in range(260):
        r = rng.randint(2, 7)
        cx, cy = rng.randint(0, W), rng.randint(int(H * 0.45), H)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=120, width=1)
    foam = np.asarray(foam.filter(ImageFilter.GaussianBlur(0.8)), np.float32)[..., None] / 255
    img = img + foam * np.array([255, 230, 170], np.float32) * 0.35
    # 周辺減光
    vx, vy = (x - W / 2) / (W / 2), (y - H / 2) / (H / 2)
    vig = np.clip(1 - 0.38 * (vx ** 2 + vy ** 2), 0.45, 1)[..., None]
    img = np.clip(img * vig, 0, 255)
    # 平均明度を TARGET_LUMA に合わせる
    luma = (img @ np.array([0.299, 0.587, 0.114], np.float32)).mean() / 255
    img = np.clip(img * (TARGET_LUMA / luma), 0, 255)
    return Image.fromarray(img.astype(np.uint8), "RGB")


def mean_luma(im):
    a = np.asarray(im.convert("RGB"), np.float32)
    return float((a @ np.array([0.299, 0.587, 0.114], np.float32)).mean() / 255)


# ---------------- 文字レイヤー ----------------
def fit_size(text, font_path, max_size, max_w, stroke):
    for s in range(max_size, 20, -2):
        f = ImageFont.truetype(font_path, s)
        b = f.getbbox(text, stroke_width=stroke)
        if b[2] - b[0] <= max_w:
            return s
    return 20


def draw_line(layer, xy, text, font, st):
    d = ImageDraw.Draw(layer)
    # 外側: 濃い縁取り → 白フチ → 塗り
    d.text(xy, text, font=font, fill=st["dark_color"], stroke_width=st["dark"], stroke_fill=st["dark_color"])
    d.text(xy, text, font=font, fill=(255, 255, 255), stroke_width=st["white"], stroke_fill=(255, 255, 255))
    d.text(xy, text, font=font, fill=st["fill"])


def make_text_layer(upper, lower, font_path):
    assert "\n" not in upper + lower and len(upper) <= 8 and len(lower) <= 8
    max_w = TEXT_RIGHT - TEXT_LEFT
    ls = fit_size(lower, font_path, LOWER_MAX, max_w, LOWER_STYLE["dark"])
    us = fit_size(upper, font_path, min(UPPER_MAX, int(ls * UPPER_RATIO)), max_w, UPPER_STYLE["dark"])
    assert ls > us, "下段は上段より大きくする"
    uf, lf = ImageFont.truetype(font_path, us), ImageFont.truetype(font_path, ls)
    ub = uf.getbbox(upper, stroke_width=UPPER_STYLE["dark"])
    lb = lf.getbbox(lower, stroke_width=LOWER_STYLE["dark"])
    uh, lh = ub[3] - ub[1], lb[3] - lb[1]
    total = uh + GAP + lh
    top = (BOTTOM_LIMIT - total) // 2 + 10          # 下10%を除いた領域の中央
    ux, uy = TEXT_LEFT - ub[0], top - ub[1]
    lx, ly = TEXT_LEFT - lb[0], top + uh + GAP - lb[1]

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # 読みやすさ用のソフトシャドウ
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((ux + 6, uy + 8), upper, font=uf, fill=(0, 0, 0, 170), stroke_width=UPPER_STYLE["dark"], stroke_fill=(0, 0, 0, 170))
    sd.text((lx + 8, ly + 10), lower, font=lf, fill=(0, 0, 0, 170), stroke_width=LOWER_STYLE["dark"], stroke_fill=(0, 0, 0, 170))
    layer = Image.alpha_composite(layer, shadow.filter(ImageFilter.GaussianBlur(8)))
    draw_line(layer, (ux, uy), upper, uf, UPPER_STYLE)
    draw_line(layer, (lx, ly), lower, lf, LOWER_STYLE)
    check_zones(layer)
    return layer, us, ls


def check_zones(layer):
    a = np.asarray(layer)[..., 3]
    for x0, y0, x1, y1 in NO_TEXT_ZONES + [(0, BOTTOM_LIMIT, W, H)]:
        # ソフトシャドウのにじみ（ごく薄い）は許容、実体の文字は置かない
        assert a[y0:y1, x0:x1].max() < 40, f"禁止領域に文字がかかっています: {(x0, y0, x1, y1)}"


# ---------------- 出力 ----------------
def contact_sheet(paths):
    s, pad, lab = 0.5, 28, 56
    tw, th = int(W * s), int(H * s)
    cols = len(paths)
    sheet = Image.new("RGB", (pad + cols * (tw + pad), lab + th + pad), (24, 24, 24))
    f = ImageFont.truetype(FONT, 30)
    d = ImageDraw.Draw(sheet)
    for i, (k, p) in enumerate(paths):
        x = pad + i * (tw + pad)
        d.text((x, 12), f"{k}案", font=f, fill=(255, 255, 255))
        sheet.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (x, lab))
    return sheet


def main():
    global FONT
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", default="")
    FONT = find_font(ap.parse_args().font)
    os.makedirs(os.path.join(HERE, "layers"), exist_ok=True)

    bg = make_background()
    bg.save(os.path.join(HERE, "layers", "background.png"))
    print(f"background mean luma = {mean_luma(bg):.3f}")

    outs = []
    for k, (upper, lower) in COPY.items():
        txt, us, ls = make_text_layer(upper, lower, FONT)
        txt.save(os.path.join(HERE, "layers", f"text_{k}.png"))
        out = os.path.join(HERE, f"thumb_{k}.png")
        Image.alpha_composite(bg.convert("RGBA"), txt).convert("RGB").save(out)
        outs.append((k, out))
        print(f"{k}: 上段「{upper}」{us}px / 下段「{lower}」{ls}px -> {out}")
    contact_sheet(outs).save(os.path.join(HERE, "contact_sheet.png"))
    print("contact_sheet.png")


if __name__ == "__main__":
    main()
