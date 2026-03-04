#!/usr/bin/env python3
"""Generate placeholder Telnyx logo PNGs for AdGen brand assets.

Produces 4 logo variants:
  - wordmark-cream.png  — "TELNYX" in cream (#F5F0E8) on transparent
  - wordmark-black.png  — "TELNYX" in black (#000000) on transparent
  - icon-cream.png      — "T" icon in cream on transparent
  - icon-black.png      — "T" icon in black on transparent

These are placeholders. Marketing will replace with real assets.
"""

import logging
import os
import sys
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("generate_logos")

# Brand colors
CREAM = "#F5F0E8"
BLACK = "#000000"

# Output directory (relative to this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGOS_DIR = os.path.join(SCRIPT_DIR, "logos")


def hex_to_rgba(hex_color: str) -> tuple:
    """Convert hex color to RGBA tuple."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)) + (255,)


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Get a bold font, falling back through available options."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    log.warning("No system font found, using default bitmap font")
    return ImageFont.load_default()


def generate_wordmark(color_name: str, color_hex: str) -> str:
    """Generate a wordmark logo: 'TELNYX' text on transparent background."""
    width, height = 800, 200
    filename = f"wordmark-{color_name}.png"
    filepath = os.path.join(LOGOS_DIR, filename)

    log.info(f"generating logo variant=wordmark-{color_name} size={width}x{height}")

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = get_font(120)
    text = "TELNYX"
    color = hex_to_rgba(color_hex)

    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (width - text_w) // 2
    y = (height - text_h) // 2 - bbox[1]

    draw.text((x, y), text, fill=color, font=font)
    img.save(filepath, "PNG")
    log.info(f"saved {os.path.relpath(filepath, SCRIPT_DIR)}")
    return filepath


def generate_icon(color_name: str, color_hex: str) -> str:
    """Generate an icon logo: bold 'T' on transparent background."""
    size = 200
    filename = f"icon-{color_name}.png"
    filepath = os.path.join(LOGOS_DIR, filename)

    log.info(f"generating logo variant=icon-{color_name} size={size}x{size}")

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = get_font(140)
    text = "T"
    color = hex_to_rgba(color_hex)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2
    y = (size - text_h) // 2 - bbox[1]

    draw.text((x, y), text, fill=color, font=font)
    img.save(filepath, "PNG")
    log.info(f"saved {os.path.relpath(filepath, SCRIPT_DIR)}")
    return filepath


def main():
    os.makedirs(LOGOS_DIR, exist_ok=True)
    log.info("starting logo generation")

    variants = [
        ("wordmark", "cream", CREAM),
        ("wordmark", "black", BLACK),
        ("icon", "cream", CREAM),
        ("icon", "black", BLACK),
    ]

    generated = []
    for kind, color_name, color_hex in variants:
        if kind == "wordmark":
            path = generate_wordmark(color_name, color_hex)
        else:
            path = generate_icon(color_name, color_hex)
        generated.append(path)

    log.info(f"logo generation complete — {len(generated)} variants created")
    return 0


if __name__ == "__main__":
    sys.exit(main())
