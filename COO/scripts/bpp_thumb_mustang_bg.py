"""BPP マスタング（PHOENIX BIO-GUARD・車内編）サムネ 5 案。

文字の型はクラウン／ディフェンダー回（bpp_thumb_20261023.py）と同じ：
上段＝白・下段＝オレンジ、どちらも太い黒フチ＋影で上側にまとめ、中央〜下は車内の写真のために空ける。
背景はマスタングの赤い車内写真の置き場（後で差し替え）。

書き出し（--out）:
  T1.png / T2.png / A.png / B.png / C.png … 仮背景＋文字の合成（1280×720）
  layers/X_text.png                     … 文字だけの透過 PNG
  layers/X_bg.png                       … 仮背景
  contact_sheet.png                     … 5 案一覧（案名のみ。A に「要確認：名前の使用許可」）
  check_250px.png                       … 幅 250px に縮小した見え方の確認用

使い方:
  python COO/scripts/bpp_thumb_mustang_bg.py --font /path/to/NotoSansCJKjp-Black.otf \
      --out clients/BPP/output/サムネ_マスタングBG
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpp_thumb_20261023  # noqa: E402
from bpp_thumb_20261023 import H, W, luminance, text_layer  # noqa: E402

# 句読点（、。）は全角の箱の右半分が空いて字間が間延びするので、字面の右端＋少しで次の字へ送る
# （ランクル250 回の B「傷、ごまかし不可」と同じ詰め方）
TIGHT_PUNCT = "、。"
TIGHT_GAP = 0.06
_orig_glyph_mask = bpp_thumb_20261023._glyph_mask


def _ink_right(c, font):
    w = int(font.getlength(c)) * 2
    m = Image.new("L", (w, w), 0)
    ImageDraw.Draw(m).text((0, 0), c, font=font, fill=255)
    return m.getbbox()[2]


def _tight_glyph_mask(text, font_path, size=400):
    if not any(c in TIGHT_PUNCT for c in text):
        return _orig_glyph_mask(text, font_path, size)
    font = ImageFont.truetype(font_path, size)
    x, pos = 0.0, []
    for c in text:
        pos.append(x)
        x += _ink_right(c, font) + size * TIGHT_GAP if c in TIGHT_PUNCT else font.getlength(c)
    m = Image.new("L", (int(x) + size * 2, size * 2), 0)
    d = ImageDraw.Draw(m)
    for c, cx in zip(text, pos):
        d.text((size // 2 + cx, size // 2), c, font=font, fill=255)
    return m.crop(m.getbbox())


bpp_thumb_20261023._glyph_mask = _tight_glyph_mask  # text_line がこの関数で字面を作る

PATTERNS = [
    ("T1", "車内の清掃", "光触媒、もう遅い"),
    ("T2", "車内に光触媒？", "暗いと反応しない…"),
    ("T3", "車内は光触媒", "〇〇が反応しない…"),  # 〇〇 は伏せ字のまま描く
    ("T4", "車内に光触媒？", "夜は反応しない…"),
    ("A", "西野さんのマスタング", "車内のニオイは…？"),
    ("B", "旧車の車内は水洗い？", "逆にニオイが増える…"),
    ("C", "芳香剤を置いた旧車", "香りが消えたら…？"),
]
NOTES = {"T1": "チェック✕：『もう遅い』が台本にない", "A": "要確認：名前の使用許可"}


def red_interior_placeholder(seed=31):
    """赤い車内を想定した仮背景。上は暗め（文字が乗る）、中央〜下にシートの明るさを想定した帯。"""
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    v = 0.55 + 0.25 * y + 0.55 * np.exp(-((y - 0.68) ** 2) / 0.03) * (0.6 + 0.4 * np.sin(np.pi * x))
    v *= 1 - 0.35 * ((x - 0.5) ** 2 + (y - 0.6) ** 2)  # 周辺を少し落とす
    base = np.array([118, 26, 30], dtype=float)
    arr = v[..., None] * base + rng.normal(0, 1.5, (H, W, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def draw_note(d, xy, note, font, fill):
    """注記を描く。「✕」は Noto Sans CJK JP に字形が無い（豆腐になる）ので 2 本線で描く。"""
    x, y = xy
    for i, part in enumerate(note.split("✕")):
        if i:
            size = font.size
            t, b = y + size * 0.34, y + size * 1.06
            w = b - t
            d.line((x + 2, t, x + 2 + w, b), fill=fill, width=3)
            d.line((x + 2, b, x + 2 + w, t), fill=fill, width=3)
            x += w + 6
        d.text((x, y), part, font=font, fill=fill)
        x += d.textlength(part, font=font)


def contact_sheet(items, font_path):
    cols, tw, th, gap, cap = 3, 600, 338, 24, 46
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (gap + cols * (tw + gap), 70 + rows * (th + cap + gap)), (244, 244, 244))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 18), "BPP マスタング（PHOENIX BIO-GUARD・車内編）｜サムネ7案（仮背景）",
           font=ImageFont.truetype(font_path, 30), fill=(20, 20, 20))
    f = ImageFont.truetype(font_path, 24)
    fn = ImageFont.truetype(font_path, 18)
    for i, (label, img) in enumerate(items):
        cx = gap + (i % cols) * (tw + gap)
        cy = 70 + (i // cols) * (th + cap + gap)
        d.text((cx, cy + 6), label, font=f, fill=(30, 30, 30))
        if label in NOTES:
            lw = d.textlength(label, font=f)
            draw_note(d, (cx + lw + 14, cy + 12), NOTES[label], fn, (200, 30, 30))
        sheet.paste(img.resize((tw, th), Image.LANCZOS), (cx, cy + cap))
    return sheet


def check_250(items, font_path):
    """幅 250px（スマホの関連動画欄くらい）に縮めたときの見え方。"""
    tw, th, gap = 250, 141, 16
    sheet = Image.new("RGB", (gap + len(items) * (tw + gap), th + 2 * gap + 26), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(font_path, 16)
    for i, (label, img) in enumerate(items):
        cx = gap + i * (tw + gap)
        d.text((cx, 6), label, font=f, fill=(30, 30, 30))
        sheet.paste(img.resize((tw, th), Image.LANCZOS), (cx, 30))
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "layers"), exist_ok=True)

    bg = red_interior_placeholder()
    items = []
    for label, upper, lower in PATTERNS:
        txt, bottom = text_layer(upper, lower, a.font)
        comp = bg.convert("RGBA")
        comp.alpha_composite(txt)
        comp = comp.convert("RGB")
        comp.save(os.path.join(a.out, f"{label}.png"))
        txt.save(os.path.join(a.out, "layers", f"{label}_text.png"))
        bg.save(os.path.join(a.out, "layers", f"{label}_bg.png"))
        zone = txt.getchannel("A").crop((int(W * 0.9), int(H * 0.9), W, H)).getextrema()
        print(label, f"text_bottom={bottom}", f"badge_zone_alpha={zone}", f"bg_luminance={luminance(bg):.2f}")
        items.append((label, comp))
    contact_sheet(items, a.font).save(os.path.join(a.out, "contact_sheet.png"))
    check_250(items, a.font).save(os.path.join(a.out, "check_250px.png"))


if __name__ == "__main__":
    main()
