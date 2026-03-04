"""
skill_store.py — Persistent CRUD and import for Skills.
Skills are stored as Markdown files in ~/.config/orchestrator/skills/
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Optional

from models.schedule import Skill


def _skills_dir() -> Path:
    p = Path.home() / ".config" / "orchestrator" / "skills"
    p.mkdir(parents=True, exist_ok=True)
    return p


class SkillStore:
    """Thread-safe, file-backed store for Skills."""

    def __init__(self, directory: Optional[Path] = None):
        self._dir = directory or _skills_dir()
        self._lock = threading.Lock()
        self._skills: dict[str, Skill] = {}
        self._load()

    def _load(self) -> None:
        """Load all .md or .json skills from the directory."""
        for path in self._dir.glob("*"):
            if path.suffix in (".md", ".json"):
                try:
                    # For now, simple metadata extraction or assume a standard format
                    # In Swift Orchestrator, skills are often Markdown with YAML frontmatter.
                    content = path.read_text()
                    # Placeholder: create a Skill object from the filename/content
                    s = Skill(
                        id=path.stem,
                        name=path.stem.replace("_", " ").title(),
                        content=content,
                        source="local",
                    )
                    self._skills[s.id] = s
                except Exception:
                    continue

    def all(self) -> list[Skill]:
        with self._lock:
            return list(self._skills.values())

    def enabled(self) -> list[Skill]:
        with self._lock:
            return [s for s in self._skills.values() if s.enabled]

    def get(self, skill_id: str) -> Optional[Skill]:
        with self._lock:
            return self._skills.get(skill_id)

    def save(self, skill: Skill) -> None:
        with self._lock:
            self._skills[skill.id] = skill
            # Save to file
            path = self._dir / f"{skill.id}.md"
            path.write_text(skill.content)

    def delete(self, skill_id: str) -> bool:
        with self._lock:
            removed = self._skills.pop(skill_id, None)
            if removed:
                path = self._dir / f"{skill_id}.md"
                if path.exists():
                    path.unlink()
                return True
            return False

    def import_from_file(self, path: Path) -> Optional[Skill]:
        """Import a skill from a local .md file."""
        if not path.exists():
            return None
        content = path.read_text()
        s = Skill(
            name=path.stem.replace("_", " ").title(),
            content=content,
            source="local",
        )
        self.save(s)
        return s


# Shared singleton
skill_store = SkillStore()
