#!/usr/bin/env python3
"""Generate embeddings for catalog assets via Telnyx AI API.

Uses `vision_description` (preferred) or `description` (fallback) as input.
Stores embedding vectors inline in catalog.json under the `embedding` field.

Usage:
    python embed_catalog.py              # process all, skip already-embedded
    python embed_catalog.py --resume     # same as default
    python embed_catalog.py --limit 100  # process up to 100 assets
    python embed_catalog.py --dry-run    # show what would be processed
"""

import argparse
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
log = logging.getLogger("embed_catalog")

WORKSPACE = Path(__file__).resolve().parent.parent
LIBRARY = WORKSPACE / "brand" / "library"
CATALOG_PATH = LIBRARY / "catalog.json"

EMBED_URL = "https://api.telnyx.com/v2/ai/openai/embeddings"
EMBED_MODEL = "thenlper/gte-large"
BATCH_SIZE = 10
SAVE_EVERY = 100
MAX_RETRIES = 5
BASE_DELAY = 2.0


def load_api_key() -> str:
    key_path = Path(os.path.expanduser("~/.secrets/telnyx"))
    if not key_path.exists():
        log.error("Telnyx API key not found at %s", key_path)
        sys.exit(1)
    return key_path.read_text().strip()


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text())


def save_catalog(catalog: dict):
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2))
    log.info("Saved catalog (%d entries)", len(catalog.get("entries", [])))


def get_description(entry: dict) -> str:
    """Get the best available description for embedding."""
    return entry.get("vision_description") or entry.get("description") or entry.get("path", "")


def generate_embeddings_batch(texts: list[str], api_key: str) -> list[list[float]]:
    """Generate embeddings for a batch of texts via Telnyx AI API."""
    import requests

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                EMBED_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": EMBED_MODEL,
                    "input": texts,
                },
                timeout=60,
            )

            if resp.status_code == 429:
                delay = BASE_DELAY * (2 ** attempt)
                log.warning("Rate limited — waiting %.1fs (attempt %d/%d)", delay, attempt + 1, MAX_RETRIES)
                time.sleep(delay)
                continue

            resp.raise_for_status()
            data = resp.json()

            # Handle both response formats
            if "data" in data:
                # OpenAI-compatible format
                embeddings = [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]
            elif "embeddings" in data:
                embeddings = data["embeddings"]
            else:
                log.error("Unexpected response format: %s", list(data.keys()))
                return []

            return embeddings

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
                return []

    return []


def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for catalog assets")
    parser.add_argument("--resume", action="store_true", default=True,
                        help="Skip already-embedded assets (default: True)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max number of assets to process")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be processed without making API calls")
    parser.add_argument("--force", action="store_true",
                        help="Re-embed even if embedding already exists")
    args = parser.parse_args()

    api_key = load_api_key()
    catalog = load_catalog()
    entries = catalog.get("entries", [])

    # Filter to assets needing embeddings
    candidates = []
    for entry in entries:
        if not args.force and args.resume and entry.get("embedding"):
            continue
        desc = get_description(entry)
        if not desc or len(desc.strip()) < 5:
            log.debug("Skipping %s — no usable description", entry.get("path", "?"))
            continue
        candidates.append(entry)

    if args.limit:
        candidates = candidates[:args.limit]

    total = len(candidates)
    already = sum(1 for e in entries if e.get("embedding"))
    with_vision = sum(1 for e in entries if e.get("vision_description"))
    log.info("Catalog: %d entries, %d with embeddings, %d with vision descriptions", len(entries), already, with_vision)
    log.info("To process: %d assets", total)

    if args.dry_run:
        for c in candidates[:20]:
            desc = get_description(c)
            src = "vision" if c.get("vision_description") else "path-desc"
            print(f"  [{src}] {c['path']}: {desc[:80]}")
        if total > 20:
            print(f"  ... and {total - 20} more")
        log.info("Dry run — %d assets would be embedded", total)
        return

    if total == 0:
        log.info("Nothing to process")
        return

    # Build index for quick lookup
    entry_index = {e["path"]: e for e in entries}
    processed = 0
    errors = 0
    t0 = time.monotonic()

    # Process in batches
    for batch_start in range(0, total, BATCH_SIZE):
        batch = candidates[batch_start:batch_start + BATCH_SIZE]
        texts = [get_description(c) for c in batch]

        log.info("[%d-%d/%d] Embedding batch of %d",
                 batch_start + 1, min(batch_start + len(batch), total), total, len(batch))

        embeddings = generate_embeddings_batch(texts, api_key)

        if not embeddings:
            log.error("Failed to generate embeddings for batch starting at %d", batch_start)
            errors += len(batch)
            continue

        if len(embeddings) != len(batch):
            log.error("Embedding count mismatch: got %d, expected %d", len(embeddings), len(batch))
            errors += len(batch)
            continue

        for entry, embedding in zip(batch, embeddings):
            entry_index[entry["path"]]["embedding"] = embedding
            processed += 1

        # Save progress periodically
        if processed > 0 and processed % SAVE_EVERY < BATCH_SIZE:
            save_catalog(catalog)
            elapsed = time.monotonic() - t0
            rate = processed / elapsed * 60
            log.info("Progress: %d/%d done (%.1f/min), %d errors", processed, total, rate, errors)

        # Small delay between batches
        time.sleep(0.2)

    # Final save
    save_catalog(catalog)
    elapsed = time.monotonic() - t0
    total_embedded = sum(1 for e in entries if e.get("embedding"))
    emb_dim = None
    for e in entries:
        if e.get("embedding"):
            emb_dim = len(e["embedding"])
            break

    log.info("=== Done ===")
    log.info("  Processed: %d/%d", processed, total)
    log.info("  Errors: %d", errors)
    log.info("  Time: %.1fs", elapsed)
    log.info("  Total with embeddings: %d/%d", total_embedded, len(entries))
    log.info("  Embedding dimensions: %s", emb_dim)


if __name__ == "__main__":
    main()
