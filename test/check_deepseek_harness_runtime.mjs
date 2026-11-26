import assert from 'node:assert/strict'
import { apply } from '../plugins/imem-dsh/index.js'

function harness(manager) {
  const registrations = []
  let injected = false
  const ctx = {
    mcpManager: {
      ...manager,
      register(server, entry) {
        registrations.push({ server, entry })
      },
    },
    inject(dependencies, callback) {
      injected = true
      assert.deepEqual(dependencies, ['mcpAccounts'])
      callback({
        effect(run, label) {
          assert.equal(label, 'imem: Plugins page account')
          run()
        },
        mcpAccounts: {
          register(account) {
            assert.equal(account.server, 'imem')
            assert.equal(account.packageName, 'dsh-plugin-imem')
          },
        },
      })
    },
  }
  return { ctx, registrations, wasInjected: () => injected }
}

const legacy = harness({})
apply(legacy.ctx)
assert.equal(legacy.registrations.length, 1)
assert.equal(legacy.registrations[0].server, 'imem')
assert.deepEqual(legacy.registrations[0].entry.headers, {
  Authorization: 'Bearer ${credential:IMEM_API_KEY}',
})
assert.equal('oauth' in legacy.registrations[0].entry, false)
assert.equal(legacy.wasInjected(), false)

const modern = harness({ startAuthorization() {} })
apply(modern.ctx)
assert.equal(modern.registrations.length, 1)
assert.deepEqual(modern.registrations[0].entry.oauth, {
  credentialKey: 'mcp-client/imem',
  scope: 'entries:read entries:write',
})
assert.equal('headers' in modern.registrations[0].entry, false)
assert.equal(modern.wasInjected(), true)

console.log('iMem DeepSeek Harness runtime modes OK')
