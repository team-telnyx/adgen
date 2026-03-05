#!/usr/bin/env python3
"""Video editing via Remotion ClipAssembly — cut, trim, splice, assemble clips.
Uses Remotion's Chromium renderer instead of editly's headless-gl.
JSON stdin → MP4 output."""

import json, logging, os, subprocess, sys, tempfile, time

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ")
log = logging.getLogger("edit_video")

VIDEO_DIR = os.path.join(os.path.dirname(__file__), "..", "video")
BRAND_DIR = os.path.join(os.path.dirname(__file__), "..", "brand")

FORMAT_DIMS = {
    "landscape": (1920, 1080),
    "square": (1080, 1080),
    "vertical": (1080, 1920),
}


def main():
    spec = json.load(sys.stdin)
    output = spec.get("output", "output/assembled.mp4")
    fmt = spec.get("format", "landscape")
    width, height = FORMAT_DIMS.get(fmt, (1920, 1080))

    abs_output = output if os.path.isabs(output) else os.path.join(os.path.dirname(__file__), "..", output)
    os.makedirs(os.path.dirname(abs_output), exist_ok=True)

    log.info("format=%s output=%s clips=%d", fmt, abs_output, len(spec.get("clips", [])))

    # Build Remotion ClipAssembly props
    clips = []
    for c in spec.get("clips", []):
        clip = {"src": os.path.abspath(c["path"]) if not c["path"].startswith("http") else c["path"]}
        if "cutFrom" in c:
            clip["startFrom"] = c["cutFrom"]
        if "cutTo" in c:
            clip["endAt"] = c["cutTo"]
        if "duration" in c:
            clip["durationInFrames"] = int(c["duration"] * 30)
        clips.append(clip)

    props = {"clips": clips}

    if spec.get("logo_overlay"):
        logo_path = spec["logo_overlay"]
        if not logo_path.startswith("http"):
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", logo_path))
        props["logoSrc"] = logo_path

    if spec.get("music"):
        music_path = spec["music"]
        if not music_path.startswith("http"):
            music_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", music_path))
        props["musicSrc"] = music_path

    if spec.get("title_card"):
        props["titleCard"] = {
            "text": spec["title_card"].get("text", ""),
            "durationInFrames": int(spec["title_card"].get("duration", 3) * 30),
        }

    # Calculate total duration
    total_frames = sum(c.get("durationInFrames", 300) for c in clips)
    if props.get("titleCard"):
        total_frames += props["titleCard"]["durationInFrames"]

    # Write props to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(props, f)
        props_file = f.name

    t0 = time.time()

    cmd = [
        "npx", "remotion", "render", "src/index.ts", "ClipAssembly", abs_output,
        f"--props={props_file}",
        f"--width={width}", f"--height={height}",
        f"--frames=0-{total_frames - 1}",
    ]

    log.info("cmd=%s", " ".join(cmd))

    try:
        result = subprocess.run(cmd, cwd=VIDEO_DIR, capture_output=True, text=True, timeout=300)
        os.unlink(props_file)

        if result.returncode != 0:
            log.error("render failed: %s", result.stderr[-500:] if result.stderr else "no stderr")
            sys.exit(1)

        elapsed = round(time.time() - t0, 1)
        size = os.path.getsize(abs_output)

        # Metadata sidecar
        meta = {
            "type": "edit",
            "clips": len(clips),
            "format": fmt,
            "width": width,
            "height": height,
            "total_frames": total_frames,
            "elapsed": elapsed,
            "size_bytes": size,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        meta_path = abs_output + ".meta.json"
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        log.info("render complete size=%d elapsed=%ss meta=%s", size, elapsed, meta_path)
        json.dump({"ok": True, "path": abs_output, "meta": meta_path, "size_bytes": size, "elapsed": elapsed}, sys.stdout)

    except subprocess.TimeoutExpired:
        log.error("render timed out (300s)")
        os.unlink(props_file)
        sys.exit(1)


if __name__ == "__main__":
    main()
