import type { Page, Locator } from '@playwright/test'

export class Q2TaskPage {
  readonly page: Page
  readonly url = '/q2/tasks'

  // Page header
  readonly pageTitle: Locator
  readonly workerStatusTag: Locator
  readonly toggleQueueButton: Locator
  readonly refreshButton: Locator

  // Tabs
  readonly runningTab: Locator
  readonly successTab: Locator
  readonly failureTab: Locator
  readonly schedulesTab: Locator
  readonly queueTab: Locator

  // Table (scoped to active tab pane)
  readonly taskTable: Locator
  readonly taskRows: Locator

  // Pagination
  readonly pagination: Locator

  // Detail dialog
  readonly detailDialog: Locator

  constructor(page: Page) {
    this.page = page
    this.pageTitle = page.getByRole('heading', { name: 'Django-Q2 任务管理' })
    // First .el-tag in the header area (Worker status)
    this.workerStatusTag = page.locator('.q2-task-management > div:first-child .el-tag').first()
    this.toggleQueueButton = page.getByRole('button', { name: /暂停|恢复/ })
    this.refreshButton = page.getByRole('button', { name: '刷新' })

    this.runningTab = page.getByRole('tab', { name: '运行中' })
    this.successTab = page.getByRole('tab', { name: '成功' })
    this.failureTab = page.getByRole('tab', { name: '失败' })
    this.schedulesTab = page.getByRole('tab', { name: '定时任务' })
    this.queueTab = page.getByRole('tab', { name: '队列' })

    // Scope table to the active tab pane
    this.taskTable = page.locator('.el-tabs__content .el-tab-pane:not([style*="display: none"]) .el-table').first()
    this.taskRows = page.locator('.el-tabs__content .el-tab-pane:not([style*="display: none"]) .el-table__row')

    this.pagination = page.locator('.el-pagination')

    this.detailDialog = page.getByRole('dialog', { name: '任务详情' })
  }

  async goto() {
    await this.page.goto(this.url)
    await this.page.waitForLoadState('domcontentloaded')
    await this.page.waitForTimeout(1500)
  }

  async switchToTab(name: 'running' | 'success' | 'failure' | 'schedules' | 'queue') {
    const tabMap = {
      running: this.runningTab,
      success: this.successTab,
      failure: this.failureTab,
      schedules: this.schedulesTab,
      queue: this.queueTab,
    }
    await tabMap[name].click()
    await this.page.waitForTimeout(500)
  }

  async getRowCount(): Promise<number> {
    return await this.taskRows.count()
  }

  async clickDetailOnRow(index: number) {
    await this.taskRows.nth(index).getByRole('button', { name: '详情' }).click()
  }

  async clickRetryOnRow(index: number) {
    await this.taskRows.nth(index).getByRole('button', { name: '重试' }).click()
  }

  async clickDeleteOnRow(index: number) {
    await this.taskRows.nth(index).getByRole('button', { name: '删除' }).click()
  }

  async confirmMessageBox() {
    await this.page.getByRole('button', { name: '确定' }).first().click()
  }
}
