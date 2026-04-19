import { test, expect } from '../fixtures/auth'
import { SandboxInstancePage } from '../pages/sandbox/sandbox-instance.page'

test.describe('Sandbox Instance Management E2E', () => {
  let sandboxPage: SandboxInstancePage

  test.beforeEach(async ({ authenticatedPage: page }) => {
    sandboxPage = new SandboxInstancePage(page)
    await sandboxPage.goto()
  })

  test.describe('page rendering', () => {
    test('should display the instance management page with header', async ({ authenticatedPage: page }) => {
      await expect(sandboxPage.pageTitle).toBeVisible()
      await expect(sandboxPage.createButton).toBeVisible()
      await expect(sandboxPage.refreshButton).toBeVisible()
    })

    test('should display filter controls', async ({ authenticatedPage: page }) => {
      await expect(sandboxPage.nameSearchInput).toBeVisible()
      await expect(sandboxPage.typeSelect).toBeVisible()
      await expect(sandboxPage.statusSelect).toBeVisible()
    })

    test('should display the data table', async ({ authenticatedPage: page }) => {
      await expect(sandboxPage.table).toBeVisible()
    })

    test('should display pagination', async ({ authenticatedPage: page }) => {
      await expect(sandboxPage.pagination).toBeVisible()
    })
  })

  test.describe('create sandbox', () => {
    test('should open create dialog when clicking create button', async ({ authenticatedPage: page }) => {
      await sandboxPage.clickCreate()
      await expect(page.getByRole('dialog', { name: '创建实例' })).toBeVisible()
    })

    test('should show validation error when saving empty form', async ({ authenticatedPage: page }) => {
      await sandboxPage.clickCreate()
      await expect(page.getByRole('dialog', { name: '创建实例' })).toBeVisible()
      await sandboxPage.clickDialogSave()
      await expect(page.getByText('请填写必填字段')).toBeVisible()
    })
  })

  test.describe('edit sandbox', () => {
    test('should open edit dialog with existing data', async ({ authenticatedPage: page }) => {
      const rowCount = await sandboxPage.getRowCount()
      if (rowCount > 0) {
        await sandboxPage.clickEditOnRow(0)
        await expect(page.getByRole('dialog', { name: '编辑实例' })).toBeVisible()
      }
    })
  })

  test.describe('detail view', () => {
    test('should show detail dialog when clicking detail', async ({ authenticatedPage: page }) => {
      const rowCount = await sandboxPage.getRowCount()
      if (rowCount > 0) {
        await sandboxPage.clickDetailOnRow(0)
        await expect(page.getByRole('dialog', { name: '沙箱实例详情' })).toBeVisible()
      }
    })
  })

  test.describe('delete sandbox', () => {
    test('should show confirmation dialog when clicking delete', async ({ authenticatedPage: page }) => {
      const rowCount = await sandboxPage.getRowCount()
      if (rowCount > 0) {
        await sandboxPage.clickDeleteOnRow(0)
        await expect(page.getByText('确认删除')).toBeVisible()
      }
    })
  })

  test.describe('actions', () => {
    test('should show start confirmation dialog', async ({ authenticatedPage: page }) => {
      const rowCount = await sandboxPage.getRowCount()
      if (rowCount > 0) {
        await sandboxPage.clickStartOnRow(0)
        await expect(page.getByText('确认启动')).toBeVisible()
      }
    })

    test('should show stop confirmation dialog', async ({ authenticatedPage: page }) => {
      const rowCount = await sandboxPage.getRowCount()
      if (rowCount > 0) {
        await sandboxPage.clickStopOnRow(0)
        await expect(page.getByText('确认停止')).toBeVisible()
      }
    })

    test('should show reset confirmation dialog', async ({ authenticatedPage: page }) => {
      const rowCount = await sandboxPage.getRowCount()
      if (rowCount > 0) {
        await sandboxPage.clickResetOnRow(0)
        await expect(page.getByText('确认重置')).toBeVisible()
      }
    })

    test('should open execute command dialog', async ({ authenticatedPage: page }) => {
      const rowCount = await sandboxPage.getRowCount()
      if (rowCount > 0) {
        await sandboxPage.clickExecuteOnRow(0)
        await expect(page.locator('.el-dialog__header:has-text("执行命令")')).toBeVisible()
        await expect(page.getByPlaceholder('输入命令，例如: echo hello')).toBeVisible()
      }
    })

    test('should show warning for empty command', async ({ authenticatedPage: page }) => {
      const rowCount = await sandboxPage.getRowCount()
      if (rowCount > 0) {
        await sandboxPage.clickExecuteOnRow(0)
        // Click the execute button inside the dialog, not the table
        await page.locator('.el-dialog').getByRole('button', { name: '执行' }).click()
        await expect(page.getByText('请输入命令')).toBeVisible()
      }
    })
  })
})
