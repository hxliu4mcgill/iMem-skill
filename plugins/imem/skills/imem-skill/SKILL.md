---
name: imem-skill
description: Use the authenticated iMem remote MCP service to save and search durable workspace memories and manage schedules and reminders. Trigger for requests to remember, recall, schedule, remind, update, cancel, or delete information stored in iMem.
---

# iMem Skill

## Purpose

Use iMem to turn user requests into durable workspace memories and manage the
integrated Schedule and Reminder module. Prefer the authenticated remote MCP
endpoint configured by the Agent host.

This file is the Agent first-read entry point. It defines when to use iMem and
how to use its remote tools. Full contracts live in:

```text
references/agent-contract.md
references/mcp-tool-spec.md
references/product-language.md
```

## When To Use iMem

Use iMem when the user asks to:

```text
remember or save durable information
create a schedule or calendar-like event
create a one-shot or recurring reminder
search workspace memories, schedules, or reminders
update an existing memory, schedule, or reminder
cancel a schedule or reminder
delete or archive a memory
```

## Choose The Capability

Route by user intent:

```text
save a fact, note, reference, decision, preference, or context -> Memory
make an explicit time arrangement                              -> Schedule + Reminder
trigger or notify at an explicit time                          -> Schedule + Reminder
add another trigger to an existing Schedule                    -> Reminder
```

A date is not enough by itself:

```text
"We decided this on June 12." -> Memory
"Schedule this for June 12."  -> Schedule + Reminder
"Remind me on June 12."       -> Schedule + Reminder
```

Do not create Schedule or Reminder for an ordinary Memory unless the user asks
for time-based behavior. For a new user request, both schedule wording and
reminder wording create a Schedule with an attached Reminder through
`imem_create_schedule(reminders=[...])`. Use `imem_create_reminder` only to add
another Reminder to an existing Schedule whose `schedule_id` has been found or
confirmed.

For image or screenshot input, first understand the image content. If essential
fields are missing, ask for clarification before writing.

## Relative Time

Schedule fields (`start_time`, `end_time`) require concrete ISO datetimes.
Before converting any relative time expression
("today", "tomorrow", "the day after", "this Thursday", "next Monday",
"in N minutes", "N days later", ...) into a concrete datetime, fetch a fresh
authoritative time baseline:

```text
1. Call imem_get_time_context.
2. Use data.server_time and data.workspace_timezone as the baseline.
3. If the tool is unavailable, stop and report that the required remote MCP
   capability is not configured. Do not substitute an earlier or local time.
```

Never reuse a date or "today" that appeared earlier in the session — a single
session can span multiple days, so an earlier date may already be stale. Fetch
a new baseline for every operation that involves relative time.

Weekday resolution priority — when turning a weekday name ("this Thursday") into
a concrete date, decide in this order instead of always assuming next week (treat
the fresh `imem_get_time_context` result as "today"):

```text
- Today is that weekday             -> use today (even in the early morning; today's weekday has not passed)
- This week's weekday not yet past  -> use this week
- This week's weekday already past  -> use next week
```

Only pick next week when the user explicitly says "next <weekday>".

## Tool Surface

Use only the authenticated remote MCP tools supplied by the Agent host. The
installable Skill does not use HTTP, a local Python adapter, CLI scripts, or
service files as runtime fallbacks.

## MCP Tools

Prefer these tools when available:

```text
imem_health
imem_get_time_context
imem_search
imem_create_memory
imem_create_schedule
imem_create_reminder
imem_update_entry
imem_cancel_entry
```

The production remote MCP does not expose export, operation-log, API-key
administration, scheduler, or delivery tools. Report that those capabilities
are outside this Skill instead of inventing a fallback.

If the MCP tools are not visible in the current tool list, do not assume they
are unavailable. First use tool discovery to search for `imem_health`,
`imem_create_memory`, `imem_create_schedule`, or other `imem_*` tools, because
hosts may expose MCP tools lazily. If discovery still cannot expose the needed
tool, stop and ask the user/operator to configure or reconnect the iMem remote
MCP server.

## Core Rules

1. Run `imem_health` before user-visible work when practical.
2. Protected calls must use an API key from the host environment or secret
   configuration.
3. Do not pass `workspace_id` in normal Agent workflows. The service derives it
   from the API key.
4. Create operations must include `request_id` and `idempotency_key`.
5. Search before update unless the exact target ID is already confirmed.
6. Search before delete or cancel unless the exact target ID is already
   confirmed.
7. If search returns multiple plausible targets, ask the user to choose.
8. If search cannot find a target, do not guess an ID.
9. Preserve MCP error codes. Do not present a failed write as successful.
10. When a datetime is derived from a relative expression, call
    `imem_get_time_context` first and never reuse an earlier session baseline.

## Minimal Workflows

For relative time, call `imem_get_time_context` for a fresh baseline and never
reuse an earlier session date.

Create memory:

```text
health -> imem_create_memory
```

Create a new schedule or reminder:

```text
health -> imem_create_schedule(reminders=[...])
```

Add another reminder to an existing schedule:

```text
health -> imem_search(schedule) -> imem_create_reminder(schedule_id=...)
```

Search:

```text
health -> imem_search -> summarize results
```

Update:

```text
health -> imem_search -> confirm target if needed -> imem_update_entry
```

Cancel or delete:

```text
health -> imem_search -> confirm target if needed -> imem_cancel_entry
```

## Error Handling

Follow `references/agent-contract.md` for complete recovery rules. Minimum behavior:

```text
UNAUTHORIZED: ask the user/operator to check API key configuration.
FORBIDDEN: report that the current key lacks the required scope.
ENTRY_NOT_FOUND: search again or ask the user to identify the target.
VALIDATION_FAILED: fix fields if clear, otherwise ask for missing information.
IDEMPOTENCY_CONFLICT: do not retry the same key; confirm intent before creating a new key.
```

## Hard Boundaries

Do not edit or generate these directly in normal Agent workflows:

```text
data/
*.db
*.jsonl
scripts/*.py
memory_service.operations
```

Do not treat Dashboard, scheduler scans, delivery logs, or real notification
channels as normal Agent-callable capabilities unless the service explicitly
implements and documents them.

Do not expose API keys, raw internal JSON, database paths, or script commands in
normal user replies unless the user explicitly asks for debugging or
maintenance details.
