#!/usr/bin/env python3
"""Feedback Summary — human-readable summary of feedback.json for AdGen learning.
Run standalone or import. Reads feedback.json, outputs per-persona and per-template stats."""
import json, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

FEEDBACK = Path(__file__).resolve().parent.parent / "brand" / "library" / "feedback.json"


def load():
    if not FEEDBACK.exists():
        return {"entries": []}
    data = json.loads(FEEDBACK.read_text())
    if "entries" not in data:
        data["entries"] = data.get("records", [])
    return data


def summarize(data):
    now = datetime.now(timezone.utc)
    persona_stats = defaultdict(lambda: {
        "total": 0, "positive": 0, "negative": 0, "revision": 0,
        "assets": defaultdict(lambda: {"positive": 0, "negative": 0, "revision": 0}),
    })
    template_stats = defaultdict(lambda: {"total": 0, "positive": 0, "negative": 0, "revision": 0})
    last_7 = {"total": 0, "positive": 0}
    all_time = {"total": 0, "positive": 0}

    for e in data.get("entries", []):
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

        try:
            ts_parsed = datetime.fromisoformat(e.get("timestamp", ""))
            if (now - ts_parsed) <= timedelta(days=7):
                last_7["total"] += 1
                if rating == "positive":
                    last_7["positive"] += 1
        except (ValueError, TypeError):
            pass

    return persona_stats, template_stats, all_time, last_7


def format_report(persona_stats, template_stats, all_time, last_7):
    lines = []
    lines.append("=" * 60)
    lines.append("  ADGEN FEEDBACK SUMMARY")
    lines.append("=" * 60)

    # Overall
    rate = round(all_time["positive"] / all_time["total"] * 100, 1) if all_time["total"] > 0 else 0
    rate_7 = round(last_7["positive"] / last_7["total"] * 100, 1) if last_7["total"] > 0 else 0
    lines.append(f"\n  Overall: {all_time['total']} feedbacks, {rate}% approval rate")
    lines.append(f"  Last 7 days: {last_7['total']} feedbacks, {rate_7}% approval rate")

    # Per persona
    lines.append(f"\n{'─' * 60}")
    lines.append("  PER PERSONA")
    lines.append(f"{'─' * 60}")
    for persona, ps in sorted(persona_stats.items()):
        approval = round(ps["positive"] / ps["total"] * 100, 1) if ps["total"] > 0 else 0
        lines.append(f"\n  [{persona}]")
        lines.append(f"    Total: {ps['total']}  |  ✅ {ps['positive']}  |  ❌ {ps['negative']}  |  🔄 {ps['revision']}  |  Rate: {approval}%")

        # Top/bottom assets
        asset_scores = [
            (a, s["positive"] - s["negative"] - s["revision"])
            for a, s in ps["assets"].items()
        ]
        asset_scores.sort(key=lambda x: x[1], reverse=True)
        if asset_scores:
            lines.append(f"    Top 3:")
            for a, score in asset_scores[:3]:
                lines.append(f"      {'+' if score >= 0 else ''}{score}  {a}")
            if len(asset_scores) > 3:
                lines.append(f"    Bottom 3:")
                for a, score in asset_scores[-3:]:
                    lines.append(f"      {'+' if score >= 0 else ''}{score}  {a}")

    # Per template
    lines.append(f"\n{'─' * 60}")
    lines.append("  PER TEMPLATE")
    lines.append(f"{'─' * 60}")
    sorted_templates = sorted(template_stats.items(),
                               key=lambda x: x[1]["positive"] / max(x[1]["total"], 1), reverse=True)
    for tid, ts in sorted_templates:
        approval = round(ts["positive"] / ts["total"] * 100, 1) if ts["total"] > 0 else 0
        lines.append(f"  {tid}: {ts['total']} feedbacks, {approval}% approval  (✅{ts['positive']} ❌{ts['negative']} 🔄{ts['revision']})")

    lines.append(f"\n{'=' * 60}\n")
    return "\n".join(lines)


def main():
    data = load()
    if not data.get("entries"):
        print("No feedback data found.")
        sys.exit(0)

    persona_stats, template_stats, all_time, last_7 = summarize(data)

    # If --json flag, output structured JSON
    if "--json" in sys.argv:
        personas = {}
        for persona, ps in persona_stats.items():
            approval = round(ps["positive"] / ps["total"] * 100, 1) if ps["total"] > 0 else 0
            asset_scores = sorted(
                [{"asset_path": a, "net_score": s["positive"] - s["negative"] - s["revision"], **s}
                 for a, s in ps["assets"].items()],
                key=lambda x: x["net_score"], reverse=True
            )
            personas[persona] = {
                "total": ps["total"], "positive": ps["positive"],
                "negative": ps["negative"], "revision": ps["revision"],
                "approval_rate": approval,
                "top_assets": asset_scores[:3],
                "worst_assets": list(reversed(asset_scores[-3:])) if len(asset_scores) > 3 else list(reversed(asset_scores)),
            }
        templates = {}
        for tid, ts in template_stats.items():
            approval = round(ts["positive"] / ts["total"] * 100, 1) if ts["total"] > 0 else 0
            templates[tid] = {"total": ts["total"], "positive": ts["positive"],
                              "negative": ts["negative"], "revision": ts["revision"],
                              "approval_rate": approval}
        rate = round(all_time["positive"] / all_time["total"] * 100, 1) if all_time["total"] > 0 else 0
        rate_7 = round(last_7["positive"] / last_7["total"] * 100, 1) if last_7["total"] > 0 else 0
        print(json.dumps({
            "personas": personas, "templates": templates,
            "overall": {"total_feedbacks": all_time["total"], "approval_rate": rate,
                        "last_7_days": {"total": last_7["total"], "approval_rate": rate_7}},
        }, indent=2))
    else:
        print(format_report(persona_stats, template_stats, all_time, last_7))


if __name__ == "__main__":
    main()
