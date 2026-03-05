#!/usr/bin/env python3
"""Feedback Loop — record, query, and compute boosts for asset feedback.
JSON stdin → JSON stdout. Append-only in brand/library/feedback.json."""
import json, logging, sys, time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SZ", level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("feedback_loop")
logging.Formatter.converter = time.gmtime
FEEDBACK = Path(__file__).resolve().parent.parent / "brand" / "library" / "feedback.json"


def load():
    return json.loads(FEEDBACK.read_text()) if FEEDBACK.exists() else {"entries": []}


def save(data):
    FEEDBACK.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK.write_text(json.dumps(data, indent=2))


def record(data, cfg):
    entry = {"asset_path": cfg["asset_path"], "template_id": cfg.get("template_id", ""),
             "persona": cfg.get("persona", ""), "rating": cfg["rating"],
             "context": cfg.get("context", ""), "timestamp": datetime.now(timezone.utc).isoformat()}
    data["entries"].append(entry)
    save(data)
    log.info("recorded asset=%s persona=%s rating=%s", entry["asset_path"], entry["persona"], entry["rating"])
    return {"ok": True, "total_entries": len(data["entries"])}


def query(data, cfg):
    persona = cfg.get("persona", "")
    scores = defaultdict(lambda: {"positive": 0, "negative": 0})
    for e in data["entries"]:
        if persona and e.get("persona") != persona:
            continue
        scores[e["asset_path"]][e.get("rating", "neutral")] += 1
    ranked = sorted(
        [{"asset_path": p, **s, "net_score": s["positive"] - s["negative"]} for p, s in scores.items()],
        key=lambda x: x["net_score"], reverse=True)
    log.info("query persona=%s → %d assets", persona, len(ranked))
    return {"results": ranked, "persona": persona}


def boosts(data, cfg):
    persona, counts = cfg.get("persona", ""), defaultdict(float)
    for e in data["entries"]:
        if persona and e.get("persona") != persona:
            continue
        if e.get("rating") == "positive":
            counts[e["asset_path"]] += 0.1
        elif e.get("rating") == "negative":
            counts[e["asset_path"]] -= 0.15
    result = {p: round(v, 4) for p, v in counts.items() if v != 0}
    log.info("boosts persona=%s → %d entries", persona, len(result))
    return {"boosts": result, "persona": persona}


def main():
    try:
        cfg = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log.error("invalid JSON: %s", e); sys.exit(1)
    action, data = cfg.get("action", ""), load()
    if action == "record":
        if not cfg.get("asset_path") or not cfg.get("rating"):
            log.error("record requires asset_path and rating"); sys.exit(1)
        result = record(data, cfg)
    elif action == "query":
        result = query(data, cfg)
    elif action == "boosts":
        result = boosts(data, cfg)
    else:
        log.error("unknown action: %s (expected record|query|boosts)", action); sys.exit(1)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
