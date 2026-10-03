# iMem Remote MCP Tool Specification

This is the public Agent contract for the production iMem remote MCP service.

## Production Connection

```text
MCP URL: https://imem.xin/mcp
Transport: Streamable HTTP
Authentication: Authorization: Bearer <personal-api-key>
OAuth: pending
```

Create a Personal API Key after registering and signing in at
`https://imem.xin/app/api-keys`. The service derives the user and workspace from
that key. Never pass `workspace_id` in normal Agent requests.

The only normal Skill call chain is:

```text
Agent -> https://imem.xin/mcp -> iMem service
```

Never access SQLite, JSONL, server data directories, scripts, or service
implementation modules during normal Agent work.

## Resource Semantics

Memory, Schedule, Reminder, and Artifact are separate stored resources.
Schedule and Reminder form one user-facing module.

```text
save a fact or context                       -> imem_create_memory
create a new schedule                        -> imem_create_schedule
create a new reminder                        -> imem_create_schedule
add another notification to an existing item -> imem_create_reminder
upload a generated text/Markdown/HTML result  -> imem_upload_artifact
```

Both new schedule wording and new reminder wording create a Schedule with its
Reminder policies. Call `imem_create_reminder` only after finding or confirming
the existing `schedule_id`.

## Production MCP Tools

| Tool | Required scope | Purpose |
|---|---|---|
| `imem_health` | `entries:read` | Verify authenticated service access |
| `imem_get_time_context` | `entries:read` | Get current server/workspace time baseline |
| `imem_search` | `entries:read` | Search memories, schedules, and reminders |
| `imem_create_memory` | `entries:write` | Create a durable Memory |
| `imem_upload_artifact` | `entries:write` | Upload a private text, Markdown, or HTML Artifact |
| `imem_create_schedule` | `entries:write` | Create a Schedule and Reminder policies |
| `imem_create_reminder` | `entries:write` | Add a Reminder policy to an existing Schedule |
| `imem_update_entry` | `entries:write` | Update a selected entry |
| `imem_cancel_entry` | `entries:write` | Cancel or soft-delete a selected entry |

The production remote MCP intentionally does not expose export, operation-log,
API-key administration, scheduler, or delivery tools.

## Tool Parameters

### `imem_health`

No parameters.

### `imem_get_time_context`

No parameters. Use `data.server_time` and `data.workspace_timezone` as the
authoritative baseline for relative dates.

### `imem_search`

```text
q?: string
entity_type?: memory | schedule | reminder
start_date?: YYYY-MM-DD
end_date?: YYYY-MM-DD
category?: string
status?: string
month?: YYYY-MM
limit?: number
include_related?: boolean
```

### `imem_create_memory`

```text
title: string
content: string
request_id: string
idempotency_key: string
category?: string
owner?: string
members?: string[]
tags?: string[]
visibility?: string
source?: object
```

### `imem_upload_artifact`

```text
title: string
content: string
media_type: text/plain | text/markdown | text/html
request_id: string
idempotency_key: string
```

The created Artifact is always private and returns its owner URL. The tool does
not accept a visibility parameter and cannot create or enable a Public Link.
Only the user can enable public access in the authenticated iMem Web App.

### `imem_create_schedule`

```text
title: string
start_time: ISO datetime
request_id: string
idempotency_key: string
end_time?: ISO datetime
location?: string
category?: string
participants?: string[]
notes?: string
memory_id?: string
memory?: object
reminders?: object[]
recurrence?: object
timezone?: IANA timezone
```

Reminder policies inside `reminders` use:

```text
offset_minutes: integer
channel?: string
message_override?: string
is_default?: boolean
```

Use a fresh `imem_get_time_context` result before resolving relative
`start_time` or `end_time`. The canonical recurrence object uses `version`,
`frequency`, and optional fields such as `interval`, `by_weekday`,
`by_monthday`, `count`, or `until`.

### `imem_create_reminder`

```text
schedule_id: string
offset_minutes: integer
request_id: string
idempotency_key: string
channel?: string
message_override?: string
is_default?: boolean
```

This tool adds another notification policy to an existing Schedule. Search for
and confirm the Schedule before calling it.

### `imem_update_entry`

```text
entity_type: memory | schedule | reminder
entity_id: string
patch: object
request_id: string
```

### `imem_cancel_entry`

```text
entity_type: memory | schedule | reminder
entity_id: string
reason: string
request_id: string
```

## MCP Return Format

Success:

```json
{
  "ok": true,
  "data": {},
  "error": null,
  "source": "imem-remote-mcp"
}
```

Failure:

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "..."
  },
  "source": "imem-remote-mcp"
}
```

Preserve `error.code`. Never present a failed write as successful.

## Idempotency and Recovery

Create and upload tools require both `request_id` and `idempotency_key`. Reuse the same
idempotency key only when retrying the same intended create with identical
arguments. A reused key with different arguments returns
`IDEMPOTENCY_CONFLICT`.

After an uncertain update or cancel failure, search current state before
retrying. When search returns multiple plausible targets, ask the user to
choose. Never guess an ID.

## Error Handling

| Error code | Required behavior |
|---|---|
| `UNAUTHORIZED` | Ask the user to check the configured API key. |
| `FORBIDDEN` | Report the missing scope. |
| `ENTRY_NOT_FOUND` | Search again or ask the user to identify the target. |
| `VALIDATION_FAILED` | Correct clear field errors or ask for missing information. |
| `INVALID_ENTITY_TYPE` | Use only `memory`, `schedule`, or `reminder`. |
| `IDEMPOTENCY_CONFLICT` | Do not retry with that key; confirm intent first. |
| `MCP_TOOL_ERROR` | Treat the outcome as failed or uncertain; never claim success. |
