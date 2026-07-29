"""Synchronize the canonical Skill into the distributable Agent Plugin."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "imem-skill"
DESTINATION = ROOT / "plugins" / "imem" / "skills" / "imem-skill"


def _files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def is_synchronized() -> bool:
    if not DESTINATION.is_dir():
        return False
    source_files = _files(SOURCE)
    destination_files = _files(DESTINATION)
    if source_files != destination_files:
        return False
    return all(
        filecmp.cmp(
            SOURCE / relative,
            DESTINATION / relative,
            shallow=False,
        )
        for relative in source_files
    )


def synchronize() -> None:
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        SOURCE,
        DESTINATION,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the Plugin mirror differs from the canonical Skill",
    )
    args = parser.parse_args()

    if args.check:
        if not is_synchronized():
            print(
                "Plugin Skill mirror is stale; run "
                "`python tools/sync_plugin_skill.py`."
            )
            return 1
        print("Plugin Skill mirror is synchronized")
        return 0

    synchronize()
    print(
        "Synchronized "
        f"{SOURCE.relative_to(ROOT).as_posix()} -> "
        f"{DESTINATION.relative_to(ROOT).as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
