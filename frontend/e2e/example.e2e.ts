import { test, expect } from '@playwright/test'

test.describe('Homepage', () => {
  test('should load the homepage successfully', async ({ page }) => {
    await page.goto('/')
    
    await expect(page).toHaveTitle(/Personify/i)
  })

  test('should navigate to chat page', async ({ page }) => {
    await page.goto('/')
    
    // Add your navigation test here
    // Example:
    // await page.click('text=Chat')
    // await expect(page).toHaveURL('/chat')
  })
})

