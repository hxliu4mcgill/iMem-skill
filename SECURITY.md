# Security Policy

## Supported versions

iMem Skill is experimental. Security fixes are applied to the latest release
and the default branch. Older revisions may not receive fixes.

## Reporting a vulnerability

Please do not publish vulnerability details, Personal API Keys, access tokens,
private memories, schedules, reminders, or other user data in a public issue.

Use GitHub's private vulnerability reporting for this repository when it is
available. If that option is not available, open a public issue containing only
a request for a private reporting channel. Do not include exploit details or
sensitive data in that issue.

Include the following non-sensitive information when possible:

- affected Skill or Plugin version;
- whether the issue affects this repository, `https://imem.xin/mcp`, or both;
- the Agent host and operating system;
- minimal reproduction steps with all credentials and personal data removed;
- expected and observed behavior.

The project is experimental and does not currently promise a fixed response
time. Reports will be reviewed and handled according to their severity.

## Compromised API Keys

If a Personal API Key may have been exposed:

1. Revoke it immediately in the iMem Web App.
2. Create a replacement key only if the integration is still needed.
3. Update the Agent host's secret or environment configuration.
4. Do not send the exposed key in a report, screenshot, prompt, or log.

## Security boundaries

This repository distributes Agent instructions and remote MCP connection
metadata. It does not contain the iMem production service, user databases, or
issued API Keys.

Normal usage sends authenticated requests to `https://imem.xin/mcp`. Users are
responsible for protecting their Personal API Keys and for reviewing the
permissions granted to each integration.

## 安全报告（中文）

iMem Skill 仍处于实验阶段，当前仅支持最新发布版本和默认分支。

请勿在公开 Issue 中发布漏洞细节、Personal API Key、访问令牌、私人记忆、日程、
提醒或其他用户数据。优先使用 GitHub 的私密漏洞报告功能；如果该功能不可用，
可以创建一个不包含漏洞细节和敏感数据的公开 Issue，仅请求私密联系方式。

如果 API Key 可能已经泄露，请立即在 iMem Web App 中撤销该 Key，并在确有需要时
重新创建和更新 Agent 端配置。不要在报告、截图、提示词或日志中发送已经泄露的
完整 Key。
