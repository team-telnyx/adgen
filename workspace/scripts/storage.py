#!/usr/bin/env python3
"""Upload, download, and list objects in Telnyx Storage (S3-compatible).

Usage:
    echo '{"action":"upload","bucket":"adgen-brand","local_path":"file.png","remote_key":"key.png"}' | python3 storage.py
    echo '{"action":"download","bucket":"adgen-output","remote_key":"out.png","local_path":"dl.png"}' | python3 storage.py
    echo '{"action":"list","bucket":"adgen-brand","prefix":"imagery/"}' | python3 storage.py
"""

import json
import logging
import os
import sys
from pathlib import Path

import boto3
from botocore.config import Config

ENDPOINT = os.environ.get(
    "TELNYX_STORAGE_ENDPOINT", "https://us-central-1.telnyxcloudstorage.com"
)
REGION = "us-central-1"
SECRETS_PATH = Path.home() / ".secrets" / "telnyx"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("storage")


def get_api_key() -> str:
    """Read Telnyx API key from secrets file at runtime."""
    key = os.environ.get("TELNYX_API_KEY")
    if key:
        return key.strip()
    if SECRETS_PATH.exists():
        return SECRETS_PATH.read_text().strip()
    log.error("No API key found. Set TELNYX_API_KEY or create %s", SECRETS_PATH)
    sys.exit(1)


def get_client():
    """Create an S3 client pointed at Telnyx Storage."""
    api_key = get_api_key()
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id=api_key,
        aws_secret_access_key=api_key,
        config=Config(signature_version="s3v4"),
    )


CONTENT_TYPES = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
    ".json": "application/json", ".pdf": "application/pdf",
}


def upload(client, bucket: str, local_path: str, remote_key: str,
           acl: str = "", content_type: str = "") -> dict:
    """Upload a local file to a bucket."""
    path = Path(local_path)
    if not path.exists():
        log.error("File not found: %s", path)
        return {"ok": False, "error": f"File not found: {path}"}

    extra = {}
    if acl:
        extra["ACL"] = acl
    # Auto-detect content type from extension if not provided
    ct = content_type or CONTENT_TYPES.get(path.suffix.lower(), "")
    if ct:
        extra["ContentType"] = ct

    log.info("Uploading %s → s3://%s/%s", path, bucket, remote_key)
    client.upload_file(str(path), bucket, remote_key, ExtraArgs=extra or None)
    size = path.stat().st_size
    log.info("Done (%d bytes, acl=%s, ct=%s)", size, acl or "default", ct or "auto")
    return {"ok": True, "bucket": bucket, "key": remote_key, "bytes": size}


def download(client, bucket: str, remote_key: str, local_path: str) -> dict:
    """Download an object from a bucket to a local file."""
    path = Path(local_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    log.info("Downloading s3://%s/%s → %s", bucket, remote_key, path)
    client.download_file(bucket, remote_key, str(path))
    size = path.stat().st_size
    log.info("Done (%d bytes)", size)
    return {"ok": True, "bucket": bucket, "key": remote_key, "local_path": str(path), "bytes": size}


def list_objects(client, bucket: str, prefix: str = "") -> dict:
    """List objects in a bucket with optional prefix."""
    log.info("Listing s3://%s/%s", bucket, prefix)
    paginator = client.get_paginator("list_objects_v2")
    items = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            items.append({
                "key": obj["Key"],
                "size": obj["Size"],
                "modified": obj["LastModified"].isoformat(),
            })
    log.info("Found %d objects", len(items))
    return {"ok": True, "bucket": bucket, "prefix": prefix, "count": len(items), "objects": items}


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        log.error("No input on stdin")
        sys.exit(1)

    try:
        params = json.loads(raw)
    except json.JSONDecodeError as e:
        log.error("Invalid JSON: %s", e)
        sys.exit(1)

    action = params.get("action")
    if not action:
        log.error("Missing 'action' field")
        sys.exit(1)

    client = get_client()

    if action == "upload":
        result = upload(client, params["bucket"], params["local_path"], params["remote_key"],
                        acl=params.get("acl", ""), content_type=params.get("content_type", ""))
    elif action == "download":
        result = download(client, params["bucket"], params["remote_key"], params["local_path"])
    elif action == "list":
        result = list_objects(client, params["bucket"], params.get("prefix", ""))
    else:
        log.error("Unknown action: %s", action)
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
