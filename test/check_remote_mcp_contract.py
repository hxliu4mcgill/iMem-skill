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

LEGACY_SECTION_MARKERS = {
    SKILL_PATH: "The following tools are migration aliases only",
    AGENT_CONTRACT_PATH: "## Compatibility",
    API_SPEC_PATH: "## Migration Aliases",
    PRODUCT_LANGUAGE_PATH: "## Compatibility Language",
}

EXPECTED_OPTIMISTIC_CONCURRENCY = {
    "revision_field": "revision",
    "expected_revision_parameter": "expected_revision",
    "canonical_update_tools": [
        "imem_update_entry",
        "imem_update_entry_reminder_rule",
    ],
    "conflict_error": "REVISION_CONFLICT",
    "skill_requires_expected_revision": True,
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
    if contract.get("optimistic_concurrency") != EXPECTED_OPTIMISTIC_CONCURRENCY:
        violations.append("contract optimistic_concurrency differs from revision contract")

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
        "expected_revision",
        "REVISION_CONFLICT",
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

    for path, marker in LEGACY_SECTION_MARKERS.items():
        text = path.read_text(encoding="utf-8")
        marker_index = text.find(marker)
        if marker_index < 0:
            violations.append(
                f"{path.relative_to(ROOT)} missing explicit compatibility marker: {marker}"
            )
            continue
        for alias in EXPECTED_LEGACY_ALIASES:
            alias_index = text.find(alias)
            if alias_index >= 0 and alias_index < marker_index:
                violations.append(
                    f"{path.relative_to(ROOT)} uses legacy alias before compatibility "
                    f"section: {alias}"
                )

    reference_texts = {
        AGENT_CONTRACT_PATH: AGENT_CONTRACT_PATH.read_text(encoding="utf-8"),
        API_SPEC_PATH: API_SPEC_PATH.read_text(encoding="utf-8"),
        PRODUCT_LANGUAGE_PATH: PRODUCT_LANGUAGE_PATH.read_text(encoding="utf-8"),
    }
    for path, text in reference_texts.items():
        for required in [
            "entry_id",
            "schedule_details",
            "reminder_rules",
            "revision",
            "expected_revision",
            "REVISION_CONFLICT",
        ]:
            if required not in text:
                violations.append(
                    f"{path.relative_to(ROOT)} missing unified term: {required}"
                )

    api_spec_text = reference_texts[API_SPEC_PATH]
    if api_spec_text.count("expected_revision?: integer") != 2:
        violations.append(
            "mcp-tool-spec.md must declare expected_revision on exactly two update tools"
        )
    if "A stale value returns `REVISION_CONFLICT`" not in api_spec_text:
        violations.append("mcp-tool-spec.md must document a stale revision conflict")
    if "imem_update_entry(entry_id=...) with" in skill_text:
        violations.append("SKILL.md still documents update without expected_revision")
    for required in [
        "Never automatically retry `REVISION_CONFLICT`",
        "never omit\n`expected_revision` to force an overwrite",
    ]:
        if required not in skill_text:
            violations.append(f"SKILL.md missing revision safety rule: {required}")

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
