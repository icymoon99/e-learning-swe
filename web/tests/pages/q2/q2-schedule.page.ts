import type { Page, Locator } from '@playwright/test'

export class Q2SchedulePage {
  readonly page: Page
  readonly url = '/q2/tasks'

  readonly schedulesTab: Locator
  readonly createScheduleButton: Locator
  readonly scheduleTable: Locator
  readonly scheduleRows: Locator
  readonly scheduleDialog: Locator

  constructor(page: Page) {
    this.page = page
    this.schedulesTab = page.getByRole('tab', { name: '定时任务' })
    this.createScheduleButton = page.getByRole('button', { name: '创建定时任务' })
    this.scheduleTable = page.locator('.el-table')
    this.scheduleRows = page.locator('.el-table__row')
    this.scheduleDialog = page.getByRole('dialog')
  }

  async goto() {
    await this.page.goto(this.url)
    await this.page.waitForLoadState('networkidle')
    await this.schedulesTab.click()
    await this.page.waitForLoadState('networkidle')
  }

  async getRowCount(): Promise<number> {
    return await this.scheduleRows.count()
  }
}
