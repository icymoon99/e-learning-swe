import type { Page, Locator } from '@playwright/test'

export class SandboxInstancePage {
  readonly page: Page
  readonly url = '/sandbox/instances'

  // Page elements
  readonly pageTitle: Locator
  readonly createButton: Locator
  readonly refreshButton: Locator
  readonly nameSearchInput: Locator
  readonly typeSelect: Locator
  readonly statusSelect: Locator
  readonly table: Locator
  readonly tableRows: Locator
  readonly pagination: Locator

  constructor(page: Page) {
    this.page = page
    this.pageTitle = page.getByRole('heading', { name: '沙箱实例管理' })
    this.createButton = page.getByRole('button', { name: '创建实例' })
    this.refreshButton = page.getByRole('button', { name: '刷新' })
    this.nameSearchInput = page.getByPlaceholder('搜索名称')
    this.typeSelect = page.locator('.el-select').filter({ hasText: '类型' })
    this.statusSelect = page.locator('.el-select').filter({ hasText: '状态' })
    this.table = page.locator('.sandbox-instance-management .el-table')
    this.tableRows = page.locator('.sandbox-instance-management .el-table__row')
    this.pagination = page.locator('.sandbox-instance-management .el-pagination')
  }

  async goto() {
    await this.page.goto(this.url)
    await this.page.waitForLoadState('domcontentloaded')
    // Wait for table data to load
    await this.page.waitForResponse(
      resp => resp.url().includes('/sandbox/instances/') && resp.status() === 200,
      { timeout: 10000 },
    ).catch(() => {})
    await this.page.waitForTimeout(500)
  }

  async getRowCount(): Promise<number> {
    return await this.tableRows.count()
  }

  async getRowText(index: number): Promise<string> {
    return await this.tableRows.nth(index).textContent()
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

  async clickEditOnRow(index: number) {
    await this.tableRows.nth(index).getByRole('button', { name: '编辑' }).click()
  }

  async clickDeleteOnRow(index: number) {
    await this.tableRows.nth(index).getByRole('button', { name: '删除' }).click()
  }

  async clickStartOnRow(index: number) {
    await this.tableRows.nth(index).getByRole('button', { name: '启动' }).click()
  }

  async clickStopOnRow(index: number) {
    await this.tableRows.nth(index).getByRole('button', { name: '停止' }).click()
  }

  async clickResetOnRow(index: number) {
    await this.tableRows.nth(index).getByRole('button', { name: '重置' }).click()
  }

  async clickExecuteOnRow(index: number) {
    await this.tableRows.nth(index).getByRole('button', { name: '执行' }).click()
  }

  // Form helpers
  async fillCreateForm(data: { name: string; type: string; rootPath: string }) {
    await this.page.getByPlaceholder('沙箱名称').fill(data.name)
    await this.page.locator('.el-dialog .el-select').first().click()
    // Select type from dropdown options
    const typeOptionMap: Record<string, string> = {
      localdocker: '本地 Docker',
      remotedocker: '远程 Docker',
      localsystem: '本地系统',
      remotesystem: '远程系统',
    }
    await this.page.getByRole('option', { name: typeOptionMap[data.type] }).click()
    await this.page.getByPlaceholder('/workspace').fill(data.rootPath)
  }

  async fillEditForm(data: { name?: string; rootPath?: string }) {
    if (data.name) {
      const nameInput = this.page.locator('.el-dialog').getByPlaceholder('沙箱名称')
      await nameInput.clear()
      await nameInput.fill(data.name)
    }
    if (data.rootPath) {
      const rootInput = this.page.locator('.el-dialog').getByPlaceholder('/workspace')
      await rootInput.clear()
      await rootInput.fill(data.rootPath)
    }
  }

  async clickDialogSave() {
    await this.page.locator('.el-dialog').getByRole('button', { name: '保存' }).click()
  }

  async clickDialogCancel() {
    await this.page.locator('.el-dialog').getByRole('button', { name: '取消' }).click()
  }

  async clickConfirmDialog() {
    // ElMessageBox confirm button
    await this.page.locator('.el-message-box__btns .el-button--primary').click()
  }

  async isDialogVisible(title: string): Promise<boolean> {
    return await this.page.getByRole('dialog', { name: title }).isVisible()
  }

  async isDrawerVisible(): Promise<boolean> {
    return await this.page.locator('.el-drawer__wrapper .el-drawer').isVisible()
  }
}
