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
DURATION_MS = 130

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
NAME_BOX = (int(W * 0.27), int(H * 0.26), int(W * 0.73), int(H * 0.74))
LEFT_MAX = int(W * 0.31)
RIGHT_MIN = int(W * 0.69)
MOTIF_Y = 46


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


def in_name(x, y, pad: int = 6) -> bool:
    return NAME_BOX[0] - pad < x < NAME_BOX[2] + pad and NAME_BOX[1] - pad < y < NAME_BOX[3] + pad


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

    radial_blob(arr, W / 2, H / 2 + 4, 320, 128, (78, 128, 210), 0.16)
    radial_blob(arr, 130, H * 0.48, 220, 160, (18, 80, 118), 0.08)
    radial_blob(arr, W - 120, H * 0.46, 250, 170, (68, 48, 128), 0.10)
    radial_blob(arr, W / 2, 18, 260, 70, (40, 70, 140), 0.04)

    yy, xx = np.ogrid[:H, :W]
    nx = (xx - W / 2) / (W * 0.52)
    ny = (yy - H / 2) / (H * 0.52)
    vignette = np.clip(1.0 - 0.42 * (nx**2 * 0.75 + ny**2), 0.45, 1.0)
    arr[..., :3] *= vignette[..., None]
    np.clip(arr, 0, 255, out=arr)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def make_left_data(rng: np.random.Generator):
    """Sparse, slightly chaotic field — elegant raw information, not a net."""
    nodes = []
    # uneven clusters, not columns
    for cx, cy, n, spread in (
        (42, 88, 5, 28),
        (78, 210, 4, 34),
        (128, 132, 4, 26),
        (176, 248, 3, 22),
        (220, 108, 3, 18),
    ):
        for _ in range(n):
            nodes.append(
                (
                    float(np.clip(cx + rng.normal(0, spread * 0.7), 18, LEFT_MAX - 8)),
                    float(np.clip(cy + rng.normal(0, spread), 32, H - 28)),
                )
            )
    loners = []
    for _ in range(7):
        p = (
            float(rng.uniform(22, LEFT_MAX - 16)),
            float(rng.uniform(40, H - 36)),
        )
        loners.append(p)
        nodes.append(p)

    edges = []
    for i, a in enumerate(nodes):
        if a in loners:
            continue
        cand = []
        for b in nodes:
            if b is a or b in loners:
                continue
            dx = b[0] - a[0]
            dist = math.hypot(dx, b[1] - a[1])
            if 18 < dist < 78 and dx > -12:
                cand.append((dist, b))
        cand.sort()
        if cand and rng.random() < 0.62:
            edges.append((a, cand[0][1]))

    streams = []
    for y0 in (78, 168, 254):
        pts = []
        for x in range(16, LEFT_MAX - 18, 26):
            y = y0 + 5 * math.sin(x * 0.042 + y0)
            pts.append((x, float(np.clip(y, 30, H - 30))))
        streams.append(pts)
    return nodes, edges, streams


def make_right_net(rng: np.random.Generator):
    """Hierarchical net that converges to three output nodes."""
    layout = [
        (W - 300, np.linspace(H * 0.22, H * 0.78, 5)),
        (W - 214, np.linspace(H * 0.18, H * 0.82, 7)),
        (W - 128, np.linspace(H * 0.26, H * 0.74, 5)),
        (W - 50, np.linspace(H * 0.36, H * 0.64, 3)),
    ]
    layers = []
    for x, ys in layout:
        layer = [(float(x + rng.normal(0, 1.6)), float(y + rng.normal(0, 3.0))) for y in ys]
        layers.append(layer)

    nodes = [p for layer in layers for p in layer]
    edges = []
    for li, layer in enumerate(layers[:-1]):
        nxt = layers[li + 1]
        for i, a in enumerate(layer):
            t0 = int(round(i * (len(nxt) - 1) / max(1, len(layer) - 1)))
            targets = {t0, min(len(nxt) - 1, t0 + 1)}
            for ti in targets:
                edges.append((a, nxt[ti]))
    # two intentional skip links into the output triad
    edges.append((layers[1][0], layers[3][0]))
    edges.append((layers[1][-1], layers[3][-1]))
    return nodes, edges, layers


def draw_streams(draw, streams):
    for pts in streams:
        for a, b in zip(pts, pts[1:]):
            if in_safe(b[0], b[1], 20) or in_name(b[0], b[1], 8):
                continue
            draw.line([a, b], fill=(*CYAN, 28), width=1)


def make_motif():
    """Signature: noise → cadence along a quiet meridian above the name."""
    pts = []
    for i in range(22):
        u = i / 21
        x = 28 + u * (W - 56)
        jitter = (1 - u) ** 1.6 * 11
        spacing_noise = (1 - u) * 7 * math.sin(i * 2.3)
        y = MOTIF_Y + jitter * math.sin(i * 1.7) + spacing_noise * 0.15
        r = 1.1 + u * 1.35
        pts.append((x, y, r, u))
    return pts


def draw_motif(draw, pts):
    visible = [(x, y) for x, y, _r, _u in pts]
    for a, b in zip(visible, visible[1:]):
        if abs(b[0] - a[0]) > 90:
            continue
        mx = (a[0] + b[0]) / 2
        col = journey_color(mx)
        draw.line([a, b], fill=(*col, 48), width=1)
    for x, y, r, u in pts:
        col = journey_color(x)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*col, int(70 + 90 * u)))


def draw_nodes(draw, nodes, kind: str):
    for i, (x, y) in enumerate(nodes):
        if in_safe(x, y, 6):
            continue
        col = journey_color(x)
        if kind == "data":
            r = 1.6 if i % 3 else 2.2
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(*col, 175))
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
    radial_blob(ba, cx, cy + 4, 250, 102, BLUE, 0.62)
    ba[..., 3] = np.clip(ba[..., 0] * 0.38, 0, 96)
    np.clip(ba, 0, 255, out=ba)
    blob = Image.fromarray(ba.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(base, blob)

    gd.text((cx - tw / 2, cy - 54), name, font=FONT_TITLE, fill=(*WHITE, 70))
    # dummy: draw_tracked for glow
    glow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g2 = ImageDraw.Draw(glow2, "RGBA")
    draw_tracked(g2, name, cy - 54, FONT_TITLE, (*WHITE, 90), 6)
    img = add_glow(img, glow2, 4.8, 0.70)

    sharp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sharp, "RGBA")
    draw_tracked(sd, name, cy - 54, FONT_TITLE, (*WHITE, 250), 6)
    draw_tracked(sd, "APPLIED AI  &  MACHINE LEARNING", cy + 10, FONT_SUB, (*BLUE, 200), 2.4)
    statement = "Turning complex data into intelligent systems."
    bbox = sd.textbbox((0, 0), statement, font=FONT_TAG)
    sd.text((cx - (bbox[2] - bbox[0]) / 2, cy + 40), statement, font=FONT_TAG, fill=(*MUTED, 185))
    img = Image.alpha_composite(img, sharp)

    atmosphere = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(atmosphere, "RGBA")
    rng = np.random.default_rng(9)
    for _ in range(10):
        x = float(rng.uniform(W * 0.34, W * 0.66))
        y = float(rng.uniform(H * 0.20, H * 0.80))
        if in_name(x, y, 18):
            continue
        r = float(rng.uniform(0.5, 1.0))
        ad.ellipse((x - r, y - r, x + r, y + r), fill=(*BLUE, int(rng.integers(18, 32))))
    img = Image.alpha_composite(img, atmosphere)

    sig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sig, "RGBA")
    label = "SPECIALIZATION"
    skills = "ML  ·  NLP  ·  PREDICTIVE SYSTEMS"
    lb = sgd.textbbox((0, 0), label, font=FONT_TINY)
    sb = sgd.textbbox((0, 0), skills, font=FONT_TINY)
    rx = W - 26
    sgd.text((rx - (lb[2] - lb[0]), H - 36), label, font=FONT_TINY, fill=(*MUTED, 130))
    sgd.text((rx - (sb[2] - sb[0]), H - 22), skills, font=FONT_TINY, fill=(*ICE, 175))
    return Image.alpha_composite(img, sig)


def static_base(left_nodes, left_edges, streams, right_nodes, right_edges, motif) -> Image.Image:
    img = background()
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust, "RGBA")
    dust_rng = np.random.default_rng(4)
    for _ in range(28):
        x, y = float(dust_rng.uniform(8, W - 8)), float(dust_rng.uniform(8, H - 8))
        if in_name(x, y, 20) or in_safe(x, y, 20):
            continue
        r = float(dust_rng.uniform(0.5, 1.2))
        dd.ellipse((x - r, y - r, x + r, y + r), fill=(*journey_color(x), int(dust_rng.integers(14, 32))))
    img = Image.alpha_composite(img, dust)
    net = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(net, "RGBA")
    draw_streams(nd, streams)
    draw_motif(nd, motif)
    draw_edges(nd, left_edges, 52)
    draw_edges(nd, right_edges, 105)
    draw_nodes(nd, left_nodes, "data")
    draw_nodes(nd, right_nodes, "intel")
    mid = net.resize((W // 2, H // 2), Image.Resampling.BILINEAR)
    mid = mid.filter(ImageFilter.GaussianBlur(2.4)).resize((W, H), Image.Resampling.BILINEAR)
    mid.putalpha(mid.split()[-1].point(lambda a: int(a * 0.40)))
    img = Image.alpha_composite(img, mid)
    img = add_glow(img, net, 1.1, 0.50)
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
        if in_safe(x, y, 4) or in_name(x, y, 4):
            continue
        col = journey_color(x)
        draw.ellipse((x - 1.3, y - 1.3, x + 1.3, y + 1.3), fill=(*col, 160))


def frame(base, t, left_nodes, left_edges, right_nodes, right_edges, motif) -> Image.Image:
    img = base.copy()
    motion = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(motion, "RGBA")

    draw_particles(md, left_edges, t, 0.18, 3)
    draw_particles(md, right_edges, t, 0.12, 4)

    for i in (0, 3, 7):
        if i >= len(left_nodes):
            continue
        x, y = left_nodes[i]
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * (t * 0.45) + i)
        if pulse < 0.72:
            continue
        md.ellipse((x - 3.2, y - 3.2, x + 3.2, y + 3.2), outline=(*CYAN, int(28 + 24 * pulse)), width=1)

    for i in (len(right_nodes) - 1, len(right_nodes) - 2, len(right_nodes) - 3, 6):
        if i >= len(right_nodes) or i < 0:
            continue
        x, y = right_nodes[i]
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * (t * 0.4) + i * 0.8)
        if pulse < 0.62:
            continue
        r = 6.0 + pulse * 1.6
        col = journey_color(x)
        md.ellipse((x - r, y - r, x + r, y + r), outline=(*col, int(36 + 40 * pulse)), width=1)

    if motif:
        u = (t * 0.22) % 1.0
        idx = int(u * (len(motif) - 1))
        x, y, r, mu = motif[idx]
        md.ellipse((x - 2.0, y - 2.0, x + 2.0, y + 2.0), fill=(*journey_color(x), 150))

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
    motif = make_motif()
    base = static_base(left_nodes, left_edges, streams, right_nodes, right_edges, motif)

    frames = []
    for i in range(FRAMES):
        frames.append(frame(base, i / FRAMES, left_nodes, left_edges, right_nodes, right_edges, motif))
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
