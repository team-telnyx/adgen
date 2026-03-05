#!/usr/bin/env python3
"""Index the brand asset library → catalog.json + embeddings.json.

Walks workspace/brand/library, extracts metadata, reads real image dimensions
via Pillow, normalizes product names, filters artifacts, parses aspect ratios.

Flags:
    --check     Report vision description and embedding coverage without re-indexing.
"""
import argparse
import json, logging, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image

log = logging.getLogger("index_library")
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)

WORKSPACE = Path(__file__).resolve().parent.parent
LIBRARY = WORKSPACE / "brand" / "library"
CATALOG_PATH = LIBRARY / "catalog.json"
EMBED_PATH = LIBRARY / "embeddings.json"
EMBED_URL = "https://api.telnyx.com/v2/ai/openai/embeddings"
EMBED_MODEL = "thenlper/gte-large"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
VIDEO_EXTS = {".mp4", ".mov", ".webm"}
ASSET_EXTS = IMAGE_EXTS | VIDEO_EXTS
MIN_FILE_SIZE = 1024

PRODUCT_NAMES = {
    "voice ai": "Voice AI Agent", "voice api": "Voice API", "esim": "eSIM",
    "rcs": "RCS", "ai assistant": "AI Assistant", "iot": "IoT SIM",
    "sip": "SIP Trunking", "mobile voice": "Mobile Voice", "object storage": "Storage",
}
EXCLUDE_DIR_EXACT = {"source files"}
EXCLUDE_PATH_SUBSTR = {"screenstudio"}
EXCLUDE_EXTS = {".aep", ".ai", ".psd"}
ASPECT_PATTERNS = [
    (re.compile(r"[_\-]16[x\-]9", re.I), "landscape"),
    (re.compile(r"[_\-]9[x\-]16", re.I), "vertical"),
    (re.compile(r"[_\-]1[x\-]1", re.I), "square"),
    (re.compile(r"[_\-]3[x\-]2", re.I), "landscape"),
]
RETINA_RE = re.compile(r"@2x", re.I)
DIMENSION_RE = re.compile(r"(\d{3,4})[\sx](\d{3,4})")
INDUSTRY_KW = {
    "healthcare": "healthcare", "health": "healthcare", "logistics": "logistics",
    "travel": "travel", "finance": "finance", "fintech": "finance",
    "retail": "retail", "insurance": "insurance", "restaurant": "restaurant",
    "automotive": "automotive",
}
PRODUCT_TEXT_FIX = {
    "Voice Ai": "Voice AI Agent", "Voice Api": "Voice API", "Esim": "eSIM",
    "Rcs": "RCS", "Ai Assistant": "AI Assistant", "Iot": "IoT SIM",
    "Sip": "SIP Trunking", "Object Storage": "Storage",
}


def should_exclude(fp: Path) -> str | None:
    parts_lower = [p.lower() for p in fp.parts]
    for d in EXCLUDE_DIR_EXACT:
        if d in parts_lower:
            return f"dir:{d}"
    rel_lower = str(fp).lower()
    for s in EXCLUDE_PATH_SUBSTR:
        if s in rel_lower:
            return f"path:{s}"
    if fp.suffix.lower() in EXCLUDE_EXTS:
        return f"ext:{fp.suffix}"
    if fp.name.lower().startswith("cursor"):
        return "cursor-artifact"
    try:
        if fp.stat().st_size < MIN_FILE_SIZE:
            return "under-1kb"
    except OSError:
        return "stat-error"
    return None


def get_dimensions(fp: Path):
    if fp.suffix.lower() not in IMAGE_EXTS - {".svg"}:
        return None, None
    try:
        with Image.open(fp) as img:
            w, h = img.width, img.height
            orient = "landscape" if w > h else ("square" if w == h else "vertical")
            return f"{w}x{h}", orient
    except Exception:
        return None, None


def extract_product(path_lower: str):
    for key, name in PRODUCT_NAMES.items():
        if key.replace(" ", "-") in path_lower or key.replace(" ", "_") in path_lower or key in path_lower:
            return name
    return None


def extract_industry(path_lower: str):
    for kw, ind in INDUSTRY_KW.items():
        if kw in path_lower:
            return ind
    return None


def parse_aspect(filename: str):
    orient = None
    for pat, o in ASPECT_PATTERNS:
        if pat.search(filename):
            orient = o; break
    return orient, bool(RETINA_RE.search(filename))


def build_catalog():
    catalog, excluded = [], []
    for fp in sorted(LIBRARY.rglob("*")):
        if not fp.is_file() or fp.suffix.lower() not in ASSET_EXTS:
            continue
        rel = str(fp.relative_to(LIBRARY))
        reason = should_exclude(fp)
        if reason:
            excluded.append({"path": rel, "reason": reason}); continue
        pl = rel.lower().replace("-", " ").replace("_", " ")
        product, industry = extract_product(pl), extract_industry(pl)
        archived = any(p in rel.lower() for p in ["zold/", "zarchive/", "archive/"])
        dims, orient = get_dimensions(fp)
        fn_orient, retina = parse_aspect(fp.name)
        if not orient and fn_orient:
            orient = fn_orient
        if not dims:
            m = DIMENSION_RE.search(fp.stem)
            if m:
                dims = f"{m.group(1)}x{m.group(2)}"
        cat = rel.split("/")[0] if "/" in rel else "uncategorized"
        mtype = "image" if fp.suffix.lower() in IMAGE_EXTS else "video"
        desc = f"{cat} {product or ''} {industry or ''} {fp.stem}".strip()
        for old, new in PRODUCT_TEXT_FIX.items():
            desc = desc.replace(old, new)
        entry = {"path": rel, "category": cat, "media_type": mtype, "format": fp.suffix.lstrip("."),
                 "product": product, "industry": industry, "dimensions": dims,
                 "orientation": orient, "retina": retina or None, "archived": archived or None,
                 "description": desc}
        catalog.append({k: v for k, v in entry.items() if v is not None})
    return catalog, excluded


def generate_embeddings(catalog, api_key):
    texts = [e.get("description", e["path"]) for e in catalog]
    entries, total = [], len(texts)
    log.info("Generating embeddings for %d assets...", total)
    for i in range(0, total, 20):
        batch = texts[i:i + 20]
        body = json.dumps({"model": EMBED_MODEL, "input": batch}).encode()
        req = Request(EMBED_URL, data=body,
                      headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
        with urlopen(req) as resp:
            data = json.loads(resp.read())
        for item, asset in zip(data["data"], catalog[i:i + 20]):
            entries.append({"path": asset["path"], "embedding": item["embedding"]})
        done = min(i + 20, total)
        if done % 200 == 0 or done == total:
            log.info("  embedded %d/%d", done, total)
    result = {"model": EMBED_MODEL, "dimensions": 1024,
              "generated": datetime.now(timezone.utc).isoformat(),
              "total_entries": len(entries), "entries": entries}
    EMBED_PATH.write_text(json.dumps(result))
    log.info("Wrote embeddings: %s (%d entries)", EMBED_PATH, len(entries))


def report_coverage(catalog_data: dict):
    """Report vision description and embedding coverage."""
    entries = catalog_data.get("entries", [])
    total = len(entries)
    with_vision = sum(1 for e in entries if e.get("vision_description"))
    with_embedding = sum(1 for e in entries if e.get("embedding"))
    images = sum(1 for e in entries if e.get("media_type") == "image")
    videos = sum(1 for e in entries if e.get("media_type") == "video")
    image_formats = {"png", "jpg", "jpeg", "webp", "gif"}
    describable = sum(1 for e in entries if e.get("format", "").lower() in image_formats)

    log.info("=== Vision & Embedding Coverage ===")
    log.info("  Total assets:          %d", total)
    log.info("  Images:                %d", images)
    log.info("  Videos:                %d", videos)
    log.info("  Describable (non-SVG): %d", describable)
    log.info("  Vision descriptions:   %d / %d (%.1f%%)",
             with_vision, describable, (with_vision / max(describable, 1)) * 100)
    log.info("  Inline embeddings:     %d / %d (%.1f%%)",
             with_embedding, total, (with_embedding / max(total, 1)) * 100)

    # Check legacy embeddings.json too
    if EMBED_PATH.exists():
        try:
            emb_data = json.loads(EMBED_PATH.read_text())
            file_emb = len(emb_data.get("entries", []))
            log.info("  Legacy embeddings.json: %d entries", file_emb)
        except (json.JSONDecodeError, OSError):
            pass

    # Per-category breakdown
    cats = {}
    for e in entries:
        cat = e.get("category", "uncategorized")
        if cat not in cats:
            cats[cat] = {"total": 0, "vision": 0, "embedding": 0}
        cats[cat]["total"] += 1
        if e.get("vision_description"):
            cats[cat]["vision"] += 1
        if e.get("embedding"):
            cats[cat]["embedding"] += 1

    log.info("  --- Per-category ---")
    for cat in sorted(cats.keys()):
        c = cats[cat]
        log.info("    %-40s total=%-4d vision=%-4d embed=%-4d", cat, c["total"], c["vision"], c["embedding"])


def main():
    parser = argparse.ArgumentParser(description="Index the brand asset library")
    parser.add_argument("--check", action="store_true",
                        help="Report coverage without re-indexing")
    args = parser.parse_args()

    if args.check:
        if not CATALOG_PATH.exists():
            log.error("No catalog.json found at %s — run without --check first", CATALOG_PATH)
            sys.exit(1)
        catalog_data = json.loads(CATALOG_PATH.read_text())
        report_coverage(catalog_data)
        return

    log.info("Indexing library at %s", LIBRARY)
    catalog, excluded = build_catalog()

    # Preserve vision_description and embedding from existing catalog
    if CATALOG_PATH.exists():
        try:
            old_data = json.loads(CATALOG_PATH.read_text())
            old_entries = {e["path"]: e for e in old_data.get("entries", [])}
            preserved_vision = 0
            preserved_embed = 0
            for entry in catalog:
                old = old_entries.get(entry["path"])
                if old:
                    if old.get("vision_description"):
                        entry["vision_description"] = old["vision_description"]
                        preserved_vision += 1
                    if old.get("embedding"):
                        entry["embedding"] = old["embedding"]
                        preserved_embed += 1
            if preserved_vision or preserved_embed:
                log.info("Preserved %d vision descriptions and %d embeddings from previous catalog",
                         preserved_vision, preserved_embed)
        except (json.JSONDecodeError, OSError):
            pass

    output = {"generated": datetime.now(timezone.utc).isoformat(), "total": len(catalog),
              "excluded": len(excluded), "entries": catalog, "excluded_entries": excluded}
    CATALOG_PATH.write_text(json.dumps(output, indent=2))
    log.info("Wrote catalog: %s", CATALOG_PATH)
    with_dims = sum(1 for e in catalog if "dimensions" in e)
    archived = sum(1 for e in catalog if e.get("archived"))
    products = {}
    for e in catalog:
        products[e.get("product", "untagged")] = products.get(e.get("product", "untagged"), 0) + 1
    log.info("=== Summary ===")
    log.info("  Total cataloged: %d", len(catalog))
    log.info("  With dimensions:  %d / %d", with_dims, len(catalog))
    log.info("  Archived:         %d", archived)
    log.info("  Excluded:         %d", len(excluded))
    log.info("  Products: %s", json.dumps(products, indent=4))

    # Report vision/embedding coverage
    report_coverage(output)

    key_path = Path.home() / ".secrets" / "telnyx"
    if key_path.exists():
        generate_embeddings(catalog, key_path.read_text().strip())
    else:
        log.warning("No API key at %s — skipping embeddings", key_path)
    log.info("Done.")


if __name__ == "__main__":
    main()
