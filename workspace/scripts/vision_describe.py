#!/usr/bin/env python3
"""Batch vision-describe assets using OpenAI GPT-4o.

Reads catalog.json, sends each image to GPT-4o vision API for a concise
description, and stores it under the `vision_description` field.

Usage:
    python vision_describe.py                     # process all, skip already-described
    python vision_describe.py --resume             # same as default (skip described)
    python vision_describe.py --limit 50           # process up to 50 images
    python vision_describe.py --category _NEW_Clawhouse  # only one category
    python vision_describe.py --dry-run            # show what would be processed
"""

import argparse
import base64
import json
import logging
import os
import sys
import time
from pathlib import Path

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    stream=sys.stderr,
)
log = logging.getLogger("vision_describe")

WORKSPACE = Path(__file__).resolve().parent.parent
LIBRARY = WORKSPACE / "brand" / "library"
CATALOG_PATH = LIBRARY / "catalog.json"

VISION_PROMPT = (
    "Describe this image in 1-2 sentences for an ad creative library. "
    "Focus on: what's depicted, visual style (dark/light/colorful), mood, "
    "what type of ad it would work for. Be specific and concrete, not generic."
)

IMAGE_FORMATS = {"png", "jpg", "jpeg", "webp"}

# Process _NEW_ folders first, then high-value categories
CATEGORY_PRIORITY = [
    "_NEW_",
    "Product_Visuals",
    "Industry_Visuals",
    "Homepage_Visuals",
    "Use_Case_Visuals",
    "Differentiators_Visuals",
    "Blog_Visuals",
]

SAVE_EVERY = 50
MAX_RETRIES = 5
BASE_DELAY = 2.0


def load_api_key() -> str:
    key_path = Path(os.path.expanduser("~/.secrets/openai"))
    if not key_path.exists():
        log.error("OpenAI API key not found at %s", key_path)
        sys.exit(1)
    return key_path.read_text().strip()


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text())


def save_catalog(catalog: dict):
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2))
    log.info("Saved catalog (%d entries)", len(catalog.get("entries", [])))


def category_sort_key(asset: dict) -> tuple:
    """Sort assets so _NEW_ folders come first, then priority categories."""
    path = asset["path"]
    for i, prefix in enumerate(CATEGORY_PRIORITY):
        if path.startswith(prefix):
            return (i, path)
    return (len(CATEGORY_PRIORITY), path)


def encode_image(file_path: Path) -> tuple[str, str]:
    """Read and base64-encode an image. Returns (base64_data, media_type)."""
    suffix = file_path.suffix.lower().lstrip(".")
    media_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }
    media_type = media_types.get(suffix, "image/png")

    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return data, media_type


def describe_image(file_path: Path, api_key: str) -> str:
    """Send image to GPT-4o vision API and get description."""
    import requests

    image_data, media_type = encode_image(file_path)

    # Limit image size — skip very large files (>20MB)
    raw_size = file_path.stat().st_size
    if raw_size > 20 * 1024 * 1024:
        log.warning("Skipping %s — too large (%d MB)", file_path.name, raw_size // (1024 * 1024))
        return ""

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": VISION_PROMPT},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{media_type};base64,{image_data}",
                                        "detail": "low",
                                    },
                                },
                            ],
                        }
                    ],
                    "max_tokens": 150,
                },
                timeout=60,
            )

            if resp.status_code == 429:
                delay = BASE_DELAY * (2 ** attempt)
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    delay = max(delay, float(retry_after))
                log.warning("Rate limited — waiting %.1fs (attempt %d/%d)", delay, attempt + 1, MAX_RETRIES)
                time.sleep(delay)
                continue

            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"].strip()

        except requests.exceptions.Timeout:
            delay = BASE_DELAY * (2 ** attempt)
            log.warning("Timeout — retrying in %.1fs (attempt %d/%d)", delay, attempt + 1, MAX_RETRIES)
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2 ** attempt)
                log.warning("Request error: %s — retrying in %.1fs", e, delay)
                time.sleep(delay)
            else:
                log.error("Failed after %d attempts: %s", MAX_RETRIES, e)
                return ""

    log.error("Exhausted retries for %s", file_path.name)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Vision-describe assets via GPT-4o")
    parser.add_argument("--resume", action="store_true", default=True,
                        help="Skip already-described assets (default: True)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max number of images to process")
    parser.add_argument("--category", type=str, default=None,
                        help="Only process assets in this category folder (prefix match)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be processed without making API calls")
    args = parser.parse_args()

    api_key = load_api_key()
    catalog = load_catalog()
    entries = catalog.get("entries", [])

    # Filter to processable image assets
    candidates = []
    for entry in entries:
        fmt = entry.get("format", "").lower()
        if fmt not in IMAGE_FORMATS:
            continue
        if args.resume and entry.get("vision_description"):
            continue
        if args.category:
            if not entry["path"].startswith(args.category):
                continue
        candidates.append(entry)

    # Sort by category priority
    candidates.sort(key=category_sort_key)

    if args.limit:
        candidates = candidates[:args.limit]

    total = len(candidates)
    already = sum(1 for e in entries if e.get("vision_description"))
    log.info("Catalog: %d entries, %d already described, %d to process", len(entries), already, total)

    if args.dry_run:
        for c in candidates:
            print(f"  Would process: {c['path']}")
        log.info("Dry run — %d images would be processed", total)
        return

    if total == 0:
        log.info("Nothing to process")
        return

    # Build index for quick lookup
    entry_index = {e["path"]: e for e in entries}
    processed = 0
    errors = 0
    t0 = time.monotonic()

    for i, candidate in enumerate(candidates):
        path = candidate["path"]
        file_path = LIBRARY / path

        if not file_path.exists():
            log.warning("File not found: %s — skipping", path)
            errors += 1
            continue

        log.info("[%d/%d] Describing: %s", i + 1, total, path)
        description = describe_image(file_path, api_key)

        if description:
            # Update the entry in the main entries list
            entry_index[path]["vision_description"] = description
            processed += 1
            log.info("  → %s", description[:100])
        else:
            log.warning("  → Empty description for %s", path)
            errors += 1

        # Save progress periodically
        if processed > 0 and processed % SAVE_EVERY == 0:
            save_catalog(catalog)
            elapsed = time.monotonic() - t0
            rate = processed / elapsed * 60
            log.info("Progress: %d/%d done (%.1f/min), %d errors", processed, total, rate, errors)

        # Small delay between requests to be respectful
        time.sleep(0.5)

    # Final save
    save_catalog(catalog)
    elapsed = time.monotonic() - t0
    log.info("=== Done ===")
    log.info("  Processed: %d/%d", processed, total)
    log.info("  Errors: %d", errors)
    log.info("  Time: %.1fs (%.1f images/min)", elapsed, processed / max(elapsed, 1) * 60)
    log.info("  Total with vision_description: %d/%d",
             sum(1 for e in entries if e.get("vision_description")), len(entries))


if __name__ == "__main__":
    main()
