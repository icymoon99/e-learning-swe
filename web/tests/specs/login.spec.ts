import { test, expect } from '@playwright/test'

test.describe('Login', () => {
  test('should show login form', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByPlaceholder('用户名')).toBeVisible()
    await expect(page.getByPlaceholder('密码')).toBeVisible()
    await expect(page.getByRole('button', { name: '登 录' })).toBeVisible()
  })

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.goto('/login')
    await page.getByRole('button', { name: '登 录' }).click()
    await expect(page.getByText('请输入用户名')).toBeVisible()
  })
})
