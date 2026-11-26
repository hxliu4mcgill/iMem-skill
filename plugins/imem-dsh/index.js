/** Adaptive iMem connector for DeepSeek Harness Desktop and Web. */
export const name = 'imem-connector'
export const inject = ['mcpManager']

const SERVER_NAME = 'imem'
const CREDENTIAL_KEY = 'mcp-client/imem'
const API_KEY_REF = '${credential:IMEM_API_KEY}'
const PACKAGE_NAME = 'dsh-plugin-imem'
const text = (zh, en) => ({ zh, en })

const COPY = {
  title: text('iMem 账号', 'iMem account'),
  connect: text('连接 iMem', 'Connect iMem'),
  activation: {
    title: text('连接 iMem 账号', 'Connect your iMem account'),
    body: text('iMem 插件已开启。连接账号后即可在对话中使用长期记忆、日程与提醒。', 'The iMem plugin is on. Connect your account to use durable memory, schedules, and reminders in conversations.'),
  },
  detail: {
    disconnected: text('连接 iMem 账号后，即可在对话中使用长期记忆、日程与提醒。', 'Connect your iMem account to use durable memory, schedules, and reminders in conversations.'),
    waitingBrowser: text('已打开 iMem 授权页面。完成授权后请返回这里。', 'The iMem authorization page is open. Finish authorization, then return here.'),
    authorizing: text('正在完成 iMem 授权。', 'Finishing authorization with iMem.'),
    connecting: text('正在连接 iMem。', 'Connecting to iMem.'),
    connected: text('现在可以在对话中直接请 Agent 使用 iMem。', 'Ask the agent to use iMem directly in a conversation.'),
    rejected: text('iMem 不再接受当前授权，请重新连接。', 'iMem no longer accepts the current authorization. Connect again.'),
    scope: text('当前授权缺少所需权限，请重新连接并确认权限。', 'The current authorization lacks required permissions. Connect again and confirm them.'),
  },
  signOut: {
    title: text('退出 iMem 登录？', 'Sign out of iMem?'),
    body: text('这会删除 DSH 保存的 iMem 授权，之后对话将无法使用 iMem。', 'This deletes the iMem authorization saved by DSH, so conversations can no longer use iMem.'),
  },
  notice: {
    connected: text('iMem 已连接', 'iMem connected'),
    signedOut: text('已退出 iMem 登录', 'Signed out of iMem'),
  },
}

export function apply(ctx) {
  const oauthAvailable = typeof ctx.mcpManager.startAuthorization === 'function'
  ctx.mcpManager.register(SERVER_NAME, {
    transport: 'streamable-http',
    url: 'https://imem.xin/mcp',
    ...(oauthAvailable
      ? { oauth: { credentialKey: CREDENTIAL_KEY, scope: 'entries:read entries:write' } }
      : { headers: { Authorization: `Bearer ${API_KEY_REF}` } }),
    startupTimeoutMs: 30_000,
  })

  if (!oauthAvailable) return
  ctx.inject(['mcpAccounts'], (scope) => {
    scope.effect(
      () => scope.mcpAccounts.register({ server: SERVER_NAME, packageName: PACKAGE_NAME, copy: COPY }),
      'imem: Plugins page account',
    )
  })
}
