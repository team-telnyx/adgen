#!/usr/bin/env python3
"""Save an image to the AdGen brand library.

Copies to brand/library/{category}/, updates catalog.json with description
and embedding. Optionally uploads to Telnyx Storage.

Usage (JSON stdin):
  {
    "source_path": "/path/to/image.png",
    "category": "Industry_Visuals",
    "tags": ["healthcare", "network"],
    "description": "Dark network visualization for healthcare"
  }

Or via CLI args:
  python3 save_to_library.py --source /path/to/image.png --category Industry_Visuals --tags healthcare,network --description "..."

JSON stdout with result.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO,
    stream=sys.stderr,
)
log = logging.getLogger("save_to_library")
logging.Formatter.converter = time.gmtime

try:
    from PIL import Image
except ImportError:
    log.error("Pillow not installed: pip install Pillow")
    sys.exit(1)

WORKSPACE = Path(__file__).resolve().parent.parent
LIBRARY_DIR = WORKSPACE / "brand" / "library"
CATALOG_PATH = LIBRARY_DIR / "catalog.json"
SCRIPTS_DIR = Path(__file__).resolve().parent

EMBED_URL = "https://api.telnyx.com/v2/ai/openai/embeddings"
EMBED_MODEL = "thenlper/gte-large"
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
MIN_DIM = 100  # Minimum dimension (permissive — quality judgment is human)


def load_telnyx_key() -> str:
    p = Path.home() / ".secrets" / "telnyx"
    if not p.exists():
        raise FileNotFoundError(f"Telnyx key not found at {p}")
    return p.read_text().strip()


def generate_filename(source: Path, category: str, tags: list[str]) -> str:
    """Generate a descriptive filename from source name and tags."""
    stem = source.stem
    # Clean up common prefixes
    stem = stem.replace("Telnyx_", "").replace("telnyx_", "")
    # If stem is too generic, add tag info
    if len(stem) < 5 and tags:
        stem = f"{stem}_{'_'.join(tags[:2])}"
    suffix = source.suffix.lower()
    return f"{stem}{suffix}"


def get_embedding(text: str, api_key: str) -> list[float]:
    """Get embedding vector for text via Telnyx API."""
    import requests

    resp = requests.post(
        EMBED_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": EMBED_MODEL, "input": text},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["data"][0]["embedding"]


def update_catalog(
    rel_path: str,
    category: str,
    tags: list[str],
    description: str,
    dimensions: str,
    media_type: str,
    fmt: str,
    embedding: list[float] | None,
) -> None:
    """Add or update an entry in catalog.json."""
    if not CATALOG_PATH.exists():
        catalog = {"generated": datetime.now(timezone.utc).isoformat(), "total": 0, "entries": []}
    else:
        catalog = json.loads(CATALOG_PATH.read_text())

    entries = catalog.get("entries", [])

    # Check if path already exists
    existing_idx = next((i for i, e in enumerate(entries) if e["path"] == rel_path), None)

    entry = {
        "path": rel_path,
        "category": category,
        "media_type": media_type,
        "format": fmt,
        "description": description,
        "tags": tags,
        "dimensions": dimensions,
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    if embedding:
        entry["embedding"] = embedding

    if existing_idx is not None:
        entries[existing_idx] = entry
        log.info("updated existing catalog entry: %s", rel_path)
    else:
        entries.append(entry)
        log.info("added new catalog entry: %s", rel_path)

    catalog["entries"] = entries
    catalog["total"] = len(entries)
    catalog["generated"] = datetime.now(timezone.utc).isoformat()

    CATALOG_PATH.write_text(json.dumps(catalog, indent=2))
    log.info("catalog updated: %d total entries", catalog["total"])


def upload_to_storage(local: str, key: str) -> bool:
    """Upload to Telnyx Storage via storage.py."""
    payload = {"action": "upload", "bucket": "adgen-brand", "local_path": local, "remote_key": key}
    try:
        p = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "storage.py")],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if p.returncode != 0:
            log.warning("upload failed: %s", p.stderr[-300:])
            return False
        log.info("uploaded key=%s", key)
        return True
    except Exception as e:
        log.warning("upload error: %s", e)
        return False


def save_image(source_path: str, category: str, tags: list[str], description: str, filename: str = "") -> dict:
    """Main save logic. Returns result dict."""
    src = Path(source_path)

    # Validate source
    if not src.is_file():
        raise FileNotFoundError(f"Source not found: {src}")

    suffix = src.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {suffix} (supported: {SUPPORTED_FORMATS})")

    # Get image dimensions
    try:
        img = Image.open(src)
        w, h = img.size
        dimensions = f"{w}x{h}"
        if max(w, h) < MIN_DIM:
            raise ValueError(f"Image too small: {w}x{h} (min {MIN_DIM}px)")
        log.info("validated %s %dx%d", suffix, w, h)
    except Exception as e:
        if "too small" in str(e) or "Unsupported" in str(e):
            raise
        # SVG or other format that PIL can't read
        dimensions = "unknown"
        log.warning("could not read image dimensions: %s", e)

    # Determine media type
    media_type = "image"
    fmt = suffix.lstrip(".")

    # Generate filename if not provided
    if not filename:
        filename = generate_filename(src, category, tags)

    # Copy to library
    dest_dir = LIBRARY_DIR / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename

    # Don't overwrite without warning
    if dest.exists():
        log.warning("file already exists, overwriting: %s", dest)

    shutil.copy2(str(src), str(dest))
    log.info("copied to %s", dest)

    # Build description text for embedding
    embed_text = " ".join(
        filter(None, [description, category, " ".join(tags)])
    )

    # Generate embedding
    embedding = None
    try:
        api_key = load_telnyx_key()
        embedding = get_embedding(embed_text, api_key)
        log.info("embedding generated (%d dimensions)", len(embedding))
    except Exception as e:
        log.warning("embedding generation failed: %s — saving without embedding", e)

    # Relative path for catalog (relative to library dir)
    rel_path = f"{category}/{filename}"

    # Update catalog
    update_catalog(rel_path, category, tags, description, dimensions, media_type, fmt, embedding)

    # Upload to storage (best-effort)
    remote_key = f"library/{category}/{filename}"
    uploaded = upload_to_storage(str(dest), remote_key)

    result = {
        "ok": True,
        "path": str(dest),
        "relative_path": rel_path,
        "category": category,
        "filename": filename,
        "dimensions": dimensions,
        "tags": tags,
        "description": description,
        "has_embedding": embedding is not None,
        "uploaded": uploaded,
        "remote_key": remote_key,
    }
    return result


def main():
    # Support both JSON stdin and CLI args
    parser = argparse.ArgumentParser(description="Save image to AdGen brand library")
    parser.add_argument("--source", help="Path to source image")
    parser.add_argument("--category", help="Library category (e.g., Industry_Visuals)")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--description", help="Image description")
    parser.add_argument("--filename", help="Override filename", default="")

    args, _ = parser.parse_known_args()

    if args.source:
        # CLI mode
        cfg = {
            "source_path": args.source,
            "category": args.category or "Uncategorized",
            "tags": [t.strip() for t in args.tags.split(",")] if args.tags else [],
            "description": args.description or "",
            "filename": args.filename,
        }
    else:
        # JSON stdin mode
        try:
            cfg = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            log.error("invalid JSON: %s", e)
            sys.exit(1)

    try:
        result = save_image(
            source_path=cfg.get("source_path", ""),
            category=cfg.get("category", "Uncategorized"),
            tags=cfg.get("tags", []),
            description=cfg.get("description", ""),
            filename=cfg.get("filename", ""),
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        log.error("save failed: %s", e)
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
