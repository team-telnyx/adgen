#!/usr/bin/env python3
"""Tests for render.py — renders all templates, formats, and edge cases."""

import json
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "render.py"
WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUT_DIR = WORKSPACE / "output" / "test"

TEMPLATES = [
    "dark-hero-left", "light-minimal", "split-panel", "full-bleed-dark",
    "stats-hero", "gradient-accent", "testimonial", "product-screenshot",
]

FORMATS_SAMPLE = ["linkedin_1200x1200", "google_rectangle", "meta_stories"]

BASE_BRIEF = {
    "headline": "Cut Patient Wait Times 40%",
    "subhead": "AI-native voice infrastructure",
    "cta": "Talk to Sales",
    "accent_color": "#D4E510",
    "background": "#000000",
    "logo_variant": "auto",
}

def is_valid_png(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            header = f.read(8)
            return header[:4] == b"\x89PNG"
    except Exception:
        return False

def run_render(data: dict) -> int:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(f"  STDERR: {proc.stderr.strip()}", file=sys.stderr)
    return proc.returncode

def test_all_templates():
    print("=== Test: one ad per template (8 total) ===")
    passed = 0
    for tmpl in TEMPLATES:
        out = str(OUTPUT_DIR / f"tmpl_{tmpl}.png")
        data = {**BASE_BRIEF, "template": tmpl, "format": "linkedin_1200x1200", "output": out}
        if tmpl in ("light-minimal", "split-panel", "product-screenshot"):
            data["background"] = "#F5F0E8"
        rc = run_render(data)
        ok = rc == 0 and is_valid_png(out)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {tmpl}")
        if ok:
            passed += 1
    print(f"  {passed}/{len(TEMPLATES)} passed\n")
    return passed == len(TEMPLATES)

def test_multi_format():
    print("=== Test: same brief in 3 formats ===")
    passed = 0
    for fmt in FORMATS_SAMPLE:
        out = str(OUTPUT_DIR / f"fmt_{fmt}.png")
        data = {**BASE_BRIEF, "template": "dark-hero-left", "format": fmt, "output": out}
        rc = run_render(data)
        ok = rc == 0 and is_valid_png(out)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {fmt}")
        if ok:
            passed += 1
    print(f"  {passed}/{len(FORMATS_SAMPLE)} passed\n")
    return passed == len(FORMATS_SAMPLE)

def test_missing_hero():
    print("=== Test: missing hero_image ===")
    out = str(OUTPUT_DIR / "no_hero.png")
    data = {**BASE_BRIEF, "template": "dark-hero-left", "format": "linkedin_1200x1200", "output": out}
    data["hero_image"] = "nonexistent/image.png"
    rc = run_render(data)
    ok = rc == 0 and is_valid_png(out)
    print(f"  [{'PASS' if ok else 'FAIL'}] renders without hero image\n")
    return ok

def test_missing_optional_fields():
    print("=== Test: missing optional fields ===")
    passed = 0
    for label, overrides in [
        ("no subhead", {"subhead": None}),
        ("no cta", {"cta": None}),
        ("no subhead+cta", {"subhead": None, "cta": None}),
    ]:
        out = str(OUTPUT_DIR / f"opt_{label.replace(' ', '_')}.png")
        data = {**BASE_BRIEF, "template": "dark-hero-left", "format": "linkedin_1200x1200", "output": out}
        for k, v in overrides.items():
            if v is None:
                data.pop(k, None)
            else:
                data[k] = v
        rc = run_render(data)
        ok = rc == 0 and is_valid_png(out)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label}")
        if ok:
            passed += 1
    print(f"  {passed}/3 passed\n")
    return passed == 3

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = [
        test_all_templates(),
        test_multi_format(),
        test_missing_hero(),
        test_missing_optional_fields(),
    ]
    total = sum(results)
    print(f"=== SUMMARY: {total}/{len(results)} test groups passed ===")
    sys.exit(0 if all(results) else 1)

if __name__ == "__main__":
    main()
