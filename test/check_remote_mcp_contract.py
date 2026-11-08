"""Check that public Skill surfaces match the versioned remote MCP contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "remote-mcp.json"
SKILL_PATH = ROOT / "skills" / "imem-skill" / "SKILL.md"
API_SPEC_PATH = ROOT / "skills" / "imem-skill" / "references" / "mcp-tool-spec.md"
AGENT_CONTRACT_PATH = ROOT / "skills" / "imem-skill" / "references" / "agent-contract.md"
PRODUCT_LANGUAGE_PATH = ROOT / "skills" / "imem-skill" / "references" / "product-language.md"
OPENAI_PATH = ROOT / "skills" / "imem-skill" / "agents" / "openai.yaml"

EXPECTED_CANONICAL_TOOLS = {
    "imem_health",
    "imem_get_time_context",
    "imem_create_entry",
    "imem_list_entries",
    "imem_get_entry",
    "imem_update_entry",
    "imem_delete_entry",
    "imem_list_entry_occurrences",
    "imem_create_entry_reminder_rule",
    "imem_update_entry_reminder_rule",
    "imem_delete_entry_reminder_rule",
    "imem_upload_artifact",
}

EXPECTED_LEGACY_ALIASES = {
    "imem_search",
    "imem_create_memory",
    "imem_create_schedule",
    "imem_create_reminder",
    "imem_cancel_entry",
}

FORBIDDEN_USER_MCP_TOOLS = {
    "imem_generate_html",
    "imem_export_jsonl",
    "imem_get_operations",
}


def main() -> int:
    violations: list[str] = []
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    canonical_tools = set(contract.get("canonical_tools") or [])
    legacy_aliases = set(contract.get("legacy_aliases") or [])
    public_tools = set(contract.get("public_tools") or [])

    if contract.get("contract_version") != "2026-11-02":
        violations.append("contract_version must be 2026-11-02")
    if contract.get("production_url") != "https://imem.xin/mcp":
        violations.append("contract production_url must be https://imem.xin/mcp")
    if contract.get("transport") != "streamable-http":
        violations.append("contract transport must be streamable-http")
    if contract.get("authentication") != "bearer-api-key":
        violations.append("contract authentication must be bearer-api-key")
    if contract.get("oauth_status") != "pending":
        violations.append("contract oauth_status must be pending")

    if canonical_tools != EXPECTED_CANONICAL_TOOLS:
        violations.append("canonical_tools differs from the unified Entry contract")
    if legacy_aliases != EXPECTED_LEGACY_ALIASES:
        violations.append("legacy_aliases differs from the migration contract")
    if public_tools != canonical_tools | legacy_aliases:
        violations.append("public_tools must equal canonical_tools plus legacy_aliases")

    for path in [SKILL_PATH, API_SPEC_PATH]:
        text = path.read_text(encoding="utf-8")
        for tool in public_tools:
            if tool not in text:
                violations.append(f"{path.relative_to(ROOT)} missing public tool: {tool}")
        for tool in FORBIDDEN_USER_MCP_TOOLS:
            if tool in text:
                violations.append(
                    f"{path.relative_to(ROOT)} exposes forbidden user tool: {tool}"
                )

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    for required in [
        "Entry(kind=note)",
        "Entry(kind=schedule)",
        "entry_id",
        "schedule_details",
        "reminder_rules",
        "migration aliases only",
    ]:
        if required not in skill_text:
            violations.append(f"SKILL.md missing unified Entry rule: {required}")

    for forbidden in [
        "health -> imem_create_memory",
        "health -> imem_create_schedule",
        "health -> imem_search ->",
        "imem_update_entry(entity_type=",
    ]:
        if forbidden in skill_text:
            violations.append(f"SKILL.md still prefers legacy workflow: {forbidden}")

    reference_texts = {
        AGENT_CONTRACT_PATH: AGENT_CONTRACT_PATH.read_text(encoding="utf-8"),
        PRODUCT_LANGUAGE_PATH: PRODUCT_LANGUAGE_PATH.read_text(encoding="utf-8"),
    }
    for path, text in reference_texts.items():
        for required in ["entry_id", "schedule_details", "reminder_rules"]:
            if required not in text:
                violations.append(
                    f"{path.relative_to(ROOT)} missing unified term: {required}"
                )

    openai_text = OPENAI_PATH.read_text(encoding="utf-8")
    for required in ["$imem-skill", "Entry", contract["production_url"]]:
        if required not in openai_text:
            violations.append(f"agents/openai.yaml missing expected text: {required}")
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
