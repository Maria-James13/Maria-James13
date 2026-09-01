"""GitHub profile banner: commit journey from ideas to intelligent systems."""

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
DURATION_MS = 140

# GitHub-adjacent calm palette — not neon, not neural-net cyan.
NAVY = (13, 17, 23)
WHITE = (230, 237, 243)
MUTED = (139, 148, 158)
LINE = (88, 110, 130)
NODE = (201, 209, 217)
ACTIVE = (136, 180, 204)
VIOLET = (130, 136, 168)

SAFE = (int(W * 0.30), int(H * 0.22), int(W * 0.70), int(H * 0.78))
EDGE_X, EDGE_Y = 72.0, 48.0


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def in_safe(x, y, pad: int = 10) -> bool:
    return SAFE[0] - pad < x < SAFE[2] + pad and SAFE[1] - pad < y < SAFE[3] + pad


def edge_fade(x, y) -> float:
    fx = min(x, W - x) / EDGE_X
    fy = min(y, H - y) / EDGE_Y
    return max(0.0, min(1.0, fx)) * max(0.0, min(1.0, fy))


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
    radial_blob(arr, W / 2, H / 2, 320, 130, (26, 34, 44), 0.18)
    yy, xx = np.ogrid[:H, :W]
    nx = (xx - W / 2) / (W * 0.5)
    ny = (yy - H / 2) / (H * 0.5)
    vig = np.clip(1.0 - 0.18 * (nx**2 * 0.5 + ny**2 * 0.9), 0.82, 1.0)
    navy = np.array(NAVY, dtype=np.float32)
    arr[..., :3] = arr[..., :3] * vig[..., None] + navy * (1.0 - vig[..., None])
    np.clip(arr, 0, 255, out=arr)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def git_connector(p, q):
    """Horizontal-then-diagonal path — GitHub commit-graph language, not a neural net."""
    if abs(p[1] - q[1]) < 3:
        return [p, q]
    # Prefer a short run along the parent lane, then a diagonal into the child.
    mid_x = p[0] + (q[0] - p[0]) * 0.45
    return [p, (mid_x, p[1]), q]


def make_graph():
    """Designed commit graph: explore → mainline → merge-complete systems."""
    # Left: exploratory, uneven, some dead ends.
    left = {
        "a": (48, 78),
        "b": (108, 78),
        "c": (168, 78),
        "d": (62, 148),
        "e": (128, 148),
        "f": (198, 148),
        "g": (252, 148),
        "h": (94, 214),
        "i": (164, 214),
        "j": (78, 278),
        "k": (148, 278),
        "orphan": (214, 242),
    }
    left_edges = [
        ("a", "b"),
        ("b", "c"),
        ("a", "d"),
        ("d", "e"),
        ("e", "f"),
        ("f", "g"),
        ("e", "h"),
        ("h", "i"),  # terminates
        ("d", "j"),
        ("j", "k"),  # terminates
        ("f", "orphan"),  # dead-end experiment
    ]

    # Center: a quiet mainline above the name — experiment becoming engineering.
    center = {
        "m1": (330, 52),
        "m2": (430, 52),
        "m3": (540, 52),
        "m4": (650, 52),
        "m5": (740, 52),
        "n1": (390, 312),
        "n2": (520, 312),
        "n3": (650, 312),
    }
    center_edges = [
        ("c", "m1"),
        ("g", "m1"),
        ("m1", "m2"),
        ("m2", "m3"),
        ("m3", "m4"),
        ("m4", "m5"),
        ("k", "n1"),
        ("n1", "n2"),
        ("n2", "n3"),
    ]

    # Right: intentional branches that merge — pipelines, models, deploy.
    right = {
        "r0": (780, 148),
        "r1": (848, 148),
        "r2": (920, 148),
        "r3": (1004, 148),
        "u1": (868, 88),
        "u2": (940, 88),
        "d1": (868, 218),
        "d2": (940, 218),
        "s1": (900, 278),
        "s2": (980, 278),
    }
    right_edges = [
        ("m5", "r0"),
        ("n3", "d1"),
        ("r0", "r1"),
        ("r1", "r2"),
        ("r2", "r3"),
        ("r1", "u1"),
        ("u1", "u2"),
        ("u2", "r3"),  # merge
        ("r1", "d1"),
        ("d1", "d2"),
        ("d2", "r3"),  # merge
        ("d1", "s1"),
        ("s1", "s2"),
    ]

    nodes = {**left, **center, **right}
    edges = left_edges + center_edges + right_edges
    labels = {
        "a": "idea",
        "h": "experiment",
        "orphan": "wip",
        "m3": "a4f92c",
        "r2": "model-v2",
        "r3": "deploy",
        "u2": "feature",
    }
    # Pulse path: a successful idea that survives into production.
    pulse = ["a", "d", "e", "f", "g", "m1", "m2", "m3", "m4", "m5", "r0", "r1", "r2", "r3"]
    return nodes, edges, labels, pulse


def draw_edges(draw, nodes, edges):
    for a, b in edges:
        p, q = nodes[a], nodes[b]
        path = git_connector(p, q)
        for u, v in zip(path, path[1:]):
            if in_safe((u[0] + v[0]) / 2, (u[1] + v[1]) / 2, 4) and 90 < (u[1] + v[1]) / 2 < 270:
                continue
            fade = edge_fade((u[0] + v[0]) / 2, (u[1] + v[1]) / 2)
            mx = (u[0] + v[0]) / 2
            col = mix(LINE, ACTIVE, mx / W * 0.35)
            draw.line([u, v], fill=(*col, int(118 * fade)), width=1)


def draw_commits(draw, nodes, labels, active=None):
    for name, (x, y) in nodes.items():
        if in_safe(x, y, 2) and 100 < y < 260:
            continue
        fade = edge_fade(x, y)
        if fade < 0.06:
            continue
        is_head = name == "r3"
        is_active = name == active
        r = 4.4 if is_head else 3.4
        fill = ACTIVE if (is_head or is_active) else NODE
        alpha = int((230 if is_head or is_active else 200) * fade)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*fill, alpha))
        draw.ellipse((x - r, y - r, x + r, y + r), outline=(*NAVY, int(180 * fade)), width=1)
        if name in labels and fade > 0.45 and not in_safe(x, y + 10, 0):
            draw.text((x + 7, y - 5), labels[name], font=FONT_MICRO, fill=(*MUTED, int(95 * fade)))


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
    radial_blob(lift, cx, cy + 4, 250, 100, (32, 42, 54), 0.32)
    lift[..., 3] = np.clip(lift[..., 0] * 0.26, 0, 64)
    np.clip(lift, 0, 255, out=lift)
    img = Image.alpha_composite(
        base, Image.fromarray(lift.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(16))
    )

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    draw_tracked(gd, "MARIA JAMES", cy - 54, FONT_TITLE, (*WHITE, 70), 7)
    img = add_glow(img, glow, 3.2, 0.4)

    sharp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sharp, "RGBA")
    draw_tracked(sd, "MARIA JAMES", cy - 54, FONT_TITLE, (*WHITE, 248), 7)
    draw_tracked(sd, "APPLIED AI  &  MACHINE LEARNING", cy + 10, FONT_SUB, (*ACTIVE, 205), 2.6)
    line = "Building systems from ideas to intelligence."
    bb = sd.textbbox((0, 0), line, font=FONT_TAG)
    sd.text((cx - (bb[2] - bb[0]) / 2, cy + 40), line, font=FONT_TAG, fill=(*MUTED, 205))
    img = Image.alpha_composite(img, sharp)

    sig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sig, "RGBA")
    mark = "BUILD  ·  EXPERIMENT  ·  ITERATE"
    mb = sgd.textbbox((0, 0), mark, font=FONT_SIG)
    sgd.text((W - (mb[2] - mb[0]) - 40, H - 26), mark, font=FONT_SIG, fill=(*MUTED, 150))
    return Image.alpha_composite(img, sig)


def static_base(nodes, edges, labels) -> Image.Image:
    img = background()
    net = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(net, "RGBA")
    draw_edges(nd, nodes, edges)
    draw_commits(nd, nodes, labels)
    img = add_glow(img, net, 0.8, 0.28)
    img = Image.alpha_composite(img, net)
    return draw_identity(img)


def polyline_of(nodes, keys):
    pts = []
    for a, b in zip(keys, keys[1:]):
        pts.extend(git_connector(nodes[a], nodes[b]))
    # collapse consecutive duplicates
    out = [pts[0]]
    for p in pts[1:]:
        if p != out[-1]:
            out.append(p)
    return out


def point_on_polyline(pts, t):
    segs = []
    total = 0.0
    for a, b in zip(pts, pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, d))
        total += d
    if total <= 0:
        return pts[0]
    target = (t % 1.0) * total
    acc = 0.0
    for a, b, d in segs:
        if acc + d >= target:
            u = 0 if d == 0 else (target - acc) / d
            return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))
        acc += d
    return pts[-1]


def frame(base, t, nodes, edges, labels, pulse_pts) -> Image.Image:
    img = base.copy()
    motion = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(motion, "RGBA")

    x, y = point_on_polyline(pulse_pts, t * 0.85)
    if not (in_safe(x, y, 8) and 100 < y < 260):
        fade = edge_fade(x, y)
        md.ellipse((x - 2.2, y - 2.2, x + 2.2, y + 2.2), fill=(*ACTIVE, int(170 * fade)))

    # HEAD breathes once per loop — continuous development, not a flash.
    hx, hy = nodes["r3"]
    pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t * 0.5)
    if pulse > 0.55:
        r = 6.2 + pulse * 1.4
        md.ellipse((hx - r, hy - r, hx + r, hy + r), outline=(*ACTIVE, int(28 + 36 * pulse)), width=1)

    img = Image.alpha_composite(img, motion)
    return img.convert("RGB")


FONT_TITLE = font("segoeuib.ttf", 46)
FONT_SUB = font("segoeui.ttf", 13)
FONT_TAG = font("segoeuil.ttf", 13)
FONT_SIG = font("segoeui.ttf", 11)
FONT_MICRO = font("consola.ttf", 9) if Path(r"C:\Windows\Fonts\consola.ttf").exists() else font("segoeui.ttf", 9)


def main() -> None:
    nodes, edges, labels, pulse = make_graph()
    pulse_pts = polyline_of(nodes, pulse)
    base = static_base(nodes, edges, labels)

    frames = []
    for i in range(FRAMES):
        frames.append(frame(base, i / FRAMES, nodes, edges, labels, pulse_pts))
        print(f"frame {i + 1}/{FRAMES}", flush=True)

    frames[0].save(OUT_PNG)
    palette = frames[0].quantize(colors=80, method=Image.Quantize.MEDIANCUT)
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
