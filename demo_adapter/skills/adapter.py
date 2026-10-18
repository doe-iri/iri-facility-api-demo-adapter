"""Skills domain demo adapter: serves the Agent Skills bundled under demo_adapter/skills/bundled/."""
import os
from pathlib import Path

from app.routers.skills.directory_adapter import DirectorySkillsAdapter

BUNDLED_SKILLS_DIR = Path(__file__).resolve().parent / "bundled"


class SkillsDemoAdapter(DirectorySkillsAdapter):
    """Demo implementation of the skills domain. Set IRI_SKILLS_DIR to serve another directory."""

    def __init__(self, skills_dir: str | os.PathLike | None = None):
        super().__init__(skills_dir or os.environ.get("IRI_SKILLS_DIR") or BUNDLED_SKILLS_DIR)
