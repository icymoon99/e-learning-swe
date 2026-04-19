import { test as base } from '@playwright/test'
import type { Page, BrowserContext } from '@playwright/test'

const ADMIN_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc2NjQ1NDgwLCJpYXQiOjE3NzY1NTkwODAsImp0aSI6ImY0MjBlM2UzNTU1NzQwZWJhNTYzOWYwOGNjNDMxYTUyIiwidXNlcl9pZCI6IjAxS1BHRzJUMjY4SE45SzgwQ1g3RUZWMDczIn0.MHuHvUQIjEUE6GUSdIjv34i8svXr4nIfi2sV_0VQais'

async function setupAuth(context: BrowserContext, page: Page) {
  await context.addInitScript((token) => {
    localStorage.setItem('el_swe_access_token', JSON.stringify(token))
    localStorage.setItem('el_swe_refresh_token', JSON.stringify(token))
    localStorage.setItem('el_swe_token_expires_at', JSON.stringify(Date.now() + 24 * 60 * 60 * 1000))
  }, ADMIN_TOKEN)

  await page.goto('/q2/tasks')
  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(1000)
}

export const test = base.extend<{ authenticatedPage: Page }>({
  authenticatedPage: async ({ page, context }, use) => {
    await setupAuth(context, page)
    await use(page)
  },
})

export { expect } from '@playwright/test'
