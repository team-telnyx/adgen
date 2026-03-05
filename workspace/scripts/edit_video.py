#!/usr/bin/env python3
"""Editly video assembly wrapper. JSON stdin → JSON stdout.
Assembles clips, adds logo overlay, music, and title cards via editly CLI."""

import json, logging, os, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SZ", level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("edit_video")
logging.Formatter.converter = time.gmtime

WORKSPACE = Path(__file__).resolve().parent.parent

FORMAT_DIMS = {"landscape": (1920, 1080), "square": (1080, 1080), "vertical": (1080, 1920)}


def resolve_path(p: str) -> str:
    path = Path(p)
    return str(path if path.is_absolute() else WORKSPACE / p)


def build_editly_spec(cfg: dict) -> dict:
    fmt = cfg.get("format", "landscape")
    width, height = FORMAT_DIMS.get(fmt, FORMAT_DIMS["landscape"])
    output = resolve_path(cfg.get("output", "output/assembled.mp4"))
    logo = cfg.get("logo_overlay")

    clips = []
    for clip in cfg.get("clips", []):
        layer: dict = {"type": "video", "path": resolve_path(clip["path"])}
        if "cutFrom" in clip:
            layer["cutFrom"] = clip["cutFrom"]
        if "cutTo" in clip:
            layer["cutTo"] = clip["cutTo"]

        layers = [layer]

        # Add logo overlay to every clip
        if logo:
            layers.append({
                "type": "image-overlay",
                "path": resolve_path(logo),
                "position": "top-right",
                "width": 0.12,
                "height": None,
            })

        clips.append({"layers": layers})

    spec: dict = {"width": width, "height": height, "fps": 30, "outPath": output,
                   "clips": clips, "defaults": {"transition": {"name": "crossfade", "duration": 0.5}}}
    music = cfg.get("music")
    if music:
        spec["audioFilePath"] = resolve_path(music)
    return spec


def assemble(cfg: dict) -> dict:
    t0 = time.time()
    spec = build_editly_spec(cfg)
    output = spec["outPath"]

    Path(output).parent.mkdir(parents=True, exist_ok=True)

    # Write spec to temp file
    spec_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json5", delete=False)
    json.dump(spec, spec_file)
    spec_file.close()

    log.info("editly spec written clips=%d output=%s", len(spec["clips"]), output)

    try:
        cmd = ["npx", "editly", "--json", spec_file.name]
        log.info("cmd=%s", " ".join(cmd))

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if proc.stderr:
            for line in proc.stderr.strip().splitlines()[-20:]:
                log.info("  [editly] %s", line)

        if proc.returncode != 0:
            log.error("editly failed exit=%d", proc.returncode)
            raise RuntimeError(f"Editly failed: {proc.stderr[-500:]}")

        out_path = Path(output)
        if not out_path.exists():
            raise RuntimeError(f"Output not created: {output}")

        file_size = out_path.stat().st_size
        elapsed = time.time() - t0

        # Write metadata sidecar
        meta = {
            "operation": cfg.get("operation", "assemble"),
            "clips": len(cfg.get("clips", [])),
            "format": cfg.get("format", "landscape"),
            "output_path": output,
            "file_size_bytes": file_size,
            "assembled_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "has_music": bool(cfg.get("music")),
            "has_logo": bool(cfg.get("logo_overlay")),
        }
        meta_path = out_path.with_suffix(".meta.json")
        meta_path.write_text(json.dumps(meta, indent=2))

        log.info("assembly complete size=%d elapsed=%.1fs", file_size, elapsed)
        return {"ok": True, "path": output, "meta": str(meta_path),
                "size_bytes": file_size, "elapsed": round(elapsed, 1)}

    finally:
        os.unlink(spec_file.name)


def main():
    try:
        cfg = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log.error("invalid JSON input: %s", e)
        sys.exit(1)

    op = cfg.get("operation", "assemble")
    if op != "assemble":
        log.error("unsupported operation: %s", op)
        sys.exit(1)

    if not cfg.get("clips"):
        log.error("missing required field: clips")
        sys.exit(1)

    try:
        result = assemble(cfg)
        print(json.dumps(result, indent=2))
    except Exception as e:
        log.error("edit failed: %s", e)
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
