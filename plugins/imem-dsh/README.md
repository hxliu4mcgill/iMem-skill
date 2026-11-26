# iMem for DeepSeek Harness

This bundle installs the canonical iMem Agent Skill and connects DeepSeek
Harness to the authenticated remote MCP service at `https://imem.xin/mcp`.

## Requirements

- DeepSeek Harness `>=0.2.1-rc.1 <0.3.0`
- An iMem account
- Network access to `https://imem.xin/mcp`

The package contains a small OAuth connector plus the canonical Skill files. It
does not ship credentials or run an install script.

## Install

### DeepSeek Harness Desktop

1. Open **Plugins** and choose **Add plugin**.
2. Enter `dsh-plugin-imem` and choose **Install**.
3. Open the installed iMem plugin and choose **Connect iMem**.
4. Approve access in the browser, return to DeepSeek Harness, and start a new
   session.

The package name works in the Desktop installer after the package has been
published to npm. During local development, the same dialog also accepts the
absolute path to this `plugins/imem-dsh` directory.

### CLI / Web profile

```bash
dsh plugin --profile web add dsh-plugin-imem
dsh web
```

Open **Plugins**, select iMem, and choose **Connect iMem**. DeepSeek Harness
performs OAuth Authorization Code with PKCE in the browser, stores the grant in
its credential provider, and refreshes it when required. No API Key or
environment variable is required.

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

In Desktop, manage the installed package from the **Plugins** page. For the Web
profile, use:

```bash
dsh plugin --profile web update dsh-plugin-imem
dsh plugin --profile web remove dsh-plugin-imem
```

Sign out from the iMem account section before uninstalling if you also want DSH
to delete its saved OAuth grant.

## Source and support

- Source: <https://github.com/hxliu4mcgill/iMem-skill/tree/main/plugins/imem-dsh>
- Issues: <https://github.com/hxliu4mcgill/iMem-skill/issues>
- iMem documentation: <https://docs.imem.xin/>

This package is an independent, unofficial integration and is not affiliated
with or endorsed by DeepSeek AI.
