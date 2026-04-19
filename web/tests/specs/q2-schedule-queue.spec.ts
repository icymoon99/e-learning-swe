import { test, expect } from '../fixtures/auth'

test.describe('Q2 Schedule Management', () => {
  test('should display the schedule tab with create button', async ({ authenticatedPage: page }) => {
    await page.goto('/q2/tasks')
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    await page.getByRole('tab', { name: '定时任务' }).click()
    await page.waitForTimeout(500)
    await expect(page.getByRole('button', { name: '创建定时任务' })).toBeVisible()
  })

  test('should open create schedule dialog when clicking create', async ({ authenticatedPage: page }) => {
    await page.goto('/q2/tasks')
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    await page.getByRole('tab', { name: '定时任务' }).click()
    await page.waitForTimeout(500)
    await page.getByRole('button', { name: '创建定时任务' }).click()
    const dialog = page.getByRole('dialog', { name: '创建定时任务' })
    await expect(dialog).toBeVisible()
    await expect(page.getByPlaceholder('任务名称')).toBeVisible()
    await expect(page.getByPlaceholder('myapp.tasks.my_task')).toBeVisible()
    await expect(page.getByRole('dialog', { name: '创建定时任务' }).locator('.el-select')).toBeVisible()
  })

  test('should validate required fields in create dialog', async ({ authenticatedPage: page }) => {
    await page.goto('/q2/tasks')
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    await page.getByRole('tab', { name: '定时任务' }).click()
    await page.waitForTimeout(500)
    await page.getByRole('button', { name: '创建定时任务' }).click()
    await page.getByRole('dialog', { name: '创建定时任务' }).getByRole('button', { name: '保存' }).click()
    await expect(page.getByText('请填写名称和函数')).toBeVisible()
  })

  test('should close dialog when clicking cancel', async ({ authenticatedPage: page }) => {
    await page.goto('/q2/tasks')
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    await page.getByRole('tab', { name: '定时任务' }).click()
    await page.waitForTimeout(500)
    await page.getByRole('button', { name: '创建定时任务' }).click()
    await page.getByRole('dialog', { name: '创建定时任务' }).getByRole('button', { name: '取消' }).click()
    await expect(page.getByRole('dialog', { name: '创建定时任务' })).not.toBeVisible()
  })
})

test.describe('Q2 Queue Status', () => {
  test('should display queue status component', async ({ authenticatedPage: page }) => {
    await page.goto('/q2/tasks')
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    await page.getByRole('tab', { name: '队列' }).click()
    await page.waitForTimeout(500)
    await expect(page.getByText('Worker 状态')).toBeVisible()
  })

  test('should display worker status', async ({ authenticatedPage: page }) => {
    await page.goto('/q2/tasks')
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    await page.getByRole('tab', { name: '队列' }).click()
    await page.waitForTimeout(500)
    await expect(page.locator('.el-tag').filter({ hasText: /Worker/ })).toBeVisible()
  })

  test('should show toggle queue button', async ({ authenticatedPage: page }) => {
    await page.goto('/q2/tasks')
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    await page.getByRole('tab', { name: '队列' }).click()
    await page.waitForTimeout(500)
    const toggleBtn = page.getByRole('button', { name: /暂停|恢复/ })
    await expect(toggleBtn).toBeVisible()
  })
})
