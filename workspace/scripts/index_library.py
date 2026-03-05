#!/usr/bin/env python3
"""Asset Cataloger — scans brand/library/ and builds semantic index with embeddings.
Outputs brand/library/catalog.json and brand/library/embeddings.json."""

import json, logging, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SZ", level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("index_library")
logging.Formatter.converter = time.gmtime

LIBRARY = Path(__file__).resolve().parent.parent / "brand" / "library"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
ARCHIVE_MARKERS = {"zold", "zarchive", "old", "archive"}
DIMENSION_RE = re.compile(r"(\d{3,4})x(\d{3,4})")
BATCH_SIZE = 50

# ── Folder → type mapping ──
FOLDER_TYPE_MAP = [
    ("hero", "hero_image"), ("social", "social_asset"), ("icon", "icon"),
    ("pattern", "background"), ("background", "background"), ("logo", "logo"),
    ("badge", "badge"), ("headshot", "headshot"), ("photography", "photography"),
    ("map", "map"), ("globe", "globe"), ("diagram", "diagram"),
    ("promo", "promo"), ("feature", "product_feature"), ("how-it-works", "how_it_works"),
    ("differentiator", "differentiator"), ("navigation", "ui_element"),
    ("thumbnail", "thumbnail"), ("widget", "widget"),
]

# ── Industry verticals ──
VERTICALS = ["healthcare", "finance", "insurance", "logistics", "restaurant",
             "retail", "travel", "automotive", "hospitality", "energy", "education"]

# ── Products ──
PRODUCTS = ["voice-ai", "voice ai", "voice-api", "voice api", "esim", "rcs",
            "ai-assistant", "ai assistant", "mobile-voice", "mobile voice",
            "object-storage", "storage", "tts", "sip", "messaging", "iot", "networking"]

FORMAT_MAP = {
    (1920, 1080): "landscape", (1080, 1920): "vertical", (1080, 1080): "square",
    (1200, 1200): "square", (1200, 628): "landscape", (900, 620): "landscape",
}

USABLE_MAP = {
    "hero_image": ["linkedin_ad", "google_display", "blog_featured", "landing_page"],
    "social_asset": ["social_post", "linkedin_ad", "meta_ad", "twitter_ad"],
    "icon": ["email", "social_post", "presentation", "ui_element"],
    "background": ["ad_background", "presentation", "landing_page"],
    "logo": ["email_signature", "presentation", "ad_overlay"],
    "product_feature": ["blog_featured", "linkedin_ad", "case_study"],
    "photography": ["blog_featured", "linkedin_ad", "landing_page"],
    "promo": ["social_post", "linkedin_ad", "google_display"],
}


def is_archived(path: Path) -> bool:
    parts_lower = [p.lower() for p in path.parts]
    return any(m in part for part in parts_lower for m in ARCHIVE_MARKERS)


def in_compressed(path: Path) -> bool:
    return any("compressed" in p.lower() for p in path.parts)


def extract_type(rel_path: Path) -> str:
    path_lower = str(rel_path).lower()
    for keyword, asset_type in FOLDER_TYPE_MAP:
        if keyword in path_lower:
            return asset_type
    return "visual"


def extract_dimensions(filename: str) -> tuple[str | None, str | None]:
    m = DIMENSION_RE.search(filename)
    if m:
        w, h = int(m.group(1)), int(m.group(2))
        dims = f"{w}x{h}"
        fmt = FORMAT_MAP.get((w, h))
        if not fmt:
            fmt = "landscape" if w > h else ("vertical" if h > w else "square")
        return dims, fmt
    return None, None


def extract_vertical(path_lower: str) -> str | None:
    for v in VERTICALS:
        if v in path_lower:
            return v
    return None


def extract_product(path_lower: str) -> str | None:
    for p in PRODUCTS:
        if p in path_lower:
            return p.replace("-", " ").replace("_", " ").title()
    return None


def extract_theme(filename_lower: str) -> str:
    if "dark" in filename_lower:
        return "dark"
    if "light" in filename_lower:
        return "light"
    if "gradient" in filename_lower:
        return "gradient"
    return "default"


def humanize(s: str) -> str:
    return re.sub(r"[-_]+", " ", s).strip()


def build_description(asset: dict) -> str:
    parts = []
    if asset.get("product"):
        parts.append(f"{asset['product']} product")
    if asset.get("vertical"):
        parts.append(f"{asset['vertical']} industry")
    parts.append(f"{asset['type'].replace('_', ' ')}")
    if asset.get("dimensions"):
        parts.append(f"{asset['dimensions']} {asset.get('format', '')} format")
    if asset.get("theme") and asset["theme"] != "default":
        parts.append(f"{asset['theme']} theme")
    usable = asset.get("usable_for", [])
    if usable:
        parts.append(f"suitable for {', '.join(usable[:3])}")
    subject = asset.get("subject", "")
    if subject:
        parts.append(f"depicting {subject}")
    return ", ".join(parts).capitalize()


def build_tags(asset: dict) -> list[str]:
    tags = set()
    tags.add(asset["type"])
    if asset.get("category"):
        tags.add(asset["category"])
    if asset.get("subcategory"):
        tags.add(asset["subcategory"])
    if asset.get("vertical"):
        tags.add(asset["vertical"])
    if asset.get("product"):
        tags.add(asset["product"].lower())
    if asset.get("format"):
        tags.add(asset["format"])
    if asset.get("theme") and asset["theme"] != "default":
        tags.add(asset["theme"])
    return sorted(tags)


def catalog_asset(rel_path: Path, full_path: Path) -> dict:
    path_lower = str(rel_path).lower()
    fname_lower = rel_path.name.lower()
    stem = rel_path.stem.lower()
    parts = rel_path.parts

    category = parts[0].lower().replace("-", "_").replace(" ", "_") if parts else "uncategorized"
    subcategory = parts[1].lower().replace("-", "_").replace(" ", "_") if len(parts) > 2 else ""

    asset_type = extract_type(rel_path)
    dims, fmt = extract_dimensions(rel_path.name)
    vertical = extract_vertical(path_lower)
    product = extract_product(path_lower)
    theme = extract_theme(fname_lower)
    archived = is_archived(rel_path)
    compressed = in_compressed(rel_path)
    subject = humanize(re.sub(r"\d{3,4}x\d{3,4}", "", stem).strip("_- "))

    try:
        size = full_path.stat().st_size
    except OSError:
        size = 0

    asset = {
        "path": str(rel_path),
        "category": humanize(category),
        "subcategory": humanize(subcategory) if subcategory else "",
        "type": asset_type,
        "subject": subject,
        "dimensions": dims,
        "format": fmt,
        "theme": theme,
        "vertical": vertical,
        "product": product,
        "archived": archived,
        "compressed": compressed,
        "size_bytes": size,
    }
    asset["usable_for"] = USABLE_MAP.get(asset_type, ["general"])
    asset["tags"] = build_tags(asset)
    asset["description"] = build_description(asset)
    return asset


def generate_embeddings(assets: list[dict]) -> list[dict]:
    telnyx_key = Path(os.path.expanduser("~/.secrets/telnyx")).read_text().strip()
    import requests

    descriptions = [a["description"] for a in assets]
    paths = [a["path"] for a in assets]
    entries = []
    total = len(descriptions)

    for i in range(0, total, BATCH_SIZE):
        batch = descriptions[i : i + BATCH_SIZE]
        batch_paths = paths[i : i + BATCH_SIZE]
        log.info("embedding batch %d-%d / %d", i + 1, min(i + BATCH_SIZE, total), total)

        for attempt in range(3):
            try:
                resp = requests.post(
                    "https://api.telnyx.com/v2/ai/openai/embeddings",
                    headers={"Authorization": f"Bearer {telnyx_key}"},
                    json={"model": "thenlper/gte-large", "input": batch},
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()["data"]
                for j, d in enumerate(data):
                    entries.append({"path": batch_paths[j], "embedding": d["embedding"]})
                break
            except Exception as e:
                log.warning("embedding attempt %d failed: %s", attempt + 1, e)
                if attempt == 2:
                    log.error("giving up on batch %d-%d", i + 1, i + len(batch))
                else:
                    time.sleep(2 ** attempt)

    return entries


def main():
    log.info("scanning %s", LIBRARY)
    assets = []
    skipped_video = 0
    skipped_other = 0

    for f in sorted(LIBRARY.rglob("*")):
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext in {".mp4", ".webm", ".mov", ".avi"}:
            skipped_video += 1
            continue
        if ext not in IMAGE_EXTS:
            skipped_other += 1
            continue
        rel = f.relative_to(LIBRARY)
        # Skip source/editable files deep in folder trees
        if "source file" in str(rel).lower() or "editable" in str(rel).lower():
            skipped_other += 1
            continue
        asset = catalog_asset(rel, f)
        assets.append(asset)

    log.info("cataloged %d images (skipped %d video, %d other)", len(assets), skipped_video, skipped_other)

    catalog = {
        "version": 1,
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_assets": len(assets),
        "active_assets": sum(1 for a in assets if not a["archived"]),
        "archived_assets": sum(1 for a in assets if a["archived"]),
        "assets": assets,
    }

    catalog_path = LIBRARY / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2))
    log.info("wrote %s (%d assets)", catalog_path, len(assets))

    # Generate embeddings for non-archived assets
    active = [a for a in assets if not a["archived"]]
    log.info("generating embeddings for %d active assets", len(active))
    entries = generate_embeddings(active)

    embeddings = {
        "model": "thenlper/gte-large",
        "dimensions": 1024,
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_entries": len(entries),
        "entries": entries,
    }

    emb_path = LIBRARY / "embeddings.json"
    emb_path.write_text(json.dumps(embeddings))
    log.info("wrote %s (%d entries)", emb_path, len(entries))

    print(json.dumps({"catalog": str(catalog_path), "embeddings": str(emb_path),
                       "total_assets": len(assets), "active": len(active),
                       "embedded": len(entries)}))


if __name__ == "__main__":
    main()
