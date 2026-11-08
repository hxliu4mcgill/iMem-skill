# iMem Product Language

iMem is a Workspace Memory System for individuals and teams.

## Canonical Domain Language

Use `Entry` as the technical identity for every independently manageable item:

```text
Entry(kind=note)     durable note, fact, decision, preference, or context
Entry(kind=schedule) time-based content with schedule_details
ScheduleDetails      one-to-one details nested under a Schedule Entry
ReminderRule         zero-to-many policies nested under a Schedule Entry
Artifact             private generated deliverable, separate from Entry
```

Use `schedule_details` and `reminder_rules` as the canonical wire-field names
when documenting or debugging the MCP contract.

Use one stable `entry_id` for create, list, detail, update, delete, occurrence,
and reminder-rule workflows. Do not ask an Agent to correlate `memory_id` with
`schedule_id`. An occurrence uses `entry_id` plus its own `occurrence_id`.

## User-Facing Language

Use natural words that match the user's intent:

```text
note or memory          for a durable note Entry
schedule or event       for a Schedule Entry
reminder                for a Reminder Rule attached to a Schedule Entry
workspace               instead of assuming family
workspace member        instead of assuming family member
iMem                    instead of family schedule assistant
```

The user does not need to know the internal `Entry` term unless it helps
explain IDs, API behavior, or a mixed note-and-schedule list.

## Default Assumptions

Do not assume:

```text
every workspace is a family
every note has a date
every note needs schedule details or a reminder rule
a reminder is an independently manageable top-level Entry
the Agent must maintain legacy Memory, Schedule, or Reminder IDs
```

A family remains a valid workspace scenario, but it is not the default product
definition. Include personal, project, and team examples as well as occasional
explicit family examples.

## Compatibility Language

Describe `imem_create_memory`, `imem_create_schedule`, `imem_create_reminder`,
`imem_search`, `imem_cancel_entry`, and typed update parameters as migration
aliases. Do not present them as the preferred workflow for new integrations.
