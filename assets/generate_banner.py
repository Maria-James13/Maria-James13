"""GitHub profile banner: mycelium / root network — intelligence through connection."""

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
DURATION_MS = 160

# Forest-charcoal, not GitHub-blue and not pure black.
SOIL = (16, 18, 17)
LIFT = (28, 32, 30)
IVORY = (226, 223, 214)
SAGE = (148, 166, 150)
MIST = (132, 146, 148)
BIO = (118, 168, 152)
MUTED = (142, 148, 140)
WHITE = (232, 230, 223)

SAFE = (int(W * 0.29), int(H * 0.22), int(W * 0.71), int(H * 0.78))
EDGE_X, EDGE_Y = 80.0, 52.0


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def in_safe(x, y, pad: int = 12) -> bool:
    return SAFE[0] - pad < x < SAFE[2] + pad and SAFE[1] - pad < y < SAFE[3] + pad


def edge_fade(x, y) -> float:
    fx = min(max(x, 0), W) 
    fy = min(max(y, 0), H)
    return max(0.0, min(1.0, min(fx, W - fx) / EDGE_X)) * max(
        0.0, min(1.0, min(fy, H - fy) / EDGE_Y)
    )


def add_glow(base, overlay, blur, amount=1.0):
    glow = overlay.filter(ImageFilter.GaussianBlur(blur))
    if amount < 1:
        glow.putalpha(glow.split()[-1].point(lambda a: int(a * amount)))
    return Image.alpha_composite(base, glow)


def radial_blob(arr, cx, cy, rx, ry, color, strength):
    yy, xx = np.ogrid[: arr.shape[0], : arr.shape[1]]
    fall = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)).astype(np.float32) * strength
    for i in range(3):
        arr[..., i] += fall * color[i]


def background(rng: np.random.Generator) -> Image.Image:
    arr = np.zeros((H, W, 4), dtype=np.float32)
    arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3] = SOIL[0], SOIL[1], SOIL[2], 255
    radial_blob(arr, W / 2, H / 2, 340, 145, LIFT, 0.20)
    radial_blob(arr, 180, 220, 260, 160, (22, 30, 26), 0.08)
    radial_blob(arr, W - 160, 140, 280, 170, (20, 26, 28), 0.07)
    # Barely visible grain — atmosphere, not noise.
    grain = rng.normal(0, 1.1, (H, W)).astype(np.float32)
    arr[..., :3] += grain[..., None]
    yy, xx = np.ogrid[:H, :W]
    nx = (xx - W / 2) / (W * 0.5)
    ny = (yy - H / 2) / (H * 0.5)
    vig = np.clip(1.0 - 0.20 * (nx**2 * 0.45 + ny**2), 0.80, 1.0)
    soil = np.array(SOIL, dtype=np.float32)
    arr[..., :3] = arr[..., :3] * vig[..., None] + soil * (1.0 - vig[..., None])
    np.clip(arr, 0, 255, out=arr)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def step_point(x, y, ang, step, rng):
    ang += rng.normal(0, 0.22)
    return x + math.cos(ang) * step, y + math.sin(ang) * step, ang


def grow(
    rng: np.random.Generator,
    x: float,
    y: float,
    ang: float,
    remaining: float,
    depth: int,
    step: float,
    toward_center: bool,
) -> list[list[tuple[float, float]]]:
    """Irregular filaments. Recurse into offshoots. Stop before the name."""
    paths: list[list[tuple[float, float]]] = []
    pts = [(x, y)]
    budget = remaining
    while budget > 0 and depth >= 0:
        x, y, ang = step_point(x, y, ang, step, rng)
        if toward_center:
            # Gentle bias inward without becoming geometric.
            desired = 0.0 if x < W / 2 else math.pi
            ang += 0.08 * math.sin(desired - ang)
        if x < -8 or x > W + 8 or y < -8 or y > H + 8:
            break
        if in_safe(x, y, 18):
            break
        pts.append((x, y))
        budget -= step
        # Occasional natural fork — more likely when "mature" (deeper remaining originally).
        if depth > 0 and rng.random() < 0.045 and budget > 18:
            fork_ang = ang + rng.choice([-1, 1]) * rng.uniform(0.45, 1.05)
            child = grow(rng, x, y, fork_ang, budget * rng.uniform(0.28, 0.55), depth - 1, step * 0.92, toward_center)
            paths.extend(child)
    if len(pts) > 2:
        paths.append(pts)
    return paths


def make_mycelium(rng: np.random.Generator):
    paths = []
    # Left: sparse, fine, exploratory — growing inward.
    for y0, ang in (
        (42, 0.12),
        (88, -0.08),
        (140, 0.18),
        (198, -0.15),
        (255, 0.10),
        (310, -0.05),
    ):
        paths.extend(
            grow(
                rng,
                rng.uniform(-6, 18),
                y0 + rng.normal(0, 8),
                ang + rng.normal(0, 0.12),
                remaining=rng.uniform(210, 290),
                depth=2,
                step=3.2,
                toward_center=True,
            )
        )
    # A few short rootlets that terminate early.
    for _ in range(4):
        paths.extend(
            grow(
                rng,
                rng.uniform(10, 80),
                rng.uniform(40, H - 40),
                rng.uniform(-0.4, 0.4),
                remaining=rng.uniform(40, 90),
                depth=1,
                step=2.8,
                toward_center=True,
            )
        )
    # Right: richer, more mature, still organic.
    for y0, ang in (
        (36, math.pi - 0.1),
        (92, math.pi + 0.16),
        (150, math.pi - 0.2),
        (205, math.pi + 0.12),
        (262, math.pi - 0.08),
        (318, math.pi + 0.14),
        (70, math.pi + 0.4),
        (240, math.pi - 0.35),
    ):
        paths.extend(
            grow(
                rng,
                rng.uniform(W - 18, W + 6),
                y0 + rng.normal(0, 10),
                ang + rng.normal(0, 0.15),
                remaining=rng.uniform(250, 360),
                depth=3,
                step=3.0,
                toward_center=True,
            )
        )
    return paths


def filament_color(x: float):
    u = max(0.0, min(1.0, x / W))
    if u < 0.4:
        return mix(MIST, SAGE, u / 0.4)
    return mix(SAGE, BIO, (u - 0.4) / 0.6)


def draw_filaments(draw: ImageDraw.ImageDraw, paths: list[list[tuple[float, float]]]):
    for pts in paths:
        n = len(pts)
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            fade = edge_fade(mx, my)
            if fade < 0.05:
                continue
            t = i / max(1, n)
            # Thicker near origin of a strand, tapering like a root.
            width = 1 if t > 0.35 else 2
            col = filament_color(mx)
            alpha = int((70 + 55 * (1 - t * 0.4)) * fade)
            draw.line([a, b], fill=(*col, alpha), width=width)


def tracked_width(draw, text, fnt, tracking):
    return sum(draw.textbbox((0, 0), c, font=fnt)[2] for c in text) + tracking * max(0, len(text) - 1)


def draw_tracked(draw, text, y, fnt, fill, tracking):
    total = tracked_width(draw, text, fnt, tracking)
    x = W / 2 - total / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textbbox((0, 0), ch, font=fnt)[2] + tracking


def draw_identity(base: Image.Image) -> Image.Image:
    cx, cy = W / 2, H / 2 - 4
    lift = np.zeros((H, W, 4), dtype=np.float32)
    radial_blob(lift, cx, cy + 6, 255, 105, (36, 44, 40), 0.28)
    lift[..., 3] = np.clip(lift[..., 1] * 0.22, 0, 58)
    np.clip(lift, 0, 255, out=lift)
    img = Image.alpha_composite(
        base, Image.fromarray(lift.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(18))
    )

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    draw_tracked(gd, "MARIA JAMES", cy - 54, FONT_TITLE, (*IVORY, 55), 8)
    img = add_glow(img, glow, 2.8, 0.32)

    sharp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sharp, "RGBA")
    draw_tracked(sd, "MARIA JAMES", cy - 54, FONT_TITLE, (*IVORY, 248), 8)
    draw_tracked(sd, "APPLIED AI  &  MACHINE LEARNING", cy + 10, FONT_SUB, (*SAGE, 195), 2.8)
    line = "Exploring patterns, building intelligence."
    bb = sd.textbbox((0, 0), line, font=FONT_TAG)
    sd.text((cx - (bb[2] - bb[0]) / 2, cy + 40), line, font=FONT_TAG, fill=(*MUTED, 200))
    img = Image.alpha_composite(img, sharp)

    whisper = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(whisper, "RGBA")
    phrase = "patterns emerge from connection"
    pb = wd.textbbox((0, 0), phrase, font=FONT_MICRO)
    wd.text((36, H - 24), phrase, font=FONT_MICRO, fill=(*MUTED, 88))
    return Image.alpha_composite(img, whisper)


def static_base(rng, paths) -> Image.Image:
    img = background(rng)
    net = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(net, "RGBA")
    draw_filaments(nd, paths)
    img = add_glow(img, net, 1.1, 0.22)
    img = Image.alpha_composite(img, net)
    return draw_identity(img)


def longest_paths(paths, n=3):
    ranked = sorted(paths, key=len, reverse=True)
    return ranked[:n]


def point_on_path(pts, t):
    if len(pts) < 2:
        return pts[0]
    segs = []
    total = 0.0
    for a, b in zip(pts, pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, d))
        total += d
    target = (t % 1.0) * max(total, 1e-6)
    acc = 0.0
    for a, b, d in segs:
        if acc + d >= target:
            u = 0 if d == 0 else (target - acc) / d
            return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))
        acc += d
    return pts[-1]


def frame(base, t, veins) -> Image.Image:
    img = base.copy()
    motion = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(motion, "RGBA")
    for i, pts in enumerate(veins):
        u = (t * 0.35 + i * 0.31) % 1.0
        x, y = point_on_path(pts, u)
        if in_safe(x, y, 8):
            continue
        fade = edge_fade(x, y)
        r = 1.6
        md.ellipse((x - r, y - r, x + r, y + r), fill=(*BIO, int(90 * fade)))
    img = Image.alpha_composite(img, motion)
    return img.convert("RGB")


FONT_TITLE = font("segoeuib.ttf", 46)
FONT_SUB = font("segoeui.ttf", 13)
FONT_TAG = font("segoeuil.ttf", 13)
FONT_MICRO = font("segoeui.ttf", 10)


def main() -> None:
    rng = np.random.default_rng(17)
    paths = make_mycelium(rng)
    base = static_base(rng, paths)
    veins = longest_paths(paths, 3)

    frames = []
    for i in range(FRAMES):
        frames.append(frame(base, i / FRAMES, veins))
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
    print("wrote", OUT_PNG, "strands", len(paths))


if __name__ == "__main__":
    main()
