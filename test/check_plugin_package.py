"""Validate the installable iMem Agent Plugin wiring."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "imem"
CODEX_PLUGIN_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
CODEX_MCP_PATH = PLUGIN_ROOT / ".mcp.json"
CODEX_MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_PLUGIN_PATH = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CLAUDE_MCP_PATH = PLUGIN_ROOT / ".claude-mcp.json"
CLAUDE_MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
CODEBUDDY_MARKETPLACE_PATH = ROOT / ".codebuddy-plugin" / "marketplace.json"
WORKBUDDY_MARKETPLACE_PATH = ROOT / ".workbuddy-plugin" / "marketplace.json"
CONTRACT_PATH = ROOT / "contracts" / "remote-mcp.json"
OPENAI_PATH = ROOT / "skills" / "imem-skill" / "agents" / "openai.yaml"
CANONICAL_SKILL = ROOT / "skills" / "imem-skill"
PLUGIN_SKILL = PLUGIN_ROOT / "skills" / "imem-skill"


def _file_map(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def main() -> int:
    violations: list[str] = []
    codex_plugin = json.loads(CODEX_PLUGIN_PATH.read_text(encoding="utf-8"))
    codex_mcp = json.loads(CODEX_MCP_PATH.read_text(encoding="utf-8"))
    codex_marketplace = json.loads(
        CODEX_MARKETPLACE_PATH.read_text(encoding="utf-8")
    )
    claude_plugin = json.loads(CLAUDE_PLUGIN_PATH.read_text(encoding="utf-8"))
    claude_mcp = json.loads(CLAUDE_MCP_PATH.read_text(encoding="utf-8"))
    claude_marketplace = json.loads(
        CLAUDE_MARKETPLACE_PATH.read_text(encoding="utf-8")
    )
    compatible_marketplaces = {
        "CodeBuddy": json.loads(
            CODEBUDDY_MARKETPLACE_PATH.read_text(encoding="utf-8")
        ),
        "WorkBuddy": json.loads(
            WORKBUDDY_MARKETPLACE_PATH.read_text(encoding="utf-8")
        ),
    }
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    for key in ("name", "version", "description", "author", "interface"):
        if not codex_plugin.get(key):
            violations.append(f"Codex plugin.json missing required field: {key}")

    if codex_plugin.get("name") != "imem":
        violations.append("Codex plugin.json name must be imem")
    if not re.fullmatch(r"\d+\.\d+\.\d+", codex_plugin.get("version", "")):
        violations.append("Codex plugin.json version must use strict stable semver")
    if codex_plugin.get("skills") != "./skills/":
        violations.append(
            "Codex plugin.json must reference its packaged ./skills/ directory"
        )
    if codex_plugin.get("mcpServers") != "./.mcp.json":
        violations.append("Codex plugin.json must reference ./.mcp.json")
    if (PLUGIN_ROOT / ".codex-mcp.json").exists():
        violations.append(
            "Plugin root must not contain legacy .codex-mcp.json"
        )

    codex_server = (codex_mcp.get("mcpServers") or {}).get("imem") or {}
    if codex_server.get("url") != contract.get("production_url"):
        violations.append(".mcp.json URL differs from the remote MCP contract")
    if codex_server.get("bearer_token_env_var") != "IMEM_API_KEY":
        violations.append(
            ".mcp.json must read the bearer token from IMEM_API_KEY"
        )

    openai_text = OPENAI_PATH.read_text(encoding="utf-8")
    if not codex_server.get("url") or codex_server["url"] not in openai_text:
        violations.append("agents/openai.yaml differs from the Codex Plugin MCP URL")

    if codex_marketplace.get("name") != "imem-plugins":
        violations.append("Codex marketplace.json name must be imem-plugins")
    entries = codex_marketplace.get("plugins") or []
    entry = next((item for item in entries if item.get("name") == "imem"), None)
    if not entry:
        violations.append("Codex marketplace.json must contain the imem Plugin")
    else:
        source = entry.get("source") or {}
        policy = entry.get("policy") or {}
        if source != {"source": "local", "path": "./plugins/imem"}:
            violations.append("Codex marketplace source must be ./plugins/imem")
        if policy.get("installation") != "AVAILABLE":
            violations.append(
                "Codex marketplace installation policy must be AVAILABLE"
            )
        if policy.get("authentication") != "ON_INSTALL":
            violations.append(
                "Codex marketplace authentication policy must be ON_INSTALL"
            )
        if entry.get("category") != "Productivity":
            violations.append("Codex marketplace category must be Productivity")

    for key in ("name", "version", "description", "author", "mcpServers", "userConfig"):
        if not claude_plugin.get(key):
            violations.append(f"Claude plugin.json missing required field: {key}")

    if claude_plugin.get("name") != "imem":
        violations.append("Claude plugin.json name must be imem")
    if not re.fullmatch(r"\d+\.\d+\.\d+", claude_plugin.get("version", "")):
        violations.append("Claude plugin.json version must use strict stable semver")
    if claude_plugin.get("mcpServers") != "./.claude-mcp.json":
        violations.append("Claude plugin.json must reference ./.claude-mcp.json")
    if claude_plugin.get("version") != codex_plugin.get("version"):
        violations.append("Codex and Claude plugin versions must match")

    api_key = (claude_plugin.get("userConfig") or {}).get("api_key") or {}
    if api_key.get("type") != "string":
        violations.append("Claude userConfig.api_key must use type string")
    if api_key.get("sensitive") is not True:
        violations.append("Claude userConfig.api_key must be sensitive")
    if api_key.get("required") is not True:
        violations.append("Claude userConfig.api_key must be required")

    claude_server = (claude_mcp.get("mcpServers") or {}).get("imem") or {}
    if claude_server.get("type") != "http":
        violations.append(".claude-mcp.json must use HTTP transport")
    if claude_server.get("url") != contract.get("production_url"):
        violations.append(".claude-mcp.json URL differs from the remote MCP contract")
    authorization = (claude_server.get("headers") or {}).get("Authorization")
    if authorization != "Bearer ${user_config.api_key}":
        violations.append(
            ".claude-mcp.json must read the bearer token from userConfig.api_key"
        )

    if claude_marketplace.get("name") != "imem-plugins":
        violations.append("Claude marketplace.json name must be imem-plugins")
    claude_entries = claude_marketplace.get("plugins") or []
    claude_entry = next(
        (item for item in claude_entries if item.get("name") == "imem"), None
    )
    if not claude_entry:
        violations.append("Claude marketplace.json must contain the imem Plugin")
    else:
        if claude_entry.get("source") != "./plugins/imem":
            violations.append("Claude marketplace source must be ./plugins/imem")
        if claude_entry.get("version") != claude_plugin.get("version"):
            violations.append(
                "Claude marketplace and plugin manifest versions must match"
            )
        if claude_entry.get("category") != "productivity":
            violations.append("Claude marketplace category must be productivity")

    for host, marketplace in compatible_marketplaces.items():
        if marketplace.get("name") != "imem-plugins":
            violations.append(f"{host} marketplace.json name must be imem-plugins")
        host_entries = marketplace.get("plugins") or []
        host_entry = next(
            (item for item in host_entries if item.get("name") == "imem"), None
        )
        if not host_entry:
            violations.append(
                f"{host} marketplace.json must contain the imem Plugin"
            )
            continue
        if host_entry.get("source") != "./plugins/imem":
            violations.append(f"{host} marketplace source must be ./plugins/imem")
        if host_entry.get("version") != claude_plugin.get("version"):
            violations.append(
                f"{host} marketplace and plugin manifest versions must match"
            )
        if host_entry.get("category") != "productivity":
            violations.append(
                f"{host} marketplace category must be productivity"
            )

    if not PLUGIN_SKILL.is_dir():
        violations.append("Plugin must package skills/imem-skill")
    elif _file_map(CANONICAL_SKILL) != _file_map(PLUGIN_SKILL):
        violations.append(
            "Plugin Skill mirror differs from canonical skills/imem-skill; "
            "run python tools/sync_plugin_skill.py"
        )

    if violations:
        print("iMem Plugin package violations:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("iMem Plugin package OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
