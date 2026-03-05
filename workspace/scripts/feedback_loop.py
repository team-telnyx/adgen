#!/usr/bin/env python3
"""Feedback Loop — record/query/boosts/summary for asset feedback. JSON stdin/stdout."""
import json, logging, sys, time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SZ", level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("feedback_loop")
logging.Formatter.converter = time.gmtime
FEEDBACK = Path(__file__).resolve().parent.parent / "brand" / "library" / "feedback.json"


def load():
    if FEEDBACK.exists():
        data = json.loads(FEEDBACK.read_text())
        # Ensure structure
        if "entries" not in data:
            data["entries"] = data.get("records", [])
        return data
    return {"entries": []}


def save(data):
    FEEDBACK.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK.write_text(json.dumps(data, indent=2))


def record(data, cfg):
    # Validate required fields
    for field in ("asset_path", "rating", "template_id"):
        if not cfg.get(field):
            log.error("record requires %s", field)
            sys.exit(1)
    entry = {
        "asset_path": cfg["asset_path"],
        "template_id": cfg["template_id"],
        "persona": cfg.get("persona", ""),
        "rating": cfg["rating"],
        "requester": cfg.get("requester", ""),
        "headline": cfg.get("headline", ""),
        "context": cfg.get("context", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    data["entries"].append(entry)
    save(data)
    log.info("recorded asset=%s persona=%s rating=%s requester=%s",
             entry["asset_path"], entry["persona"], entry["rating"], entry["requester"])
    return {"ok": True, "total_entries": len(data["entries"])}


def query(data, cfg):
    persona = cfg.get("persona", "")
    scores = defaultdict(lambda: {"positive": 0, "negative": 0, "revision": 0})
    for e in data["entries"]:
        if persona and e.get("persona") != persona:
            continue
        rating = e.get("rating", "neutral")
        if rating in ("positive", "negative", "revision"):
            scores[e["asset_path"]][rating] += 1
    ranked = sorted(
        [{"asset_path": p, **s, "net_score": s["positive"] - s["negative"] - s["revision"]}
         for p, s in scores.items()],
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
        elif e.get("rating") == "revision":
            counts[e["asset_path"]] -= 0.05
    result = {p: round(v, 4) for p, v in counts.items() if v != 0}
    log.info("boosts persona=%s → %d entries", persona, len(result))
    return {"boosts": result, "persona": persona}


def summary(data, cfg):
    """Per-persona stats: total feedbacks, approval rate, top/worst assets."""
    persona_stats = defaultdict(lambda: {
        "total": 0, "positive": 0, "negative": 0, "revision": 0,
        "assets": defaultdict(lambda: {"positive": 0, "negative": 0, "revision": 0}),
    })
    template_stats = defaultdict(lambda: {"total": 0, "positive": 0, "negative": 0, "revision": 0})
    now = datetime.now(timezone.utc)
    last_7_days = {"total": 0, "positive": 0}
    all_time = {"total": 0, "positive": 0}

    for e in data["entries"]:
        persona = e.get("persona", "unknown")
        rating = e.get("rating", "neutral")
        asset = e.get("asset_path", "unknown")
        template = e.get("template_id", "unknown")

        ps = persona_stats[persona]
        ps["total"] += 1
        if rating in ("positive", "negative", "revision"):
            ps[rating] += 1
            ps["assets"][asset][rating] += 1

        ts = template_stats[template]
        ts["total"] += 1
        if rating in ("positive", "negative", "revision"):
            ts[rating] += 1

        all_time["total"] += 1
        if rating == "positive":
            all_time["positive"] += 1

        # Check if within last 7 days
        try:
            entry_time = datetime.fromisoformat(e.get("timestamp", ""))
            if (now - entry_time) <= timedelta(days=7):
                last_7_days["total"] += 1
                if rating == "positive":
                    last_7_days["positive"] += 1
        except (ValueError, TypeError):
            pass

    # Build per-persona summary
    personas = {}
    for persona, ps in persona_stats.items():
        approval_rate = round(ps["positive"] / ps["total"] * 100, 1) if ps["total"] > 0 else 0.0
        asset_scores = [
            {"asset_path": a, "net_score": s["positive"] - s["negative"] - s["revision"], **s}
            for a, s in ps["assets"].items()
        ]
        asset_scores.sort(key=lambda x: x["net_score"], reverse=True)
        personas[persona] = {
            "total": ps["total"],
            "positive": ps["positive"],
            "negative": ps["negative"],
            "revision": ps["revision"],
            "approval_rate": approval_rate,
            "top_assets": asset_scores[:3],
            "worst_assets": asset_scores[-3:] if len(asset_scores) > 3 else list(reversed(asset_scores[-3:])),
        }

    # Build per-template summary
    templates = {}
    for tid, ts in template_stats.items():
        approval_rate = round(ts["positive"] / ts["total"] * 100, 1) if ts["total"] > 0 else 0.0
        templates[tid] = {
            "total": ts["total"],
            "positive": ts["positive"],
            "negative": ts["negative"],
            "revision": ts["revision"],
            "approval_rate": approval_rate,
        }

    overall_rate = round(all_time["positive"] / all_time["total"] * 100, 1) if all_time["total"] > 0 else 0.0
    last7_rate = round(last_7_days["positive"] / last_7_days["total"] * 100, 1) if last_7_days["total"] > 0 else 0.0

    result = {
        "personas": personas,
        "templates": templates,
        "overall": {
            "total_feedbacks": all_time["total"],
            "approval_rate": overall_rate,
            "last_7_days": {
                "total": last_7_days["total"],
                "approval_rate": last7_rate,
            },
        },
    }
    log.info("summary: %d personas, %d templates, %d total feedbacks",
             len(personas), len(templates), all_time["total"])
    return result


def main():
    try:
        cfg = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log.error("invalid JSON: %s", e)
        sys.exit(1)
    action, data = cfg.get("action", ""), load()
    if action == "record":
        if not cfg.get("asset_path") or not cfg.get("rating"):
            log.error("record requires asset_path and rating")
            sys.exit(1)
        result = record(data, cfg)
    elif action == "query":
        result = query(data, cfg)
    elif action == "boosts":
        result = boosts(data, cfg)
    elif action == "summary":
        result = summary(data, cfg)
    else:
        log.error("unknown action: %s (expected record|query|boosts|summary)", action)
        sys.exit(1)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
