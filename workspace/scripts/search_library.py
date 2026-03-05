#!/usr/bin/env python3
"""Semantic Asset Search — finds best matching brand assets for a brief/query.

Supports two embedding sources:
1. Inline embeddings in catalog.json (preferred — from embed_catalog.py)
2. Separate embeddings.json file (legacy fallback)

Falls back to keyword matching when no embeddings are available.

JSON stdin → JSON stdout.
"""

import json
import logging
import math
import os
import re
import sys
import time
from pathlib import Path

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO,
    stream=sys.stderr,
)
log = logging.getLogger("search_library")
logging.Formatter.converter = time.gmtime

LIBRARY = Path(__file__).resolve().parent.parent / "brand" / "library"
CATALOG_PATH = LIBRARY / "catalog.json"
EMBEDDINGS_PATH = LIBRARY / "embeddings.json"
FEEDBACK_PATH = LIBRARY / "feedback.json"

EMBED_URL = "https://api.telnyx.com/v2/ai/openai/embeddings"
EMBED_MODEL = "thenlper/gte-large"


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text())


def load_embeddings_file() -> dict:
    """Load legacy embeddings.json file."""
    if not EMBEDDINGS_PATH.exists():
        return {}
    data = json.loads(EMBEDDINGS_PATH.read_text())
    lookup = {}
    for entry in data.get("entries", []):
        lookup[entry["path"]] = entry["embedding"]
    return lookup


def build_embedding_lookup(catalog: dict) -> tuple[dict, str]:
    """Build path→embedding lookup. Prefer inline catalog embeddings, fall back to file.

    Returns (lookup_dict, source_label).
    """
    entries = catalog.get("entries", catalog.get("assets", []))
    inline_count = sum(1 for e in entries if e.get("embedding"))

    if inline_count > 0:
        lookup = {}
        for e in entries:
            if e.get("embedding"):
                lookup[e["path"]] = e["embedding"]
        log.info("Using %d inline catalog embeddings", len(lookup))
        return lookup, "inline"

    # Fall back to embeddings.json
    file_lookup = load_embeddings_file()
    if file_lookup:
        log.info("Using %d embeddings from embeddings.json (legacy)", len(file_lookup))
        return file_lookup, "file"

    log.warning("No embeddings available — will use keyword matching")
    return {}, "none"


def load_feedback() -> dict:
    if not FEEDBACK_PATH.exists():
        log.info("no feedback.json found — skipping feedback boosts")
        return {}
    try:
        data = json.loads(FEEDBACK_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        log.warning("failed to load feedback.json: %s — skipping boosts", e)
        return {}
    entries = data.get("entries", data.get("records", []))
    if not entries:
        log.info("feedback.json is empty — no boosts to apply")
        return {}
    scores = {}
    for record in entries:
        path = record.get("asset_path", "")
        if not path:
            continue
        persona = record.get("persona", "")
        rating = record.get("rating", "neutral")
        if path not in scores:
            scores[path] = {}
        if persona not in scores[path]:
            scores[path][persona] = 0.0
        if rating == "positive":
            scores[path][persona] += 1.0
        elif rating == "negative":
            scores[path][persona] -= 1.0
        elif rating == "revision":
            scores[path][persona] -= 0.5
    log.info("loaded feedback for %d assets", len(scores))
    return scores


def cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def get_query_embedding(query: str) -> list[float]:
    import requests

    telnyx_key = Path(os.path.expanduser("~/.secrets/telnyx")).read_text().strip()
    resp = requests.post(
        EMBED_URL,
        headers={"Authorization": f"Bearer {telnyx_key}"},
        json={"model": EMBED_MODEL, "input": query},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "data" in data:
        return data["data"][0]["embedding"]
    elif "embeddings" in data:
        return data["embeddings"][0]
    else:
        raise ValueError(f"Unexpected embedding response format: {list(data.keys())}")


def keyword_score(query: str, asset: dict) -> float:
    """Simple keyword matching score as fallback when no embeddings exist."""
    query_terms = set(re.findall(r'\w+', query.lower()))
    if not query_terms:
        return 0.0

    # Search across all text fields
    searchable = " ".join([
        asset.get("description", ""),
        asset.get("vision_description", ""),
        asset.get("category", ""),
        asset.get("product", ""),
        asset.get("industry", ""),
        asset.get("path", ""),
        " ".join(asset.get("tags", [])),
    ]).lower()

    asset_terms = set(re.findall(r'\w+', searchable))
    if not asset_terms:
        return 0.0

    matches = query_terms & asset_terms
    return len(matches) / len(query_terms)


def search(
    query: str,
    catalog: dict,
    emb_lookup: dict,
    feedback: dict,
    limit: int = 5,
    type_filter: str | None = None,
    format_filter: str | None = None,
    persona: str | None = None,
) -> list[dict]:
    t0 = time.monotonic()

    entries = catalog.get("entries", catalog.get("assets", []))
    use_embeddings = bool(emb_lookup)

    if use_embeddings:
        query_emb = get_query_embedding(query)
    else:
        query_emb = None
        log.info("No embeddings — using keyword matching")

    results = []
    for asset in entries:
        path = asset.get("path", "")
        if asset.get("archived"):
            continue
        if type_filter and asset.get("type") != type_filter and asset.get("media_type") != type_filter:
            continue
        if format_filter and asset.get("format") != format_filter:
            continue

        # Calculate score
        if use_embeddings and path in emb_lookup:
            score = cosine_sim(query_emb, emb_lookup[path])
        elif use_embeddings:
            # Asset has no embedding — give it a low keyword score
            score = keyword_score(query, asset) * 0.5
        else:
            score = keyword_score(query, asset)

        # Apply feedback boosts
        base_score = score
        if path in feedback:
            if persona:
                persona_score = feedback[path].get(persona, 0.0)
            else:
                persona_score = sum(feedback[path].values())
            if persona_score > 0:
                score += 0.1
            elif persona_score < 0:
                score -= 0.15
            if base_score != score:
                log.info(
                    "feedback boost: %s base=%.4f → boosted=%.4f (persona=%s, feedback_score=%.1f)",
                    path, base_score, score, persona or "all", persona_score,
                )

        # Use vision_description if available, else description
        description = asset.get("vision_description") or asset.get("description", "")

        results.append({
            "path": f"brand/library/{path}",
            "score": round(score, 4),
            "base_score": round(base_score, 4),
            "description": description,
            "vision_description": asset.get("vision_description"),
            "category": asset.get("category", ""),
            "type": asset.get("type", asset.get("media_type", "")),
            "dimensions": asset.get("dimensions"),
            "format": asset.get("format"),
            "theme": asset.get("theme"),
            "vertical": asset.get("vertical"),
            "product": asset.get("product"),
            "tags": asset.get("tags", []),
            "usable_for": asset.get("usable_for", []),
        })

    results.sort(key=lambda r: r["score"], reverse=True)

    # Log ranking changes due to feedback boosts
    if feedback and persona:
        unboosted = sorted(results, key=lambda r: r.get("base_score", r["score"]), reverse=True)
        for i, r in enumerate(results[:limit]):
            unboosted_idx = next((j for j, u in enumerate(unboosted) if u["path"] == r["path"]), i)
            if unboosted_idx != i:
                log.info(
                    "ranking change: %s moved from #%d → #%d due to feedback boost",
                    r["path"], unboosted_idx + 1, i + 1,
                )

    elapsed = time.monotonic() - t0
    search_method = "embedding" if use_embeddings else "keyword"
    log.info(
        "search completed in %.3fs — %d candidates, returning top %d (method: %s)",
        elapsed, len(results), limit, search_method,
    )
    return results[:limit]


def main():
    try:
        cfg = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log.error("invalid JSON input: %s", e)
        sys.exit(1)

    query = cfg.get("query", "")
    if not query:
        log.error("missing required field: query")
        sys.exit(1)

    limit = cfg.get("limit", 5)
    type_filter = cfg.get("type_filter")
    format_filter = cfg.get("format_filter")
    persona = cfg.get("persona")

    log.info("loading catalog")
    catalog = load_catalog()
    emb_lookup, emb_source = build_embedding_lookup(catalog)
    feedback = load_feedback()

    entries = catalog.get("entries", catalog.get("assets", []))
    log.info(
        "loaded %d assets, %d embeddings (%s source), %d feedback entries",
        len(entries), len(emb_lookup), emb_source,
        sum(len(v) for v in feedback.values()),
    )

    results = search(query, catalog, emb_lookup, feedback, limit, type_filter, format_filter, persona)

    print(
        json.dumps(
            {
                "results": results,
                "query": query,
                "total_candidates": len(entries),
                "search_method": "embedding" if emb_lookup else "keyword",
                "embedding_source": emb_source,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
