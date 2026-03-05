#!/usr/bin/env python3
"""Semantic Asset Search — finds best matching brand assets for a brief/query.
JSON stdin → JSON stdout. Loads catalog + embeddings into memory for fast search."""

import json, logging, math, os, sys, time
from pathlib import Path

logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SZ", level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("search_library")
logging.Formatter.converter = time.gmtime

LIBRARY = Path(__file__).resolve().parent.parent / "brand" / "library"
CATALOG_PATH = LIBRARY / "catalog.json"
EMBEDDINGS_PATH = LIBRARY / "embeddings.json"
FEEDBACK_PATH = LIBRARY / "feedback.json"


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text())


def load_embeddings() -> dict:
    data = json.loads(EMBEDDINGS_PATH.read_text())
    # Build path→embedding lookup
    lookup = {}
    for entry in data["entries"]:
        lookup[entry["path"]] = entry["embedding"]
    return lookup


def load_feedback() -> dict:
    if not FEEDBACK_PATH.exists():
        log.info("no feedback.json found — skipping feedback boosts")
        return {}
    try:
        data = json.loads(FEEDBACK_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        log.warning("failed to load feedback.json: %s — skipping boosts", e)
        return {}
    # Support both "entries" (current) and "records" (legacy) keys
    entries = data.get("entries", data.get("records", []))
    if not entries:
        log.info("feedback.json is empty — no boosts to apply")
        return {}
    # Build path→{persona→score} lookup
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
        "https://api.telnyx.com/v2/ai/openai/embeddings",
        headers={"Authorization": f"Bearer {telnyx_key}"},
        json={"model": "thenlper/gte-large", "input": query},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]


def search(query: str, catalog: dict, emb_lookup: dict, feedback: dict,
           limit: int = 5, type_filter: str | None = None,
           format_filter: str | None = None, persona: str | None = None) -> list[dict]:
    t0 = time.monotonic()
    query_emb = get_query_embedding(query)

    # Build asset lookup
    asset_map = {a["path"]: a for a in catalog["assets"]}

    results = []
    for path, embedding in emb_lookup.items():
        asset = asset_map.get(path)
        if not asset:
            continue
        # Skip archived
        if asset.get("archived"):
            continue
        # Apply filters
        if type_filter and asset.get("type") != type_filter:
            continue
        if format_filter and asset.get("format") != format_filter:
            continue

        score = cosine_sim(query_emb, embedding)

        # Apply feedback boosts BEFORE ranking
        base_score = score
        if path in feedback:
            # Apply persona-specific boost if persona given, else aggregate
            if persona:
                persona_score = feedback[path].get(persona, 0.0)
            else:
                persona_score = sum(feedback[path].values())
            if persona_score > 0:
                score += 0.1
            elif persona_score < 0:
                score -= 0.15
            if base_score != score:
                log.info("feedback boost: %s base=%.4f → boosted=%.4f (persona=%s, feedback_score=%.1f)",
                         path, base_score, score, persona or "all", persona_score)

        results.append({
            "path": f"brand/library/{path}",
            "score": round(score, 4),
            "base_score": round(base_score, 4),
            "description": asset.get("description", ""),
            "category": asset.get("category", ""),
            "type": asset.get("type", ""),
            "dimensions": asset.get("dimensions"),
            "format": asset.get("format"),
            "theme": asset.get("theme"),
            "vertical": asset.get("vertical"),
            "product": asset.get("product"),
            "tags": asset.get("tags", []),
            "usable_for": asset.get("usable_for", []),
        })

    # Sort by score — feedback boosts may change ranking order
    results.sort(key=lambda r: r["score"], reverse=True)

    # Log ranking changes due to feedback boosts
    if feedback and persona:
        unboosted = sorted(results, key=lambda r: r.get("base_score", r["score"]), reverse=True)
        for i, r in enumerate(results[:limit]):
            unboosted_idx = next((j for j, u in enumerate(unboosted) if u["path"] == r["path"]), i)
            if unboosted_idx != i:
                log.info("ranking change: %s moved from #%d → #%d due to feedback boost",
                         r["path"], unboosted_idx + 1, i + 1)

    elapsed = time.monotonic() - t0
    log.info("search completed in %.3fs — %d candidates, returning top %d", elapsed, len(results), limit)
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

    log.info("loading catalog and embeddings")
    catalog = load_catalog()
    emb_lookup = load_embeddings()
    feedback = load_feedback()
    log.info("loaded %d assets, %d embeddings, %d feedback entries",
             catalog["total_assets"], len(emb_lookup), sum(len(v) for v in feedback.values()))

    results = search(query, catalog, emb_lookup, feedback, limit, type_filter, format_filter, persona)

    print(json.dumps({"results": results, "query": query, "total_candidates": catalog.get("active_assets", 0)}, indent=2))


if __name__ == "__main__":
    main()
