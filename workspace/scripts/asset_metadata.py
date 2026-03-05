#!/usr/bin/env python3
"""Asset Metadata System.

Creates/updates JSON metadata alongside every generated asset.
Uploads metadata JSON to adgen-output bucket in Telnyx Storage.
Appends to a central JSONL index for searchability.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
STORAGE_BUCKET = "adgen-output"


def log(level: str, msg: str, **kw):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    extra = " ".join(f"{k}={v}" for k, v in kw.items())
    print(f"[{ts}] [{level}] {msg} {extra}".rstrip(), file=sys.stderr)


def upload_to_storage(local_path: str, remote_key: str, bucket: str = STORAGE_BUCKET) -> dict:
    """Upload a file to Telnyx Storage via storage.py."""
    payload = {
        "action": "upload",
        "bucket": bucket,
        "local_path": local_path,
        "remote_key": remote_key,
        "content_type": "application/json",
    }
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "storage.py")],
            input=json.dumps(payload), capture_output=True, text=True, timeout=60,
        )
        if proc.returncode != 0:
            log("WARNING", f"Storage upload failed: {proc.stderr[-300:]}")
            return {"ok": False, "error": proc.stderr[-300:]}
        result = json.loads(proc.stdout) if proc.stdout.strip() else {}
        return result
    except Exception as e:
        log("WARNING", f"Storage upload error: {e}")
        return {"ok": False, "error": str(e)}


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

    # Build metadata record matching the spec schema
    meta = {
        "asset_path": str(asset),
        "asset_exists": asset.exists(),
        "campaign": cfg.get("campaign", ""),
        "persona": cfg.get("persona", ""),
        "template": cfg.get("template", cfg.get("template_id", "")),
        "headline": cfg.get("headline", ""),
        "accent_color": cfg.get("accent_color", ""),
        "imagery_source": cfg.get("imagery_source", cfg.get("hero_source", "")),
        "created": now.isoformat(),
        "updated_at": now.isoformat(),
        "performance": cfg.get("performance", {}),
    }

    # Copy remaining fields not already mapped
    skip_keys = {"asset_path", "campaign", "persona", "template", "template_id",
                 "headline", "accent_color", "imagery_source", "hero_source",
                 "performance", "upload_to_storage"}
    for k, v in cfg.items():
        if k not in skip_keys and k not in meta:
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
            meta["created"] = existing.get("created", existing.get("created_at", meta["created"]))
            log("INFO", "Updating existing metadata", path=str(meta_path))
        except (json.JSONDecodeError, Exception):
            pass
    else:
        log("INFO", "Creating new metadata", path=str(meta_path))

    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    log("INFO", "Wrote metadata sidecar", path=str(meta_path))

    # Upload metadata JSON to Telnyx Storage
    storage_url = None
    if cfg.get("upload_to_storage", True):
        campaign = cfg.get("campaign", "misc")
        asset_name = Path(asset_path).stem
        remote_key = f"metadata/{campaign}/{asset_name}.meta.json"
        upload_result = upload_to_storage(str(meta_path), remote_key)
        if upload_result.get("ok"):
            storage_url = f"https://{STORAGE_BUCKET}.us-central-1.telnyxcloudstorage.com/{remote_key}"
            meta["storage_url"] = storage_url
            log("INFO", "Uploaded metadata to storage", url=storage_url)
        else:
            log("WARNING", "Metadata storage upload failed", error=str(upload_result.get("error", "")))

    # Append to central index
    index_path = Path("output/asset_index.jsonl")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "a") as f:
        f.write(json.dumps(meta) + "\n")
    log("INFO", "Appended to index", path=str(index_path))

    # Output result
    result = {
        "meta_path": str(meta_path),
        "index_path": str(index_path),
        "storage_url": storage_url,
        "record": meta,
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
