#!/usr/bin/env python3
"""Library health check — reports category stats, gaps, and usage from the brand library.

Reports:
- Total images by category
- Categories with <3 images (gaps)
- Most/least used assets (from asset_index.jsonl)
- Embedding coverage
- Clean, actionable output
"""

import json
import logging
import sys
from collections import Counter
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("library_health")

WORKSPACE = Path(__file__).resolve().parent.parent
LIBRARY_DIR = WORKSPACE / "brand" / "library"
CATALOG_PATH = LIBRARY_DIR / "catalog.json"
ASSET_INDEX_PATH = WORKSPACE / "output" / "asset_index.jsonl"
MIN_ASSETS_PER_CATEGORY = 3


def load_catalog() -> dict:
    if not CATALOG_PATH.exists():
        log.error("catalog.json not found at %s", CATALOG_PATH)
        return {"entries": [], "total": 0}
    return json.loads(CATALOG_PATH.read_text())


def load_usage() -> Counter:
    """Load asset usage counts from asset_index.jsonl."""
    usage = Counter()
    if not ASSET_INDEX_PATH.exists():
        log.info("No asset_index.jsonl found — skipping usage stats")
        return usage
    for line in ASSET_INDEX_PATH.read_text().splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            # Track template usage
            template = record.get("template", "")
            if template:
                usage[f"template:{template}"] += 1
            # Track persona usage
            persona = record.get("persona", "")
            if persona:
                usage[f"persona:{persona}"] += 1
            # Track imagery source
            source = record.get("imagery_source", "")
            if source:
                usage[f"source:{source}"] += 1
            # Track campaign
            campaign = record.get("campaign", "")
            if campaign:
                usage[f"campaign:{campaign}"] += 1
        except json.JSONDecodeError:
            continue
    return usage


def main():
    catalog = load_catalog()
    entries = catalog.get("entries", [])

    if not entries:
        print("❌ No entries in catalog.json")
        sys.exit(1)

    # Category breakdown
    category_counts = Counter()
    media_type_counts = Counter()
    format_counts = Counter()
    with_embedding = 0
    with_vision = 0
    total = len(entries)

    for entry in entries:
        category_counts[entry.get("category", "Uncategorized")] += 1
        media_type_counts[entry.get("media_type", "unknown")] += 1
        format_counts[entry.get("format", "unknown")] += 1
        if entry.get("embedding"):
            with_embedding += 1
        if entry.get("vision_description"):
            with_vision += 1

    # Identify gaps
    gaps = [(cat, count) for cat, count in category_counts.items() if count < MIN_ASSETS_PER_CATEGORY]
    gaps.sort(key=lambda x: x[1])

    # Load usage data
    usage = load_usage()

    # Print report
    print("=" * 60)
    print("  AdGen Brand Library Health Report")
    print("=" * 60)

    print(f"\n📊 Overview")
    print(f"  Total assets:      {total}")
    print(f"  Categories:        {len(category_counts)}")
    print(f"  With embeddings:   {with_embedding}/{total} ({100*with_embedding//total}%)")
    if with_vision:
        print(f"  With vision desc:  {with_vision}/{total} ({100*with_vision//total}%)")

    print(f"\n📁 Assets by Category (top 15)")
    for cat, count in category_counts.most_common(15):
        bar = "█" * min(count // 5, 40)
        print(f"  {cat:<45} {count:>4}  {bar}")
    remaining = len(category_counts) - 15
    if remaining > 0:
        print(f"  ... and {remaining} more categories")

    print(f"\n📐 Media Types")
    for mt, count in media_type_counts.most_common():
        print(f"  {mt:<20} {count:>4}")

    print(f"\n📄 Formats")
    for fmt, count in format_counts.most_common(10):
        print(f"  {fmt:<20} {count:>4}")

    if gaps:
        print(f"\n⚠️  Categories with <{MIN_ASSETS_PER_CATEGORY} assets ({len(gaps)} gaps)")
        for cat, count in gaps:
            print(f"  {cat:<45} {count:>4} ← needs more assets")
    else:
        print(f"\n✅ No category gaps (all have ≥{MIN_ASSETS_PER_CATEGORY} assets)")

    # Usage stats from asset_index.jsonl
    if usage:
        print(f"\n🔄 Asset Generation Usage (from asset_index.jsonl)")

        templates = {k.split(":", 1)[1]: v for k, v in usage.items() if k.startswith("template:")}
        if templates:
            print(f"\n  Most Used Templates:")
            for t, c in sorted(templates.items(), key=lambda x: -x[1])[:5]:
                print(f"    {t:<30} {c:>3} uses")
            print(f"  Least Used Templates:")
            for t, c in sorted(templates.items(), key=lambda x: x[1])[:3]:
                print(f"    {t:<30} {c:>3} uses")

        personas = {k.split(":", 1)[1]: v for k, v in usage.items() if k.startswith("persona:")}
        if personas:
            print(f"\n  Personas Targeted:")
            for p, c in sorted(personas.items(), key=lambda x: -x[1]):
                print(f"    {p:<30} {c:>3} assets")

        sources = {k.split(":", 1)[1]: v for k, v in usage.items() if k.startswith("source:")}
        if sources:
            print(f"\n  Imagery Sources:")
            for s, c in sorted(sources.items(), key=lambda x: -x[1]):
                print(f"    {s:<30} {c:>3}")
    else:
        print(f"\n📝 No usage data yet (asset_index.jsonl empty or missing)")

    # Health verdict
    health_issues = []
    if with_embedding < total * 0.5:
        health_issues.append(f"Only {100*with_embedding//total}% have embeddings")
    if len(gaps) > len(category_counts) * 0.3:
        health_issues.append(f"{len(gaps)} categories below minimum threshold")

    print(f"\n{'=' * 60}")
    if health_issues:
        print(f"  Health: ⚠️  ISSUES FOUND")
        for issue in health_issues:
            print(f"    - {issue}")
    else:
        print(f"  Health: ✅ HEALTHY")
    print(f"{'=' * 60}\n")

    # JSON output to stdout for machine consumption
    report = {
        "total_assets": total,
        "categories": len(category_counts),
        "category_counts": dict(category_counts.most_common()),
        "media_types": dict(media_type_counts),
        "formats": dict(format_counts),
        "embedding_coverage": f"{100*with_embedding//total}%",
        "gaps": [{"category": cat, "count": count} for cat, count in gaps],
        "healthy": len(health_issues) == 0,
        "issues": health_issues,
    }

    # Write JSON to a file for programmatic access
    report_path = WORKSPACE / "output" / "library_health.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    log.info("JSON report written to %s", report_path)

    sys.exit(0 if report["healthy"] else 1)


if __name__ == "__main__":
    main()
