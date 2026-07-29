# iMem Product Language

iMem is a Workspace Memory System for individuals and teams.

`Memory` is the foundational capability. `Schedule` and `Reminder` remain
separate API resources, but together form the Schedule and Reminder
application module.

## Preferred Language

```text
workspace                 instead of assuming family
workspace member / member instead of assuming family member
memory / workspace memory instead of family memory
iMem / Workspace Memory System instead of family schedule assistant
Schedule and Reminder module instead of separate schedule/reminder products
```

A family is a valid workspace scenario, but it is not the default product
definition.

Agent examples should include personal, project, and team contexts as well as
occasional explicit family contexts.

## Default Assumptions

Do not assume:

```text
every workspace is a family
every memory has a date
every memory needs a schedule or reminder
Schedule and Reminder are unrelated product modules
```

This language contract does not change current schemas or APIs. `memory_id`
remains optional when creating a Schedule. The Agent-facing
`imem_create_reminder` tool requires `schedule_id` because it is reserved for
adding another Reminder to an existing Schedule.
