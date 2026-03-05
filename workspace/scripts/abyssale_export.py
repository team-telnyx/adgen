#!/usr/bin/env python3
"""Abyssale Smart Export — auto-discovers elements, maps fields, generates banners.

Takes template ID + brief fields via JSON stdin. Auto-discovers template
elements and formats, maps brief to elements, generates all formats,
downloads results. Prints JSON manifest to stdout.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


def log(level: str, msg: str, **kw):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    extra = " ".join(f"{k}={v}" for k, v in kw.items())
    print(f"[{ts}] [{level}] {msg} {extra}".rstrip(), file=sys.stderr)


BASE = "https://api.abyssale.com"


def read_secret(name: str) -> str:
    path = Path.home() / ".secrets" / name
    if not path.exists():
        raise FileNotFoundError(f"Secret not found: {path}")
    return path.read_text().strip()


def api_headers(key: str) -> dict:
    return {"x-api-key": key, "Content-Type": "application/json"}


def fetch_template(template_id: str, key: str) -> dict:
    """Fetch template details to discover elements and formats."""
    log("INFO", "Fetching template", template_id=template_id)
    resp = requests.get(
        f"{BASE}/templates/{template_id}", headers=api_headers(key), timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def discover_and_categorize(template_info: dict) -> dict:
    """Auto-discover and categorize template elements."""
    result = {"text": [], "image": [], "logo": [], "container": [], "other": []}
    for el in template_info.get("elements", []):
        el_type = el.get("type", "unknown")
        bucket = result.get(el_type, result["other"])
        entry = {
            "name": el["name"],
            "type": el_type,
            "mandatory": el.get("settings", {}).get("is_mandatory", False),
        }
        # Extract default values
        for attr in el.get("attributes", []):
            vals = attr.get("values", {})
            if vals:
                entry[attr["id"]] = list(vals.values())[0]
        bucket.append(entry)
    return result


def smart_map_elements(brief: dict, hero_url: str | None, discovered: dict) -> dict:
    """Intelligently map brief fields to template elements."""
    mapped = {}

    # Text mapping patterns (lowercase name fragment → brief field)
    text_patterns = {
        "headline": "headline", "title": "headline", "heading": "headline",
        "proper_name": "headline", "name": "headline",
        "subhead": "subhead", "subtitle": "subhead", "lead": "subhead",
        "description": "subhead", "text_0": "subhead",
        "cta": "cta", "button": "cta",
    }

    for el in discovered.get("text", []):
        name = el["name"]
        name_lower = name.lower().replace("-", "_").replace(" ", "_")

        # Try pattern matching
        matched = False
        for pattern, field in text_patterns.items():
            if pattern in name_lower and brief.get(field):
                mapped[name] = {"payload": brief[field]}
                log("INFO", f"Mapped text {name} → {field}")
                matched = True
                break

        if not matched:
            # Infer from default value length
            default = el.get("payload", "")
            if isinstance(default, str):
                if len(default) < 30 and brief.get("headline"):
                    mapped[name] = {"payload": brief["headline"]}
                    log("INFO", f"Mapped text {name} → headline (inferred)")
                elif brief.get("subhead"):
                    mapped[name] = {"payload": brief["subhead"]}
                    log("INFO", f"Mapped text {name} → subhead (inferred)")

    # Map hero image to first non-logo image element
    if hero_url:
        for el in discovered.get("image", []):
            name = el["name"]
            if "logo" not in name.lower():
                mapped[name] = {"image_url": hero_url}
                log("INFO", f"Mapped image {name} → hero_url")
                break

    return mapped


def generate_banner(template_id: str, format_name: str,
                    elements: dict, key: str) -> dict:
    """Generate a single banner format via Abyssale API."""
    log("INFO", "Generating banner", template_id=template_id, format=format_name)
    t0 = time.monotonic()

    resp = requests.post(
        f"{BASE}/banner-builder/{template_id}/generate",
        headers=api_headers(key),
        json={
            "template_format_name": format_name,
            "elements": elements,
        },
        timeout=120,
    )
    resp.raise_for_status()
    result = resp.json()

    elapsed = time.monotonic() - t0
    log("INFO", f"Abyssale responded in {elapsed:.1f}s")
    return result


def download_banner(url: str, output_path: str) -> int:
    """Download a generated banner to local path."""
    log("INFO", "Downloading", url=url[:80])
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(resp.content)
    log("INFO", f"Saved {len(resp.content)} bytes", path=str(out))
    return len(resp.content)


def main():
    try:
        raw = sys.stdin.read()
        cfg = json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        log("ERROR", f"Invalid JSON input: {e}")
        sys.exit(1)

    template_id = cfg.get("template_id", "")
    output_dir = cfg.get("output_dir", "output/export/")
    formats = cfg.get("formats", [])  # If empty, use all available
    hero_url = cfg.get("hero_url", None)

    # Brief fields (can be passed directly or under "brief" key)
    brief = cfg.get("brief", {})
    if not brief:
        brief = {
            "headline": cfg.get("headline", ""),
            "subhead": cfg.get("subhead", ""),
            "cta": cfg.get("cta", ""),
        }

    # Legacy support: direct elements override
    direct_elements = cfg.get("elements", None)

    if not template_id:
        log("ERROR", "No template_id provided")
        sys.exit(1)

    try:
        key = read_secret("abyssale")

        # Step 1: Fetch template
        template_info = fetch_template(template_id, key)
        available_formats = [f["id"] for f in template_info.get("formats", [])]
        log("INFO", f"Template loaded",
            name=template_info.get("name", "?"),
            available_formats=str(available_formats))

        # Use all formats if none specified
        if not formats:
            formats = available_formats
            log("INFO", f"Using all available formats: {formats}")

        # Step 2: Discover elements and build mapping
        if direct_elements:
            # Legacy mode: use provided elements directly
            element_map = {}
            for name, value in direct_elements.items():
                if "image_url" in value:
                    element_map[name] = {"image_url": value["image_url"]}
                elif "text" in value:
                    element_map[name] = {"payload": value["text"]}
                elif "payload" in value:
                    element_map[name] = {"payload": value["payload"]}
            log("INFO", f"Using {len(element_map)} direct elements")
        else:
            # Smart mode: auto-discover and map
            discovered = discover_and_categorize(template_info)
            element_map = smart_map_elements(brief, hero_url, discovered)
            log("INFO", f"Smart-mapped {len(element_map)} elements")

        # Step 3: Generate for each format
        downloaded = []
        for fmt_name in formats:
            if fmt_name not in available_formats:
                log("WARN", f"Format {fmt_name} not available, skipping")
                continue

            try:
                result = generate_banner(template_id, fmt_name, element_map, key)
                cdn_url = (result.get("file", {}).get("cdn_url")
                           or result.get("file", {}).get("url", ""))

                if not cdn_url:
                    log("WARN", f"No URL in response for {fmt_name}")
                    continue

                ext = "jpeg" if "jpeg" in cdn_url else "png"
                filepath = str(Path(output_dir) / f"{fmt_name}.{ext}")
                size = download_banner(cdn_url, filepath)

                downloaded.append({
                    "format": fmt_name,
                    "path": filepath,
                    "size_bytes": size,
                    "cdn_url": cdn_url,
                    "abyssale_id": result.get("id", ""),
                    "width": result.get("format", {}).get("width"),
                    "height": result.get("format", {}).get("height"),
                })
            except Exception as e:
                log("ERROR", f"Failed to generate {fmt_name}: {e}")
                continue

        manifest = {
            "template_id": template_id,
            "template_name": template_info.get("name", ""),
            "formats_requested": formats,
            "formats_generated": len(downloaded),
            "files": downloaded,
            "element_mapping": {k: list(v.keys())[0] for k, v in element_map.items()},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        print(json.dumps(manifest, indent=2))
        sys.exit(0)

    except requests.HTTPError as e:
        body = ""
        if e.response is not None:
            body = e.response.text[:500]
        log("ERROR", f"API error: {e} — {body}")
        sys.exit(1)
    except Exception as e:
        log("ERROR", f"Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
