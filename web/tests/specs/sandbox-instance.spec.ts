import { test, expect } from '../fixtures/auth'
import { SandboxInstancePage } from '../pages/sandbox/sandbox-instance.page'

test.describe('Sandbox Instance Management', () => {
  test('should display the instance management page with header', async ({ authenticatedPage: page }) => {
    const sandboxPage = new SandboxInstancePage(page)
    await sandboxPage.goto()
    await expect(sandboxPage.pageTitle).toBeVisible()
    await expect(sandboxPage.createButton).toBeVisible()
    await expect(sandboxPage.refreshButton).toBeVisible()
  })

  test('should display the data table', async ({ authenticatedPage: page }) => {
    const sandboxPage = new SandboxInstancePage(page)
    await sandboxPage.goto()
    await expect(sandboxPage.table).toBeVisible()
  })

  test('should display pagination', async ({ authenticatedPage: page }) => {
    const sandboxPage = new SandboxInstancePage(page)
    await sandboxPage.goto()
    await expect(sandboxPage.pagination).toBeVisible()
  })

  test('should open create dialog when clicking create button', async ({ authenticatedPage: page }) => {
    const sandboxPage = new SandboxInstancePage(page)
    await sandboxPage.goto()
    await sandboxPage.clickCreate()
    await expect(page.getByRole('dialog', { name: '创建实例' })).toBeVisible()
  })

  test('should show detail dialog when clicking detail', async ({ authenticatedPage: page }) => {
    const sandboxPage = new SandboxInstancePage(page)
    await sandboxPage.goto()
    const rowCount = await sandboxPage.getRowCount()
    if (rowCount > 0) {
      await sandboxPage.clickDetailOnRow(0)
      await expect(page.getByRole('dialog', { name: '沙箱实例详情' })).toBeVisible()
    }
  })

  test('should show confirmation dialog when clicking delete', async ({ authenticatedPage: page }) => {
    const sandboxPage = new SandboxInstancePage(page)
    await sandboxPage.goto()
    const rowCount = await sandboxPage.getRowCount()
    if (rowCount > 0) {
      await sandboxPage.clickDeleteOnRow(0)
      await expect(page.getByText('确认删除')).toBeVisible()
    }
  })
})
