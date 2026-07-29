"""Validate that iMem-skill can stand as an independent repository.

This check focuses on repository coupling: parent-repository paths, service
implementation imports, local developer paths, and runtime references that
would require cloning the iMem service repository.
"""

from __future__ import annotations

import py_compile
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
}

LOCAL_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:[\\/](?:Projects|Users|workspace|repo)[\\/]", re.IGNORECASE),
    re.compile(r"/Users/"),
    re.compile(r"/home/[^/\s]+/"),
]

PARENT_REPOSITORY_PATTERNS = [
    "../iMem",
    "..\\iMem",
    "REPO_DIR / \"iMem\"",
    "REPO_DIR / 'iMem'",
]

FORBIDDEN_IMPORT_MODULES = (
    "memory_service",
    "server",
    "scripts",
    "iMem",
)

COMPILE_TARGETS = [
    ROOT / "test" / "check_package_boundary.py",
    ROOT / "test" / "check_plugin_package.py",
    ROOT / "test" / "check_publication_layout.py",
    ROOT / "test" / "check_remote_mcp_contract.py",
]


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _iter_text_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and "__pycache__" not in path.parts
        and path != Path(__file__).resolve()
    ]


def _check_local_paths(violations: list[str]) -> None:
    for path in _iter_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in LOCAL_PATH_PATTERNS:
            if pattern.search(text):
                violations.append(f"{_relative(path)} contains local developer path")
                break


def _check_parent_repository_paths(violations: list[str]) -> None:
    for path in _iter_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in PARENT_REPOSITORY_PATTERNS:
            if pattern in text:
                violations.append(f"{_relative(path)} contains parent repository path: {pattern}")


def _check_python_imports(violations: list[str]) -> None:
    import_pattern = re.compile(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", re.MULTILINE)

    for path in ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in import_pattern.finditer(text):
            module = match.group(1).split(".")[0]
            if module in FORBIDDEN_IMPORT_MODULES:
                violations.append(f"{_relative(path)} imports service repository module: {match.group(0).strip()}")


def _check_required_runtime_files(violations: list[str]) -> None:
    for path in [
        ROOT / "skills" / "imem-skill" / "SKILL.md",
    ]:
        if not path.exists():
            violations.append(f"missing standalone runtime file: {_relative(path)}")


def _check_syntax(violations: list[str]) -> None:
    for path in COMPILE_TARGETS:
        if not path.exists():
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            violations.append(f"{_relative(path)} does not compile: {exc.msg}")


def main() -> int:
    violations: list[str] = []

    _check_required_runtime_files(violations)
    _check_local_paths(violations)
    _check_parent_repository_paths(violations)
    _check_python_imports(violations)
    _check_syntax(violations)

    if violations:
        print("iMem-skill standalone repository violations:")
        for violation in sorted(violations):
            print(f"- {violation}")
        return 1

    print("iMem-skill standalone repository OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
