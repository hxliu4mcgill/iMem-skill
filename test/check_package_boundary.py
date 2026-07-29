"""Validate that iMem-skill stays an Agent-side package.

The skill package must not contain service implementation directories, local
service state, generated pages, or nested service repository copies.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_NAMES = {
    "memory_service",
    "server",
    "scripts",
    "data",
    "pages",
    "backups",
    ".venv",
    ".venv-win",
    ".env",
    ".env.local",
    ".env.production",
    "secrets.json",
    "token.json",
    "iMem",
}

FORBIDDEN_SUFFIXES = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".jsonl",
    ".html",
    ".zip",
    ".pem",
    ".key",
    ".p12",
}

IGNORED_NAMES = {
    "__pycache__",
}


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    violations: list[str] = []

    for path in ROOT.rglob("*"):
        if any(part in IGNORED_NAMES for part in path.relative_to(ROOT).parts):
            continue
        if path.name in FORBIDDEN_NAMES:
            violations.append(_relative(path))
            continue
        if path.is_file() and path.suffix in FORBIDDEN_SUFFIXES:
            violations.append(_relative(path))

    if violations:
        print("iMem-skill package boundary violations:")
        for violation in sorted(violations):
            print(f"- {violation}")
        return 1

    print("iMem-skill package boundary OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
