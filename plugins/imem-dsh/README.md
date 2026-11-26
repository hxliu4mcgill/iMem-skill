# iMem for DeepSeek Harness

This bundle installs the canonical iMem Agent Skill and connects DeepSeek
Harness to the authenticated remote MCP service at `https://imem.xin/mcp`.

## Requirements

- DeepSeek Harness `>=0.2.1-rc.1 <0.3.0`
- An iMem account
- Network access to `https://imem.xin/mcp`

The package contains an adaptive connector plus the canonical Skill files. It
selects the best authentication mode supported by the installed DSH runtime:

- DSH `>=0.2.3-alpha.1`: OAuth account connection with no API Key.
- DSH `0.2.1` and `0.2.2`: Personal API Key fallback through the DSH
  credential named `IMEM_API_KEY`.

The package does not ship credentials or run an install script.

## Install

### DeepSeek Harness Desktop

1. Open **Plugins** and choose **Add plugin**.
2. Enter `dsh-plugin-imem` and choose **Install**.
3. Fully quit and reopen DeepSeek Harness. A newly installed or updated Bundle
   joins the Desktop Profile only on its next start.
4. Make sure the installed iMem plugin is enabled.
5. Complete the authentication path shown by your DSH version:
   - If the plugin has an account section, choose **Connect iMem** and approve
     access in the browser.
   - If no account section is shown, configure the `IMEM_API_KEY` credential
     as described below.
6. Fully restart DSH after adding a credential, then start a new session.

The package name works in the Desktop installer after the package has been
published to npm. During local development, the same dialog also accepts the
absolute path to this `plugins/imem-dsh` directory.

### Personal API Key fallback

On DSH without the account section, create a Personal API Key at
<https://imem.xin/app/api-keys> and add it to `~/.dsh/.credentials.yaml`:

```yaml
version: 1
refs:
  IMEM_API_KEY: your-personal-api-key
records: {}
```

If that file already exists, preserve its other `refs` and `records`; only
add `IMEM_API_KEY` under `refs`.

Alternatively, add `IMEM_API_KEY=your-personal-api-key` to `~/.dsh/.env`,
then fully quit and reopen DSH.

### CLI / Web profile

```bash
dsh plugin --profile web add dsh-plugin-imem
dsh web
```

Open **Plugins** and select iMem. When an account section is available, choose
**Connect iMem**; DSH performs OAuth Authorization Code with PKCE, stores the
grant, and refreshes it when required. When no account section is available,
configure `IMEM_API_KEY` before starting `dsh web`. The connector selects the
matching mode automatically.

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

In Desktop, manage the installed package from the **Plugins** page, then fully
quit and reopen DeepSeek Harness after an update. For the Web profile, use:

```bash
dsh plugin --profile web update dsh-plugin-imem
dsh plugin --profile web remove dsh-plugin-imem
```

Restart the Web profile after updating the Bundle.

In OAuth mode, sign out from the iMem account section before uninstalling if
you also want DSH to delete its saved grant. In API Key mode, remove
`IMEM_API_KEY` from the DSH credential store separately when it is no longer
needed.

## Source and support

- Source: <https://github.com/hxliu4mcgill/iMem-skill/tree/main/plugins/imem-dsh>
- Issues: <https://github.com/hxliu4mcgill/iMem-skill/issues>
- iMem documentation: <https://docs.imem.xin/>

This package is an independent, unofficial integration and is not affiliated
with or endorsed by DeepSeek AI.
