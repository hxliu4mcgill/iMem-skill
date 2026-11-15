# iMem Remote MCP Tool Specification

This is the public Agent contract for production iMem remote MCP contract
`2026-11-02`.

## Production Connection

```text
MCP URL: https://imem.xin/mcp
Transport: Streamable HTTP
Authentication: Authorization: Bearer <personal-api-key>
OAuth: pending
```

Create a Personal API Key at `https://imem.xin/app/api-keys`. The service
derives user and workspace identity from that key. Never pass `workspace_id` in
normal Agent requests.

## Canonical Resource Shape

```json
{
  "id": "MEM-20261101-001",
  "revision": 1,
  "kind": "schedule",
  "title": "Product review",
  "content": "Review the launch scope",
  "category": "Work",
  "owner": "agent",
  "members": [],
  "tags": [],
  "visibility": "private",
  "source": {"type": "agent"},
  "status": "pending",
  "created_at": "2026-11-01T09:00:00",
  "updated_at": null,
  "deleted_at": null,
  "schedule_details": {
    "start_time": "2026-11-05T10:00:00+08:00",
    "end_time": "2026-11-05T11:00:00+08:00",
    "location": "",
    "participants": [],
    "notes": "",
    "recurrence": null,
    "timezone": "Asia/Shanghai",
    "next_occurrence_at": "2026-11-05T02:00:00Z"
  },
  "reminder_rules": []
}
```

`schedule_details` is `null` and `reminder_rules` is empty for a note Entry.
Every Entry has a top-level integer `revision`. Every nested Reminder Rule also
has its own integer `revision`. Reminder Rules are nested under Schedule Entries.
Occurrences expose `entry_id` and `occurrence_id`, never legacy identity as the
canonical key.

## Canonical Production Tools

| Tool | Scope | Purpose |
|---|---|---|
| `imem_health` | `entries:read` | Verify authenticated service access and contract version |
| `imem_get_time_context` | `entries:read` | Get authoritative server and workspace time |
| `imem_create_entry` | `entries:write` | Create a note or Schedule Entry |
| `imem_list_entries` | `entries:read` | List and filter Entries |
| `imem_get_entry` | `entries:read` | Read one Entry by canonical ID |
| `imem_update_entry` | `entries:write` | Patch one Entry |
| `imem_delete_entry` | `entries:write` | Soft-delete or cancel one Entry |
| `imem_list_entry_occurrences` | `entries:read` | Read Schedule occurrences for a range |
| `imem_create_entry_reminder_rule` | `entries:write` | Add a Reminder Rule to a Schedule Entry |
| `imem_update_entry_reminder_rule` | `entries:write` | Patch a nested Reminder Rule |
| `imem_delete_entry_reminder_rule` | `entries:write` | Delete/cancel a nested Reminder Rule |
| `imem_upload_artifact` | `entries:write` | Upload a private text, Markdown, or HTML Artifact |

## Tool Parameters

### `imem_health`

No parameters. Verify `data.status`, `data.mcp_url`, and
`data.contract_version`.

### `imem_get_time_context`

No parameters. Use `data.server_time` and `data.workspace_timezone` before
resolving relative dates or times.

### `imem_create_entry`

```text
kind: note | schedule
title: string
request_id: string
idempotency_key: string
content?: string
category?: string
owner?: string
members?: string[]
tags?: string[]
visibility?: string
source?: object
status?: string
created_at?: ISO datetime
schedule_details?: object
reminder_rules?: object[]
```

For `kind=schedule`, set `schedule_details.start_time` and optionally:

```text
end_time?: ISO datetime
location?: string
participants?: string[]
notes?: string
recurrence?: object
timezone?: IANA timezone
```

For `kind=note`, omit schedule details and reminder rules. Return
`data.entry`.

### `imem_list_entries`

```text
kind?: note | schedule
q?: string
status?: string
scheduled_from?: ISO datetime
scheduled_to?: ISO datetime
include_deleted?: boolean
limit?: integer
offset?: integer
```

Return `data.entries`, `data.total`, `data.limit`, and `data.offset`.

### `imem_get_entry`

```text
entry_id: string
```

Return `data.entry` or `ENTRY_NOT_FOUND`.

### `imem_update_entry`

Canonical input:

```text
entry_id: string
patch: object
request_id: string
expected_revision?: integer
```

Do not set `id`, `kind`, or `revision`. Nest Schedule changes under
`patch.schedule_details`. Canonical Skill callers must read `data.entry.revision`
first and pass it as `expected_revision`; the parameter is optional only for
legacy client compatibility. Return `data.entry` with its incremented revision.
A stale value returns `REVISION_CONFLICT` without applying the patch.

During migration, the tool also accepts this mutually exclusive legacy form:

```text
entity_type: memory | schedule | reminder
entity_id: string
patch: object
request_id: string
```

New integrations must use `entry_id`.

### `imem_delete_entry`

```text
entry_id: string
reason: string
request_id: string
```

Perform a soft delete/cancel and return `data.entry`.

### `imem_list_entry_occurrences`

```text
start: ISO datetime
end: ISO datetime
limit?: integer
```

Return `data.occurrences`. Each item uses canonical `entry_id` plus an
occurrence-specific `occurrence_id`.

### `imem_create_entry_reminder_rule`

```text
entry_id: string
request_id: string
idempotency_key: string
remind_at?: ISO datetime
offset_minutes?: integer
channel?: string
is_default?: boolean
status?: string
message?: string
title?: string
notification_endpoint_id?: string
```

Use only with a Schedule Entry and provide a valid timing rule. Return the
updated `data.entry`.

### `imem_update_entry_reminder_rule`

```text
entry_id: string
rule_id: string
patch: object
request_id: string
expected_revision?: integer
```

Canonical Skill callers must read the selected nested Reminder Rule's `revision`
and pass it as `expected_revision`; omission remains only for legacy client
compatibility. Return the updated `data.entry`, including the incremented rule
revision. A stale value returns `REVISION_CONFLICT` without applying the patch.

### `imem_delete_entry_reminder_rule`

```text
entry_id: string
rule_id: string
reason: string
request_id: string
```

Return the updated `data.entry`.

### `imem_upload_artifact`

```text
title: string
content: string
media_type: text/plain | text/markdown | text/html
request_id: string
idempotency_key: string
```

The Artifact is private and returns an owner URL. The tool cannot enable a
Public Link.

## Return Envelope

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
  "error": {"code": "VALIDATION_FAILED", "message": "..."},
  "source": "imem-remote-mcp"
}
```

Preserve `error.code`. Never present a failed write as successful.

## Idempotency And Recovery

`imem_create_entry`, `imem_create_entry_reminder_rule`, and
`imem_upload_artifact` require both `request_id` and `idempotency_key`. Reuse a
key only for an identical retry. Different arguments with the same key return
`IDEMPOTENCY_CONFLICT`.

After an uncertain update or delete, read current state before retrying. Ask
the user to choose when a list returns multiple plausible targets.

## Optimistic Concurrency

Before `imem_update_entry`, get the Entry and send its top-level `revision` as
`expected_revision`. Before `imem_update_entry_reminder_rule`, get the owning
Schedule Entry, select the rule, and send that rule's `revision`. The update
returns the resource with an incremented revision.

If either update returns `REVISION_CONFLICT`, do not retry automatically and do
not omit `expected_revision` to force a write. Re-read current state, explain
that another client changed the resource, and ask the user whether to retry the
intended patch against the latest revision or merge the competing changes.

## Migration Aliases

Production temporarily retains:

```text
imem_search
imem_create_memory
imem_create_schedule
imem_create_reminder
imem_cancel_entry
```

These aliases preserve older integrations. New Skill workflows must use the
canonical Entry tools. Do not remove aliases before a separately approved
deprecation and telemetry review.

## Error Handling

| Error code | Required behavior |
|---|---|
| `UNAUTHORIZED` | Check the configured API key. |
| `FORBIDDEN` | Report the missing scope. |
| `ENTRY_NOT_FOUND` | List again or ask the user to identify the Entry. |
| `VALIDATION_FAILED` | Correct clear fields or ask for missing information. |
| `INVALID_ENTRY_KIND` | Use `note` or `schedule`. |
| `IDEMPOTENCY_CONFLICT` | Do not retry with that key; confirm intent. |
| `REVISION_CONFLICT` | Re-read current state, explain the concurrent change, and ask whether to retry or merge. Never force overwrite. |
| `MCP_TOOL_ERROR` | Treat the outcome as failed or uncertain. |
