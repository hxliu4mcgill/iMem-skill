"""Check that public Skill surfaces match the versioned remote MCP contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "remote-mcp.json"
SKILL_PATH = ROOT / "skills" / "imem-skill" / "SKILL.md"
API_SPEC_PATH = ROOT / "skills" / "imem-skill" / "references" / "mcp-tool-spec.md"
OPENAI_PATH = ROOT / "skills" / "imem-skill" / "agents" / "openai.yaml"

FORBIDDEN_USER_MCP_TOOLS = {
    "imem_generate_html",
    "imem_export_jsonl",
    "imem_get_operations",
}
def main() -> int:
    violations: list[str] = []
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    remote_tools = set(contract["public_tools"])

    if contract.get("production_url") != "https://imem.xin/mcp":
        violations.append("contract production_url must be https://imem.xin/mcp")
    if contract.get("transport") != "streamable-http":
        violations.append("contract transport must be streamable-http")
    if contract.get("authentication") != "bearer-api-key":
        violations.append("contract authentication must be bearer-api-key")
    if contract.get("oauth_status") != "pending":
        violations.append("contract oauth_status must be pending")

    for path in [SKILL_PATH, API_SPEC_PATH]:
        text = path.read_text(encoding="utf-8")
        for tool in remote_tools:
            if tool not in text:
                violations.append(f"{path.relative_to(ROOT)} missing remote tool: {tool}")
        for tool in FORBIDDEN_USER_MCP_TOOLS:
            if tool in text:
                violations.append(f"{path.relative_to(ROOT)} exposes forbidden user tool: {tool}")

    openai_text = OPENAI_PATH.read_text(encoding="utf-8")
    if contract["production_url"] not in openai_text:
        violations.append("agents/openai.yaml does not use the contract production URL")
    if 'transport: "streamable_http"' not in openai_text:
        violations.append("agents/openai.yaml must declare streamable_http")

    if violations:
        print("iMem remote MCP contract violations:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("iMem remote MCP contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
