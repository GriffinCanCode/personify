import { expect, test } from './fixtures'

test.describe('Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should load the homepage successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/Personify/i)
  })

  test('should have proper meta tags', async ({ page }) => {
    const description = page.locator('meta[name="description"]')
    await expect(description).toHaveCount(1)
  })

  test('should be accessible', async ({ page }) => {
    // Basic accessibility check
    const main = page.locator('main')
    await expect(main).toBeVisible()
  })
})

test.describe('Navigation', () => {
  test('should navigate between pages', async ({ page }) => {
    await page.goto('/')

    // Test navigation to chat
    const chatLink = page.locator('a[href*="/chat"]')
    if ((await chatLink.count()) > 0) {
      await chatLink.first().click()
      await expect(page).toHaveURL(/\/chat/)
    }
  })

  test('should handle 404 pages', async ({ page }) => {
    const response = await page.goto('/non-existent-page')
    expect(response?.status()).toBe(404)
  })
})

test.describe('Responsive Design', () => {
  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')

    await expect(page.locator('body')).toBeVisible()
  })

  test('should work on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.goto('/')

    await expect(page.locator('body')).toBeVisible()
  })
})
