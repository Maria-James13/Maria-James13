"""GitHub profile project cards — quieter aurora plates under the banner."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "aurora-hero-base.png"
OUT = ROOT / "cards"
OUT.mkdir(exist_ok=True)

CW, CH = 920, 500
IVORY = (228, 225, 218)
SUB = (176, 186, 204)
MUTED = (150, 160, 176)
NAVY = np.array([10, 14, 26], dtype=np.float32)
GREEN = np.array([112, 186, 148], dtype=np.float32)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


FONT_KICK = font("segoeui.ttf", 15)
FONT_TITLE = font("segoeuib.ttf", 36)
FONT_LINE = font("segoeuil.ttf", 20)
FONT_FOOT = font("segoeui.ttf", 15)


PROJECTS = [
    {
        "slug": "freight-rate",
        "kicker": "TABULAR ML",
        "title": "FREIGHT RATE",
        "line": "Leakage-safe CatBoost on rate-per-mile.",
        "foot": "Oct holdout MAE  $111   ·   reefer error  −58.6%",
        "crop": (0.02, 0.38, 0.72, 0.55),
    },
    {
        "slug": "nba-predictor",
        "kicker": "MODEL SERVING",
        "title": "NBA PREDICTOR",
        "line": "Evaluated home-win model behind FastAPI.",
        "foot": "64.1% accuracy   ·   Brier 0.22   ·   59 tests",
        "crop": (0.28, 0.18, 0.70, 0.55),
    },
    {
        "slug": "drug-interaction",
        "kicker": "RAG  /  LLM",
        "title": "DRUG INTERACTION",
        "line": "Retrieval over FDA labels, then Gemini.",
        "foot": "ChromaDB   ·   MiniLM   ·   FastAPI",
        "crop": (0.42, 0.08, 0.58, 0.52),
    },
    {
        "slug": "pathfinder-ai",
        "kicker": "NLP AGENTS",
        "title": "PATHFINDER AI",
        "line": "Learning-path assistant with retrieval and Llama.",
        "foot": "TF-IDF   ·   Groq   ·   Streamlit",
        "crop": (0.24, 0.22, 0.68, 0.54),
    },
    {
        "slug": "selftalk-ai",
        "kicker": "NLP  /  EVAL",
        "title": "SELFTALK AI",
        "line": "Mood and cognitive-distortion analysis.",
        "foot": "MiniLM   ·   Gradio   ·   MSE / MAE / RMSE",
        "crop": (0.18, 0.42, 0.68, 0.52),
    },
    {
        "slug": "nlp-tasks",
        "kicker": "COURSEWORK",
        "title": "NLP TASKS",
        "line": "Foundation labs from tokenization to modeling.",
        "foot": "NLTK   ·   sequence notebooks",
        "crop": (0.50, 0.28, 0.50, 0.50),
    },
    {
        "slug": "traffic-analysis",
        "kicker": "APPLIED ML",
        "title": "TRAFFIC ANALYSIS",
        "line": "Exploratory modeling on Bangalore congestion.",
        "foot": "urban mobility   ·   tabular EDA",
        "crop": (0.00, 0.22, 0.64, 0.50),
    },
    {
        "slug": "cia3-ada",
        "kicker": "COMPUTER VISION",
        "title": "IMAGE  &  VIDEO",
        "line": "Inspection notebooks, including counterfeit goods.",
        "foot": "OpenCV-style analysis   ·   coursework",
        "crop": (0.35, 0.00, 0.62, 0.50),
    },
    {
        "slug": "spr-lab",
        "kicker": "SPEECH  /  SPR",
        "title": "PATTERN RECOGNITION",
        "line": "Speech features, classification, and reporting.",
        "foot": "SPR lab sequence",
        "crop": (0.12, 0.50, 0.70, 0.48),
    },
    {
        "slug": "smart-agriculture",
        "kicker": "IOT SYSTEMS",
        "title": "SMART AGRICULTURE",
        "line": "Telemetry dashboard around sensor data.",
        "foot": "ESP8266   ·   charts   ·   device views",
        "crop": (0.22, 0.30, 0.66, 0.50),
    },
]


def crop_frac(img: Image.Image, fx, fy, fw, fh) -> Image.Image:
    w, h = img.size
    x0, y0 = int(w * fx), int(h * fy)
    x1, y1 = min(w, x0 + int(w * fw)), min(h, y0 + int(h * fh))
    return img.crop((x0, y0, x1, y1)).resize((CW, CH), Image.Resampling.LANCZOS)


def plate_from(crop: Image.Image) -> Image.Image:
    arr = np.array(crop.convert("RGB"), dtype=np.float32)
    lum = arr @ np.array([0.21, 0.62, 0.17], dtype=np.float32)
    # Quiet green in the bright filaments only.
    gmask = np.clip((lum - 50) / 90.0, 0, 1) ** 1.3 * 0.16
    arr = arr * (1.0 - gmask[..., None] * 0.55) + GREEN * gmask[..., None]
    arr[..., 1] += 10 * gmask

    yy, xx = np.ogrid[:CH, :CW]
    # Left well for type; aurora lives on the right.
    left = np.clip(0.18 + 0.82 * (xx / CW) ** 1.55, 0.18, 1.0)
    arr *= 0.56 * left[..., None]
    arr = arr * 0.78 + NAVY * 0.22

    nx = (xx - CW / 2) / (CW * 0.5)
    ny = (yy - CH / 2) / (CH * 0.5)
    vig = np.clip(1.0 - 0.28 * (nx**2 * 0.35 + ny**2), 0.72, 1.0)
    arr = arr * vig[..., None] + NAVY * (1.0 - vig[..., None])
    fx = np.clip(np.minimum(xx, CW - 1 - xx) / 36.0, 0, 1)
    fy = np.clip(np.minimum(yy, CH - 1 - yy) / 28.0, 0, 1)
    edge = np.minimum(fx, fy)
    arr = arr * edge[..., None] + NAVY * (1.0 - edge[..., None])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def tracked(draw, text, x, y, fnt, fill, tracking):
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textbbox((0, 0), ch, font=fnt)[2] + tracking


def draw_type(img: Image.Image, spec: dict) -> Image.Image:
    rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")
    x, y = 56, 86
    tracked(d, spec["kicker"], x, y, FONT_KICK, (*MUTED, 210), 3.2)
    tracked(d, spec["title"], x, y + 36, FONT_TITLE, (*IVORY, 250), 4.5)
    d.text((x, y + 92), spec["line"], font=FONT_LINE, fill=(*SUB, 220))
    d.text((x, CH - 78), spec["foot"], font=FONT_FOOT, fill=(*MUTED, 200))
    return Image.alpha_composite(rgba, overlay).convert("RGB")


def round_mask(radius: int = 22) -> Image.Image:
    m = Image.new("L", (CW, CH), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=radius, fill=255)
    return m.filter(ImageFilter.GaussianBlur(0.4))


def main() -> None:
    src = Image.open(BASE).convert("RGB")
    mask = round_mask()
    for spec in PROJECTS:
        plate = plate_from(crop_frac(src, *spec["crop"]))
        card = draw_type(plate, spec).convert("RGBA")
        card.putalpha(mask)
        path = OUT / f"{spec['slug']}.png"
        card.save(path, "PNG")
        print("wrote", path.name)


if __name__ == "__main__":
    main()
