#!/usr/bin/env python3
"""AdGen Pipeline — Brief → AI Hero → Telnyx Storage → Abyssale → Download.
Falls back to Pillow render.py if Abyssale fails. JSON stdin → JSON stdout."""

import json, logging, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SZ", level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("pipeline")
logging.Formatter.converter = time.gmtime

SCRIPTS_DIR = Path(__file__).resolve().parent
WORKSPACE = SCRIPTS_DIR.parent
ABYSSALE_BASE = "https://api.abyssale.com"
STORAGE_BUCKET = "adgen-brand"


def read_secret(name: str) -> str:
    p = Path.home() / ".secrets" / name
    if not p.exists():
        raise FileNotFoundError(f"Secret not found: {p}")
    return p.read_text().strip()


def run_script(name: str, payload: dict) -> dict:
    script = SCRIPTS_DIR / name
    log.info("calling %s", name)
    proc = subprocess.run([sys.executable, str(script)], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=300)
    if proc.stderr:
        for line in proc.stderr.strip().splitlines():
            log.info("  [%s] %s", name, line)
    if proc.returncode != 0:
        raise RuntimeError(f"{name} exited {proc.returncode}: {proc.stderr[-500:]}")
    return json.loads(proc.stdout) if proc.stdout.strip() else {}


def upload_to_storage(local_path: str, remote_key: str) -> str:
    log.info("uploading to storage key=%s", remote_key)
    result = run_script("storage.py", {"action": "upload", "bucket": STORAGE_BUCKET,
                                        "local_path": local_path, "remote_key": remote_key,
                                        "acl": "public-read"})
    if not result.get("ok"):
        raise RuntimeError(f"Storage upload failed: {result}")
    url = f"https://{STORAGE_BUCKET}.us-central-1.telnyxcloudstorage.com/{remote_key}"
    log.info("uploaded url=%s", url)
    return url


def fetch_template(template_id: str, api_key: str) -> dict:
    import requests
    resp = requests.get(f"{ABYSSALE_BASE}/templates/{template_id}",
                        headers={"x-api-key": api_key}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def discover_elements(template_info: dict) -> dict:
    elems = {"text": [], "image": [], "logo": [], "container": []}
    for el in template_info.get("elements", []):
        t = el.get("type", "unknown")
        if t in elems:
            elems[t].append(el)
    return elems


def map_brief_to_elements(brief: dict, discovered: dict, hero_url: str | None) -> dict:
    mapped = {}
    patterns = {
        "headline": "headline", "title": "headline", "proper_name": "headline",
        "heading": "headline", "subhead": "subhead", "subtitle": "subhead",
        "lead": "subhead", "description": "subhead", "cta": "cta", "button": "cta",
    }
    for el in discovered.get("text", []):
        name, name_lc = el["name"], el["name"].lower().replace("-", "_")
        for pat, field in patterns.items():
            if pat in name_lc and brief.get(field):
                mapped[name] = {"payload": brief[field]}
                break
        else:
            for attr in el.get("attributes", []):
                if attr.get("id") == "payload":
                    vals = list(attr.get("values", {}).values())
                    if vals and isinstance(vals[0], str):
                        if len(vals[0]) < 30 and brief.get("headline"):
                            mapped[name] = {"payload": brief["headline"]}
                        elif brief.get("subhead"):
                            mapped[name] = {"payload": brief["subhead"]}
    if hero_url:
        for el in discovered.get("image", []):
            if "logo" not in el["name"].lower():
                mapped[el["name"]] = {"image_url": hero_url}
                break
    log.info("mapped %d elements", len(mapped))
    return mapped


def generate_abyssale(template_id: str, fmt: str, elements: dict, api_key: str) -> dict:
    import requests
    log.info("abyssale generate template=%s format=%s", template_id, fmt)
    t0 = time.monotonic()
    resp = requests.post(f"{ABYSSALE_BASE}/banner-builder/{template_id}/generate",
                         headers={"x-api-key": api_key, "Content-Type": "application/json"},
                         json={"template_format_name": fmt, "elements": elements}, timeout=120)
    resp.raise_for_status()
    log.info("abyssale responded in %.1fs", time.monotonic() - t0)
    return resp.json()


def download_file(url: str, local_path: str) -> int:
    import requests
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    out = Path(local_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(resp.content)
    log.info("saved %d bytes → %s", len(resp.content), local_path)
    return len(resp.content)


def pillow_fallback(brief: dict, fmt: str, output: str, hero: str, bg: str) -> str:
    log.warning("pillow fallback for format=%s", fmt)
    run_script("render.py", {"template": "dark-hero-left", "format": fmt,
                              "background": bg, "headline": brief["headline"],
                              "subhead": brief.get("subhead", ""), "cta": brief.get("cta", ""),
                              "accent_color": "#D4E510", "hero_image": hero, "output": output})
    return str(WORKSPACE / output) if not Path(output).is_absolute() else output


def write_metadata(asset_path: str, brief: dict, extra: dict):
    meta = {"asset_path": asset_path, "campaign": brief.get("campaign", ""),
            "persona": brief.get("persona", ""), "headline": brief["headline"],
            "subhead": brief.get("subhead", ""), "cta": brief.get("cta", "")}
    meta.update(extra)
    run_script("asset_metadata.py", meta)


def run_video_pipeline(cfg: dict, hero_url: str | None, hero_local: str | None) -> dict:
    """Route to render_video.py for Remotion output or edit_video.py for Editly assembly."""
    brief = cfg["brief"]
    output_type = cfg.get("output_type", "video")
    output_dir = cfg.get("output_dir", "output/campaign")
    fmt = cfg.get("video_format", "landscape")

    if output_type == "edit":
        edit_cfg = cfg.get("edit_config", {})
        edit_cfg.setdefault("format", fmt)
        edit_cfg.setdefault("output", f"{output_dir}/assembled.mp4")
        return run_script("edit_video.py", edit_cfg)

    # output_type == "video" → Remotion render
    composition = cfg.get("composition", "ProductLaunch")
    duration = cfg.get("video_duration", 15)
    accent = cfg.get("accent_color", brief.get("accent_color", "#00C26E"))
    render_cfg = {
        "composition": composition,
        "props": {
            "headline": brief["headline"],
            "subhead": brief.get("subhead", ""),
            "cta": brief.get("cta", "Learn More"),
            "heroImage": hero_url or "",
            "accentColor": accent,
        },
        "format": fmt,
        "duration": duration,
        "output": f"{output_dir}/{composition.lower()}.mp4",
    }
    return run_script("render_video.py", render_cfg)


def run_pipeline(cfg: dict) -> dict:
    t0 = time.time()
    brief = cfg["brief"]
    output_type = cfg.get("output_type", "static")
    provider = cfg.get("image_provider", "dalle")
    prompt = cfg.get("image_prompt", "")
    template_id = cfg.get("abyssale_template", "")
    formats = cfg.get("formats", ["facebook-featured"])
    output_dir = cfg.get("output_dir", "output/campaign")
    bg = cfg.get("background", "#000000")

    log.info("pipeline start output_type=%s provider=%s template=%s formats=%d",
             output_type, provider, template_id, len(formats))
    manifest = {"brief": brief, "files": [], "started_at": datetime.now(timezone.utc).isoformat()}

    # Step 1: Generate hero image
    hero_local, hero_url = None, None
    if prompt:
        hero_out = str(WORKSPACE / output_dir / "hero.png")
        result = run_script("generate_image.py", {"prompt": prompt, "output": hero_out, "provider": provider})
        hero_local = result.get("path", hero_out)
        manifest["hero_image"] = hero_local

        # Step 2: Upload to Telnyx Storage
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        try:
            hero_url = upload_to_storage(hero_local, f"heroes/{brief.get('campaign','misc')}/{ts}-hero.png")
            manifest["hero_url"] = hero_url
        except Exception as e:
            log.warning("storage upload failed: %s", e)

    # Video/Edit routing (non-static output types)
    if output_type in ("video", "edit"):
        log.info("routing to %s pipeline", output_type)
        try:
            video_result = run_video_pipeline(cfg, hero_url, hero_local)
            video_path = video_result.get("path", "")
            manifest["files"].append({
                "format": cfg.get("video_format", "landscape"),
                "path": video_path,
                "renderer": "remotion" if output_type == "video" else "editly",
                "meta": video_result.get("meta", ""),
            })
            elapsed = time.time() - t0
            manifest.update({
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "elapsed_seconds": round(elapsed, 1),
                "total_files": len(manifest["files"]),
                "renderer_used": "remotion" if output_type == "video" else "editly",
            })
            log.info("video pipeline complete path=%s elapsed=%.1fs", video_path, elapsed)
            return manifest
        except Exception as e:
            log.error("video pipeline failed: %s", e)
            raise

    # Auto-select template if not specified
    if not template_id and output_type == "static":
        log.info("no template specified, auto-selecting via select_template.py")
        try:
            selector_input = {
                "use_case": brief.get("use_case", "blog_featured"),
                "persona": brief.get("persona", "general"),
                "format": formats[0] if formats else "facebook-featured",
                "has_hero_image": hero_url is not None,
            }
            sel_result = run_script("select_template.py", selector_input)
            if isinstance(sel_result, list) and len(sel_result) > 0:
                template_id = sel_result[0]["id"]
                log.info("auto-selected template=%s name=%s score=%s",
                         template_id, sel_result[0].get("name"), sel_result[0].get("score"))
            else:
                log.warning("select_template.py returned no matches")
        except Exception as e:
            log.warning("auto-select failed: %s — proceeding without template", e)

    # Steps 3-7: Abyssale rendering (static output)
    abyssale_ok = False
    if template_id:
        try:
            api_key = read_secret("abyssale")
            tinfo = fetch_template(template_id, api_key)
            avail = [f["id"] for f in tinfo.get("formats", [])]
            discovered = discover_elements(tinfo)
            elem_map = map_brief_to_elements(brief, discovered, hero_url)

            for fmt in formats:
                if fmt not in avail:
                    log.warning("format %s not in template (available: %s)", fmt, avail)
                    p = pillow_fallback(brief, "linkedin_1200x1200", f"{output_dir}/{fmt}.png", hero_local or "", bg)
                    manifest["files"].append({"format": fmt, "path": p, "renderer": "pillow-fallback"})
                    continue
                res = generate_abyssale(template_id, fmt, elem_map, api_key)
                cdn = res.get("file", {}).get("cdn_url") or res.get("file", {}).get("url", "")
                if cdn:
                    ext = "jpeg" if "jpeg" in cdn else "png"
                    local = str(WORKSPACE / output_dir / f"{fmt}.{ext}")
                    download_file(cdn, local)
                    manifest["files"].append({"format": fmt, "path": local, "renderer": "abyssale",
                                              "cdn_url": cdn, "abyssale_id": res.get("id")})
                    abyssale_ok = True
                    write_metadata(local, brief, {"template_id": template_id, "format": fmt,
                                                   "renderer": "abyssale", "cdn_url": cdn, "hero_url": hero_url or ""})
        except Exception as e:
            log.error("abyssale failed: %s — using pillow", e)

    # Fallback
    if not abyssale_ok:
        fmt_map = {"facebook-featured": "linkedin_1200x1200", "docs-to-strapi": "linkedin_1200x1200"}
        for fmt in formats:
            pfmt = fmt_map.get(fmt, "linkedin_1200x1200")
            try:
                p = pillow_fallback(brief, pfmt, f"{output_dir}/{fmt}.png", hero_local or "", bg)
                manifest["files"].append({"format": fmt, "path": p, "renderer": "pillow-fallback"})
                write_metadata(p, brief, {"format": pfmt, "renderer": "pillow-fallback"})
            except Exception as e:
                log.error("pillow fallback failed for %s: %s", fmt, e)

    elapsed = time.time() - t0
    manifest.update({"completed_at": datetime.now(timezone.utc).isoformat(),
                     "elapsed_seconds": round(elapsed, 1), "total_files": len(manifest["files"]),
                     "renderer_used": "abyssale" if abyssale_ok else "pillow-fallback"})
    log.info("pipeline complete files=%d renderer=%s elapsed=%.1fs",
             manifest["total_files"], manifest["renderer_used"], elapsed)
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
