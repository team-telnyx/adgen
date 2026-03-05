#!/usr/bin/env python3
"""Remotion video render orchestrator. JSON stdin → JSON stdout.
Renders a composition via `npx remotion render` with props, format, and output path."""

import json, logging, os, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SZ", level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("render_video")
logging.Formatter.converter = time.gmtime

VIDEO_DIR = Path(__file__).resolve().parent.parent / "video"
WORKSPACE = Path(__file__).resolve().parent.parent

FORMAT_DIMS = {
    "landscape": (1920, 1080),
    "square": (1080, 1080),
    "vertical": (1080, 1920),
}


def render(cfg: dict) -> dict:
    t0 = time.time()
    composition = cfg["composition"]
    props = cfg.get("props", {})
    fmt = cfg.get("format", "landscape")
    duration = cfg.get("duration", 15)
    output_rel = cfg.get("output", f"output/{composition}.mp4")

    # Resolve output path
    output_path = Path(output_rel)
    if not output_path.is_absolute():
        output_path = WORKSPACE / output_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width, height = FORMAT_DIMS.get(fmt, FORMAT_DIMS["landscape"])
    fps = 30
    frames = duration * fps

    # Include format in props for the composition
    props["format"] = fmt

    # Write props to temp file
    props_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(props, props_file)
    props_file.close()

    log.info("rendering composition=%s format=%s %dx%d duration=%ds frames=%d",
             composition, fmt, width, height, duration, frames)
    log.info("output=%s", output_path)

    try:
        cmd = [
            "npx", "remotion", "render", "src/index.ts", composition,
            str(output_path),
            f"--props={props_file.name}",
            f"--width={width}",
            f"--height={height}",
        ]
        log.info("cmd=%s", " ".join(cmd))

        proc = subprocess.run(
            cmd, cwd=str(VIDEO_DIR), capture_output=True, text=True, timeout=600
        )

        if proc.stderr:
            for line in proc.stderr.strip().splitlines()[-20:]:
                log.info("  [remotion] %s", line)

        if proc.returncode != 0:
            log.error("remotion render failed exit=%d", proc.returncode)
            raise RuntimeError(f"Render failed: {proc.stderr[-500:]}")

        if not output_path.exists():
            raise RuntimeError(f"Output file not created: {output_path}")

        file_size = output_path.stat().st_size
        elapsed = time.time() - t0

        # Write metadata sidecar
        meta = {
            "composition": composition,
            "format": fmt,
            "width": width,
            "height": height,
            "duration_seconds": duration,
            "fps": fps,
            "frames": frames,
            "output_path": str(output_path),
            "file_size_bytes": file_size,
            "rendered_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "props": props,
        }
        meta_path = output_path.with_suffix(".meta.json")
        meta_path.write_text(json.dumps(meta, indent=2))

        log.info("render complete size=%d elapsed=%.1fs meta=%s", file_size, elapsed, meta_path)
        return {"ok": True, "path": str(output_path), "meta": str(meta_path),
                "size_bytes": file_size, "elapsed": round(elapsed, 1)}

    finally:
        os.unlink(props_file.name)


def main():
    try:
        cfg = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log.error("invalid JSON input: %s", e)
        sys.exit(1)

    if "composition" not in cfg:
        log.error("missing required field: composition")
        sys.exit(1)

    try:
        result = render(cfg)
        print(json.dumps(result, indent=2))
    except Exception as e:
        log.error("render failed: %s", e)
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
