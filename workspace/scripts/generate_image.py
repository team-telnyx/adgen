#!/usr/bin/env python3
"""AI Image Generation — DALL-E 3 or Gemini (Nano Banana).

Reads JSON from stdin, generates an image, saves to output path.
Prints JSON result to stdout on success, exits 1 on failure.
"""

import base64
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def log(level: str, msg: str, **kw):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    extra = " ".join(f"{k}={v}" for k, v in kw.items())
    print(f"[{ts}] [{level}] {msg} {extra}".rstrip(), file=sys.stderr)


def read_secret(name: str) -> str:
    path = Path.home() / ".secrets" / name
    if not path.exists():
        raise FileNotFoundError(f"Secret not found: {path}")
    return path.read_text().strip()


def generate_dalle(prompt: str, size: str, style: str, output: str) -> dict:
    """Generate image via OpenAI DALL-E 3."""
    import openai

    key = read_secret("openai")
    client = openai.OpenAI(api_key=key)

    log("INFO", "Requesting DALL-E 3 generation", size=size, style=style)
    t0 = time.monotonic()

    resp = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        style=style,
        response_format="b64_json",
        n=1,
    )

    elapsed = time.monotonic() - t0
    log("INFO", f"DALL-E responded in {elapsed:.1f}s")

    img_data = base64.b64decode(resp.data[0].b64_json)
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(img_data)
    log("INFO", f"Saved {len(img_data)} bytes", path=str(out_path))

    return {"path": str(out_path), "provider": "dalle", "prompt": prompt}


def generate_gemini(prompt: str, size: str, output: str) -> dict:
    """Generate image via Gemini 2.0 Flash image generation."""
    import requests

    key = read_secret("gemini")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.0-flash-exp-image-generation:generateContent"
    )

    log("INFO", "Requesting Gemini image generation")
    t0 = time.monotonic()

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }

    resp = requests.post(f"{url}?key={key}", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    elapsed = time.monotonic() - t0
    log("INFO", f"Gemini responded in {elapsed:.1f}s")

    # Extract image from response parts
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                img_b64 = part["inlineData"]["data"]
                img_data = base64.b64decode(img_b64)
                out_path = Path(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(img_data)
                log("INFO", f"Saved {len(img_data)} bytes", path=str(out_path))
                return {"path": str(out_path), "provider": "gemini", "prompt": prompt}

    raise RuntimeError("No image data in Gemini response")


def main():
    try:
        raw = sys.stdin.read()
        cfg = json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        log("ERROR", f"Invalid JSON input: {e}")
        sys.exit(1)

    provider = cfg.get("provider", "dalle")
    prompt = cfg.get("prompt", "")
    size = cfg.get("size", "1024x1024")
    style = cfg.get("style", "natural")
    output = cfg.get("output", "output/generated/image.png")

    if not prompt:
        log("ERROR", "No prompt provided")
        sys.exit(1)

    log("INFO", f"Starting generation", provider=provider)

    try:
        if provider == "dalle":
            result = generate_dalle(prompt, size, style, output)
        elif provider == "gemini":
            result = generate_gemini(prompt, size, output)
        else:
            log("ERROR", f"Unknown provider: {provider}")
            sys.exit(1)

        print(json.dumps(result))
        sys.exit(0)

    except Exception as e:
        log("ERROR", f"Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
