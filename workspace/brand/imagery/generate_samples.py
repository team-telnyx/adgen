#!/usr/bin/env python3
"""Generate placeholder sample imagery for AdGen brand library.

Produces:
  - product/portal-dashboard.png      — Mock portal UI
  - product/api-docs-screen.png       — Mock API documentation
  - abstract/network-pattern-dark.png  — Geometric network pattern
  - abstract/gradient-green.png        — Green gradient with shapes
  - photography/data-center-01.png     — Placeholder datacenter visual

All images are 2400×2400px minimum. Generated with Pillow.
These are placeholders for testing render.py compositing.
"""

import logging
import math
import os
import random
import sys
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("generate_samples")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Brand colors
BLACK = (0, 0, 0)
CREAM = (245, 240, 232)
GREEN = (0, 194, 110)
CITRON = (212, 229, 16)
PINK = (255, 107, 157)
DARK_GRAY = (26, 26, 26)
MID_GRAY = (102, 102, 102)

SIZE = 2400


def get_font(size: int):
    """Get available font."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_bold_font(size: int):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def generate_portal_dashboard(output_dir: str) -> str:
    """Mock portal dashboard — dark UI with colored panels."""
    filepath = os.path.join(output_dir, "portal-dashboard.png")
    log.info(f"generating product imagery=portal-dashboard size={SIZE}x{SIZE}")

    img = Image.new("RGB", (SIZE, SIZE), DARK_GRAY)
    draw = ImageDraw.Draw(img)

    # Top nav bar
    draw.rectangle([0, 0, SIZE, 80], fill=(15, 15, 15))
    font_sm = get_font(28)
    draw.text((40, 25), "Mission Control", fill=CREAM, font=font_sm)

    # Sidebar
    draw.rectangle([0, 80, 300, SIZE], fill=(20, 20, 20))
    menu_items = ["Dashboard", "Numbers", "Messaging", "Voice", "Storage", "Billing"]
    for i, item in enumerate(menu_items):
        y = 120 + i * 60
        if i == 0:
            draw.rectangle([0, y - 5, 300, y + 45], fill=(40, 40, 40))
            draw.rectangle([0, y - 5, 4, y + 45], fill=GREEN)
        draw.text((40, y), item, fill=CREAM if i == 0 else MID_GRAY, font=font_sm)

    # Main content area — metric cards
    card_data = [
        ("Active Numbers", "1,247", GREEN),
        ("Messages Today", "45.2K", CITRON),
        ("Voice Minutes", "12.8K", PINK),
        ("API Calls", "2.1M", GREEN),
    ]
    card_w = 440
    card_h = 200
    start_x = 380
    for i, (label, value, color) in enumerate(card_data):
        x = start_x + (i % 2) * (card_w + 40)
        y = 140 + (i // 2) * (card_h + 40)
        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=12, fill=(30, 30, 30))
        draw.rectangle([x, y, x + 4, y + card_h], fill=color)
        font_label = get_font(22)
        font_val = get_bold_font(48)
        draw.text((x + 30, y + 30), label, fill=MID_GRAY, font=font_label)
        draw.text((x + 30, y + 80), value, fill=CREAM, font=font_val)

    # Chart area
    chart_y = 520
    draw.rounded_rectangle([380, chart_y, SIZE - 80, chart_y + 600], radius=12, fill=(30, 30, 30))
    draw.text((420, chart_y + 20), "API Traffic — Last 7 Days", fill=CREAM, font=get_font(26))

    # Fake bar chart
    random.seed(42)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    max_bar_h = 400
    bar_w = 180
    for i, day in enumerate(days):
        bar_h = random.randint(150, max_bar_h)
        bx = 420 + i * (bar_w + 30)
        by = chart_y + 500 - bar_h
        draw.rounded_rectangle([bx, by, bx + bar_w, chart_y + 500], radius=6, fill=GREEN)
        draw.text((bx + 60, chart_y + 520), day, fill=MID_GRAY, font=get_font(20))

    # Bottom table
    table_y = 1200
    draw.rounded_rectangle([380, table_y, SIZE - 80, SIZE - 80], radius=12, fill=(30, 30, 30))
    draw.text((420, table_y + 20), "Recent Activity", fill=CREAM, font=get_font(26))
    headers = ["Event", "Status", "Time", "Details"]
    for i, h in enumerate(headers):
        draw.text((420 + i * 450, table_y + 80), h, fill=MID_GRAY, font=get_font(20))
    draw.line([420, table_y + 110, SIZE - 120, table_y + 110], fill=(50, 50, 50), width=1)

    rows = [
        ("Number provisioned", "✓ Complete", "2m ago", "+1 (555) 012-3456"),
        ("Message sent", "✓ Delivered", "5m ago", "Campaign: Q2 Launch"),
        ("Voice call", "● Active", "8m ago", "Duration: 4:32"),
        ("Webhook fired", "✓ 200 OK", "12m ago", "POST /webhooks/sms"),
    ]
    for j, (evt, status, time, detail) in enumerate(rows):
        ry = table_y + 130 + j * 55
        draw.text((420, ry), evt, fill=CREAM, font=get_font(20))
        color = GREEN if "✓" in status else CITRON
        draw.text((870, ry), status, fill=color, font=get_font(20))
        draw.text((1320, ry), time, fill=MID_GRAY, font=get_font(20))
        draw.text((1770, ry), detail, fill=MID_GRAY, font=get_font(20))

    img.save(filepath, "PNG", quality=95)
    log.info(f"saved brand/imagery/product/portal-dashboard.png")
    return filepath


def generate_api_docs(output_dir: str) -> str:
    """Mock API documentation screen."""
    filepath = os.path.join(output_dir, "api-docs-screen.png")
    log.info(f"generating product imagery=api-docs-screen size={SIZE}x{SIZE}")

    img = Image.new("RGB", (SIZE, SIZE), (18, 18, 18))
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, SIZE, 100], fill=(12, 12, 12))
    draw.text((40, 30), "Telnyx API Reference", fill=CREAM, font=get_bold_font(36))

    # Sidebar — endpoint list
    draw.rectangle([0, 100, 400, SIZE], fill=(14, 14, 14))
    endpoints = [
        ("Messaging", ["Send Message", "List Messages", "Get Message"]),
        ("Voice", ["Create Call", "Hangup", "Transfer"]),
        ("Numbers", ["List Numbers", "Search", "Order"]),
    ]
    y = 140
    font_cat = get_bold_font(22)
    font_ep = get_font(18)
    for cat, items in endpoints:
        draw.text((30, y), cat, fill=GREEN, font=font_cat)
        y += 40
        for item in items:
            draw.text((50, y), item, fill=MID_GRAY, font=font_ep)
            y += 35
        y += 20

    # Main content — endpoint detail
    cx = 440
    cy = 140
    draw.text((cx, cy), "Send a Message", fill=CREAM, font=get_bold_font(40))
    cy += 70

    # Method badge
    draw.rounded_rectangle([cx, cy, cx + 80, cy + 36], radius=4, fill=GREEN)
    draw.text((cx + 10, cy + 6), "POST", fill=BLACK, font=get_bold_font(18))
    draw.text((cx + 100, cy + 6), "/v2/messages", fill=CREAM, font=get_font(22))
    cy += 70

    draw.text((cx, cy), "Send an SMS or MMS message.", fill=MID_GRAY, font=get_font(20))
    cy += 60

    # Code block
    code_lines = [
        'curl -X POST "https://api.telnyx.com/v2/messages" \\',
        '  -H "Authorization: Bearer YOUR_API_KEY" \\',
        '  -H "Content-Type: application/json" \\',
        '  -d \'{',
        '    "from": "+15551234567",',
        '    "to": "+15559876543",',
        '    "text": "Hello from Telnyx!"',
        "  }'",
    ]
    code_h = len(code_lines) * 35 + 40
    draw.rounded_rectangle([cx, cy, SIZE - 80, cy + code_h], radius=8, fill=(25, 25, 25))
    code_font = get_font(18)
    for i, line in enumerate(code_lines):
        draw.text((cx + 20, cy + 20 + i * 35), line, fill=CITRON, font=code_font)
    cy += code_h + 40

    # Response
    draw.text((cx, cy), "Response — 200 OK", fill=CREAM, font=get_bold_font(24))
    cy += 50
    resp_lines = [
        "{",
        '  "data": {',
        '    "record_type": "message",',
        '    "id": "msg_abc123",',
        '    "type": "SMS",',
        '    "direction": "outbound",',
        '    "messaging_profile_id": "prof_456"',
        "  }",
        "}",
    ]
    resp_h = len(resp_lines) * 32 + 40
    draw.rounded_rectangle([cx, cy, SIZE - 80, cy + resp_h], radius=8, fill=(25, 25, 25))
    for i, line in enumerate(resp_lines):
        draw.text((cx + 20, cy + 20 + i * 32), line, fill=GREEN, font=code_font)

    img.save(filepath, "PNG", quality=95)
    log.info(f"saved brand/imagery/product/api-docs-screen.png")
    return filepath


def generate_network_pattern(output_dir: str) -> str:
    """Dark geometric network pattern with nodes and connections."""
    filepath = os.path.join(output_dir, "network-pattern-dark.png")
    log.info(f"generating abstract imagery=network-pattern-dark size={SIZE}x{SIZE}")

    img = Image.new("RGB", (SIZE, SIZE), BLACK)
    draw = ImageDraw.Draw(img)

    random.seed(7)
    nodes = [(random.randint(100, SIZE - 100), random.randint(100, SIZE - 100)) for _ in range(60)]

    # Draw connections
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if i >= j:
                continue
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if dist < 500:
                alpha = max(20, int(255 * (1 - dist / 500)))
                line_color = (0, int(194 * alpha / 255), int(110 * alpha / 255))
                draw.line([(x1, y1), (x2, y2)], fill=line_color, width=1)

    # Draw nodes
    for x, y in nodes:
        r = random.choice([4, 6, 8, 12])
        node_color = random.choice([GREEN, CITRON, (100, 100, 100)])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=node_color)

    # Add subtle glow around larger nodes
    for x, y in nodes[:15]:
        for gr in range(30, 5, -5):
            c = int(20 * (gr / 30))
            draw.ellipse([x - gr, y - gr, x + gr, y + gr], outline=(0, c, int(c * 0.6)))

    img.save(filepath, "PNG", quality=95)
    log.info(f"saved brand/imagery/abstract/network-pattern-dark.png")
    return filepath


def generate_gradient_green(output_dir: str) -> str:
    """Green gradient with geometric overlay."""
    filepath = os.path.join(output_dir, "gradient-green.png")
    log.info(f"generating abstract imagery=gradient-green size={SIZE}x{SIZE}")

    img = Image.new("RGB", (SIZE, SIZE), BLACK)
    draw = ImageDraw.Draw(img)

    # Diagonal gradient from black to green
    for y in range(SIZE):
        for x in range(0, SIZE, 4):  # Step by 4 for performance
            t = (x + y) / (SIZE * 2)
            r = int(0 * (1 - t))
            g = int(194 * t * 0.6)
            b = int(110 * t * 0.4)
            draw.rectangle([x, y, x + 3, y], fill=(r, g, b))

    # Geometric overlay — concentric hexagon outlines
    cx, cy = SIZE // 2, SIZE // 2
    for radius in range(200, 1400, 150):
        points = []
        for angle in range(6):
            a = math.radians(60 * angle - 30)
            px = cx + int(radius * math.cos(a))
            py = cy + int(radius * math.sin(a))
            points.append((px, py))
        points.append(points[0])
        alpha = max(30, int(80 * (1 - radius / 1400)))
        draw.line(points, fill=(212, 229, 16, alpha), width=2)

    img.save(filepath, "PNG", quality=95)
    log.info(f"saved brand/imagery/abstract/gradient-green.png")
    return filepath


def generate_datacenter(output_dir: str) -> str:
    """Placeholder datacenter visual — abstract server rack representation."""
    filepath = os.path.join(output_dir, "data-center-01.png")
    log.info(f"generating photography imagery=data-center-01 size={SIZE}x{SIZE}")

    img = Image.new("RGB", (SIZE, SIZE), (8, 8, 12))
    draw = ImageDraw.Draw(img)

    # Draw server rack columns
    rack_w = 280
    gap = 40
    racks_start_x = 200
    num_racks = 6

    for rack in range(num_racks):
        rx = racks_start_x + rack * (rack_w + gap)
        # Rack frame
        draw.rectangle([rx, 100, rx + rack_w, SIZE - 100], outline=(40, 40, 45), width=2)

        # Server units
        unit_h = 50
        for u in range(int((SIZE - 300) / (unit_h + 8))):
            uy = 120 + u * (unit_h + 8)
            # Server body
            draw.rounded_rectangle(
                [rx + 8, uy, rx + rack_w - 8, uy + unit_h],
                radius=3,
                fill=(20, 20, 25),
            )
            # LED indicators
            random.seed(rack * 100 + u)
            num_leds = random.randint(2, 5)
            for led in range(num_leds):
                lx = rx + 20 + led * 18
                ly = uy + 10
                led_color = random.choice([GREEN, GREEN, GREEN, CITRON, (60, 60, 60)])
                draw.ellipse([lx, ly, lx + 6, ly + 6], fill=led_color)

            # Drive bays
            num_bays = random.randint(4, 8)
            for bay in range(num_bays):
                bx = rx + rack_w - 20 - bay * 22
                draw.rectangle([bx, uy + 20, bx + 16, uy + unit_h - 8], outline=(45, 45, 50))

    # Floor reflection
    for y in range(SIZE - 100, SIZE):
        alpha = int(30 * (1 - (y - (SIZE - 100)) / 100))
        draw.rectangle([0, y, SIZE, y + 1], fill=(0, alpha // 3, alpha // 5))

    # Ambient blue-green light wash
    for y in range(0, SIZE, 2):
        for x in range(0, SIZE, 60):
            dist_center = abs(x - SIZE // 2) / (SIZE // 2)
            if random.random() > 0.97:
                glow = int(15 * (1 - dist_center))
                draw.rectangle([x, y, x + 50, y + 1], fill=(0, glow, int(glow * 0.7)))

    img.save(filepath, "PNG", quality=95)
    log.info(f"saved brand/imagery/photography/data-center-01.png")
    return filepath


def main():
    product_dir = os.path.join(SCRIPT_DIR, "product")
    abstract_dir = os.path.join(SCRIPT_DIR, "abstract")
    photo_dir = os.path.join(SCRIPT_DIR, "photography")

    os.makedirs(product_dir, exist_ok=True)
    os.makedirs(abstract_dir, exist_ok=True)
    os.makedirs(photo_dir, exist_ok=True)

    log.info("starting sample imagery generation")

    generate_portal_dashboard(product_dir)
    generate_api_docs(product_dir)
    generate_network_pattern(abstract_dir)
    generate_gradient_green(abstract_dir)
    generate_datacenter(photo_dir)

    log.info("sample imagery generation complete — 5 images created")
    return 0


if __name__ == "__main__":
    sys.exit(main())
