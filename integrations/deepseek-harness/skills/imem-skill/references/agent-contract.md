# iMem Agent Contract

Use this contract with the authenticated production MCP at
`https://imem.xin/mcp`. Read `mcp-tool-spec.md` for exact parameters and
`product-language.md` for terminology.

## Domain Contract

Every independently manageable note or schedule is one Entry with one stable
`entry_id`:

```text
Entry(kind=note)     -> schedule_details=null, reminder_rules=[]
Entry(kind=schedule) -> schedule_details object, reminder_rules array
```

ScheduleDetails belong one-to-one to a Schedule Entry. Reminder Rules belong
zero-to-many to a Schedule Entry and are not top-level Entries. Occurrences use
`entry_id` and `occurrence_id`; they do not require legacy Memory or Schedule
IDs. Artifact remains a separate private deliverable resource.

## Authentication And Workspace

Use Personal API Key bearer authentication over Streamable HTTP. Let the
service derive `user_id`, `workspace_id`, client identity, and scopes from the
key. Never pass `workspace_id` in normal Agent calls. OAuth remains pending.

Do not use service internals during normal work:

```text
data/
*.db
*.jsonl
scripts/*.py
memory_service.operations
```

## Required Behavior

1. Run `imem_health` before user-visible work when practical.
2. Call `imem_get_time_context` before resolving relative dates and use a fresh
   `server_time` and `workspace_timezone` for each operation.
3. Include `request_id` on mutations.
4. Include `idempotency_key` on Entry, Reminder Rule, and Artifact creates.
5. List Entries to select a target when `entry_id` is unknown. Before every
   Entry update, read that Entry and capture its top-level `revision`, even if
   the ID is already confirmed.
6. Before every Reminder Rule update, read the owning Schedule Entry and
   capture the selected rule's `revision`.
7. Send the captured revision as `expected_revision` on canonical update calls.
8. Ask the user to choose when multiple plausible Entries match.
9. Never guess `entry_id`, `rule_id`, or a revision.
10. Keep Entry `kind` immutable and nest Schedule changes under
    `schedule_details`.
11. Preserve service error codes and never report a failed write as successful.

## Intent Routing

```text
fact, note, reference, decision, preference, or context
-> imem_create_entry(kind=note)

explicit time arrangement
-> imem_create_entry(kind=schedule, schedule_details=...)

new timed reminder
-> imem_create_entry(kind=schedule, reminder_rules=[...])

additional reminder for an existing Schedule Entry
-> imem_create_entry_reminder_rule(entry_id=...)

generated text, Markdown, or HTML deliverable
-> imem_upload_artifact
```

Do not route solely from extracted dates. Descriptive or historical dates stay
in a note unless the user asks for time-based behavior.

## Scope Matrix

| Capability | MCP tool | Scope |
|---|---|---|
| Health | `imem_health` | `entries:read` |
| Time baseline | `imem_get_time_context` | `entries:read` |
| Create Entry | `imem_create_entry` | `entries:write` |
| List Entries | `imem_list_entries` | `entries:read` |
| Get Entry | `imem_get_entry` | `entries:read` |
| Update Entry | `imem_update_entry` | `entries:write` |
| Delete/cancel Entry | `imem_delete_entry` | `entries:write` |
| List occurrences | `imem_list_entry_occurrences` | `entries:read` |
| Create Reminder Rule | `imem_create_entry_reminder_rule` | `entries:write` |
| Update Reminder Rule | `imem_update_entry_reminder_rule` | `entries:write` |
| Delete Reminder Rule | `imem_delete_entry_reminder_rule` | `entries:write` |
| Upload private Artifact | `imem_upload_artifact` | `entries:write` |

Exports, operation logs, API-key administration, scheduler scans, and delivery
operations remain outside the public MCP surface.

## Idempotency

Use idempotency for:

```text
imem_create_entry
imem_create_entry_reminder_rule
imem_upload_artifact
```

Reuse the same key only to retry the identical intended create. A different
body with the same key returns `IDEMPOTENCY_CONFLICT`. After an uncertain
update or delete, read current state before retrying.

## Update And Delete

Use `imem_update_entry(entry_id=..., expected_revision=...)` with common
fields at the top level and Schedule fields inside `patch.schedule_details`.
Never patch `id`, `kind`, or `revision`. Read the latest Entry immediately
before the update and copy its top-level `revision` into `expected_revision`.

Use `imem_delete_entry` for soft deletion. A note becomes deleted. A Schedule
Entry becomes canceled/deleted together with its active Reminder Rules
according to service policy. Do not physically delete storage rows or files.

Manage Reminder Rules through the nested create, update, and delete tools. A
Reminder Rule mutation requires both the owning Schedule `entry_id` and the
rule's `rule_id` where applicable. Before `imem_update_entry_reminder_rule`,
read the Schedule Entry, select the nested rule, and send that rule's `revision`
as `expected_revision`.

The service keeps `expected_revision` optional for older clients, but canonical
Skill update paths must always send it. On `REVISION_CONFLICT`, re-read the
Entry and explain that another client changed it. Never silently retry without
user review, omit `expected_revision`, or force an overwrite. Retry with the
new revision only after the user chooses to apply or merge the intended change.

## Artifact Upload

Use `imem_upload_artifact` for complete text, Markdown, or HTML deliverables.
Every upload starts private. Do not claim it is public or try to enable a
Public Link; only the user can do that in the authenticated iMem App.

## Compatibility

The following tools remain temporary migration aliases:

```text
imem_search
imem_create_memory
imem_create_schedule
imem_create_reminder
imem_cancel_entry
```

`imem_update_entry` also accepts the legacy `entity_type + entity_id` form.
New Agent workflows must use canonical tools and `entry_id` only. Do not remove
or recommend legacy aliases until a separate deprecation contract authorizes
it.

## Failure Handling

| Error code | Required Agent behavior |
|---|---|
| `UNAUTHORIZED` | Ask the user/operator to check API key configuration. |
| `FORBIDDEN` | Report the missing scope. |
| `ENTRY_NOT_FOUND` | List again or ask the user to identify the target. |
| `VALIDATION_FAILED` | Fix clear fields or ask for missing information. |
| `INVALID_ENTRY_KIND` | Use `note` or `schedule`. |
| `IDEMPOTENCY_CONFLICT` | Do not retry the same key; confirm intent. |
| `REVISION_CONFLICT` | Re-read current state, explain the concurrent change, and ask whether to retry or merge. Never force overwrite. |
| `CONFIGURATION_ERROR` | Check the MCP URL and host configuration. |
| `MCP_TOOL_ERROR` | Treat the outcome as failed or uncertain. |
