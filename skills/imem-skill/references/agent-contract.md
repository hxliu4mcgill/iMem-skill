# iMem Agent Contract

This is the Agent-side copy of the iMem behavior contract. It keeps the
standalone `iMem-skill` package usable without requiring service-source access.

For tool details, read:

```text
mcp-tool-spec.md
```

Memory, Schedule, Reminder, and Artifact are separate service resources.
Schedule and Reminder form one user-facing module. New schedule and reminder
requests both create a Schedule with an attached Reminder. Direct Reminder
creation is only for adding another Reminder to an existing Schedule.

## Stable Agent Surface

Use iMem through this surface:

```text
Authenticated remote MCP tools at https://imem.xin/mcp
```

Do not use service internals for normal Agent work:

```text
data/
*.db
*.jsonl
scripts/*.py
memory_service.operations
```

## Authentication And Workspace

Protected calls use:

```text
Authorization: Bearer <api-key>
```

The service resolves the API key to a tenant context:

```text
user_id
workspace_id
client_id
client_name
scopes
```

Agents must not pass `workspace_id` in normal workflows. Workspace isolation is
derived from the API key.

The production remote MCP uses Streamable HTTP with Personal API Key bearer
authentication. OAuth is pending.

## Required Behavior

1. Run health check before user-visible work when practical.
2. Create operations require `request_id` and `idempotency_key`.
3. Search before update unless the exact target ID is already confirmed.
4. Search before cancel/delete unless the exact target ID is already confirmed.
5. Ask the user to choose when search returns multiple plausible targets.
6. Do not guess IDs when search finds no target.
7. Preserve service error codes and do not present failed writes as successful.
8. Call `imem_get_time_context` before resolving relative dates. Use its
   `server_time` and `workspace_timezone`, and never reuse an earlier session
   baseline.

## Intent Routing

Select the capability from the user's requested outcome:

```text
Fact, note, reference, decision, preference, or context
-> imem_create_memory

Explicit time arrangement
-> imem_create_schedule with reminders

Explicit timed trigger or notification
-> imem_create_schedule with reminders

Additional trigger for an existing Schedule
-> imem_create_reminder with the confirmed schedule_id

Agent-generated text, Markdown, or HTML deliverable
-> imem_upload_artifact
```

Do not route solely from extracted dates:

```text
"The decision was made on June 12." -> Memory
"Schedule the review for June 12."   -> Schedule + Reminder
"Remind me on June 12."              -> Schedule + Reminder
```

Rules:

1. Descriptive or historical dates do not imply a Schedule.
2. New schedule and reminder requests use one `imem_create_schedule` call with
   an attached reminder.
3. Use `imem_create_reminder` only after selecting an existing Schedule.
4. Ask for clarification when save and time-based behavior are materially
   different plausible outcomes.
5. Do not assume a family workspace or family relationships.

Reminder policies attached to a Schedule use `offset_minutes`, `channel`,
`message_override`, and `is_default`. The production `imem_create_reminder`
tool uses the same policy fields and requires a confirmed `schedule_id`.

## Scope Matrix

| Capability | MCP tool | Scope |
|---|---|---|
| Health | `imem_health` | `entries:read` |
| Time baseline | `imem_get_time_context` | `entries:read` |
| Search entries | `imem_search` | `entries:read` |
| Create memory | `imem_create_memory` | `entries:write` |
| Upload private Artifact | `imem_upload_artifact` | `entries:write` |
| Create schedule | `imem_create_schedule` | `entries:write` |
| Add reminder to a schedule | `imem_create_reminder` | `entries:write` |
| Update entry | `imem_update_entry` | `entries:write` |
| Delete/cancel entry | `imem_cancel_entry` | `entries:write` |

The production remote MCP exposes normal entry, Artifact upload, and
time-context tools.
Operation logs, exports, API-key administration, scheduler scans, and delivery
operations remain outside that MCP surface.

## Idempotency

Idempotency is supported for:

```text
imem_create_memory
imem_upload_artifact
imem_create_schedule
imem_create_reminder
```

Reuse the same key and same body only for retrying the same intended create.
If the object changes, confirm the new intent and use a new key. Reusing a key
with a different request produces `IDEMPOTENCY_CONFLICT`.

## Artifact Upload

Use `imem_upload_artifact` for complete deliverables that should remain
readable as text, Markdown, or rendered HTML. Every upload starts private. The
Agent must not claim it is publicly accessible or try to change visibility;
the user enables and disables the Public Link in the authenticated iMem App.

## Update, Delete, And Cancel

Update only after selecting a clear target from search or a confirmed current
tool response.

Deletion is soft state transition:

| Entity type | User wording | Service behavior |
|---|---|---|
| `memory` | delete or archive | status becomes deleted |
| `schedule` | cancel | status becomes canceled; related reminders are canceled |
| `reminder` | cancel | status becomes canceled |

Do not physically delete rows, files, or JSONL lines.

## Failure Handling

| Error code | Required Agent behavior |
|---|---|
| `UNAUTHORIZED` | Ask the user/operator to check API key configuration. |
| `FORBIDDEN` | Report that the current key lacks the required scope. |
| `ENTRY_NOT_FOUND` | Search again or ask the user to identify the target. Do not guess IDs. |
| `VALIDATION_FAILED` | Fix fields if clear, otherwise ask for missing information. |
| `INVALID_ENTITY_TYPE` | Use only `memory`, `schedule`, or `reminder`. |
| `IDEMPOTENCY_CONFLICT` | Do not retry the same key. Confirm intent before creating a new key. |
| `CONFIGURATION_ERROR` | Check the MCP URL and host configuration. |
| `MCP_TOOL_ERROR` | Inspect the structured error. Do not assume the write succeeded. |

Scheduler scans, delivery logs, and real notification channels are outside the
normal Agent surface unless explicitly implemented and documented.
