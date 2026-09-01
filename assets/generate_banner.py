"""Premium GitHub profile banner: DATA → SIGNAL → INTELLIGENCE."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUT_GIF = ROOT / "github-banner.gif"
OUT_PNG = ROOT / "github-banner.png"

W, H = 1080, 360
FRAMES = 24
DURATION_MS = 110

# Restrained palette: cyan → ice blue → violet
NAVY = (5, 8, 16)
ICE = (186, 230, 253)
CYAN = (56, 189, 248)
BLUE = (96, 165, 250)
VIOLET = (139, 124, 220)
WHITE = (246, 248, 252)
MUTED = (148, 163, 184)
INK = (226, 232, 240)

SAFE = (int(W * 0.30), int(H * 0.16), int(W * 0.70), int(H * 0.84))
LEFT_MAX = int(W * 0.31)
RIGHT_MIN = int(W * 0.69)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def journey_color(x: float):
    u = max(0.0, min(1.0, x / W))
    if u < 0.45:
        return mix(CYAN, BLUE, u / 0.45)
    return mix(BLUE, VIOLET, (u - 0.45) / 0.55)


def in_safe(x, y, pad: int = 8) -> bool:
    return SAFE[0] - pad < x < SAFE[2] + pad and SAFE[1] - pad < y < SAFE[3] + pad


def add_glow(base: Image.Image, overlay: Image.Image, blur: float, amount: float = 1.0) -> Image.Image:
    glow = overlay.filter(ImageFilter.GaussianBlur(blur))
    if amount < 1:
        glow.putalpha(glow.split()[-1].point(lambda a: int(a * amount)))
    return Image.alpha_composite(base, glow)


def radial_blob(arr, cx, cy, rx, ry, color, strength):
    yy, xx = np.ogrid[: arr.shape[0], : arr.shape[1]]
    fall = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)).astype(np.float32) * strength
    for i in range(3):
        arr[..., i] += fall * color[i]


def background() -> Image.Image:
    arr = np.zeros((H, W, 4), dtype=np.float32)
    arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3] = NAVY[0], NAVY[1], NAVY[2], 255

    radial_blob(arr, W / 2, H / 2, 300, 150, (70, 120, 200), 0.13)
    radial_blob(arr, 150, H * 0.45, 240, 170, (20, 90, 130), 0.10)
    radial_blob(arr, W - 130, H * 0.48, 260, 180, (70, 50, 130), 0.11)
    radial_blob(arr, W / 2, 20, 280, 90, (40, 70, 140), 0.05)

    yy, xx = np.ogrid[:H, :W]
    nx = (xx - W / 2) / (W * 0.52)
    ny = (yy - H / 2) / (H * 0.52)
    vignette = np.clip(1.0 - 0.42 * (nx**2 * 0.75 + ny**2), 0.45, 1.0)
    arr[..., :3] *= vignette[..., None]
    np.clip(arr, 0, 255, out=arr)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def make_left_data(rng: np.random.Generator):
    """Fragmented raw-data field that funnels rightward into the center."""
    columns = [
        (36, np.linspace(36, H - 40, 6)),
        (84, np.linspace(48, H - 70, 5)),
        (138, np.array([72, 118, 168, 228])),
        (192, np.array([96, 150, 204])),
        (248, np.array([124, 176])),
    ]
    nodes = []
    for x, ys in columns:
        for y in ys:
            nodes.append((float(x + rng.normal(0, 3.2)), float(np.clip(y + rng.normal(0, 6), 26, H - 34))))

    edges = []
    for i, a in enumerate(nodes):
        best = []
        for j, b in enumerate(nodes):
            if b[0] <= a[0] + 6:
                continue
            dist = math.hypot(b[0] - a[0], b[1] - a[1])
            if dist < 110:
                best.append((dist, b))
        best.sort()
        for _, b in best[:2]:
            if rng.random() < 0.85:
                edges.append((a, b))

    streams = []
    for y0 in (64, 132, 198, 268):
        pts = []
        for x in range(18, LEFT_MAX - 12, 20):
            y = y0 + 6 * math.sin(x * 0.038 + y0 * 0.015)
            converge = (x / LEFT_MAX) * 18
            y = lerp(y, H * 0.48, converge / 80)
            pts.append((x, float(np.clip(y, 28, H - 28))))
        streams.append(pts)
    return nodes, edges, streams


def make_right_net(rng: np.random.Generator):
    """Structured intelligence: irregular layered net, denser toward outputs."""
    layout = [
        (W - 308, 4),
        (W - 222, 7),
        (W - 136, 5),
        (W - 52, 3),
    ]
    layers = []
    for li, (x, n) in enumerate(layout):
        lo, hi = (H * 0.20, H * 0.78) if li < 3 else (H * 0.32, H * 0.68)
        raw = np.sort(rng.uniform(lo, hi, n))
        ys = []
        last = lo - 10
        for y in raw:
            y = max(y, last + 18)
            ys.append(min(y, hi))
            last = ys[-1]
        layer = [(float(x + rng.normal(0, 4.8)), float(y)) for y in ys]
        layers.append(layer)

    nodes = [p for layer in layers for p in layer]
    edges = []
    for li, layer in enumerate(layers[:-1]):
        nxt = layers[li + 1]
        for i, a in enumerate(layer):
            targets = {i % len(nxt), (i + 1) % len(nxt), (i * 2) % len(nxt)}
            for ti in targets:
                edges.append((a, nxt[ti]))
        if li == 0:
            edges.append((layer[0], layers[2][0]))
            edges.append((layer[-1], layers[2][-1]))
    return nodes, edges, layers


def draw_streams(draw, streams):
    for pts in streams:
        for a, b in zip(pts, pts[1:]):
            if in_safe(b[0], b[1], 20):
                continue
            draw.line([a, b], fill=(*CYAN, 28), width=1)


def draw_sparkline(draw):
    """Quiet, readable training curve — one ice-blue series, no rainbow."""
    x0, y0, x1, y1 = 28, H - 78, 168, H - 22
    draw.rounded_rectangle((x0, y0, x1, y1), radius=4, fill=(6, 10, 18, 150), outline=(*CYAN, 38))
    draw.text((x0 + 8, y0 + 4), "LOSS", font=FONT_TINY, fill=(*CYAN, 140))
    xs = np.linspace(0, 1, 36)
    ys = 0.90 * np.exp(-3.6 * xs) + 0.08 + 0.025 * np.sin(16 * xs)
    pts = []
    for x, y in zip(xs, ys):
        px = x0 + 10 + x * (x1 - x0 - 18)
        py = y1 - 8 - y * (y1 - y0 - 20)
        pts.append((px, py))
    draw.line(pts, fill=(*CYAN, 175), width=2)
    draw.ellipse((pts[-1][0] - 2.2, pts[-1][1] - 2.2, pts[-1][0] + 2.2, pts[-1][1] + 2.2), fill=(*ICE, 200))


def draw_nodes(draw, nodes, kind: str):
    for i, (x, y) in enumerate(nodes):
        if in_safe(x, y, 6):
            continue
        col = journey_color(x)
        if kind == "data":
            r = 2.1 if i % 4 else 2.7
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*col, 200))
        else:
            r = 3.3 if i < len(nodes) - 3 else 4.1
            if i % 3 == 0:
                draw.ellipse((x - r - 2, y - r - 2, x + r + 2, y + r + 2), outline=(*col, 190), width=1)
                draw.ellipse((x - 1.3, y - 1.3, x + 1.3, y + 1.3), fill=(*col, 200))
            else:
                draw.ellipse((x - r, y - r, x + r, y + r), fill=(*col, 220))
                draw.ellipse((x - r * 2.1, y - r * 2.1, x + r * 2.1, y + r * 2.1), outline=(*col, 40), width=1)


def draw_edges(draw, edges, alpha: int):
    for p, q in edges:
        if in_safe((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, 10):
            continue
        col = journey_color((p[0] + q[0]) / 2)
        draw.line([p, q], fill=(*col, alpha), width=1)


def tracked_width(draw, text, fnt, tracking):
    return sum(draw.textbbox((0, 0), c, font=fnt)[2] for c in text) + tracking * max(0, len(text) - 1)


def draw_tracked(draw, text, y, fnt, fill, tracking):
    total = tracked_width(draw, text, fnt, tracking)
    x = W / 2 - total / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textbbox((0, 0), ch, font=fnt)[2] + tracking


def draw_identity(base: Image.Image) -> Image.Image:
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    cx, cy = W / 2, H / 2 - 6
    name = "MARIA JAMES"
    tw = tracked_width(gd, name, FONT_TITLE, 6)
    # soft radial presence behind the name — ice blue, not neon
    blob = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ba = np.zeros((H, W, 4), dtype=np.float32)
    radial_blob(ba, cx, cy + 6, 230, 96, BLUE, 0.72)
    ba[..., 3] = np.clip(ba[..., 0] * 0.42, 0, 110)
    np.clip(ba, 0, 255, out=ba)
    blob = Image.fromarray(ba.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(base, blob)

    gd.text((cx - tw / 2, cy - 54), name, font=FONT_TITLE, fill=(*WHITE, 70))
    # dummy: draw_tracked for glow
    glow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g2 = ImageDraw.Draw(glow2, "RGBA")
    draw_tracked(g2, name, cy - 54, FONT_TITLE, (*WHITE, 90), 6)
    img = add_glow(img, glow2, 5.5, 0.85)

    sharp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sharp, "RGBA")
    draw_tracked(sd, name, cy - 54, FONT_TITLE, (*WHITE, 250), 6)
    draw_tracked(sd, "APPLIED AI  &  MACHINE LEARNING", cy + 10, FONT_SUB, (*BLUE, 200), 2.4)
    statement = "Turning complex data into intelligent systems."
    bbox = sd.textbbox((0, 0), statement, font=FONT_TAG)
    sd.text((cx - (bbox[2] - bbox[0]) / 2, cy + 40), statement, font=FONT_TAG, fill=(*MUTED, 185))
    img = Image.alpha_composite(img, sharp)

    sig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sig, "RGBA")
    mark = "ML  ·  NLP  ·  PREDICTIVE SYSTEMS"
    mb = sgd.textbbox((0, 0), mark, font=FONT_TINY)
    sgd.text((W - (mb[2] - mb[0]) - 22, H - 20), mark, font=FONT_TINY, fill=(*VIOLET, 110))
    return Image.alpha_composite(img, sig)


def static_base(left_nodes, left_edges, streams, right_nodes, right_edges) -> Image.Image:
    img = background()
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust, "RGBA")
    dust_rng = np.random.default_rng(4)
    for _ in range(36):
        x, y = float(dust_rng.uniform(8, W - 8)), float(dust_rng.uniform(8, H - 8))
        if in_safe(x, y, 36):
            continue
        r = float(dust_rng.uniform(0.5, 1.3))
        dd.ellipse((x - r, y - r, x + r, y + r), fill=(*journey_color(x), int(dust_rng.integers(16, 38))))
    img = Image.alpha_composite(img, dust)
    net = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(net, "RGBA")
    draw_streams(nd, streams)
    draw_edges(nd, left_edges, 70)
    draw_edges(nd, right_edges, 88)
    draw_nodes(nd, left_nodes, "data")
    draw_nodes(nd, right_nodes, "intel")
    draw_sparkline(nd)
    mid = net.resize((W // 2, H // 2), Image.Resampling.BILINEAR)
    mid = mid.filter(ImageFilter.GaussianBlur(2.4)).resize((W, H), Image.Resampling.BILINEAR)
    mid.putalpha(mid.split()[-1].point(lambda a: int(a * 0.45)))
    img = Image.alpha_composite(img, mid)
    img = add_glow(img, net, 1.15, 0.55)
    img = Image.alpha_composite(img, net)
    return draw_identity(img)


def draw_particles(draw, edges, t, speed, count_mod):
    for ei, (p, q) in enumerate(edges):
        if ei % count_mod:
            continue
        if in_safe((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, 14):
            continue
        u = (t * speed + ei * 0.11) % 1.0
        x = lerp(p[0], q[0], u)
        y = lerp(p[1], q[1], u)
        if in_safe(x, y, 4):
            continue
        col = journey_color(x)
        draw.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=(*col, 200))


def frame(base, t, left_nodes, left_edges, right_nodes, right_edges) -> Image.Image:
    img = base.copy()
    motion = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(motion, "RGBA")

    draw_particles(md, left_edges, t, 0.32, 2)
    draw_particles(md, right_edges, t, 0.22, 3)

    # occasional right-side activation, never the whole field
    for i in (1, 4, 8, len(right_nodes) - 1, len(right_nodes) - 2):
        if i >= len(right_nodes):
            continue
        x, y = right_nodes[i]
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * (t * 0.7) + i * 0.9)
        if pulse < 0.55:
            continue
        r = 5.5 + pulse * 2.0
        col = journey_color(x)
        md.ellipse((x - r, y - r, x + r, y + r), outline=(*col, int(30 + 50 * pulse)), width=1)

    # two left packets drifting toward center
    for k, y0 in enumerate((96.0, 214.0)):
        u = (t * 0.28 + k * 0.5) % 1.0
        x = 30 + u * (LEFT_MAX - 40)
        y = y0 + 4 * math.sin(u * math.pi * 2)
        md.ellipse((x - 1.6, y - 1.6, x + 1.6, y + 1.6), fill=(*CYAN, 170))

    img = Image.alpha_composite(img, motion)
    return img.convert("RGB")


FONT_TITLE = font("segoeuib.ttf", 46)
FONT_SUB = font("segoeui.ttf", 13)
FONT_TAG = font("segoeuil.ttf", 13)
FONT_TINY = font("consola.ttf", 10) if Path(r"C:\Windows\Fonts\consola.ttf").exists() else font("arial.ttf", 10)


def main() -> None:
    rng = np.random.default_rng(21)
    left_nodes, left_edges, streams = make_left_data(rng)
    right_nodes, right_edges, _ = make_right_net(rng)
    base = static_base(left_nodes, left_edges, streams, right_nodes, right_edges)

    frames = []
    for i in range(FRAMES):
        frames.append(frame(base, i / FRAMES, left_nodes, left_edges, right_nodes, right_edges))
        print(f"frame {i + 1}/{FRAMES}", flush=True)

    frames[0].save(OUT_PNG)
    palette = frames[0].quantize(colors=72, method=Image.Quantize.MEDIANCUT)
    quantized = [im.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for im in frames]
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
