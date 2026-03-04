#!/usr/bin/env python3
"""Abyssale Multi-Format Export.

Takes template ID, element values, and format list via JSON stdin.
Fetches template details, generates banners, downloads all variants.
Prints JSON manifest to stdout.
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
    log("INFO", f"Fetching template", template_id=template_id)
    resp = requests.get(
        f"{BASE}/templates/{template_id}", headers=api_headers(key), timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def build_generation_payload(
    template_id: str, elements: dict, formats: list, template_info: dict
) -> dict:
    """Build multi-format generation request payload."""
    element_payloads = {}
    for name, value in elements.items():
        if "image_url" in value:
            element_payloads[name] = {"image_url": value["image_url"]}
        elif "text" in value:
            element_payloads[name] = {"payload": value["text"]}

    # Build format list with element overrides
    format_payloads = []
    for fmt_name in formats:
        format_payloads.append({"format_name": fmt_name, "elements": element_payloads})

    return {"template_id": template_id, "formats": format_payloads}


def generate_banners(payload: dict, key: str) -> dict:
    """Call Abyssale generation endpoint."""
    log("INFO", "Requesting banner generation", formats=str(len(payload["formats"])))
    t0 = time.monotonic()

    resp = requests.post(
        f"{BASE}/banner/generate-multi-format",
        headers=api_headers(key),
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    result = resp.json()

    elapsed = time.monotonic() - t0
    log("INFO", f"Abyssale responded in {elapsed:.1f}s")
    return result


def download_banners(generation_result: dict, output_dir: str) -> list:
    """Download all generated banner images."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    downloaded = []

    banners = generation_result.get("banners", [])
    if not banners:
        # Try alternate response shapes
        banners = generation_result.get("data", {}).get("banners", [])

    for banner in banners:
        fmt_name = banner.get("format_name", "unknown")
        url = banner.get("generation_url") or banner.get("url", "")
        if not url:
            log("WARN", f"No URL for format {fmt_name}, skipping")
            continue

        ext = "png"
        if ".jpg" in url or ".jpeg" in url:
            ext = "jpg"

        filename = f"{fmt_name}.{ext}"
        filepath = out / filename

        log("INFO", f"Downloading {fmt_name}", url=url[:80])
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        filepath.write_bytes(resp.content)
        log("INFO", f"Saved {len(resp.content)} bytes", path=str(filepath))

        downloaded.append(
            {
                "format": fmt_name,
                "path": str(filepath),
                "size_bytes": len(resp.content),
                "url": url,
            }
        )

    return downloaded


def main():
    try:
        raw = sys.stdin.read()
        cfg = json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        log("ERROR", f"Invalid JSON input: {e}")
        sys.exit(1)

    template_id = cfg.get("template_id", "")
    elements = cfg.get("elements", {})
    formats = cfg.get("formats", [])
    output_dir = cfg.get("output_dir", "output/export/")

    if not template_id:
        log("ERROR", "No template_id provided")
        sys.exit(1)
    if not formats:
        log("ERROR", "No formats provided")
        sys.exit(1)

    try:
        key = read_secret("abyssale")

        # Step 1: Fetch template to discover elements/formats
        template_info = fetch_template(template_id, key)
        log(
            "INFO",
            f"Template loaded",
            name=template_info.get("name", "?"),
            formats=str(len(template_info.get("formats", []))),
        )

        # Step 2: Build generation payload
        payload = build_generation_payload(template_id, elements, formats, template_info)

        # Step 3: Generate banners
        gen_result = generate_banners(payload, key)

        # Step 4: Download all generated images
        downloaded = download_banners(gen_result, output_dir)

        manifest = {
            "template_id": template_id,
            "formats_requested": formats,
            "files": downloaded,
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
