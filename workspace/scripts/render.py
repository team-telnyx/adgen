#!/usr/bin/env python3
"""AdGen render engine. JSON via stdin → PNG out."""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO,
    stream=sys.stderr,
)
log = logging.getLogger("render")
logging.Formatter.converter = time.gmtime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WORKSPACE = Path(__file__).resolve().parent.parent  # workspace/
LOGO_DIR = WORKSPACE / "brand" / "logos"

FORMATS = {
    "linkedin_1200x1200": (1200, 1200),
    "linkedin_carousel": (1080, 1080),
    "google_rectangle": (300, 250),
    "google_leaderboard": (728, 90),
    "google_skyscraper": (160, 600),
    "reddit_feed": (1080, 1350),
    "twitter_single": (1200, 675),
    "meta_feed": (1080, 1080),
    "meta_stories": (1080, 1920),
}

DARK_TEMPLATES = {"dark-hero-left", "full-bleed-dark", "stats-hero", "gradient-accent", "testimonial"}
LIGHT_TEMPLATES = {"light-minimal", "split-panel", "product-screenshot"}

# ---------------------------------------------------------------------------
# Font helper
# ---------------------------------------------------------------------------
_font_cache: dict[tuple[int, bool], ImageFont.FreeTypeFont] = {}

FONT_PATHS = [
    "/usr/share/fonts/truetype/inter/Inter-Regular.ttf",
    "/usr/share/fonts/truetype/inter/Inter-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def _find_font(bold: bool = False) -> str | None:
    tag = "Bold" if bold else ""
    for p in FONT_PATHS:
        if tag in p and os.path.isfile(p):
            return p
    for p in FONT_PATHS:
        if os.path.isfile(p):
            return p
    return None

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    path = _find_font(bold)
    if path:
        font = ImageFont.truetype(path, size)
    else:
        font = ImageFont.load_default()
    _font_cache[key] = font
    return font

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def is_dark_bg(bg: str) -> bool:
    r, g, b = hex_to_rgb(bg)
    return (r * 0.299 + g * 0.587 + b * 0.114) < 128

def load_hero(path_str: str | None) -> Image.Image | None:
    if not path_str:
        return None
    p = WORKSPACE / path_str
    if not p.is_file():
        p = Path(path_str)
    if not p.is_file():
        log.warning("hero image not found path=%s", path_str)
        return None
    img = Image.open(p).convert("RGBA")
    log.info("hero image loaded path=%s size=%dx%d", path_str, img.width, img.height)
    return img

def fit_image(img: Image.Image, w: int, h: int) -> Image.Image:
    """Resize + center-crop to fill w×h."""
    scale = max(w / img.width, h / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return img.crop((left, top, left + w, top + h))

def composite_logo(canvas: Image.Image, variant: str, bg: str, pos: str, w: int, h: int) -> None:
    """Composite logo onto canvas."""
    if variant == "auto":
        variant = "wordmark-cream" if is_dark_bg(bg) else "wordmark-black"
    logo_path = LOGO_DIR / f"{variant}.png"
    if not logo_path.is_file():
        log.warning("logo not found variant=%s", variant)
        return
    logo = Image.open(logo_path).convert("RGBA")
    max_w = int(w * 0.20)
    max_h = 48
    logo.thumbnail((max_w, max_h), Image.LANCZOS)
    pad = 48
    positions = {
        "bottom-left": (pad, h - logo.height - pad),
        "upper-left": (pad, pad),
        "bottom-right": (w - logo.width - pad, h - logo.height - pad),
        "upper-right": (w - logo.width - pad, pad),
    }
    x, y = positions.get(pos, positions["bottom-left"])
    canvas.paste(logo, (x, y), logo)
    log.info("logo composited variant=%s pos=%d,%d", variant, x, y)

def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = f"{cur} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]

def draw_text_block(draw, text, font, x, y, max_w, color, line_spacing=1.3):
    lines = wrap_text(draw, text, font, max_w)
    cy = y
    for line in lines:
        draw.text((x, cy), line, font=font, fill=color)
        bbox = draw.textbbox((0, 0), line, font=font)
        cy += int((bbox[3] - bbox[1]) * line_spacing)
    return cy

def draw_pill_button(draw, text, font, x, y, accent, text_color):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px, py = 32, 14
    r = (th + py * 2) // 2
    x1, y1 = x, y
    x2, y2 = x + tw + px * 2, y + th + py * 2
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=accent)
    draw.text((x1 + px, y1 + py), text, font=font, fill=text_color)
    log.info("cta rendered text=\"%s\" pos=%d,%d", text, x1, y1)

# ---------------------------------------------------------------------------
# Template renderers
# ---------------------------------------------------------------------------
def _colors(data):
    bg = data.get("background", "#000000")
    accent = data.get("accent_color", "#D4E510")
    dark = is_dark_bg(bg)
    fg = "#F5F0E8" if dark else "#000000"
    sub_fg = (245, 240, 232, 180) if dark else (0, 0, 0, 140)
    return bg, accent, dark, fg, sub_fg

def _scale(base: int, w: int, h: int) -> int:
    ref = min(w, h)
    return max(14, int(base * ref / 1200))

def render_dark_hero_left(canvas, draw, data, w, h):
    bg, accent, dark, fg, sub_fg = _colors(data)
    hero = load_hero(data.get("hero_image"))
    hero_w = int(w * 0.55)
    if hero:
        fitted = fit_image(hero, hero_w, h)
        canvas.paste(fitted, (0, 0), fitted if fitted.mode == "RGBA" else None)
        log.info("hero placed zone=0,0,%d,%d", hero_w, h)
    tx = int(w * 0.60)
    tw = int(w * 0.35)
    hl_size = _scale(52, w, h)
    sh_size = _scale(26, w, h)
    cta_size = _scale(22, w, h)
    y = int(h * 0.20)
    y = draw_text_block(draw, data["headline"], load_font(hl_size, True), tx, y, tw, fg)
    if data.get("subhead"):
        y = draw_text_block(draw, data["subhead"], load_font(sh_size), tx, y + 20, tw, sub_fg)
    if data.get("cta"):
        draw_pill_button(draw, data["cta"], load_font(cta_size, True), tx, int(h * 0.75), hex_to_rgb(accent), hex_to_rgb(bg))

def render_light_minimal(canvas, draw, data, w, h):
    bg, accent, dark, fg, sub_fg = _colors(data)
    hl_size = _scale(48, w, h)
    sh_size = _scale(24, w, h)
    cta_size = _scale(20, w, h)
    tw = int(w * 0.70)
    tx = (w - tw) // 2
    y = int(h * 0.30)
    y = draw_text_block(draw, data["headline"], load_font(hl_size, True), tx, y, tw, fg)
    if data.get("subhead"):
        y = draw_text_block(draw, data["subhead"], load_font(sh_size), tx, y + 16, tw, sub_fg)
    if data.get("cta"):
        draw_pill_button(draw, data["cta"], load_font(cta_size, True), tx, y + 40, hex_to_rgb(accent), hex_to_rgb(bg))
    hero = load_hero(data.get("hero_image"))
    if hero:
        ih = int(h * 0.20)
        iw = int(w * 0.40)
        fitted = fit_image(hero, iw, ih)
        canvas.paste(fitted, ((w - iw) // 2, h - ih - 80), fitted if fitted.mode == "RGBA" else None)
        log.info("hero placed zone=%d,%d,%d,%d", (w-iw)//2, h-ih-80, iw, ih)

def render_split_panel(canvas, draw, data, w, h):
    bg, accent, dark, fg, sub_fg = _colors(data)
    half = w // 2
    hero = load_hero(data.get("hero_image"))
    if hero:
        fitted = fit_image(hero, half, h)
        canvas.paste(fitted, (0, 0), fitted if fitted.mode == "RGBA" else None)
        log.info("hero placed zone=0,0,%d,%d", half, h)
    tx = half + int(w * 0.05)
    tw = int(w * 0.40)
    hl_size = _scale(44, w, h)
    sh_size = _scale(22, w, h)
    cta_size = _scale(20, w, h)
    y = int(h * 0.25)
    y = draw_text_block(draw, data["headline"], load_font(hl_size, True), tx, y, tw, fg)
    if data.get("subhead"):
        y = draw_text_block(draw, data["subhead"], load_font(sh_size), tx, y + 16, tw, sub_fg)
    if data.get("cta"):
        draw_pill_button(draw, data["cta"], load_font(cta_size, True), tx, y + 32, hex_to_rgb(accent), hex_to_rgb(bg))

def render_full_bleed_dark(canvas, draw, data, w, h):
    bg, accent, dark, fg, sub_fg = _colors(data)
    hero = load_hero(data.get("hero_image"))
    if hero:
        fitted = fit_image(hero, w, h)
        canvas.paste(fitted, (0, 0), fitted if fitted.mode == "RGBA" else None)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 160))
        canvas.paste(Image.alpha_composite(Image.new("RGBA", (w, h), (0,0,0,0)), overlay), (0,0), overlay)
        log.info("hero placed zone=0,0,%d,%d with dark overlay", w, h)
    tx = int(w * 0.10)
    tw = int(w * 0.80)
    hl_size = _scale(56, w, h)
    sh_size = _scale(26, w, h)
    cta_size = _scale(22, w, h)
    y = int(h * 0.30)
    y = draw_text_block(draw, data["headline"], load_font(hl_size, True), tx, y, tw, "#FFFFFF")
    if data.get("subhead"):
        y = draw_text_block(draw, data["subhead"], load_font(sh_size), tx, y + 20, tw, (255,255,255,180))
    if data.get("cta"):
        draw_pill_button(draw, data["cta"], load_font(cta_size, True), tx, y + 40, hex_to_rgb(accent), (0,0,0))

def render_stats_hero(canvas, draw, data, w, h):
    bg, accent, dark, fg, sub_fg = _colors(data)
    headline = data["headline"]
    sh_size = _scale(22, w, h)
    cta_size = _scale(20, w, h)
    tw = int(w * 0.80)
    tx = (w - tw) // 2
    # Auto-size stat text to fit within 80% canvas width
    stat_size = _scale(120, w, h)
    while stat_size > 24:
        stat_font = load_font(stat_size, True)
        bbox = draw.textbbox((0, 0), headline, font=stat_font)
        if bbox[2] - bbox[0] <= tw:
            break
        stat_size -= 4
    stat_font = load_font(stat_size, True)
    bbox = draw.textbbox((0, 0), headline, font=stat_font)
    sw = bbox[2] - bbox[0]
    draw.text(((w - sw) // 2, int(h * 0.18)), headline, font=stat_font, fill=hex_to_rgb(accent))
    log.info("stat rendered text=\"%s\" size=%d pos=center,%d", headline, stat_size, int(h*0.18))
    y = int(h * 0.55)
    if data.get("subhead"):
        y = draw_text_block(draw, data["subhead"], load_font(sh_size), tx, y, tw, sub_fg)
    if data.get("cta"):
        draw_pill_button(draw, data["cta"], load_font(cta_size, True), tx, y + 32, hex_to_rgb(accent), hex_to_rgb(bg))

def render_gradient_accent(canvas, draw, data, w, h):
    bg, accent, dark, fg, sub_fg = _colors(data)
    # Draw gradient from bg to accent
    bg_rgb = hex_to_rgb(bg)
    ac_rgb = hex_to_rgb(accent)
    for row in range(h):
        t = row / max(h - 1, 1)
        r = int(bg_rgb[0] + (ac_rgb[0] - bg_rgb[0]) * t * 0.4)
        g = int(bg_rgb[1] + (ac_rgb[1] - bg_rgb[1]) * t * 0.4)
        b = int(bg_rgb[2] + (ac_rgb[2] - bg_rgb[2]) * t * 0.4)
        draw.line([(0, row), (w, row)], fill=(r, g, b))
    log.info("gradient rendered bg=%s accent=%s", bg, accent)
    tw = int(w * 0.70)
    tx = (w - tw) // 2
    hl_size = _scale(50, w, h)
    sh_size = _scale(24, w, h)
    cta_size = _scale(20, w, h)
    y = int(h * 0.28)
    y = draw_text_block(draw, data["headline"], load_font(hl_size, True), tx, y, tw, fg)
    if data.get("subhead"):
        y = draw_text_block(draw, data["subhead"], load_font(sh_size), tx, y + 16, tw, sub_fg)
    if data.get("cta"):
        draw_pill_button(draw, data["cta"], load_font(cta_size, True), tx, y + 40, hex_to_rgb(accent), hex_to_rgb(bg))

def render_testimonial(canvas, draw, data, w, h):
    bg, accent, dark, fg, sub_fg = _colors(data)
    tw = int(w * 0.75)
    tx = (w - tw) // 2
    # Big opening quote mark
    q_size = _scale(140, w, h)
    draw.text((tx - 10, int(h * 0.08)), "\u201C", font=load_font(q_size, True), fill=hex_to_rgb(accent))
    hl_size = _scale(38, w, h)
    sh_size = _scale(22, w, h)
    y = int(h * 0.28)
    y = draw_text_block(draw, data["headline"], load_font(hl_size, False), tx, y, tw, fg)
    if data.get("subhead"):
        draw.text((tx, y + 30), f"— {data['subhead']}", font=load_font(sh_size, True), fill=sub_fg)
        log.info("attribution rendered text=\"%s\"", data["subhead"])

def render_product_screenshot(canvas, draw, data, w, h):
    bg, accent, dark, fg, sub_fg = _colors(data)
    hero = load_hero(data.get("hero_image"))
    hl_size = _scale(40, w, h)
    sh_size = _scale(20, w, h)
    tw = int(w * 0.80)
    tx = (w - tw) // 2
    y = int(h * 0.06)
    y = draw_text_block(draw, data["headline"], load_font(hl_size, True), tx, y, tw, fg)
    if data.get("subhead"):
        y = draw_text_block(draw, data["subhead"], load_font(sh_size), tx, y + 12, tw, sub_fg)
    if hero:
        iw = int(w * 0.85)
        ih = int(h * 0.55)
        fitted = fit_image(hero, iw, ih)
        # Drop shadow
        shadow = Image.new("RGBA", (iw + 16, ih + 16), (0, 0, 0, 60))
        sx, sy = (w - iw) // 2 + 4, int(h * 0.38) + 4
        canvas.paste(shadow, (sx, sy), shadow)
        canvas.paste(fitted, ((w - iw) // 2, int(h * 0.38)), fitted if fitted.mode == "RGBA" else None)
        log.info("hero placed zone=%d,%d,%d,%d", (w-iw)//2, int(h*0.38), iw, ih)

TEMPLATE_RENDERERS = {
    "dark-hero-left": render_dark_hero_left,
    "light-minimal": render_light_minimal,
    "split-panel": render_split_panel,
    "full-bleed-dark": render_full_bleed_dark,
    "stats-hero": render_stats_hero,
    "gradient-accent": render_gradient_accent,
    "testimonial": render_testimonial,
    "product-screenshot": render_product_screenshot,
}

# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------
def render(data: dict) -> None:
    t0 = time.time()
    template = data.get("template", "dark-hero-left")
    fmt = data.get("format", "linkedin_1200x1200")
    bg = data.get("background", "#000000")
    output = data.get("output", "output/render.png")

    log.info("render started template=%s format=%s", template, fmt)

    if fmt not in FORMATS:
        raise ValueError(f"Unknown format: {fmt}")
    w, h = FORMATS[fmt]

    canvas = Image.new("RGBA", (w, h), hex_to_rgb(bg))
    log.info("canvas created size=%dx%d bg=%s", w, h, bg)
    draw = ImageDraw.Draw(canvas)

    renderer = TEMPLATE_RENDERERS.get(template)
    if not renderer:
        raise ValueError(f"Unknown template: {template}")
    renderer(canvas, draw, data, w, h)

    logo_variant = data.get("logo_variant", "auto")
    logo_pos = data.get("logo_position", "bottom-left")
    composite_logo(canvas, logo_variant, bg, logo_pos, w, h)

    out_path = Path(output)
    if not out_path.is_absolute():
        out_path = WORKSPACE / output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(str(out_path), "PNG")
    size_kb = out_path.stat().st_size / 1024
    elapsed = time.time() - t0
    log.info("render complete output=%s size=%.0fKB elapsed=%.1fs", out_path, size_kb, elapsed)

def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log.error("invalid JSON input: %s", e)
        sys.exit(1)
    try:
        render(data)
    except Exception as e:
        log.error("render failed: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
