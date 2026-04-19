import { test as base } from '@playwright/test'
import type { Page, BrowserContext } from '@playwright/test'

// Fresh token from backend login (exp: 1776698932 = 2026-04-20)
const ADMIN_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc2Njk4OTMyLCJpYXQiOjE3NzY2MTI1MzIsImp0aSI6IjM0MDQyOGU2NDQwMzRlNDJiMDhkZTRlMzFlYzM0NTUwIiwidXNlcl9pZCI6IjAxS1BKUVFRRlk0VkQ0UjcyRTJTNDE4OEo2In0.1WUDQCFwFAXWOR0BDGcvA4Gg3TY53UicCyZysReYZyY'

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
