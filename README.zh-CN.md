<div align="center">

[English](README.md) | [简体中文](README.zh-CN.md)

# 🧠 iMem Skill

### 你的记忆，不属于任何单一 AI。

[![Status](https://img.shields.io/badge/status-experimental-f59e0b?style=flat-square)](#项目状态)
[![Codex](https://img.shields.io/badge/Codex-supported-111827?style=flat-square)](#agent-平台支持)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-d97757?style=flat-square)](#agent-平台支持)
[![WorkBuddy](https://img.shields.io/badge/WorkBuddy-plugin-2563eb?style=flat-square)](#agent-平台支持)
[![Hermes](https://img.shields.io/badge/Hermes-skill-9333ea?style=flat-square)](#agent-平台支持)
[![MCP](https://img.shields.io/badge/MCP-remote-7c3aed?style=flat-square)](#工作原理)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](LICENSE)

一个独立于任何单一 AI 的长期记忆空间。记录一次，持续存在，让不同的授权 AI
理解你的世界。

iMem 让记忆、日程和提醒跨越单次对话或单一 AI 持续发挥作用，同时由你决定哪些
集成可以访问它们。

**Web App：** [https://imem.xin](https://imem.xin)

**远程 MCP：** `https://imem.xin/mcp`

[为什么选择 iMem？](#为什么选择-imem) · [功能](#功能) ·
[快速开始](#快速开始) · [使用示例](#使用示例) ·
[兼容性](#兼容性) · [安全](#安全)

</div>

> [!IMPORTANT]
> `iMem-skill` 是一个独立、非官方且处于实验阶段的项目，与 OpenAI、Codex、
> Anthropic、Claude Code、WorkBuddy、CodeBuddy、Nous Research 或 Hermes Agent
> 均不存在隶属、认可或官方合作关系。它通过本仓库提供的自定义 Marketplace 和
> Skill 直装方式分发，并未进入厂商精选公共目录。

## 为什么选择 iMem？

更换 AI，不应该意味着失去你的上下文。

iMem 将记忆和日程保存在长期工作区中，让不同的授权 Agent 都能基于同一份上下文
继续工作。你的记忆不绑定于任何单一 AI 产品，每个集成都可以使用独立、可撤销的
Personal API Key。

`iMem-skill` 是 Agent 接入这一体验的连接层。它告诉 Agent 何时以及如何保存、
查找和更新上下文，远程 MCP 服务则提供实时工具；Skill 本身并不存储你的数据。

产品遵循清晰的 **记录（Capture）→ 连接（Connect）→ 找回（Recall）** 循环：
保存重要信息、连接相关上下文，并在需要时重新找回。

## 功能

| 能力 | Agent 可以做什么 |
|---|---|
| 🧠 长期记忆 | 在长期工作区中保存决策、事实、偏好和项目上下文 |
| 🔗 一份记忆，连接多个 Agent | 让不同的授权 Agent 基于同一份长期上下文继续工作 |
| 🔎 找回重要信息 | 在你或 Agent 需要时搜索记忆、日程和提醒 |
| 📅 记忆 + 日程 | 让“发生了什么”与“何时重要”保持关联 |
| ⏰ 提醒 | 创建、更新和取消时间安排与提醒策略 |
| 🔐 可控访问 | 为每个集成使用独立、可撤销的 Personal API Key |
| 🔌 远程 MCP | 无需在用户电脑运行 Python 或本地 MCP 进程 |

## 工作原理

```text
你
 └─ Agent
     ├─ iMem Skill：行为与工作流
     └─ https://imem.xin/mcp：需要认证的工具
         └─ 你的 iMem 工作区
```

Skill 告诉 Agent 何时以及如何使用 iMem；远程 MCP 提供实时工具，并根据 API Key
确定数据所属工作区。Skill 本身不存储用户数据。

## 快速开始

### 1. 创建 iMem API Key

1. [注册账号](https://imem.xin/app/register)，完成邮箱验证并登录。
2. 打开 [API Keys](https://imem.xin/app/api-keys)，创建一把新 Key。
3. 如果希望 Agent 保存或更新信息，选择读写权限。
4. 创建后立即复制并安全保存；完整 Key 只显示一次。

建议为每个 Agent 或集成创建独立 Key，不再使用时可在同一页面撤销。

### 2A. 安装 Claude Code Plugin

在 Claude Code 中执行：

```text
/plugin marketplace add hxliu4mcgill/iMem-skill
/plugin install imem@imem-plugins
```

也可以使用终端命令：

```bash
claude plugin marketplace add hxliu4mcgill/iMem-skill
claude plugin install imem@imem-plugins
```

安装时 Claude Code 会提示填写 iMem API Key。该值被标记为敏感配置，只会注入远程
MCP 的认证请求头，不需要设置环境变量。安装后执行 `/reload-plugins`，或新建会话。

> [!CAUTION]
> 不要把 API Key 提交到仓库、写进提示词或放进截图。

### 2B. 安装 Codex Plugin

首先把 Personal API Key 配置为 `IMEM_API_KEY`。

Plugin 从 `IMEM_API_KEY` 环境变量读取 Personal API Key。

PowerShell 持久化当前用户环境变量：

```powershell
[Environment]::SetEnvironmentVariable("IMEM_API_KEY", "你的-api-key", "User")
```

macOS/Linux Shell：

```bash
export IMEM_API_KEY="你的-api-key"
```

配置后重启 Codex。桌面应用需要从能够读取 `IMEM_API_KEY` 的环境中启动。

> [!CAUTION]
> 不要把 API Key 提交到仓库、写进提示词或放进截图。
> Plugin 中的 `bearer_token_env_var` 填的是环境变量名称，不是 Key 本身。

然后安装 Plugin：

```bash
codex plugin marketplace add hxliu4mcgill/iMem-skill
codex plugin add imem@imem-plugins
```

添加 Marketplace 后，也可以重启 Codex App，打开 Plugin Directory，选择
**iMem Plugins**，然后安装 **iMem**。

Plugin 会同时安装 iMem Skill 并注册远程 MCP 连接。安装后新建一个任务。

### 2C. 安装 WorkBuddy / CodeBuddy Plugin

在 WorkBuddy 或 CodeBuddy 中执行：

```text
/plugin marketplace add hxliu4mcgill/iMem-skill
/plugin install imem@imem-plugins
/reload-plugins
```

CodeBuddy CLI 用户也可以在终端执行：

```bash
codebuddy plugin marketplace add hxliu4mcgill/iMem-skill
codebuddy plugin install imem@imem-plugins
```

安装器会把 iMem API Key 作为敏感用户配置收集，并同时安装 Skill 与远程 MCP
连接。仓库同时提供 `.workbuddy-plugin/marketplace.json` 和
`.codebuddy-plugin/marketplace.json` 两个发现入口，但复用 Claude 兼容的 Plugin
清单，不维护第三份重复安装包。

### 2D. 安装到 Hermes Agent

直接从本仓库安装标准 Agent Skill：

```bash
hermes skills install https://raw.githubusercontent.com/hxliu4mcgill/iMem-skill/main/skills/imem-skill/SKILL.md
```

然后添加远程 MCP Server：

```bash
hermes mcp add imem --url https://imem.xin/mcp
```

Hermes 询问是否需要认证时选择 yes，并在遮罩输入框中填写 iMem API Key。Hermes
会把密钥保存到本地环境，并配置 Bearer 认证请求头。最后验证两部分：

```bash
hermes skills list
hermes mcp test imem
```

这会把 iMem 添加为 Agent Skill 和远程 MCP 集成，不会取代 Hermes 内置的 Memory
Provider。

### 仅连接 MCP

如果只需要工具、不需要 Plugin 附带的 Skill，可以直接连接 MCP：

```bash
codex mcp add imem --url https://imem.xin/mcp --bearer-token-env-var IMEM_API_KEY
```

不要同时使用 Direct MCP 和 Plugin；两者都会注册名为 `imem` 的 MCP Server。

## 使用示例

```text
使用 $imem-skill 记住 API 迁移已于今天获得批准。

使用 $imem-skill 查找我们保存的有关 API 迁移的决策。

使用 $imem-skill 将设计评审安排在周五 10:00，并提前一天提醒我。
```

在 Claude Code 中，显式调用形式是 `/imem:imem-skill`。

## 环境要求

推荐的远程模式只需要：

- iMem 账号与 Personal API Key
- 支持 Streamable HTTP MCP 和本地 Skill 的 Agent 宿主
- 可以访问 `https://imem.xin/mcp`

不需要运行本地 Python 进程或 stdio MCP 适配器。

## Agent 平台支持

| 平台 | 状态 |
|---|---|
| Codex | 已支持 GitHub Marketplace Plugin |
| Claude Code | 已完成 GitHub Marketplace Plugin 打包；待实机安装验证 |
| WorkBuddy / CodeBuddy | 已完成兼容的 GitHub Marketplace Plugin 打包；待实机安装验证 |
| Hermes Agent | 已提供 Skill 直装与远程 MCP 安装说明；待实机安装验证 |
| 其他 Streamable HTTP MCP 宿主 | 协议兼容，尚未验证 |
| OpenCode、Cursor | 计划验证 |

“计划支持”或“协议兼容”不代表当前已经完成安装验证。

## 兼容性

```text
Skill 版本：v0.1.0
Skill 名称：imem-skill
生产 MCP：https://imem.xin/mcp
认证方式：Personal API Key Bearer Token
OAuth：pending
```

服务端必须提供
[MCP 工具规范](skills/imem-skill/references/mcp-tool-spec.md) 中描述的行为。
版本化的机器可读工具契约位于
[`contracts/remote-mcp.json`](contracts/remote-mcp.json)。

## 安全与数据边界

正常调用路径：

```text
Agent -> 远程 MCP -> 已部署的 iMem 服务
```

Skill 不得直接读写 SQLite、JSONL 用户数据、服务器数据目录或服务实现模块。

## 验证

以下检查不需要任何密钥：

`skills/imem-skill/` 是唯一需要编辑的 Skill 源。修改后运行
`python tools/sync_plugin_skill.py`，同步 Plugin 中的打包副本。

```bash
python test/check_publication_layout.py
python test/check_standalone_repository.py
python test/check_package_boundary.py
python test/check_remote_mcp_contract.py
python test/check_plugin_package.py
```

## 升级

Codex：

```bash
codex plugin marketplace upgrade imem-plugins
```

Claude Code：

```text
/plugin marketplace update imem-plugins
/reload-plugins
```

WorkBuddy / CodeBuddy：

```text
/plugin marketplace update imem-plugins
/reload-plugins
```

Hermes：

```bash
hermes skills check
hermes skills update
hermes mcp test imem
```

升级后新建任务或会话。

## 卸载

```bash
codex plugin remove imem@imem-plugins
codex plugin marketplace remove imem-plugins
```

Claude Code：

```text
/plugin uninstall imem@imem-plugins
/plugin marketplace remove imem-plugins
```

WorkBuddy / CodeBuddy：

```text
/plugin uninstall imem@imem-plugins
/plugin marketplace remove imem-plugins
```

Hermes：

```bash
hermes skills uninstall imem-skill
hermes mcp remove imem
```

如果希望以后重新安装，可以保留 iMem Marketplace。不再使用该集成时，在 Web App 中
撤销对应的 API Key。

## 项目状态

- 项目仍处于实验阶段。
- 本仓库不部署 iMem 服务，也不签发 API Key。
- OAuth 尚未实现；当前使用用户自行创建的 Personal API Key。
- 提醒发送渠道取决于已部署服务。
- Codex 是当前经过线上实机验证的 Agent 路径。
- Claude Code 已完成安装包和静态契约实现；仍需在安装了 Claude Code 的环境中实机验证。
- WorkBuddy / CodeBuddy Marketplace 入口和 Hermes 安装路径已实现；仍待实机安装验证。

## 安全

安全问题请按照[安全策略](SECURITY.md)报告。请勿在公开 Issue 中包含 API Key、
访问令牌或私人用户数据。

## 许可证

本项目基于 [MIT License](LICENSE) 发布。

<div align="center">

为那些应该记住重要事项的 Agent 而构建。

</div>
