#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天領盃（加登仙一の日本酒大学）サムネ生成: 白・黄の極太文字 + 赤強調、右側に加登社長の切り抜き用スペース
1280x720 PNG。各案ごとに 背景レイヤー / 文字レイヤー（透過）/ 合成 を出力し、全案のコンタクトシートも作る。
フォント: Noto Sans JP Black（Noto Sans CJK JP Black の Google Fonts 配布版）。無ければ Google Fonts から取得する。

使い方: python3 COO/scripts/tenryohai_thumb.py --spec SPEC.json --out DIR [--font PATH]
SPEC.json 例:
{"name": "20261024_九州編", "cases": [
  {"id": 1, "top": "焼酎だけじゃない", "bottom": "九州の日本酒", "emph": "日本酒"}, ...]}
"""
import argparse, json, os, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
FONT_URL = "https://fonts.gstatic.com/s/notosansjp/v57/-F6jfjtqLzI2JPCgQBnw7HFyzSD-AsregP8VFLgk75s.ttf"
WHITE, YELLOW, RED, INK = (255, 255, 255, 255), (255, 230, 0, 255), (235, 20, 30, 255), (10, 10, 14, 255)
PERSON_X = 860          # ここから右は加登社長の切り抜き用に空ける
NO_TEXT = (int(W * 0.9), int(H * 0.9))   # 右下10%（再生時間バッジ）に文字を置かない
MARGIN_L = 48
MAX_TEXT_W = PERSON_X - MARGIN_L - 24
STROKE_RATIO = 0.085    # 文字サイズに対する縁取りの太さ

def get_font(path):
    if path and os.path.isfile(path): return path
    cache = os.path.join(os.path.expanduser("~"), ".cache", "fonts", "NotoSansJP-Black.ttf")
    if not os.path.isfile(cache):
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        print(f"[font] downloading Noto Sans JP Black -> {cache}", file=sys.stderr)
        urllib.request.urlretrieve(FONT_URL, cache)
    return cache

def fit_size(font_path, text, max_w, max_size, min_size=60):
    size = max_size
    while size > min_size:
        f = ImageFont.truetype(font_path, size)
        if f.getlength(text) + size * STROKE_RATIO * 2 <= max_w: break
        size -= 2
    return size

def draw_line(layer, font_path, text, size, x, y, color, emph=None, emph_color=RED):
    """縁取り（黒）+ 影つきで1行描く。emph の部分だけ色を変える。戻り値: 行の実幅"""
    f = ImageFont.truetype(font_path, size)
    stroke = max(4, int(size * STROKE_RATIO))
    # 影
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((x + size * 0.05, y + size * 0.06), text, font=f, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * 0.04))
    layer.alpha_composite(shadow)
    d = ImageDraw.Draw(layer)
    # 縁取りを先に全体へ、次に本体を色分けして重ねる（縁が文字間で切れないように）
    d.text((x, y), text, font=f, fill=INK, stroke_width=stroke, stroke_fill=INK)
    cx = x
    segs = []
    if emph and emph in text:
        i = text.index(emph)
        segs = [(text[:i], color), (emph, emph_color), (text[i + len(emph):], color)]
    else:
        segs = [(text, color)]
    for s, c in segs:
        if not s: continue
        d.text((cx, y), s, font=f, fill=c)
        cx += f.getlength(s)
    return f.getlength(text)

def background(seed=0):
    """仮背景: 濃紺→墨のグラデーション + 日本酒瓶のシルエット列（実写の瓶写真に差し替える前提）"""
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    px = bg.load()
    for yy in range(H):
        t = yy / H
        r, g, b = int(28 + 10 * t), int(30 + 12 * t), int(52 - 30 * t)
        for xx in range(W):
            px[xx, yy] = (r, g, b, 255)
    # 瓶のシルエット（下段に並ぶ）
    bottles = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bottles)
    import random
    rnd = random.Random(seed)
    x = 30
    while x < W - 60:
        bw = rnd.randint(70, 95); bh = rnd.randint(330, 420); top = H - bh + 40
        col = rnd.choice([(40, 90, 70, 110), (60, 120, 100, 100), (120, 110, 60, 100), (70, 70, 110, 100), (140, 60, 60, 90)])
        bd.rounded_rectangle([x, top + 90, x + bw, H + 40], radius=22, fill=col)
        bd.rounded_rectangle([x + bw * 0.33, top, x + bw * 0.67, top + 110], radius=10, fill=col)
        bd.rounded_rectangle([x + bw * 0.3, top - 8, x + bw * 0.7, top + 22], radius=6, fill=(220, 220, 220, 80))
        bd.rectangle([x + 8, top + 150, x + bw - 8, top + 250], fill=(235, 235, 230, 60))
        x += bw + rnd.randint(8, 24)
    bottles = bottles.filter(ImageFilter.GaussianBlur(2.5))
    bg.alpha_composite(bottles)
    # 左側を暗くして文字を読みやすく、右側（人物）を少し明るく
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gp = grad.load()
    for xx in range(W):
        a = int(150 * max(0.0, 1 - xx / PERSON_X)) if xx < PERSON_X else 0
        for yy in range(H): gp[xx, yy] = (0, 0, 0, a)
    bg.alpha_composite(grad)
    # 上下の帯
    ImageDraw.Draw(bg).rectangle([0, 0, W, 6], fill=RED)
    return bg

def text_layer(font_path, case):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    top, bottom, emph = case["top"], case["bottom"], case.get("emph")
    s_top = fit_size(font_path, top, MAX_TEXT_W, 150)
    s_bot = fit_size(font_path, bottom, MAX_TEXT_W, 200)
    y_top = 112
    y_bot = y_top + int(s_top * 1.25) + 46
    draw_line(layer, font_path, top, s_top, MARGIN_L, y_top, WHITE, emph if emph in top else None)
    draw_line(layer, font_path, bottom, s_bot, MARGIN_L, y_bot, YELLOW, emph if emph in bottom else None)
    # 下段の下に黄色の下線（型の装飾）
    f = ImageFont.truetype(font_path, s_bot)
    uw = int(f.getlength(bottom))
    uy = y_bot + int(s_bot * 1.22) + 6
    ImageDraw.Draw(layer).rounded_rectangle([MARGIN_L, uy, MARGIN_L + uw, uy + 14], radius=7, fill=YELLOW)
    ImageDraw.Draw(layer).rounded_rectangle([MARGIN_L, uy - 3, MARGIN_L + uw, uy + 17], radius=9, outline=INK, width=3)
    return layer, {"top_size": s_top, "bottom_size": s_bot, "text_bottom_y": uy + 17}

def guides(img, font_path):
    g = img.copy(); d = ImageDraw.Draw(g); gf = ImageFont.truetype(font_path, 34)
    d.rectangle([PERSON_X, 0, W - 1, H - 1], outline=(0, 200, 255, 255), width=4)
    d.text((PERSON_X + 16, 16), "加登社長 切り抜き", font=gf, fill=(0, 200, 255, 255))
    d.rectangle([NO_TEXT[0], NO_TEXT[1], W - 1, H - 1], outline=(255, 80, 80, 255), width=4)
    d.text((NO_TEXT[0] - 230, NO_TEXT[1] + 18), "右下10% 文字禁止", font=gf, fill=(255, 80, 80, 255))
    return g

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True); ap.add_argument("--out", required=True); ap.add_argument("--font")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8")); font_path = get_font(a.font)
    os.makedirs(a.out, exist_ok=True)
    bg = background()
    bg.save(os.path.join(a.out, "bg_placeholder.png"))
    comps = []
    for c in spec["cases"]:
        layer, info = text_layer(font_path, c)
        assert info["text_bottom_y"] < NO_TEXT[1], "文字が右下10%帯に入っている"
        comp = bg.copy(); comp.alpha_composite(layer)
        base = f"{c['id']:02d}"
        layer.save(os.path.join(a.out, f"{base}_text.png"))
        comp.convert("RGB").save(os.path.join(a.out, f"{base}_thumb.png"))
        comps.append((c, comp))
        print(f"[case {c['id']}] top={c['top']}({info['top_size']}px) bottom={c['bottom']}({info['bottom_size']}px) emph={c.get('emph')}", file=sys.stderr)
    # コンタクトシート（ガイド線つき）
    n = len(comps); cols = 1; cw, ch = W // 2, H // 2; pad = 24
    sheet = Image.new("RGB", (cols * cw + pad * (cols + 1), n * (ch + 40) + pad * (n + 1)), (245, 245, 245))
    sd = ImageDraw.Draw(sheet); lf = ImageFont.truetype(font_path, 22)
    for i, (c, comp) in enumerate(comps):
        y = pad + i * (ch + 40 + pad)
        sd.text((pad, y), f"案{c['id']}  上: {c['top']} ／ 下: {c['bottom']} ／ 強調: {c.get('emph')}", font=lf, fill=(20, 20, 20))
        sheet.paste(guides(comp, font_path).convert("RGB").resize((cw, ch), Image.LANCZOS), (pad, y + 36))
    sheet.save(os.path.join(a.out, "contact_sheet.png"))
    print("[done]", a.out, file=sys.stderr)

if __name__ == "__main__":
    main()
