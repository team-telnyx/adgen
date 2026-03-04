#!/usr/bin/env python3
"""Asset Metadata System.

Creates/updates JSON metadata alongside every generated asset.
Appends to a central JSONL index for searchability.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def log(level: str, msg: str, **kw):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    extra = " ".join(f"{k}={v}" for k, v in kw.items())
    print(f"[{ts}] [{level}] {msg} {extra}".rstrip(), file=sys.stderr)


def main():
    try:
        raw = sys.stdin.read()
        cfg = json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        log("ERROR", f"Invalid JSON input: {e}")
        sys.exit(1)

    asset_path = cfg.get("asset_path", "")
    if not asset_path:
        log("ERROR", "No asset_path provided")
        sys.exit(1)

    asset = Path(asset_path)
    now = datetime.now(timezone.utc)

    # Build metadata record
    meta = {
        "asset_path": str(asset),
        "asset_exists": asset.exists(),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    # Copy all fields except asset_path (already included)
    for k, v in cfg.items():
        if k != "asset_path":
            meta[k] = v

    # If file size is available, include it
    if asset.exists():
        meta["file_size_bytes"] = asset.stat().st_size

    # Write sidecar .meta.json
    meta_path = Path(f"{asset_path}.meta.json")
    meta_path.parent.mkdir(parents=True, exist_ok=True)

    # If meta already exists, preserve created_at
    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text())
            meta["created_at"] = existing.get("created_at", meta["created_at"])
            log("INFO", "Updating existing metadata", path=str(meta_path))
        except (json.JSONDecodeError, Exception):
            pass
    else:
        log("INFO", "Creating new metadata", path=str(meta_path))

    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    log("INFO", f"Wrote metadata sidecar", path=str(meta_path))

    # Append to central index
    index_path = Path("output/asset_index.jsonl")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "a") as f:
        f.write(json.dumps(meta) + "\n")
    log("INFO", f"Appended to index", path=str(index_path))

    # Output result
    result = {"meta_path": str(meta_path), "index_path": str(index_path), "record": meta}
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
