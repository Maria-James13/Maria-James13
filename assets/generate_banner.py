"""GitHub profile banner: aurora / flowing intelligence."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "aurora-hero-base.png"
OUT_GIF = ROOT / "github-banner.gif"
OUT_PNG = ROOT / "github-banner.png"

W, H = 1280, 400
FRAMES = 16
DURATION_MS = 210

IVORY = (228, 225, 218)
SUB = (176, 186, 204)
MUTED = (156, 164, 182)
NAVY = (10, 14, 26)
# Real aurora oxygen green — muted, not neon.
AURORA_GREEN = np.array([112, 186, 148], dtype=np.float32)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


def crop_cinematic(src: Image.Image) -> Image.Image:
    img = src.convert("RGB")
    sw, sh = img.size
    th = min(int(sw / (W / H)), sh)
    # Bias slightly down so the brightest arc sits under the type.
    top = int((sh - th) * 0.46)
    top = max(0, min(top, sh - th))
    return img.crop((0, top, sw, top + th)).resize((W, H), Image.Resampling.LANCZOS)


def add_green_ribbon(img: Image.Image) -> Image.Image:
    """A second, thinner curtain of aurora green riding the existing flow."""
    arr = np.array(img, dtype=np.float32)
    lum = arr @ np.array([0.21, 0.62, 0.17], dtype=np.float32)
    ribbon = np.clip((lum - 38) / 85.0, 0, 1) ** 1.15
    # Offset so it reads as its own strand, not a recolor of the blue.
    strand = np.roll(np.roll(ribbon, -7, axis=1), -5, axis=0)
    strand = np.clip((strand - 0.22) / 0.58, 0, 1)
    yy, xx = np.ogrid[:H, :W]
    # Strongest along the left-to-center sweep; a quieter echo on the right dissolve.
    where = np.exp(-(((xx - W * 0.36) / 400) ** 2 + ((yy - H * 0.64) / 130) ** 2))
    where = where + 0.45 * np.exp(-(((xx - W * 0.74) / 340) ** 2 + ((yy - H * 0.30) / 110) ** 2))
    # Keep the name island clean.
    well = np.exp(-(((xx - W / 2) / 260) ** 2 + ((yy - H / 2 + 8) / 82) ** 2))
    amt = np.clip(strand * np.clip(where, 0, 1) * (1.0 - 0.85 * well), 0, 1) * 0.26
    mixed = arr * (1.0 - amt[..., None] * 0.72) + AURORA_GREEN * amt[..., None]
    mixed[..., 1] += 16.0 * amt
    mixed[..., 0] *= 1.0 - 0.10 * amt
    return Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8), "RGB")


def dim_identity_well(img: Image.Image) -> Image.Image:
    arr = np.array(img, dtype=np.float32)
    yy, xx = np.ogrid[:H, :W]
    cx, cy = W / 2.0, H / 2.0 - 8
    well = np.exp(-(((xx - cx) / 268) ** 2 + ((yy - cy) / 86) ** 2)).astype(np.float32)
    navy = np.array(NAVY, dtype=np.float32)
    arr = arr * (1.0 - 0.28 * well[..., None]) + navy * (0.28 * well[..., None])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def edge_vignette(img: Image.Image) -> Image.Image:
    arr = np.array(img, dtype=np.float32)
    yy, xx = np.ogrid[:H, :W]
    nx = (xx - W / 2) / (W * 0.5)
    ny = (yy - H / 2) / (H * 0.5)
    vig = np.clip(1.0 - 0.18 * (nx**2 * 0.42 + ny**2), 0.82, 1.0)
    navy = np.array(NAVY, dtype=np.float32)
    arr = arr * vig[..., None] + navy * (1.0 - vig[..., None])
    fx = np.clip(np.minimum(xx, W - 1 - xx) / 28.0, 0, 1)
    fy = np.clip(np.minimum(yy, H - 1 - yy) / 22.0, 0, 1)
    edge = np.minimum(fx, fy)
    arr = arr * edge[..., None] + navy * (1.0 - edge[..., None])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def tracked(draw: ImageDraw.ImageDraw, text: str, y: float, fnt, fill, tracking: float):
    total = sum(draw.textbbox((0, 0), c, font=fnt)[2] for c in text) + tracking * max(0, len(text) - 1)
    x = W / 2 - total / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textbbox((0, 0), ch, font=fnt)[2] + tracking


def identity_overlay() -> Image.Image:
    ident = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(ident, "RGBA")
    cx, cy = W / 2, H / 2 - 6
    tracked(sd, "MARIA JAMES", cy - 58, FONT_TITLE, (*IVORY, 252), 11)
    tracked(sd, "APPLIED AI  &  MACHINE LEARNING", cy + 10, FONT_SUB, (*SUB, 215), 3.4)
    line = "Exploring patterns. Building intelligence."
    bb = sd.textbbox((0, 0), line, font=FONT_TAG)
    sd.text((cx - (bb[2] - bb[0]) / 2, cy + 42), line, font=FONT_TAG, fill=(*MUTED, 215))
    return ident


def highlight_layer(rgb: Image.Image) -> Image.Image:
    arr = np.array(rgb, dtype=np.float32)
    lum = arr @ np.array([0.21, 0.62, 0.17], dtype=np.float32)
    m = np.clip((lum - 48) / 90.0, 0, 1) ** 1.35
    layer = Image.fromarray(np.clip(arr * m[..., None], 0, 255).astype(np.uint8), "RGB")
    return layer.filter(ImageFilter.GaussianBlur(3.2))


def shift_no_wrap(img: Image.Image, dx: int, dy: int) -> Image.Image:
    shifted = ImageChops.offset(img, dx, dy)
    d = ImageDraw.Draw(shifted)
    if dx > 0:
        d.rectangle((0, 0, dx, H), fill=NAVY)
    elif dx < 0:
        d.rectangle((W + dx, 0, W, H), fill=NAVY)
    if dy > 0:
        d.rectangle((0, 0, W, dy), fill=NAVY)
    elif dy < 0:
        d.rectangle((0, H + dy, W, H), fill=NAVY)
    return shifted


def frame(base_rgb: Image.Image, ident: Image.Image, glow: Image.Image, t: float) -> Image.Image:
    breath = 1.0 + 0.028 * math.sin(2 * math.pi * t * 0.5)
    shifted = shift_no_wrap(
        glow,
        int(round(2.2 * math.sin(2 * math.pi * t))),
        int(round(1.1 * math.cos(2 * math.pi * t * 0.7))),
    )
    lit = Image.blend(base_rgb, ImageChops.screen(base_rgb, shifted), 0.08)
    lit = ImageEnhance.Brightness(lit).enhance(breath)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay, "RGBA")
    rng = np.random.default_rng(23)
    n = 18
    xs = rng.uniform(W * 0.64, W * 0.96, n)
    ys = rng.uniform(H * 0.08, H * 0.40, n)
    for i in range(n):
        u = (t * 0.16 + i * 0.047) % 1.0
        x = xs[i] + 14 * u
        y = ys[i] + 3.5 * math.sin(2 * math.pi * (u + i * 0.1))
        if abs(x - W / 2) < 250 and abs(y - H / 2) < 70:
            continue
        a = int(62 * (0.50 + 0.50 * math.sin(2 * math.pi * (u + 0.2))))
        r = 1.1 if i % 3 else 0.8
        od.ellipse((x - r, y - r, x + r, y + r), fill=(198, 216, 230, max(16, a)))

    img = Image.alpha_composite(lit.convert("RGBA"), overlay)
    return Image.alpha_composite(img, ident).convert("RGB")


FONT_TITLE = font("segoeuib.ttf", 54)
FONT_SUB = font("segoeui.ttf", 14)
FONT_TAG = font("segoeuil.ttf", 15)


def main() -> None:
    plate = edge_vignette(dim_identity_well(add_green_ribbon(crop_cinematic(Image.open(BASE)))))
    ident = identity_overlay()
    still = Image.alpha_composite(plate.convert("RGBA"), ident)
    still.convert("RGB").save(OUT_PNG)
    print("wrote", OUT_PNG, flush=True)

    glow = highlight_layer(plate)
    frames = [frame(plate, ident, glow, i / FRAMES) for i in range(FRAMES)]
    for i in range(FRAMES):
        print(f"frame {i + 1}/{FRAMES}", flush=True)

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


if __name__ == "__main__":
    main()
