#!/usr/bin/env python3
"""Tests for the skills demo adapter and the bundled demo skill served by GET /skills."""

import base64
import unittest

from fastapi.testclient import TestClient

from app import config
from app.main import APP
from demo_adapter.skills.adapter import BUNDLED_SKILLS_DIR

_BASE = f"/{config.API_URL}"
SKILL_ID = "demo-iri-facility-api"
SCRIPT_PATH = "scripts/demo_iri_client.py"


class SkillsDemoTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(APP)

    def test_list_skills(self):
        response = self.client.get(f"{_BASE}/skills")
        self.assertEqual(response.status_code, 200)
        skill = next(s for s in response.json() if s["id"] == SKILL_ID)
        self.assertTrue(skill["self_uri"].endswith(f"{_BASE}/skills/{SKILL_ID}"))
        self.assertIn("demo adapter", skill["description"])
        self.assertNotIn("files", skill)

    def test_bundle_has_every_file_inline(self):
        response = self.client.get(f"{_BASE}/skills/{SKILL_ID}")
        self.assertEqual(response.status_code, 200)
        files = response.json()["files"]
        self.assertEqual(files[0]["path"], "SKILL.md")
        skill_dir = BUNDLED_SKILLS_DIR / SKILL_ID
        on_disk = sorted(p.relative_to(skill_dir).as_posix() for p in skill_dir.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
        self.assertEqual(sorted(f["path"] for f in files), on_disk)
        for f in files:
            raw = base64.b64decode(f["content"]) if f["encoding"] == "base64" else f["content"].encode("utf-8")
            self.assertEqual(raw, (skill_dir / f["path"]).read_bytes(), f["path"])
        script = next(f for f in files if f["path"] == SCRIPT_PATH)
        self.assertTrue(script["executable"])

    def test_skill_md_references_only_bundled_scripts(self):
        skill_md = (BUNDLED_SKILLS_DIR / SKILL_ID / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(SCRIPT_PATH, skill_md)
        self.assertTrue((BUNDLED_SKILLS_DIR / SKILL_ID / SCRIPT_PATH).is_file())

    def test_unknown_skill_is_404(self):
        self.assertEqual(self.client.get(f"{_BASE}/skills/nope").status_code, 404)


if __name__ == "__main__":
    unittest.main()
