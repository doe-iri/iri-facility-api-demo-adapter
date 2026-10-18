#!/usr/bin/env python3
"""Minimal stdlib client for the IRI Facility API demo adapter.

Usage: demo_iri_client.py facility | resources | whoami
Env: IRI_API_URL (default http://127.0.0.1:8000/api/v2), IRI_API_TOKEN (default demo key 12345).
"""
import json
import os
import sys
import urllib.request

BASE = os.environ.get("IRI_API_URL", "http://127.0.0.1:8000/api/v2").rstrip("/")


def get(path: str, auth: bool = False):
    """GET a JSON document from the API."""
    req = urllib.request.Request(f"{BASE}{path}", headers={"Accept": "application/json"})
    if auth:
        req.add_header("Authorization", f"Bearer {os.environ.get('IRI_API_TOKEN', '12345')}")
    with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310 - URL is operator-configured
        return json.load(resp)


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "facility"
    if cmd == "facility":
        out = get("/facility")
    elif cmd == "resources":
        out = [{"name": r.get("name"), "resource_type": r.get("resource_type"), "current_status": r.get("current_status")} for r in get("/status/resources")]
    elif cmd == "whoami":
        out = get("/account/whoami", auth=True)
    else:
        print(__doc__, file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
