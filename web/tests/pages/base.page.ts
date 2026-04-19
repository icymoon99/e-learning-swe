import type { Page, Locator } from '@playwright/test'

export class BasePage {
  readonly page: Page
  readonly sidebar: Locator
  readonly header: Locator

  constructor(page: Page) {
    this.page = page
    this.sidebar = page.locator('.sidebar')
    this.header = page.locator('.app-header')
  }

  async navigateTo(path: string) {
    await this.page.goto(path)
  }

  async clickSidebarItem(text: string) {
    await this.page.getByText(text).click()
  }
}
