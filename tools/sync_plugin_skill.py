"""Synchronize the canonical Skill into distributable Agent packages."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "imem-skill"
DESTINATIONS = [
    ROOT / "plugins" / "imem" / "skills" / "imem-skill",
    ROOT / "plugins" / "imem-dsh" / "skills" / "imem-skill",
]


def _files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def _is_synchronized(destination: Path) -> bool:
    if not destination.is_dir():
        return False
    source_files = _files(SOURCE)
    destination_files = _files(destination)
    if source_files != destination_files:
        return False
    return all(
        filecmp.cmp(
            SOURCE / relative,
            destination / relative,
            shallow=False,
        )
        for relative in source_files
    )


def is_synchronized() -> bool:
    return all(_is_synchronized(destination) for destination in DESTINATIONS)


def synchronize() -> None:
    for destination in DESTINATIONS:
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            SOURCE,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if a packaged Skill mirror differs from the canonical Skill",
    )
    args = parser.parse_args()

    if args.check:
        if not is_synchronized():
            print(
                "Packaged Skill mirror is stale; run "
                "`python tools/sync_plugin_skill.py`."
            )
            return 1
        print("Packaged Skill mirrors are synchronized")
        return 0

    synchronize()
    print(
        "Synchronized "
        f"{SOURCE.relative_to(ROOT).as_posix()} -> "
        + ", ".join(
            destination.relative_to(ROOT).as_posix()
            for destination in DESTINATIONS
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
