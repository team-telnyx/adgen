#!/usr/bin/env python3
"""Library health check — reports category gaps in brand imagery."""

import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("library_health")

REQUIRED_CATEGORIES = ["product", "abstract", "photography"]
MIN_ASSETS_PER_CATEGORY = 2
IMAGERY_DIR = Path(__file__).parent.parent / "brand" / "imagery"


def check_category(category: str) -> dict:
    cat_dir = IMAGERY_DIR / category
    if not cat_dir.is_dir():
        return {"category": category, "status": "missing", "count": 0, "gap": True}
    assets = [f for f in cat_dir.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    count = len(assets)
    gap = count < MIN_ASSETS_PER_CATEGORY
    return {
        "category": category,
        "status": "ok" if not gap else "low",
        "count": count,
        "gap": gap,
        "files": [f.name for f in assets],
    }


def main():
    log.info("Scanning imagery library at %s", IMAGERY_DIR)
    results = []
    for cat in REQUIRED_CATEGORIES:
        r = check_category(cat)
        results.append(r)
        level = logging.WARNING if r["gap"] else logging.INFO
        log.log(level, "  %s: %d assets (%s)", cat, r["count"], r["status"])

    # Check for uncategorized files at top level
    top_files = [f for f in IMAGERY_DIR.iterdir() if f.is_file() and f.suffix.lower() in (".png", ".jpg")]
    if top_files:
        log.warning("  %d uncategorized files in imagery root", len(top_files))

    gaps = [r for r in results if r["gap"]]
    total_assets = sum(r["count"] for r in results)

    report = {
        "total_assets": total_assets,
        "categories": results,
        "gaps": [r["category"] for r in gaps],
        "healthy": len(gaps) == 0,
    }

    print(json.dumps(report, indent=2))
    log.info("Health: %s — %d assets, %d gaps", "HEALTHY" if report["healthy"] else "GAPS FOUND", total_assets, len(gaps))
    sys.exit(0 if report["healthy"] else 1)


if __name__ == "__main__":
    main()
