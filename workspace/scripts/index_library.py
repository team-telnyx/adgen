#!/usr/bin/env python3
"""Index the brand asset library → catalog.json + embeddings.json.

Walks workspace/brand/library, extracts metadata, reads real image dimensions
via Pillow, normalizes product names, filters artifacts, parses aspect ratios.
"""
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


def main():
    log.info("Indexing library at %s", LIBRARY)
    catalog, excluded = build_catalog()
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
    key_path = Path.home() / ".secrets" / "telnyx"
    if key_path.exists():
        generate_embeddings(catalog, key_path.read_text().strip())
    else:
        log.warning("No API key at %s — skipping embeddings", key_path)
    log.info("Done.")


if __name__ == "__main__":
    main()
