#!/usr/bin/env python3
"""Search past AdGen assets via Telnyx Embeddings API (semantic similarity)."""

import json
import logging
import math
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
log = logging.getLogger("search_assets")

WORKSPACE = Path(__file__).resolve().parent.parent
INDEX_PATH = WORKSPACE / "output" / "asset_index.jsonl"
CACHE_PATH = WORKSPACE / "output" / ".embedding_cache.json"
EMBED_URL = "https://api.telnyx.com/v2/ai/openai/embeddings"
MODEL = "thenlper/gte-large"


def load_key() -> str:
    p = Path.home() / ".secrets" / "telnyx"
    if not p.exists():
        log.error("Telnyx key not found at %s", p)
        sys.exit(1)
    return p.read_text().strip()


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except json.JSONDecodeError:
            log.warning("Corrupt cache, starting fresh")
    return {}


def save_cache(cache: dict):
    CACHE_PATH.write_text(json.dumps(cache))


def get_embeddings(texts: list[str], key: str, cache: dict) -> list[list[float]]:
    """Fetch embeddings, using cache for known texts."""
    uncached = [t for t in texts if t not in cache]
    if uncached:
        log.info("Embedding %d texts (%d cached)", len(uncached), len(texts) - len(uncached))
        for i in range(0, len(uncached), 20):
            batch = uncached[i : i + 20]
            body = json.dumps({"model": MODEL, "input": batch}).encode()
            req = Request(EMBED_URL, data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            with urlopen(req) as resp:
                data = json.loads(resp.read())
            for item, text in zip(data["data"], batch):
                cache[text] = item["embedding"]
        save_cache(cache)
    return [cache[t] for t in texts]


def cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0

def asset_text(rec: dict) -> str:
    """Build searchable text from asset metadata."""
    fields = ["headline", "campaign", "persona", "template", "accent_color", "imagery_source"]
    return " | ".join(rec[f] for f in fields if rec.get(f))


def load_assets() -> list[dict]:
    if not INDEX_PATH.exists():
        log.warning("No asset index at %s", INDEX_PATH)
        return []
    assets = []
    for line in INDEX_PATH.read_text().splitlines():
        if line.strip():
            try:
                assets.append(json.loads(line))
            except json.JSONDecodeError:
                log.warning("Skipping malformed line")
    log.info("Loaded %d assets", len(assets))
    return assets


def search(query: str, limit: int = 5) -> list[dict]:
    key, cache, assets = load_key(), load_cache(), load_assets()
    if not assets:
        return []
    texts = [asset_text(a) for a in assets]
    embeddings = get_embeddings([query] + texts, key, cache)
    q_emb = embeddings[0]
    scored = [{**a, "similarity": round(cosine_sim(q_emb, e), 4)} for a, e in zip(assets, embeddings[1:])]
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:limit]


def main():
    inp = json.load(sys.stdin)
    query = inp.get("query", "")
    limit = inp.get("limit", 5)
    if not query:
        log.error("No query provided")
        sys.exit(1)
    log.info("Searching for: %s (limit=%d)", query, limit)
    results = search(query, limit)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
