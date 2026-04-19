import { test } from '@playwright/test'

test('debug login', async ({ page }) => {
  // Listen to console and network
  page.on('console', msg => console.log('PAGE LOG:', msg.text()))
  page.on('response', resp => {
    if (resp.url().includes('/api/')) {
      console.log(`API: ${resp.status()} ${resp.url()}`)
      resp.text().then(body => console.log('API BODY:', body)).catch(() => {})
    }
  })

  await page.goto('/login')
  await page.getByPlaceholder('用户名').fill('admin')
  await page.getByPlaceholder('密码').fill('Admin@1234')
  await page.getByRole('button', { name: '登 录' }).click()

  // Wait a bit
  await page.waitForTimeout(3000)
  await page.screenshot({ path: 'web/test-results/debug-login.png' })

  // Check URL
  console.log('Current URL:', page.url())

  // Check for error messages (ElMessage uses .el-message class)
  const messages = page.locator('.el-message')
  const count = await messages.count()
  console.log('Message count:', count)
  for (let i = 0; i < count; i++) {
    const text = await messages.nth(i).textContent()
    console.log(`Message ${i}:`, text)
  }
})
