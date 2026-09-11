"""Portable launcher for the repository's single document-audit engine."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def find_project_root(start: Path) -> Path:
    """Find the repository root without depending on the agent's CWD."""
    for candidate in (start, *start.parents):
        if (candidate / "scripts" / "audit_docx.py").is_file():
            return candidate
    raise FileNotFoundError("Cannot locate scripts/audit_docx.py from the installed Skill")


def main() -> int:
    try:
        project_root = find_project_root(Path(__file__).resolve().parent)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    command = [sys.executable, str(project_root / "scripts" / "audit_docx.py"), *sys.argv[1:]]
    return subprocess.run(command, cwd=project_root, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
