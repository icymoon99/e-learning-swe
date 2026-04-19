import { test, expect } from '../fixtures/auth'
import { Q2TaskPage } from '../pages/q2/q2-task.page'

test.describe('Q2 Task Management', () => {
  test('should display the task management page with header and status', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await expect(q2Page.pageTitle).toBeVisible()
    await expect(q2Page.workerStatusTag).toBeVisible()
    await expect(q2Page.runningTab).toBeVisible()
    await expect(q2Page.successTab).toBeVisible()
    await expect(q2Page.failureTab).toBeVisible()
    await expect(q2Page.schedulesTab).toBeVisible()
    await expect(q2Page.queueTab).toBeVisible()
  })

  test('should display the refresh button', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await expect(q2Page.refreshButton).toBeVisible()
  })

  test('should switch to running tab and load data', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await q2Page.switchToTab('running')
    await expect(q2Page.taskTable).toBeVisible()
  })

  test('should switch to success tab and load data', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await q2Page.switchToTab('success')
    await expect(q2Page.taskTable).toBeVisible()
  })

  test('should switch to failure tab and load data', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await q2Page.switchToTab('failure')
    await expect(q2Page.taskTable).toBeVisible()
  })

  test('should switch to schedules tab', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await q2Page.switchToTab('schedules')
    await expect(page.getByRole('button', { name: '创建定时任务' })).toBeVisible()
  })

  test('should switch to queue tab', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await q2Page.switchToTab('queue')
    await expect(page.getByText('Worker 状态')).toBeVisible()
  })

  test('should open detail dialog when clicking detail button', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await q2Page.switchToTab('success')
    const rowCount = await q2Page.getRowCount()
    if (rowCount > 0) {
      await q2Page.clickDetailOnRow(0)
      await expect(q2Page.detailDialog).toBeVisible()
    }
  })

  test('should display pagination when there are results', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await q2Page.switchToTab('success')
    const rowCount = await q2Page.getRowCount()
    if (rowCount > 0) {
      await expect(q2Page.pagination).toBeVisible()
    }
  })

  test('should show confirmation dialog when clicking delete', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await q2Page.switchToTab('success')
    const rowCount = await q2Page.getRowCount()
    if (rowCount > 0) {
      await q2Page.clickDeleteOnRow(0)
      await expect(page.getByText('确认删除')).toBeVisible()
    }
  })

  test('should show confirmation dialog when clicking retry', async ({ authenticatedPage: page }) => {
    const q2Page = new Q2TaskPage(page)
    await q2Page.goto()
    await q2Page.switchToTab('failure')
    const rowCount = await q2Page.getRowCount()
    if (rowCount > 0) {
      await q2Page.clickRetryOnRow(0)
      await expect(page.getByText('确认重试')).toBeVisible()
    }
  })
})
