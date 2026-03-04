#!/usr/bin/env python3
"""Save an image to the AdGen brand library.

Validates, copies to brand/imagery/{category}/, updates index.md,
uploads to Telnyx Storage. JSON stdin → JSON stdout.
"""

import json, logging, shutil, subprocess, sys, time
from pathlib import Path
from PIL import Image

logging.basicConfig(format="[%(asctime)s] %(levelname)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%SZ", level=logging.INFO, stream=sys.stderr)
log = logging.getLogger("save_to_library")
logging.Formatter.converter = time.gmtime

WORKSPACE = Path(__file__).resolve().parent.parent
IMAGERY_DIR = WORKSPACE / "brand" / "imagery"
INDEX_PATH = IMAGERY_DIR / "index.md"
SCRIPTS_DIR = Path(__file__).resolve().parent
MIN_DIM = 2400


def upload(local: str, key: str) -> bool:
    payload = {"action": "upload", "bucket": "adgen-brand",
               "local_path": local, "remote_key": key}
    p = subprocess.run([sys.executable, str(SCRIPTS_DIR / "storage.py")],
                       input=json.dumps(payload), capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        log.warning("upload failed: %s", p.stderr[-300:])
        return False
    log.info("uploaded key=%s", key)
    return True


def update_index(category: str, filename: str, tags: list, desc: str, res: str):
    if not INDEX_PATH.exists():
        return
    content = INDEX_PATH.read_text()
    row = f"| `{category}/{filename}` | {', '.join(tags)} | {desc} | {res} |"
    sections = {"product": "## Product Screenshots", "abstract": "## Abstract",
                "photography": "## Photography"}
    hdr = sections.get(category, "")
    if hdr and hdr in content:
        idx = content.index(hdr)
        lines = content[idx:].split("\n")
        last_row = max((i for i, l in enumerate(lines) if l.startswith("|")), default=0)
        lines.insert(last_row + 1, row)
        content = content[:idx] + "\n".join(lines)
    else:
        content += f"\n{row}\n"
    INDEX_PATH.write_text(content)
    log.info("index updated category=%s file=%s", category, filename)


def main():
    try:
        cfg = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log.error("invalid JSON: %s", e); sys.exit(1)

    src = Path(cfg.get("source_path", ""))
    category, filename = cfg.get("category", "product"), cfg.get("filename", "")
    tags, desc = cfg.get("tags", []), cfg.get("description", "")

    if not src.is_file():
        log.error("source not found: %s", src); sys.exit(1)
    if not filename:
        log.error("filename required"); sys.exit(1)

    img = Image.open(src)
    w, h = img.size
    if max(w, h) < MIN_DIM:
        log.error("too small: %dx%d (min %dpx)", w, h, MIN_DIM); sys.exit(1)
    if src.suffix.lower() not in (".png", ".jpg", ".jpeg"):
        log.error("unsupported format: %s", src.suffix); sys.exit(1)
    log.info("validated %dx%d", w, h)

    dest_dir = IMAGERY_DIR / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    shutil.copy2(str(src), str(dest))
    log.info("copied to %s", dest)

    res = f"{w}×{h}"
    update_index(category, filename, tags, desc, res)
    rkey = f"imagery/{category}/{filename}"
    ok = upload(str(dest), rkey)

    print(json.dumps({"ok": True, "path": str(dest), "category": category,
                       "filename": filename, "resolution": res, "tags": tags,
                       "uploaded": ok, "remote_key": rkey}, indent=2))


if __name__ == "__main__":
    main()
