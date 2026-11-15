"""Validate the installable DeepSeek Harness bundle."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "plugins" / "imem-dsh"
PACKAGE_PATH = PACKAGE_ROOT / "package.json"
PATCH_PATH = PACKAGE_ROOT / "cordis.patch.yml"
CANONICAL_SKILL = ROOT / "skills" / "imem-skill"
PACKAGED_SKILL = PACKAGE_ROOT / "skills" / "imem-skill"


def _file_map(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def main() -> int:
    violations: list[str] = []

    for path in (PACKAGE_PATH, PATCH_PATH, PACKAGE_ROOT / "README.md"):
        if not path.is_file():
            violations.append(f"missing DSH package file: {path.relative_to(ROOT)}")

    if violations:
        for violation in violations:
            print(f"- {violation}")
        return 1

    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
    if package.get("name") != "dsh-plugin-imem":
        violations.append("DSH package name must be dsh-plugin-imem")
    if not re.fullmatch(r"\d+\.\d+\.\d+", package.get("version", "")):
        violations.append("DSH package version must use stable SemVer")
    if package.get("dsh") != {"bundle": {"patch": "./cordis.patch.yml"}}:
        violations.append("DSH package must declare dsh.bundle.patch")
    if not (package.get("engines") or {}).get("dsh"):
        violations.append("DSH package must declare engines.dsh")

    files = set(package.get("files") or [])
    if files != {"cordis.patch.yml", "README.md", "skills"}:
        violations.append("DSH package files allowlist is unexpected")

    patch = PATCH_PATH.read_text(encoding="utf-8")
    required_patch_text = [
        "id: imem-mcp",
        "name: '@deepseek-ai/dsh-mcp-client'",
        "serverName: imem",
        "transport: streamable-http",
        "url: https://imem.xin/mcp",
        "Authorization: 'Bearer ${credential:IMEM_API_KEY}'",
        "expandTemplates: true",
        "id: imem-skill-filesystem",
        "name: '@deepseek-ai/dsh-skill-filesystem'",
        "providerName: imem-plugin",
        "includeDefaultRoots: false",
        "watch: false",
        "bundledSkillDir:",
        "resolve('dsh-plugin-imem/package.json')",
    ]
    for required in required_patch_text:
        if required not in patch:
            violations.append(f"cordis.patch.yml missing expected text: {required}")

    if not PACKAGED_SKILL.is_dir():
        violations.append("DSH package must include skills/imem-skill")
    elif _file_map(CANONICAL_SKILL) != _file_map(PACKAGED_SKILL):
        violations.append(
            "DSH Skill mirror differs from canonical skills/imem-skill; "
            "run python tools/sync_plugin_skill.py"
        )

    if violations:
        print("iMem DeepSeek Harness package violations:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("iMem DeepSeek Harness package OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
