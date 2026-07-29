"""Validate the public iMem Skill repository layout."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "imem-skill"
PLUGIN_DIR = ROOT / "plugins" / "imem"


REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / ".gitignore",
    ROOT / ".agents" / "plugins" / "marketplace.json",
    ROOT / ".claude-plugin" / "marketplace.json",
    ROOT / ".codebuddy-plugin" / "marketplace.json",
    ROOT / ".workbuddy-plugin" / "marketplace.json",
    PLUGIN_DIR / ".codex-plugin" / "plugin.json",
    PLUGIN_DIR / ".mcp.json",
    PLUGIN_DIR / ".claude-plugin" / "plugin.json",
    PLUGIN_DIR / ".claude-mcp.json",
    PLUGIN_DIR / "skills" / "imem-skill" / "SKILL.md",
    ROOT / ".github" / "workflows" / "validate.yml",
    ROOT / "contracts" / "remote-mcp.json",
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "agents" / "openai.yaml",
    SKILL_DIR / "references" / "agent-contract.md",
    SKILL_DIR / "references" / "mcp-tool-spec.md",
    SKILL_DIR / "references" / "product-language.md",
]


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    violations: list[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            violations.append(f"missing required file: {_relative(path)}")

    skill_path = SKILL_DIR / "SKILL.md"
    if skill_path.exists():
        text = skill_path.read_text(encoding="utf-8")
        if not re.search(r"(?m)^name:\s*imem-skill\s*$", text):
            violations.append("SKILL.md frontmatter must use name: imem-skill")
        for reference in [
            "references/agent-contract.md",
            "references/mcp-tool-spec.md",
            "references/product-language.md",
        ]:
            if reference not in text:
                violations.append(f"SKILL.md must reference {reference}")
        for forbidden in [
            "docs/agent_contract.md",
            "docs/api_tool_spec.md",
            "docs/product_language.md",
        ]:
            if forbidden in text:
                violations.append(f"SKILL.md must not reference copied-skill-external path {forbidden}")

    openai_path = SKILL_DIR / "agents" / "openai.yaml"
    if openai_path.exists():
        text = openai_path.read_text(encoding="utf-8")
        for required in [
            "display_name:",
            "short_description:",
            "default_prompt:",
            "$imem-skill",
            'transport: "streamable_http"',
            'url: "https://imem.xin/mcp"',
        ]:
            if required not in text:
                violations.append(f"openai.yaml missing expected text: {required}")

    readme_path = ROOT / "README.md"
    if readme_path.exists():
        text = readme_path.read_text(encoding="utf-8")
        normalized_text = text.lower()
        for required in [
            "unofficial",
            "experimental",
            "not affiliated with",
            "codex",
            "claude code",
            "workbuddy",
            "hermes",
            "agent platform support",
            "https://imem.xin/mcp",
            "bearer_token_env_var",
            "imem_api_key",
            "skills/imem-skill",
            "$imem-skill",
            "compatibility",
            "safety and data boundaries",
            "contracts/remote-mcp.json",
            "upgrade",
            "uninstall",
            "mit license",
        ]:
            if required not in normalized_text:
                violations.append(f"README.md missing expected text: {required}")

    license_path = ROOT / "LICENSE"
    if license_path.exists() and "MIT License" not in license_path.read_text(encoding="utf-8"):
        violations.append("LICENSE must contain MIT License")

    workflow_path = ROOT / ".github" / "workflows" / "validate.yml"
    if workflow_path.exists():
        text = workflow_path.read_text(encoding="utf-8")
        for required in [
            "check_publication_layout.py",
            "check_standalone_repository.py",
            "check_package_boundary.py",
            "check_plugin_package.py",
            "check_remote_mcp_contract.py",
            "py_compile",
        ]:
            if required not in text:
                violations.append(f"validate.yml missing expected text: {required}")

    if skill_path.exists():
        text = skill_path.read_text(encoding="utf-8").lower()
        for required in [
            "imem_get_time_context",
            "authenticated remote mcp tools",
        ]:
            if required not in text:
                violations.append(f"SKILL.md missing remote MCP contract: {required}")

    removed_user_tools = {
        "imem_" + "generate_html",
        "imem_" + "export_jsonl",
        "imem_" + "get_operations",
    }
    public_roots = [
        ROOT / "README.md",
        ROOT / "README.zh-CN.md",
        ROOT / "agents",
        ROOT / "references",
        ROOT / "skills",
    ]
    for public_root in public_roots:
        paths = [public_root] if public_root.is_file() else public_root.rglob("*")
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in {".md", ".py", ".yaml", ".yml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for removed_tool in removed_user_tools:
                if removed_tool in text:
                    violations.append(
                        f"{_relative(path)} references removed MCP tool: {removed_tool}"
                    )

    if violations:
        print("iMem-skill publication layout violations:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("iMem-skill publication layout OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
