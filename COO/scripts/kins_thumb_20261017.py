#!/usr/bin/env python3
"""KINS 2026-10-17「歯周病と腸内環境」サムネ3案（Pillow）。
背景レイヤーと文字レイヤーを別々に描画して最後に合成。はみ出し・168x94縮小可読性を自動チェックし、NGなら文字サイズを調整して再生成。
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat

W, H = 1280, 720
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"   # index 0 = Noto Sans CJK JP Black
OUT = sys.argv[1] if len(sys.argv) > 1 else "clients/KINS/output/thumbnails"
LAYERS = os.path.join(OUT, "layers")
PREFIX = "kins_20261017_shishubyo"

# レイアウト制約
LEFT = 44                      # 左マージン
RIGHT_LIMIT = W * 2 // 3       # 右1/3（x>=853）は演者の切り抜き用に空ける
NO_TEXT_BOX = (int(W * 0.9), int(H * 0.9), W, H)   # 右下10%には文字を置かない
TOP, BOTTOM = 36, H - 36
MAX_TEXT_W = RIGHT_LIMIT - LEFT - 8   # 文字が使える最大幅（≈ 801px = 画面幅の62.6%）
THUMB = (168, 94)

PLANS = {
    "A": {"l1": "歯周病の菌が", "l2": "大腸がんの腸に",
          "bg": ((132, 24, 48), (62, 8, 26)), "accent": (255, 214, 92), "stroke": (46, 4, 18)},
    "B": {"l1": "歯周病の人は", "l2": [("死亡率", 1.0), ("1.3", 1.55), ("倍", 1.0)],
          "bg": ((84, 86, 94), (30, 31, 36)), "accent": (255, 214, 92), "stroke": (12, 12, 16), "hero_color": (255, 80, 80)},
    "C": {"l1": "腸活する前に", "l2": "歯周病を疑え",
          "bg": ((22, 112, 100), (8, 48, 46)), "accent": (255, 232, 110), "stroke": (4, 34, 32)},
}

def font(size): return ImageFont.truetype(FONT, int(size), index=0)

def seg_list(line): return line if isinstance(line, list) else [(line, 1.0)]

def measure(segs, base):
    """セグメント列の総幅・最大高さ・各セグメントの(font, bbox)"""
    parts = []; total = 0; maxh = 0
    for text, k in segs:
        f = font(base * k); bb = f.getbbox(text, anchor="ls")   # left-baseline
        parts.append((text, f, bb)); total += bb[2] - bb[0]; maxh = max(maxh, -bb[1])
    return total, maxh, parts

def fit_base(segs, target_w, max_size=400):
    lo, hi = 20, max_size
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if measure(segs, mid)[0] <= target_w: lo = mid
        else: hi = mid
    return lo

# ---------- 背景レイヤー ----------
def make_bg(c1, c2):
    bg = Image.new("RGB", (W, H), c1); px = bg.load()
    for y in range(H):
        for x in range(W):
            t = 0.55 * (x / W) + 0.45 * (y / H)          # 左上→右下の斜めグラデーション
            px[x, y] = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
    # 右側（演者位置）をほんのり明るく、左の文字域はやや暗く
    glow = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(glow)
    gd.ellipse((W * 0.55, -H * 0.2, W * 1.25, H * 1.2), fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    light = Image.new("RGB", (W, H), (255, 255, 255))
    bg = Image.composite(Image.blend(bg, light, 0.18), bg, glow)
    # 細い斜めストライプで質感
    stripe = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(stripe)
    for i in range(-H, W + H, 28): sd.line((i, 0, i - H, H), fill=255, width=1)
    bg = Image.composite(Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.10), bg, stripe)
    return bg

# ---------- 文字レイヤー ----------
def draw_line(layer, segs, base, x, baseline_y, fill, stroke, hero_color=None):
    d = ImageDraw.Draw(layer)
    total, maxh, parts = measure(segs, base)
    sw = max(4, int(base * 0.075))
    cx = x
    # ドロップシャドウ（別レイヤーにぼかして合成）
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0)); shd = ImageDraw.Draw(sh)
    cx2 = x
    for text, f, bb in parts:
        shd.text((cx2 + 8, baseline_y + 8), text, font=f, fill=(0, 0, 0, 170), anchor="ls", stroke_width=sw, stroke_fill=(0, 0, 0, 170))
        cx2 += bb[2] - bb[0]
    sh = sh.filter(ImageFilter.GaussianBlur(6)); layer.alpha_composite(sh)
    d = ImageDraw.Draw(layer); boxes = []
    for (text, k), (_, f, bb) in zip(segs, parts):
        col = hero_color if (hero_color and k > 1.0) else fill
        d.text((cx, baseline_y), text, font=f, fill=col + (255,), anchor="ls", stroke_width=sw, stroke_fill=stroke + (255,))
        boxes.append((cx + bb[0] - sw, baseline_y + bb[1] - sw, cx + bb[2] + sw, baseline_y + bb[3] + sw))
        cx += bb[2] - bb[0]
    return boxes

def make_text_layer(plan, scale):
    """scale: 文字サイズ係数（自動調整用）。戻り値: (layer, bboxes, sizes)"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s1 = seg_list(plan["l1"]); s2 = seg_list(plan["l2"])
    base2 = int(fit_base(s2, MAX_TEXT_W) * scale)                 # 下段（主役）: 幅いっぱい
    base1 = int(min(fit_base(s1, MAX_TEXT_W), base2 * 0.82) * scale)  # 上段: 一回り小さく
    w1, h1, _ = measure(s1, base1); w2, h2, _ = measure(s2, base2)
    gap = int(base2 * 0.22)
    block_h = h1 + gap + h2
    top = max(TOP, (H - block_h) // 2 - int(H * 0.03))
    y1 = top + h1; y2 = y1 + gap + h2
    boxes = draw_line(layer, s1, base1, LEFT, y1, plan["accent"], plan["stroke"])
    boxes += draw_line(layer, s2, base2, LEFT, y2, (255, 255, 255), plan["stroke"], plan.get("hero_color"))
    return layer, boxes, (base1, base2)

# ---------- 自動チェック ----------
def check(img, boxes, sizes):
    problems = []
    for b in boxes:
        if b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H: problems.append(f"overflow-canvas {b}")
        if b[2] > RIGHT_LIMIT + 6: problems.append(f"overflow-right-third x2={b[2]:.0f}>{RIGHT_LIMIT}")
        if b[3] > BOTTOM: problems.append(f"overflow-bottom y2={b[3]:.0f}")
        nb = NO_TEXT_BOX
        if not (b[2] < nb[0] or b[0] > nb[2] or b[3] < nb[1] or b[1] > nb[3]): problems.append("in-no-text-box")
    # 168x94 縮小可読性: 文字高さ >= 10px、文字域と背景のコントラスト
    small = img.resize(THUMB, Image.LANCZOS).convert("L")
    k = THUMB[0] / W
    for i, sz in enumerate(sizes):
        if sz * k < 10: problems.append(f"line{i+1} too small at 168px ({sz*k:.1f}px)")
    # 文字ピクセル（白/黄）と周辺のコントラスト
    sm = img.resize(THUMB, Image.LANCZOS)
    bright = sum(1 for p in sm.convert("L").getdata() if p > 200)
    if bright < 40: problems.append(f"low bright-text pixels at 168px ({bright})")
    return problems

def build(key, plan):
    bg = make_bg(*plan["bg"])
    bg.save(os.path.join(LAYERS, f"{PREFIX}_{key}_bg.png"))
    scale = 1.0; log = []
    for attempt in range(8):
        layer, boxes, sizes = make_text_layer(plan, scale)
        img = bg.copy().convert("RGBA"); img.alpha_composite(layer); img = img.convert("RGB")
        probs = check(img, boxes, sizes)
        log.append((attempt, scale, sizes, probs))
        if not probs: break
        if any("overflow" in p or "no-text" in p for p in probs): scale *= 0.94
        else: scale *= 1.06
    layer.save(os.path.join(LAYERS, f"{PREFIX}_{key}_text.png"))
    img.save(os.path.join(OUT, f"{PREFIX}_{key}.png"))
    img.resize(THUMB, Image.LANCZOS).save(os.path.join(LAYERS, f"{PREFIX}_{key}_168x94.png"))
    return img, sizes, probs, log

def main():
    os.makedirs(LAYERS, exist_ok=True)
    results = {}
    for key, plan in PLANS.items():
        img, sizes, probs, log = build(key, plan)
        results[key] = img
        print(f"[{key}] sizes={sizes} attempts={len(log)} result={'OK' if not probs else probs}")
        for a in log: print("   ", a)
    # コンタクトシート（縦並び）
    gutter, label_h = 36, 60
    sheet = Image.new("RGB", (W + gutter * 2, label_h * 3 + H * 3 + gutter * 4), (245, 245, 245))
    d = ImageDraw.Draw(sheet); lf = font(34)
    y = gutter
    for key, plan in PLANS.items():
        l1 = plan["l1"]; l2 = plan["l2"] if isinstance(plan["l2"], str) else "".join(t for t, _ in plan["l2"])
        d.text((gutter, y + 8), f"案{key}　{l1}／{l2}" + ("（本命）" if key == "A" else ""), font=lf, fill=(30, 30, 30))
        y += label_h
        sheet.paste(results[key], (gutter, y))
        # 168x94 縮小プレビューをラベル右端に
        sm = results[key].resize(THUMB, Image.LANCZOS)
        sheet.paste(sm, (gutter + W - THUMB[0], y - label_h + 2 - 0))
        y += H + gutter
    sheet.save(os.path.join(OUT, f"{PREFIX}_contactsheet.png"))
    print("[done]", OUT)

if __name__ == "__main__":
    main()
