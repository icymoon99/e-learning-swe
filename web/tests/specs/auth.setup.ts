import { test as setup, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const authFile = path.join(__dirname, '../../.auth/user.json')

setup('authenticate as admin', async ({ page }) => {
  // Call login API directly to get tokens
  const response = await page.request.post('http://localhost:8600/api/user/token/', {
    data: {
      username: 'admin',
      password: 'DWTAv0B/nRzAztriQenVrw==', // AES encrypted Admin@1234
    },
  })
  expect(response.ok()).toBeTruthy()
  const body = await response.json()
  const tokens = body.content

  // Create auth state with localStorage
  const authState = {
    cookies: [],
    origins: [
      {
        origin: 'http://localhost:3001',
        localStorage: [
          { name: 'el_swe_access_token', value: tokens.access },
          { name: 'el_swe_refresh_token', value: tokens.refresh },
          { name: 'el_swe_token_expires_at', value: String(Date.now() + 24 * 60 * 60 * 1000) },
        ],
      },
    ],
  }

  fs.writeFileSync(authFile, JSON.stringify(authState, null, 2))
  console.log('Auth state saved with tokens')
})
