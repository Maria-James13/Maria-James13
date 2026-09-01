"""Render a looping GitHub profile GIF for Maria James."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
STILL_CANDIDATES = [
    ROOT / "github-banner-still.png",
    Path(
        r"C:\Users\Maria james\.cursor\projects"
        r"\c-Users-Maria-james-Downloads-Freight-Prediction"
        r"\assets\github-banner-still.png"
    ),
]
OUT_GIF = ROOT / "github-banner.gif"
OUT_PNG = ROOT / "github-banner.png"

W, H = 960, 320
FRAMES = 20
DURATION_MS = 90
RNG = np.random.default_rng(13)

CYAN = (34, 211, 238)
VIOLET = (167, 139, 250)
TEAL = (45, 212, 191)
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = Path(r"C:\Windows\Fonts") / name
    return ImageFont.truetype(str(path), size)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def add_glow(base: Image.Image, overlay: Image.Image, blur: float) -> Image.Image:
    glow = overlay.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, glow)


def radial_blob(arr: np.ndarray, cx, cy, rx, ry, color, strength):
    yy, xx = np.ogrid[: arr.shape[0], : arr.shape[1]]
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    fall = np.exp(-d).astype(np.float32) * strength
    for i in range(3):
        arr[..., i] += fall * color[i]
    arr[..., 3] += fall * 255 * 0.55


def gradient_mesh(_t: float = 0.0) -> Image.Image:
    arr = np.zeros((H, W, 4), dtype=np.float32)
    arr[..., 0] = 7
    arr[..., 1] = 11
    arr[..., 2] = 20
    arr[..., 3] = 255
    radial_blob(arr, 180, 70, 340, 190, CYAN, 0.16)
    radial_blob(arr, W - 140, 90, 360, 200, VIOLET, 0.18)
    radial_blob(arr, W / 2, H - 10, 400, 150, TEAL, 0.09)
    radial_blob(arr, W / 2, 24, 300, 100, (96, 165, 250), 0.07)
    np.clip(arr, 0, 255, out=arr)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def make_network():
    layers = [
        [(56, 58 + i * 36) for i in range(6)],
        [(160, 42 + i * 32) for i in range(7)],
        [(270, 54 + i * 36) for i in range(6)],
        [(W - 56, 64 + i * 42) for i in range(5)],
        [(W - 160, 46 + i * 34) for i in range(6)],
        [(W - 270, 58 + i * 38) for i in range(5)],
    ]
    extra = [
        (110, 20),
        (230, 16),
        (370, 22),
        (590, 20),
        (720, 16),
        (850, 24),
        (100, 298),
        (860, 296),
        (740, 278),
        (200, 286),
    ]
    nodes = [p for layer in layers for p in layer] + extra
    edges = []
    for a, b in zip(layers[0], layers[1]):
        edges.append((a, b))
    for i, a in enumerate(layers[0]):
        edges.append((a, layers[1][(i + 1) % len(layers[1])]))
    for a, b in zip(layers[1], layers[2]):
        edges.append((a, b))
    for i, a in enumerate(layers[1]):
        edges.append((a, layers[2][i % len(layers[2])]))
    for a, b in zip(layers[3], layers[4]):
        edges.append((a, b))
    for i, a in enumerate(layers[3]):
        edges.append((a, layers[4][(i + 2) % len(layers[4])]))
    for a, b in zip(layers[4], layers[5]):
        edges.append((a, b))
    for i, a in enumerate(layers[4]):
        edges.append((a, layers[5][i % len(layers[5])]))
    # constellation across the top
    top = extra[:6]
    for a, b in zip(top, top[1:]):
        edges.append((a, b))
    edges.append((layers[0][0], extra[0]))
    edges.append((layers[3][0], extra[5]))
    return nodes, edges, layers


def edge_color(p, q):
    mx = (p[0] + q[0]) / 2
    return mix(CYAN, VIOLET, mx / W)


def draw_network(draw: ImageDraw.ImageDraw, nodes, edges, t: float, hollow):
    for p, q in edges:
        col = edge_color(p, q)
        pulse = 0.35 + 0.25 * (0.5 + 0.5 * math.sin(2 * math.pi * t + (p[0] + q[0]) * 0.01))
        a = int(90 * pulse)
        draw.line([p, q], fill=(*col, a), width=1)

    for i, (x, y) in enumerate(nodes):
        phase = 2 * math.sin(2 * math.pi * t + i * 0.37)
        r = 3.2 + phase * 0.55
        col = mix(CYAN, VIOLET, x / W)
        if i in hollow:
            draw.ellipse((x - r - 2, y - r - 2, x + r + 2, y + r + 2), outline=(*col, 200), width=2)
            draw.ellipse((x - 1.4, y - 1.4, x + 1.4, y + 1.4), fill=(*col, 160))
        else:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*col, 230))
            draw.ellipse((x - r * 2.4, y - r * 2.4, x + r * 2.4, y + r * 2.4), outline=(*col, 50), width=1)


def draw_particles(draw: ImageDraw.ImageDraw, edges, t: float):
    for ei, (p, q) in enumerate(edges):
        n = 1
        for k in range(n):
            u = (t * 0.85 + ei * 0.07 + k * 0.45) % 1.0
            x = lerp(p[0], q[0], u)
            y = lerp(p[1], q[1], u)
            col = edge_color(p, q)
            r = 1.8
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*col, 230))
            draw.ellipse((x - r * 3, y - r * 3, x + r * 3, y + r * 3), fill=(*col, 40))


def loss_points(t: float, seed: int, n: int = 48):
    xs = np.linspace(0, 1, n)
    base = 0.92 * np.exp(-3.1 * xs) + 0.04
    wobble = 0.035 * np.sin(14 * xs + seed) + 0.02 * np.sin(31 * xs + t * 6 + seed)
    noise = 0.012 * np.sin(55 * xs + seed * 2)
    y = np.clip(base + wobble + noise, 0.02, 1.0)
    return xs, y


def draw_loss_chart(draw: ImageDraw.ImageDraw, t: float):
    x0, y0, x1, y1 = 24, 208, 200, 304
    draw.rectangle((x0, y0, x1, y1), fill=(8, 12, 22, 140), outline=(148, 163, 184, 50))
    for frac, label in [(0.0, "1.0"), (0.33, "0.1"), (0.66, "0.01"), (1.0, "0.001")]:
        y = y0 + 18 + frac * (y1 - y0 - 36)
        draw.line((x0 + 28, y, x1 - 10, y), fill=(148, 163, 184, 28), width=1)
        draw.text((x0 + 6, y - 6), label, font=FONT_TINY, fill=(*MUTED, 160))
    draw.text((x0 + 8, y0 + 4), "LOSS", font=FONT_TINY, fill=(*CYAN, 180))
    draw.text((x0 + 88, y1 - 14), "EPOCHS", font=FONT_TINY, fill=(*MUTED, 150))

    palette = [CYAN, TEAL, VIOLET]
    for s, col in enumerate(palette):
        xs, ys = loss_points(t, s + 3)
        pts = []
        for x, y in zip(xs, ys):
            px = x0 + 30 + x * (x1 - x0 - 42)
            py = y0 + 18 + y * (y1 - y0 - 38)
            pts.append((px, py))
        draw.line(pts, fill=(*col, 170), width=2)
        head = min(len(pts) - 1, int((0.35 + 0.65 * ((t + s * 0.2) % 1.0)) * (len(pts) - 1)))
        hx, hy = pts[head]
        draw.ellipse((hx - 3, hy - 3, hx + 3, hy + 3), fill=(*col, 230))


def draw_text(draw: ImageDraw.ImageDraw, t: float):
    cx, cy = W / 2, H / 2 - 6
    title = "MARIA JAMES"
    sub = "AI / MACHINE LEARNING"
    tag = "DATA  →  PATTERNS  →  INTELLIGENCE"

    def centered(text, y, fnt, fill):
        bbox = draw.textbbox((0, 0), text, font=fnt)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw / 2, y), text, font=fnt, fill=fill)

    centered(title, cy - 58, FONT_TITLE, (*WHITE, 245))
    centered(sub, cy + 8, FONT_SUB, (*CYAN, 220))
    centered(tag, cy + 52, FONT_TAG, (*MUTED, 200))

    # traveling dots on the tagline arrows
    bbox = draw.textbbox((0, 0), tag, font=FONT_TAG)
    tw = bbox[2] - bbox[0]
    left = cx - tw / 2
    for frac in (0.30, 0.62):
        u = (t + frac) % 1.0
        x = left + tw * (0.22 + 0.18 * math.sin(u * math.pi))
        if frac > 0.5:
            x = left + tw * (0.52 + 0.18 * math.sin(u * math.pi))
        y = cy + 60
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(*CYAN, 210))


def static_base(nodes, edges, hollow) -> Image.Image:
    img = gradient_mesh()
    net = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(net, "RGBA")
    draw_network(nd, nodes, edges, 0.0, hollow)
    img = add_glow(img, net, 1.4)
    img = Image.alpha_composite(img, net)
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ud = ImageDraw.Draw(ui, "RGBA")
    draw_loss_chart(ud, 0.0)
    draw_text(ud, 0.0)
    return Image.alpha_composite(img, ui)


def frame(base: Image.Image, t: float, nodes, edges, hollow) -> Image.Image:
    img = base.copy()
    motion = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(motion, "RGBA")
    draw_particles(md, edges, t)
    for i, (x, y) in enumerate(nodes):
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t + i * 0.37)
        r = 4.5 + pulse * 2.2
        col = mix(CYAN, VIOLET, x / W)
        md.ellipse((x - r, y - r, x + r, y + r), outline=(*col, int(40 + 70 * pulse)), width=1)
    x0, y0, x1, y1 = 24, 208, 200, 304
    xs, ys = loss_points(t, 0)
    head = int((0.15 + 0.8 * t) * (len(xs) - 1))
    hx = x0 + 28 + xs[head] * (x1 - x0 - 38)
    hy = y0 + 16 + ys[head] * (y1 - y0 - 32)
    md.ellipse((hx - 3, hy - 3, hx + 3, hy + 3), fill=(*CYAN, 230))
    img = Image.alpha_composite(img, motion)
    return img.convert("RGB")


def load_still() -> Image.Image | None:
    for path in STILL_CANDIDATES:
        if path.is_file():
            im = Image.open(path).convert("RGB")
            im = im.resize((W, H), Image.Resampling.LANCZOS)
            dest = ROOT / "github-banner-still.png"
            if path.resolve() != dest.resolve():
                im.save(dest)
            return im
    return None


FONT_TITLE = font("segoeuib.ttf", 40)
FONT_SUB = font("segoeui.ttf", 15)
FONT_TAG = font("segoeuil.ttf", 12)
FONT_TINY = font("consola.ttf", 9) if Path(r"C:\Windows\Fonts\consola.ttf").exists() else font("arial.ttf", 9)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    nodes, edges, _layers = make_network()
    hollow = {i for i, n in enumerate(nodes) if 480 < n[0] < 800 or i % 5 == 0}

    still = load_still()
    base = static_base(nodes, edges, hollow)
    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        frames.append(frame(base, t, nodes, edges, hollow))
        print(f"frame {i + 1}/{FRAMES}", flush=True)

    if still is not None:
        still.save(ROOT / "github-banner-still.png")
    frames[0].save(OUT_PNG)

    global_palette = frames[0].quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    quantized = [im.quantize(palette=global_palette, dither=Image.Dither.FLOYDSTEINBERG) for im in frames]
    quantized[0].save(
        OUT_GIF,
        save_all=True,
        append_images=quantized[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print("wrote", OUT_GIF, "size_kb", round(OUT_GIF.stat().st_size / 1024, 1))
    print("wrote", OUT_PNG)


if __name__ == "__main__":
    main()
