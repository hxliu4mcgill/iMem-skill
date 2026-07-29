<div align="center">

[English](README.md) | [简体中文](README.zh-CN.md)

# 🧠 iMem Skill

### Your memory, beyond any one AI.

[![Status](https://img.shields.io/badge/status-experimental-f59e0b?style=flat-square)](#project-status)
[![Codex](https://img.shields.io/badge/Codex-supported-111827?style=flat-square)](#agent-platform-support)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-d97757?style=flat-square)](#agent-platform-support)
[![WorkBuddy](https://img.shields.io/badge/WorkBuddy-plugin-2563eb?style=flat-square)](#agent-platform-support)
[![Hermes](https://img.shields.io/badge/Hermes-skill-9333ea?style=flat-square)](#agent-platform-support)
[![MCP](https://img.shields.io/badge/MCP-remote-7c3aed?style=flat-square)](#how-it-works)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](LICENSE)

A long-term memory space for you and the AI Agents you trust.
Capture once. Remember everywhere. Let authorized AI understand your world.

iMem keeps memories, schedules, and reminders useful beyond a single
conversation or AI, while you control which integrations can access them.

**Web App:** [https://imem.xin](https://imem.xin)

**Remote MCP:** `https://imem.xin/mcp`

[Why iMem?](#why-imem) · [Features](#features) · [Quick Start](#quick-start) ·
[Examples](#try-it) · [Compatibility](#compatibility) ·
[Security](#security)

</div>

> [!IMPORTANT]
> `iMem-skill` is an independent, unofficial, and experimental project. It is
> not affiliated with or endorsed by OpenAI, Codex, Anthropic, Claude Code,
> WorkBuddy, CodeBuddy, Nous Research, or Hermes Agent. It is distributed from
> this repository through custom Marketplaces and direct Skill installation,
> not through a vendor-curated public directory.

## Why iMem?

Changing AI should not mean losing your context.

iMem keeps memories and schedules in a long-term workspace so different
authorized Agents can continue from the same context. Your memory remains
independent of any single AI product, and each integration can use its own
revocable Personal API Key.

`iMem-skill` is the Agent-facing connection to that experience. It tells an
Agent when and how to save, find, and update context, while the remote MCP
service provides the live tools. The Skill itself does not store your data.

The product follows a simple **Capture → Connect → Recall** loop: save what
matters, keep related context connected, and bring it back when needed.

## Features

| Capability | What your Agent can do |
|---|---|
| 🧠 Long-term memory | Save decisions, facts, preferences, and project context in a persistent workspace |
| 🔗 One memory across Agents | Let different authorized Agents continue from the same long-term context |
| 🔎 Recall what matters | Search memories, schedules, and reminders when you or an Agent needs them |
| 📅 Memory + Schedule | Keep what happened connected to when it matters |
| ⏰ Reminders | Create, update, and cancel time-based arrangements and reminder policies |
| 🔐 Controlled access | Use a separate revocable Personal API Key for each integration |
| 🔌 Remote MCP | Connect directly without running Python or a local MCP process |

## How it works

```text
You
 └─ Agent
     ├─ iMem Skill: behavior and workflow
     └─ https://imem.xin/mcp: authenticated tools
         └─ your iMem workspace
```

The Skill tells the Agent when and how to use iMem. The remote MCP server
provides the live tools and stores data in the workspace selected by the API
key. The Skill itself does not store user data.

## Quick Start

### 1. Create an iMem API Key

1. [Create an account](https://imem.xin/app/register), verify your email, and
   sign in.
2. Open [API Keys](https://imem.xin/app/api-keys) and create a new key.
3. Choose read/write access if the Agent should save or update information.
4. Copy the key immediately and store it securely; the full value is shown
   only once.

Use a separate key for each Agent or integration. Revoke a key from the same
page when it is no longer needed.

### 2A. Install the Claude Code Plugin

Run these commands inside Claude Code:

```text
/plugin marketplace add hxliu4mcgill/iMem-skill
/plugin install imem@imem-plugins
```

Or use the terminal equivalents:

```bash
claude plugin marketplace add hxliu4mcgill/iMem-skill
claude plugin install imem@imem-plugins
```

Claude Code asks for the iMem API Key during installation. The value is marked
as sensitive and is injected only into the remote MCP authorization header; no
environment variable is required. Run `/reload-plugins` or start a new session
after installation.

> [!CAUTION]
> Never commit the API key, place it in prompts, or include it in screenshots.

### 2B. Install the Codex Plugin

First, make the Personal API Key available as `IMEM_API_KEY`.

The Plugin reads the Personal API Key from `IMEM_API_KEY`.

PowerShell example for a persistent per-user environment variable:

```powershell
[Environment]::SetEnvironmentVariable("IMEM_API_KEY", "your-api-key", "User")
```

macOS/Linux shell example:

```bash
export IMEM_API_KEY="your-api-key"
```

Restart Codex after configuring the server. Desktop applications must be
started from an environment that can read `IMEM_API_KEY`.

> [!CAUTION]
> Never commit the API key, place it in prompts, or include it in screenshots.
> The Plugin's `bearer_token_env_var` contains the variable name, not the key
> value.

Then install the Plugin:

```bash
codex plugin marketplace add hxliu4mcgill/iMem-skill
codex plugin add imem@imem-plugins
```

Or restart the Codex app after adding the Marketplace, open the Plugin
Directory, select **iMem Plugins**, and install **iMem**.

The Plugin installs the iMem Skill and registers the remote MCP connection
together. Start a new task after installation.

### 2C. Install the WorkBuddy / CodeBuddy Plugin

Run these commands in WorkBuddy or CodeBuddy:

```text
/plugin marketplace add hxliu4mcgill/iMem-skill
/plugin install imem@imem-plugins
/reload-plugins
```

CodeBuddy CLI users can run the terminal equivalents:

```bash
codebuddy plugin marketplace add hxliu4mcgill/iMem-skill
codebuddy plugin install imem@imem-plugins
```

The installer asks for the iMem API Key as sensitive user configuration. The
same package installs the Skill and remote MCP connection together. The
repository publishes both `.workbuddy-plugin/marketplace.json` and
`.codebuddy-plugin/marketplace.json` discovery entries, while reusing the
Claude-compatible Plugin manifest instead of maintaining a duplicate package.

### 2D. Install in Hermes Agent

Install the standard Agent Skill directly from this repository:

```bash
hermes skills install https://raw.githubusercontent.com/hxliu4mcgill/iMem-skill/main/skills/imem-skill/SKILL.md
```

Then add the remote MCP server:

```bash
hermes mcp add imem --url https://imem.xin/mcp
```

When Hermes asks whether authentication is required, choose yes and enter the
iMem API Key at the masked prompt. Hermes stores the secret in its local
environment and configures the bearer authorization header. Verify both parts:

```bash
hermes skills list
hermes mcp test imem
```

This adds iMem as an Agent Skill and remote MCP integration. It does not replace
Hermes' built-in memory provider.

### Direct MCP alternative

If you only want the tools and do not want the bundled Skill, connect the MCP
server directly:

```bash
codex mcp add imem --url https://imem.xin/mcp --bearer-token-env-var IMEM_API_KEY
```

Do not combine Direct MCP with the Plugin; both register a server named
`imem`.

## Try it

```text
Use $imem-skill to remember that the API migration was approved today.

Use $imem-skill to find the decisions we saved about the API migration.

Use $imem-skill to schedule the design review for Friday at 10:00 and remind
me one day before.
```

In Claude Code, the explicit namespaced form is `/imem:imem-skill`.

## Requirements

For the recommended remote setup:

- An iMem account and Personal API Key
- An Agent host with Streamable HTTP MCP and local Skill support
- Network access to `https://imem.xin/mcp`

No local Python process or stdio MCP adapter is required.

## Agent platform support

| Platform | Status |
|---|---|
| Codex | GitHub Marketplace Plugin supported |
| Claude Code | GitHub Marketplace Plugin packaged; live install validation pending |
| WorkBuddy / CodeBuddy | Compatible GitHub Marketplace Plugin packaged; live install validation pending |
| Hermes Agent | Direct Skill and remote MCP installation documented; live install validation pending |
| Other Streamable HTTP MCP hosts | Protocol-compatible; not yet validated |
| OpenCode, Cursor | Planned validation |

A planned or protocol-compatible platform is not an installable promise.

## Compatibility

```text
Skill release: v0.1.0
Skill name: imem-skill
Production MCP: https://imem.xin/mcp
Authentication: Personal API Key bearer token
OAuth: pending
```

The service must expose the behavior described in the
[MCP tool specification](skills/imem-skill/references/mcp-tool-spec.md).
The versioned machine-readable surface is
[`contracts/remote-mcp.json`](contracts/remote-mcp.json).

## Safety and data boundaries

Normal operations follow:

```text
Agent -> remote MCP -> deployed iMem service
```

The Skill must not directly read or write SQLite, JSONL user data, server data
directories, or service implementation modules.

## Validation

These checks require no secrets:

The canonical editable Skill is `skills/imem-skill/`. After changing it, run
`python tools/sync_plugin_skill.py` to refresh the packaged Plugin copy.

```bash
python test/check_publication_layout.py
python test/check_standalone_repository.py
python test/check_package_boundary.py
python test/check_remote_mcp_contract.py
python test/check_plugin_package.py
```

## Upgrade

Codex:

```bash
codex plugin marketplace upgrade imem-plugins
```

Claude Code:

```text
/plugin marketplace update imem-plugins
/reload-plugins
```

WorkBuddy / CodeBuddy:

```text
/plugin marketplace update imem-plugins
/reload-plugins
```

Hermes:

```bash
hermes skills check
hermes skills update
hermes mcp test imem
```

Start a new task or session after upgrading.

## Uninstall

```bash
codex plugin remove imem@imem-plugins
codex plugin marketplace remove imem-plugins
```

For Claude Code:

```text
/plugin uninstall imem@imem-plugins
/plugin marketplace remove imem-plugins
```

For WorkBuddy / CodeBuddy:

```text
/plugin uninstall imem@imem-plugins
/plugin marketplace remove imem-plugins
```

For Hermes:

```bash
hermes skills uninstall imem-skill
hermes mcp remove imem
```

Removing the Marketplace is optional if you want to reinstall later. Revoke
the integration's API Key in the Web App when it is no longer needed.

## Project status

- The project is experimental.
- The repository does not deploy the iMem service or issue API keys.
- OAuth is pending; current authentication uses user-created Personal API Keys.
- Reminder delivery channels depend on the deployed service.
- Codex is the currently live-validated Agent path.
- The Claude Code package and static contract are implemented; live install
  validation is pending on a machine with Claude Code.
- WorkBuddy / CodeBuddy Marketplace entries and the Hermes installation path
  are implemented; live installation validation is pending.

## Security

Report security issues according to the [Security Policy](SECURITY.md). Never
include API Keys, access tokens, or private user data in public issues.

## License

Released under the [MIT License](LICENSE).

<div align="center">

Built for Agents that should remember what matters.

</div>
