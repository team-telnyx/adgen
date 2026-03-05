#!/usr/bin/env python3
"""Variant Engine — generate N ad variants from a single brief.

Takes a brief + variation axes and produces a matrix of smart combinations,
rendering each via Pillow (speed over quality — Abyssale for final winner only).

JSON stdin → JSON stdout (manifest with all variant files + params).
"""

import itertools
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO,
    stream=sys.stderr,
)
log = logging.getLogger("variant_engine")
logging.Formatter.converter = time.gmtime

SCRIPTS_DIR = Path(__file__).resolve().parent
WORKSPACE = SCRIPTS_DIR.parent

# Import sibling modules directly for speed (no subprocess overhead)
sys.path.insert(0, str(SCRIPTS_DIR))
import search_library
import feedback_loop as fb_loop
import render as render_engine

# ---------------------------------------------------------------------------
# Brand palette — accent color options
# ---------------------------------------------------------------------------
BRAND_ACCENTS = {
    "citron": "#D4E510",
    "green": "#00C26E",
    "pink": "#FF6B9D",
}

# Pillow template names from render.py
PILLOW_TEMPLATES = [
    "dark-hero-left",
    "split-panel",
    "stats-hero",
    "full-bleed-dark",
    "gradient-accent",
    "light-minimal",
    "product-screenshot",
    "testimonial",
]


# ---------------------------------------------------------------------------
# Headline variations
# ---------------------------------------------------------------------------
def generate_headline_variants(headline: str) -> list[str]:
    """Generate 2-3 headline variations from the original."""
    variants = [headline]

    # Shorter version: strip articles, compress
    words = headline.split()
    if len(words) > 4:
        # Drop filler words for a punchier version
        short = " ".join(w for w in words if w.lower() not in {"the", "a", "an", "your", "our", "and"})
        if short != headline and len(short) > 5:
            variants.append(short)

    # Stat-driven reframe: if there's a number, lead with it
    numbers = re.findall(r'\d+[%$KkMm]?', headline)
    if numbers:
        stat = numbers[0]
        # "The X% Advantage" pattern
        variants.append(f"The {stat} Advantage")
    else:
        # If no stat, try a "How to..." reframe
        if not headline.lower().startswith("how"):
            action_words = headline.split()[:3]
            variants.append(f"How to {' '.join(action_words)}")

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            unique.append(v)

    return unique[:3]


# ---------------------------------------------------------------------------
# Template selection — use select_template logic but via Pillow names
# ---------------------------------------------------------------------------
def get_best_templates(persona: str, has_hero: bool, feedback_boosts: dict) -> list[str]:
    """Return top 2-3 Pillow templates for the persona, informed by feedback."""
    # Default ranking by persona type
    if "cio" in persona.lower() or "enterprise" in persona.lower():
        preferred = ["dark-hero-left", "stats-hero", "split-panel", "gradient-accent"]
    elif "developer" in persona.lower() or "dev" in persona.lower():
        preferred = ["dark-hero-left", "full-bleed-dark", "stats-hero", "product-screenshot"]
    elif "marketer" in persona.lower() or "marketing" in persona.lower():
        preferred = ["split-panel", "light-minimal", "gradient-accent", "dark-hero-left"]
    else:
        preferred = ["dark-hero-left", "split-panel", "stats-hero", "gradient-accent"]

    # Apply feedback boosts — templates with positive history get priority
    template_scores = {}
    for t in PILLOW_TEMPLATES:
        base = preferred.index(t) if t in preferred else len(preferred)
        # Lower index = better; invert for scoring
        score = max(0, 10 - base)
        # Check feedback for this template+persona combo
        boost = feedback_boosts.get(t, 0.0)
        score += boost * 5  # Amplify feedback signal
        template_scores[t] = score

    ranked = sorted(template_scores.items(), key=lambda x: x[1], reverse=True)

    # If no hero image, apply a mild penalty to hero-dependent templates
    # but don't completely remove them — they still work (just no hero composited)
    if not has_hero:
        hero_dependent = {"dark-hero-left", "split-panel", "full-bleed-dark", "product-screenshot"}
        ranked = sorted(
            [(t, s - 1.0) if t in hero_dependent else (t, s) for t, s in ranked],
            key=lambda x: x[1],
            reverse=True,
        )

    return [t[0] for t in ranked[:3]]


# ---------------------------------------------------------------------------
# Asset search — find best hero images
# ---------------------------------------------------------------------------
def find_hero_images(brief: dict, limit: int = 2) -> list[dict]:
    """Search brand library for matching hero images."""
    query_parts = [
        brief.get("persona", ""),
        brief.get("headline", ""),
        brief.get("campaign", ""),
    ]
    query = " ".join(filter(None, query_parts))
    if not query.strip():
        return []

    try:
        catalog = search_library.load_catalog()
        emb_lookup, emb_source = search_library.build_embedding_lookup(catalog)
        feedback = search_library.load_feedback()

        results = search_library.search(
            query=query,
            catalog=catalog,
            emb_lookup=emb_lookup,
            feedback=feedback,
            limit=limit,
            type_filter="image",
            persona=brief.get("persona"),
        )
        log.info("found %d hero candidates", len(results))
        return results
    except Exception as e:
        log.warning("hero search failed: %s — will render without hero", e)
        return []


# ---------------------------------------------------------------------------
# Feedback-informed template boosts
# ---------------------------------------------------------------------------
def get_template_boosts(persona: str) -> dict:
    """Query feedback_loop for template-level boosts for this persona."""
    try:
        data = fb_loop.load()
        entries = data.get("entries", [])
        template_scores = {}
        for entry in entries:
            if persona and entry.get("persona") != persona:
                continue
            tid = entry.get("template_id", "")
            if not tid:
                continue
            if tid not in template_scores:
                template_scores[tid] = 0.0
            rating = entry.get("rating", "")
            if rating == "positive":
                template_scores[tid] += 1.0
            elif rating == "negative":
                template_scores[tid] -= 1.0
            elif rating == "revision":
                template_scores[tid] -= 0.5
        log.info("template boosts for persona=%s: %s", persona, template_scores)
        return template_scores
    except Exception as e:
        log.warning("feedback boosts failed: %s", e)
        return {}


# ---------------------------------------------------------------------------
# Smart combination selection
# ---------------------------------------------------------------------------
def select_combinations(
    headlines: list[str],
    templates: list[str],
    accent_colors: list[tuple[str, str]],  # (name, hex)
    hero_images: list[dict],  # search results
    n_variants: int,
    feedback_boosts: dict,
) -> list[dict]:
    """Select the best N combinations — not random, not exhaustive.

    Strategy:
    1. Always include the top-ranked combo (best template + best color + original headline)
    2. Ensure each axis varies at least once
    3. Fill remaining slots with diverse combos (maximize difference from existing)
    """
    # Build all possible combos
    all_combos = []
    hero_options = hero_images if hero_images else [None]

    for headline, template, (color_name, color_hex), hero in itertools.product(
        headlines, templates, accent_colors, hero_options,
    ):
        combo = {
            "headline": headline,
            "template": template,
            "accent_color_name": color_name,
            "accent_color": color_hex,
            "hero_image": hero,
        }
        # Score this combo
        score = 0.0
        # Prefer top-ranked template
        if template == templates[0]:
            score += 3.0
        elif template == templates[1] if len(templates) > 1 else False:
            score += 1.5
        # Prefer original headline for safety
        if headline == headlines[0]:
            score += 1.0
        # Feedback boost for template
        score += feedback_boosts.get(template, 0.0)
        # Hero image score
        if hero and hero.get("score", 0) > 0.5:
            score += hero["score"]

        combo["_score"] = score
        all_combos.append(combo)

    # Sort by score descending
    all_combos.sort(key=lambda c: c["_score"], reverse=True)

    if len(all_combos) <= n_variants:
        return all_combos[:n_variants]

    # Greedy diverse selection
    selected = [all_combos[0]]  # Always pick the top combo

    def combo_diff(a, b):
        """Count how many axes differ between two combos."""
        diff = 0
        if a["headline"] != b["headline"]:
            diff += 1
        if a["template"] != b["template"]:
            diff += 1
        if a["accent_color"] != b["accent_color"]:
            diff += 1
        h_a = a["hero_image"]["path"] if a["hero_image"] else None
        h_b = b["hero_image"]["path"] if b["hero_image"] else None
        if h_a != h_b:
            diff += 1
        return diff

    for _ in range(n_variants - 1):
        best_candidate = None
        best_diversity = -1
        best_score = -1

        for combo in all_combos:
            if any(
                combo["headline"] == s["headline"]
                and combo["template"] == s["template"]
                and combo["accent_color"] == s["accent_color"]
                and combo.get("hero_image") == s.get("hero_image")
                for s in selected
            ):
                continue  # Skip exact duplicates

            # Minimum difference from all selected
            min_diff = min(combo_diff(combo, s) for s in selected)
            # Prefer combos that differ on more axes, break ties by score
            if (min_diff > best_diversity) or (
                min_diff == best_diversity and combo["_score"] > best_score
            ):
                best_candidate = combo
                best_diversity = min_diff
                best_score = combo["_score"]

        if best_candidate:
            selected.append(best_candidate)
        else:
            break

    return selected


# ---------------------------------------------------------------------------
# Render a single variant via Pillow
# ---------------------------------------------------------------------------
def render_variant(
    variant_num: int,
    combo: dict,
    brief: dict,
    output_dir: str,
    fmt: str = "linkedin_1200x1200",
) -> dict:
    """Render one variant using render.py (Pillow) and return file info."""
    hero_path = None
    if combo["hero_image"]:
        hero_path = combo["hero_image"].get("path", "")

    output_file = f"{output_dir}/V{variant_num}.png"

    render_data = {
        "template": combo["template"],
        "format": fmt,
        "background": "#000000" if combo["template"] in render_engine.DARK_TEMPLATES else "#F5F0E8",
        "headline": combo["headline"],
        "subhead": brief.get("subhead", ""),
        "cta": brief.get("cta", ""),
        "accent_color": combo["accent_color"],
        "hero_image": hero_path,
        "output": output_file,
    }

    try:
        render_engine.render(render_data)
        abs_path = str(WORKSPACE / output_file) if not Path(output_file).is_absolute() else output_file
        log.info("V%d rendered → %s", variant_num, abs_path)
        return {
            "path": abs_path,
            "rendered": True,
        }
    except Exception as e:
        log.error("V%d render failed: %s", variant_num, e)
        return {
            "path": "",
            "rendered": False,
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# Build variant label
# ---------------------------------------------------------------------------
def variant_label(num: int, combo: dict) -> str:
    """Human-readable label: V1: dark-hero-left / citron / 'Cut Wait Times 40%'"""
    headline_short = combo["headline"][:40] + ("..." if len(combo["headline"]) > 40 else "")
    hero_tag = ""
    if combo["hero_image"]:
        hero_name = Path(combo["hero_image"].get("path", "unknown")).stem
        hero_tag = f" / hero:{hero_name}"
    return f"V{num}: {combo['template']} / {combo['accent_color_name']} / \"{headline_short}\"{hero_tag}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def generate_variants(cfg: dict) -> dict:
    """Main entry point. Takes full config, returns manifest."""
    t0 = time.monotonic()

    brief = cfg["brief"]
    n_variants = cfg.get("variants", 4)
    vary_axes = cfg.get("vary", ["headline", "template", "accent_color", "hero_image"])
    output_dir = cfg.get("output_dir", "output/variants")
    render_fmt = cfg.get("format", "linkedin_1200x1200")
    persona = brief.get("persona", "")

    log.info(
        "variant engine start: variants=%d vary=%s persona=%s",
        n_variants, vary_axes, persona,
    )

    # 1. Get feedback boosts for smart selection
    feedback_boosts = get_template_boosts(persona) if persona else {}

    # 2. Generate headline options
    if "headline" in vary_axes:
        headlines = generate_headline_variants(brief["headline"])
    else:
        headlines = [brief["headline"]]
    log.info("headlines: %s", headlines)

    # 3. Get template options
    hero_images = []
    if "hero_image" in vary_axes:
        hero_images = find_hero_images(brief, limit=2)

    if "template" in vary_axes:
        templates = get_best_templates(persona, bool(hero_images), feedback_boosts)
    else:
        templates = ["dark-hero-left"]
    log.info("templates: %s", templates)

    # 4. Get accent color options
    if "accent_color" in vary_axes:
        accent_colors = [("citron", BRAND_ACCENTS["citron"]), ("green", BRAND_ACCENTS["green"])]
    else:
        accent_colors = [("citron", BRAND_ACCENTS["citron"])]

    # 5. Select smart combinations
    combos = select_combinations(
        headlines=headlines,
        templates=templates,
        accent_colors=accent_colors,
        hero_images=hero_images,
        n_variants=n_variants,
        feedback_boosts=feedback_boosts,
    )
    log.info("selected %d combinations from matrix", len(combos))

    # 6. Render each variant
    # Ensure output directory exists
    out_path = WORKSPACE / output_dir
    out_path.mkdir(parents=True, exist_ok=True)

    variants = []
    for i, combo in enumerate(combos, 1):
        label = variant_label(i, combo)
        render_result = render_variant(i, combo, brief, output_dir, render_fmt)

        variant_entry = {
            "variant": i,
            "label": label,
            "headline": combo["headline"],
            "template": combo["template"],
            "accent_color_name": combo["accent_color_name"],
            "accent_color": combo["accent_color"],
            "hero_image": combo["hero_image"]["path"] if combo["hero_image"] else None,
            "path": render_result["path"],
            "rendered": render_result["rendered"],
        }
        if not render_result["rendered"]:
            variant_entry["error"] = render_result.get("error", "")
        variants.append(variant_entry)
        log.info("  %s → %s", label, "OK" if render_result["rendered"] else "FAILED")

    elapsed = time.monotonic() - t0
    manifest = {
        "brief": brief,
        "variants": variants,
        "total_variants": len(variants),
        "rendered_ok": sum(1 for v in variants if v["rendered"]),
        "vary_axes": vary_axes,
        "output_dir": str(out_path),
        "format": render_fmt,
        "feedback_boosts_applied": bool(feedback_boosts),
        "hero_images_found": len(hero_images),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 2),
    }

    log.info(
        "variant engine complete: %d/%d rendered in %.2fs",
        manifest["rendered_ok"], manifest["total_variants"], elapsed,
    )
    return manifest


def main():
    try:
        cfg = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log.error("invalid JSON input: %s", e)
        sys.exit(1)

    if "brief" not in cfg or "headline" not in cfg.get("brief", {}):
        log.error("missing required field: brief.headline")
        sys.exit(1)

    try:
        manifest = generate_variants(cfg)
        print(json.dumps(manifest, indent=2))
    except Exception as e:
        log.error("variant engine failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
