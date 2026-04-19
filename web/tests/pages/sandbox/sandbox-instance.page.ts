import type { Page, Locator } from '@playwright/test'

export class SandboxInstancePage {
  readonly page: Page
  readonly url = '/sandbox/instances'

  // Page elements
  readonly pageTitle: Locator
  readonly createButton: Locator
  readonly refreshButton: Locator
  readonly nameSearchInput: Locator
  readonly table: Locator
  readonly tableRows: Locator
  readonly pagination: Locator

  constructor(page: Page) {
    this.page = page
    this.pageTitle = page.getByRole('heading', { name: '沙箱实例管理' })
    this.createButton = page.getByRole('button', { name: '创建实例' })
    this.refreshButton = page.getByRole('button', { name: '刷新' })
    this.nameSearchInput = page.getByPlaceholder('搜索名称')
    this.table = page.locator('.sandbox-instance-management .el-table')
    this.tableRows = page.locator('.sandbox-instance-management .el-table__row')
    this.pagination = page.locator('.sandbox-instance-management .el-pagination')
  }

  async goto() {
    await this.page.goto(this.url)
    await this.page.waitForLoadState('domcontentloaded')
    await this.page.waitForTimeout(1000)
  }

  async getRowCount(): Promise<number> {
    return await this.tableRows.count()
  }

  async clickCreate() {
    await this.createButton.click()
  }

  async clickRefresh() {
    await this.refreshButton.click()
  }

  async searchByName(name: string) {
    await this.nameSearchInput.fill(name)
    await this.page.keyboard.press('Enter')
    await this.page.waitForTimeout(500)
  }

  async clickDetailOnRow(index: number) {
    await this.tableRows.nth(index).getByRole('button', { name: '详情' }).click()
  }

  async clickDeleteOnRow(index: number) {
    await this.tableRows.nth(index).getByRole('button', { name: '删除' }).click()
  }
}
