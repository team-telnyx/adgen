#!/usr/bin/env python3
"""Smart Template Selector — picks best Abyssale template for a brief.
JSON stdin → JSON stdout (top 3 matches with scores). Under 100 lines."""

import json, sys
from datetime import datetime, timezone
from pathlib import Path


def log(level, msg, **kw):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    extra = " ".join(f"{k}={v}" for k, v in kw.items())
    print(f"[{ts}] [{level}] {msg} {extra}".rstrip(), file=sys.stderr)


def load_templates():
    p = Path(__file__).resolve().parent.parent / "brand" / "template_map.json"
    return json.loads(p.read_text())["templates"]


def parse_format(fmt):
    """Return (normalized_name, width, height) from format string."""
    parts = fmt.lower().replace("-", "_")
    w = h = None
    for seg in parts.split("_"):
        if "x" in seg:
            try:
                dims = seg.split("x"); w, h = int(dims[0]), int(dims[1])
            except (ValueError, IndexError):
                pass
    return parts, w, h


def score(tmpl, brief):
    s = 0.0
    uc = brief.get("use_case", "").lower()
    persona = brief.get("persona", "").lower()
    req_fmt, req_w, req_h = parse_format(brief.get("format", ""))
    has_hero = brief.get("has_hero_image", False)
    uses = [u.lower() for u in tmpl.get("use_cases", [])]
    # Use-case (0-40)
    if uc in uses:
        s += 40
    elif any(uc in u or u in uc for u in uses):
        s += 20
    # Format (0-30)
    fmt_hit = False
    for f in tmpl.get("formats", []):
        fn = f["name"].lower().replace("-", "_")
        if req_fmt and (req_fmt in fn or fn in req_fmt):
            s += 30; fmt_hit = True; break
        if req_w and req_h and f["width"] == req_w and f["height"] == req_h:
            s += 25; fmt_hit = True; break
    if not fmt_hit and req_w and req_h:
        for f in tmpl.get("formats", []):
            if abs(f["width"] / max(f["height"], 1) - req_w / max(req_h, 1)) < 0.1:
                s += 10; break
    # Persona (0-20)
    tp = [p.lower() for p in tmpl.get("personas", [])]
    if persona in tp:
        s += 20
    elif any(persona in p or p in persona for p in tp):
        s += 10
    # Hero compat (0-10)
    has_img = len(tmpl.get("elements", {}).get("image", [])) > 0
    s += 10 if (has_hero and has_img) else (5 if not has_hero and not has_img else 0)
    # Prefer static unless animated requested
    if "animated" not in uc and tmpl.get("type") == "static":
        s += 2
    return s


def main():
    try:
        brief = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log("ERROR", f"Invalid JSON: {e}"); sys.exit(1)
    templates = load_templates()
    log("INFO", f"Scoring {len(templates)} templates", use_case=brief.get("use_case", "?"))
    scored = sorted(
        [({**t, "_score": score(t, brief)}) for t in templates],
        key=lambda x: x["_score"], reverse=True
    )
    top = scored[:3]
    results = [{"id": t["id"], "name": t["name"], "type": t["type"],
                "category": t["category"], "score": t["_score"],
                "formats": t["formats"], "use_cases": t["use_cases"],
                "elements": t["elements"]} for t in top if t["_score"] > 0]
    log("INFO", f"Top match: {results[0]['name']}={results[0]['score']}" if results else "No matches")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
