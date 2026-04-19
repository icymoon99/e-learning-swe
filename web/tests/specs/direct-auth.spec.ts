import { test, expect } from '@playwright/test'

test('q2 page auth - should stay authenticated on q2/tasks page', async ({ page, context }) => {
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc2NjQ1NDgwLCJpYXQiOjE3NzY1NTkwODAsImp0aSI6ImY0MjBlM2UzNTU1NzQwZWJhNTYzOWYwOGNjNDMxYTUyIiwidXNlcl9pZCI6IjAxS1BHRzJUMjY4SE45SzgwQ1g3RUZWMDczIn0.MHuHvUQIjEUE6GUSdIjv34i8svXr4nIfi2sV_0VQais'

  await context.addInitScript((t) => {
    localStorage.setItem('el_swe_access_token', JSON.stringify(t))
    localStorage.setItem('el_swe_refresh_token', JSON.stringify(t))
    localStorage.setItem('el_swe_token_expires_at', JSON.stringify(Date.now() + 24 * 60 * 60 * 1000))
  }, token)

  await page.goto('/q2/tasks')
  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(2000)

  // Should NOT redirect to login
  await expect(page).toHaveURL(/\/q2\/tasks/)
})
