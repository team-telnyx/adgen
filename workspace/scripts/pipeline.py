#!/usr/bin/env python3
"""AdGen Pipeline — Brief-to-Assets orchestrator.

Reads a campaign brief from stdin, orchestrates render, metadata, export,
and optional variant generation. Prints a JSON manifest to stdout.
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO,
    stream=sys.stderr,
)
log = logging.getLogger("pipeline")
logging.Formatter.converter = time.gmtime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).resolve().parent
WORKSPACE = SCRIPTS_DIR.parent
BRAND_PALETTE = ["#00C26E", "#D4E510", "#FF6B9D"]
ALL_TEMPLATES = [
    "dark-hero-left", "light-minimal", "split-panel", "full-bleed-dark",
    "stats-hero", "gradient-accent", "testimonial", "product-screenshot",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_script(name: str, payload: dict) -> dict:
    """Run a sibling script with JSON on stdin, return parsed stdout."""
    script = SCRIPTS_DIR / name
    log.info("calling %s", name)
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=300,
    )
    if proc.stderr:
        for line in proc.stderr.strip().splitlines():
            log.info("  [%s] %s", name, line)
    if proc.returncode != 0:
        raise RuntimeError(f"{name} exited {proc.returncode}: {proc.stderr[-500:]}")
    if proc.stdout.strip():
        return json.loads(proc.stdout)
    return {}


def pick_variant_params(variant_idx: int, base_template: str | None, base_accent: str | None):
    """Rotate accent colors and optionally templates for variant N."""
    accent = BRAND_PALETTE[variant_idx % len(BRAND_PALETTE)]
    if base_accent and variant_idx == 0:
        accent = base_accent
    template = base_template
    if not template:
        template = ALL_TEMPLATES[variant_idx % len(ALL_TEMPLATES)]
    return template, accent


def build_render_payload(brief: dict, template: str, accent: str, fmt: str,
                         hero_image: str, bg: str, output: str) -> dict:
    """Build the JSON payload for render.py."""
    return {
        "template": template,
        "format": fmt,
        "background": bg,
        "headline": brief["headline"],
        "subhead": brief.get("subhead", ""),
        "cta": brief.get("cta", ""),
        "accent_color": accent,
        "hero_image": hero_image,
        "output": output,
    }


def build_metadata_payload(asset_path: str, brief: dict, template: str,
                           accent: str, fmt: str, variant: int) -> dict:
    """Build the JSON payload for asset_metadata.py."""
    return {
        "asset_path": asset_path,
        "template": template,
        "format": fmt,
        "accent_color": accent,
        "variant": variant,
        "campaign": brief.get("campaign", ""),
        "persona": brief.get("persona", ""),
        "headline": brief["headline"],
        "subhead": brief.get("subhead", ""),
        "cta": brief.get("cta", ""),
    }

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(cfg: dict) -> dict:
    t0 = time.time()
    brief = cfg["brief"]
    base_template = cfg.get("template")
    base_accent = cfg.get("accent_color")
    hero_image = cfg.get("hero_image", "")
    generate_hero = cfg.get("generate_hero", False)
    hero_prompt = cfg.get("hero_prompt", "")
    formats = cfg.get("formats", ["linkedin_1200x1200"])
    num_variants = max(1, cfg.get("variants", 1))
    output_dir = cfg.get("output_dir", "output/campaign")
    bg = cfg.get("background", "#000000")

    master_format = formats[0]
    extra_formats = formats[1:] if len(formats) > 1 else []

    log.info("pipeline start variants=%d formats=%d output=%s", num_variants, len(formats), output_dir)

    # Step 1: Generate hero if requested
    if generate_hero and hero_prompt:
        log.info("generating hero image via AI")
        gen_out = str(WORKSPACE / output_dir / "generated_hero.png")
        result = run_script("generate_image.py", {
            "prompt": hero_prompt,
            "output": gen_out,
            "provider": cfg.get("hero_provider", "dalle"),
        })
        hero_image = result.get("path", gen_out)
        log.info("hero generated path=%s", hero_image)

    manifest = {
        "brief": brief,
        "variants": [],
        "total_files": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    for vi in range(num_variants):
        template, accent = pick_variant_params(vi, base_template, base_accent)
        variant_label = f"v{vi + 1}"
        variant_dir = output_dir if num_variants == 1 else f"{output_dir}/{variant_label}"
        variant_files = []

        log.info("variant %s template=%s accent=%s", variant_label, template, accent)

        # Step 2: Render master format
        master_out = f"{variant_dir}/{master_format}.png"
        render_payload = build_render_payload(
            brief, template, accent, master_format, hero_image, bg, master_out,
        )
        run_script("render.py", render_payload)
        master_abs = str(WORKSPACE / master_out)
        variant_files.append({"format": master_format, "path": master_abs})
        log.info("master rendered path=%s", master_abs)

        # Step 3: Metadata sidecar
        meta_payload = build_metadata_payload(
            master_abs, brief, template, accent, master_format, vi,
        )
        meta_result = run_script("asset_metadata.py", meta_payload)
        variant_files.append({
            "format": "metadata",
            "path": meta_result.get("meta_path", ""),
        })

        # Step 4: Extra formats via Abyssale (if configured) or render fallback
        for fmt in extra_formats:
            fmt_out = f"{variant_dir}/{fmt}.png"
            fmt_payload = build_render_payload(
                brief, template, accent, fmt, hero_image, bg, fmt_out,
            )
            run_script("render.py", fmt_payload)
            fmt_abs = str(WORKSPACE / fmt_out)
            variant_files.append({"format": fmt, "path": fmt_abs})
            log.info("format rendered fmt=%s path=%s", fmt, fmt_abs)

            # Metadata for each format
            fmt_meta = build_metadata_payload(
                fmt_abs, brief, template, accent, fmt, vi,
            )
            run_script("asset_metadata.py", fmt_meta)

        manifest["variants"].append({
            "variant": variant_label,
            "template": template,
            "accent_color": accent,
            "files": variant_files,
        })
        manifest["total_files"] += len(variant_files)

    elapsed = time.time() - t0
    manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
    manifest["elapsed_seconds"] = round(elapsed, 1)
    log.info("pipeline complete variants=%d files=%d elapsed=%.1fs",
             num_variants, manifest["total_files"], elapsed)
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
        manifest = run_pipeline(cfg)
        print(json.dumps(manifest, indent=2))
    except Exception as e:
        log.error("pipeline failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
