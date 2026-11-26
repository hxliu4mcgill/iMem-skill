# iMem for DeepSeek Harness

This bundle installs the canonical iMem Agent Skill and connects DeepSeek
Harness to the authenticated remote MCP service at `https://imem.xin/mcp`.

## Requirements

- DeepSeek Harness `>=0.2.1-rc.1 <0.3.0`
- An iMem account and a dedicated Personal API Key
- Network access to `https://imem.xin/mcp`

The package contains configuration and Skill files only. It does not ship an
iMem API Key or run an install script.

## Install

Create a Personal API Key at <https://imem.xin/app/api-keys>. Make it available
to the process that starts DeepSeek Harness as `IMEM_API_KEY`, then install the
bundle into the profile you use:

```powershell
$env:IMEM_API_KEY = "your-api-key"
dsh plugin --profile web add dsh-plugin-imem
dsh web
```

On macOS or Linux:

```bash
export IMEM_API_KEY="your-api-key"
dsh plugin --profile web add dsh-plugin-imem
dsh web
```

The secret is resolved through the DeepSeek Harness credential provider. It is
not stored in this package or expanded into the raw plugin configuration.

## What the bundle adds

- The canonical `imem-skill` instructions and references
- One authenticated Streamable HTTP MCP server named `imem`
- Durable memory, Artifact, schedule, and reminder workflows backed by iMem

## Verify

Start a new Session and ask it to use the `imem-skill`. The MCP tools should be
available under names beginning with `mcp__imem__`.

Do not install a second MCP entry named `imem`; DeepSeek Harness rejects
duplicate server names in the same scope.

## Upgrade and uninstall

```bash
dsh plugin --profile web update dsh-plugin-imem
dsh plugin --profile web remove dsh-plugin-imem
```

Revoke the integration's API Key in the iMem Web App after uninstalling if the
key is no longer needed.

## Source and support

- Source: <https://github.com/hxliu4mcgill/iMem-skill/tree/main/plugins/imem-dsh>
- Issues: <https://github.com/hxliu4mcgill/iMem-skill/issues>
- iMem documentation: <https://docs.imem.xin/>

This package is an independent, unofficial integration and is not affiliated
with or endorsed by DeepSeek AI.
