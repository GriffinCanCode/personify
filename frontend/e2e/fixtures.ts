import { type Page, test as base } from '@playwright/test'

/**
 * Custom fixtures for E2E tests
 * Extend Playwright's base test with custom functionality
 */

type CustomFixtures = {
  // Add custom fixtures here
  authenticatedPage: Page // Example fixture
}

export const test = base.extend<CustomFixtures>({
  // Example: Auto-authenticated page
  authenticatedPage: async ({ page }: { page: Page }, use: (page: Page) => Promise<void>) => {
    // Setup authentication if needed
    // await page.goto('/login')
    // await page.fill('[name="email"]', 'test@example.com')
    // await page.fill('[name="password"]', 'password')
    // await page.click('[type="submit"]')

    await use(page)

    // Cleanup if needed
  },
})

export { expect } from '@playwright/test'
