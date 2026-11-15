---
name: imem-skill
description: Use the authenticated iMem remote MCP service to create, find, update, and delete durable note or schedule Entries; manage nested Schedule reminder rules and occurrences; and upload text, Markdown, or HTML deliverables as private Artifacts. Trigger for requests to remember, recall, schedule, remind, update, cancel, delete, save a durable deliverable, or publish an Agent-generated artifact to iMem.
---

# iMem Skill

## Purpose

Use iMem as a durable workspace system. Treat every independently manageable
note or schedule as one `Entry` with one `entry_id`:

```text
Entry(kind=note)     -> durable note or memory
Entry(kind=schedule) -> common content + schedule_details + reminder_rules
Artifact             -> private generated text, Markdown, or HTML deliverable
```

Do not make the Agent coordinate legacy Memory, Schedule, and Reminder IDs.
Read the detailed contracts only when needed:

```text
references/agent-contract.md
references/mcp-tool-spec.md
references/product-language.md
```

## Route User Intent

```text
save a fact, note, reference, decision, preference, or context
-> imem_create_entry(kind=note)

make an explicit time arrangement
-> imem_create_entry(kind=schedule, schedule_details=...)

create a new timed reminder
-> imem_create_entry(kind=schedule, schedule_details=..., reminder_rules=[...])

add another reminder to an existing Schedule Entry
-> imem_create_entry_reminder_rule(entry_id=...)

save a generated text, Markdown, or HTML deliverable
-> imem_upload_artifact
```

A date alone does not make content a Schedule:

```text
"We decided this on June 12." -> note Entry
"Schedule this for June 12."  -> schedule Entry
"Remind me on June 12."       -> schedule Entry with a reminder rule
```

Ask for clarification only when note and time-based behavior are materially
different plausible outcomes. For image or screenshot input, understand the
content first and ask for essential missing fields before writing.

## Resolve Relative Time

Before converting relative time such as "today", "tomorrow", "this Thursday",
"next Monday", or "in two hours":

```text
1. Call imem_get_time_context.
2. Use data.server_time and data.workspace_timezone as the baseline.
3. Stop if the tool is unavailable; do not substitute local or stale time.
```

Fetch a fresh baseline for every operation involving relative time. Resolve a
weekday in this order:

```text
today is that weekday            -> today
this week's weekday is ahead     -> this week
this week's weekday has passed   -> next week
explicit "next <weekday>"        -> next week
```

## Use The Remote MCP Surface

Use only the authenticated remote MCP tools supplied by the Agent host. Do not
use HTTP, local adapters, service files, SQLite, JSONL, or implementation
modules as runtime fallbacks.

Prefer these canonical tools:

```text
imem_health
imem_get_time_context
imem_create_entry
imem_list_entries
imem_get_entry
imem_update_entry
imem_delete_entry
imem_list_entry_occurrences
imem_create_entry_reminder_rule
imem_update_entry_reminder_rule
imem_delete_entry_reminder_rule
imem_upload_artifact
```

The following tools are migration aliases only. Do not use them for new
workflows:

```text
imem_search
imem_create_memory
imem_create_schedule
imem_create_reminder
imem_cancel_entry
```

`imem_update_entry` temporarily accepts either canonical `entry_id` or the
legacy `entity_type + entity_id` pair. Always use `entry_id`.

If tools are not visible, use tool discovery for `imem_health`,
`imem_create_entry`, or another canonical `imem_*` tool. If discovery still
cannot expose the needed capability, ask the user or operator to reconnect the
iMem remote MCP server.

## Follow Core Rules

1. Run `imem_health` before user-visible work when practical.
2. Let authentication determine the workspace; never pass `workspace_id`.
3. Include `request_id` on mutations.
4. Include `idempotency_key` on Entry, Reminder Rule, and Artifact creates.
5. List Entries to select a target when `entry_id` is unknown. Before every
   Entry update, get that Entry and capture its latest top-level `revision`,
   even when `entry_id` is already confirmed.
6. Before every Reminder Rule update, get the owning Schedule Entry, select the
   rule, and capture that rule's latest `revision`.
7. Pass the captured value as `expected_revision` to canonical Entry and
   Reminder Rule update tools.
8. Ask the user to choose when multiple Entries plausibly match.
9. Never guess `entry_id`, `rule_id`, or a revision.
10. Keep `kind` immutable. Put schedule changes under `schedule_details`.
11. Manage reminders only through a Schedule Entry's nested reminder-rule tools.
12. Preserve MCP error codes and never present a failed write as successful.
13. Keep Artifact uploads private. Only the user can enable a Public Link.

## Use Minimal Workflows

```text
create note
health -> imem_create_entry(kind=note)

create schedule or reminder
health -> time context if relative -> imem_create_entry(kind=schedule)

find content
health -> imem_list_entries -> imem_get_entry when details are needed

update Entry
health -> list if ID unknown -> get Entry -> capture Entry revision
-> imem_update_entry(entry_id=..., expected_revision=revision)

delete or cancel
health -> list/get unless ID confirmed -> imem_delete_entry(entry_id=...)

calendar or Today range
health -> time context if relative -> imem_list_entry_occurrences

add or delete a reminder rule
health -> get Schedule Entry -> nested create/delete reminder-rule tool

update a reminder rule
health -> get Schedule Entry -> select rule -> capture rule revision
-> imem_update_entry_reminder_rule(expected_revision=revision)

upload a deliverable
health -> imem_upload_artifact
```

Use `text/plain`, `text/markdown`, or `text/html` for Artifacts. Return the
owner URL and state that the Artifact remains private until the user enables
its Public Link.

## Handle Errors

Follow `references/agent-contract.md`. Minimum behavior:

```text
UNAUTHORIZED          -> ask the user/operator to check the API key
FORBIDDEN             -> report the missing scope
ENTRY_NOT_FOUND       -> list again or ask the user to identify the target
VALIDATION_FAILED     -> fix clear fields or ask for missing information
INVALID_ENTRY_KIND    -> use note or schedule
IDEMPOTENCY_CONFLICT  -> do not retry that key; confirm intent
REVISION_CONFLICT     -> re-read, explain the concurrent change, and ask
                         whether to retry with the latest revision or merge
MCP_TOOL_ERROR        -> treat the outcome as failed or uncertain
```

Never automatically retry `REVISION_CONFLICT` and never omit
`expected_revision` to force an overwrite. Re-read the Entry, show the user
what changed, and wait for an explicit retry or merge decision.

## Respect Boundaries

Do not edit or generate these directly during normal Agent workflows:

```text
data/
*.db
*.jsonl
scripts/*.py
memory_service.operations
```

Do not treat exports, operation logs, API-key administration, scheduler scans,
delivery logs, or delivery channels as Agent-callable unless the remote MCP
explicitly exposes and documents them.
