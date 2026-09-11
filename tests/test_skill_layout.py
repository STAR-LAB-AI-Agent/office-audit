from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def frontmatter_name(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError(f"missing YAML frontmatter: {path}")
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.partition(":")[2].strip()
    raise AssertionError(f"missing frontmatter name: {path}")


class SkillLayoutTests(unittest.TestCase):
    def test_root_and_workspace_entry_share_name(self) -> None:
        self.assertEqual(frontmatter_name(ROOT / "SKILL.md"), "office-audit")
        self.assertEqual(
            frontmatter_name(ROOT / "skills" / "office-audit" / "SKILL.md"),
            "office-audit",
        )

    def test_workspace_folder_matches_skill_name(self) -> None:
        skill_dir = ROOT / "skills" / "office-audit"
        self.assertEqual(skill_dir.name, frontmatter_name(skill_dir / "SKILL.md"))

    def test_portable_launcher_exposes_core_cli(self) -> None:
        launcher = ROOT / "skills" / "office-audit" / "scripts" / "run_audit.py"
        result = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            cwd=ROOT.parent,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--input", result.stdout)
        self.assertIn("--request", result.stdout)
        self.assertIn("fields_format", result.stdout)


if __name__ == "__main__":
    unittest.main()
