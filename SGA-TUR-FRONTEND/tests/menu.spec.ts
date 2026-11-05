import { test, expect } from '@playwright/test';

test.describe('Public Menu Verification', () => {
  test('should display the main navigation menu items', async ({ page }) => {
    // Navigate to the homepage on the correct port
    await page.goto('http://localhost:3001/');

    // Wait for the navigation bar to be visible
    const navBar = await page.waitForSelector('nav');
    expect(navBar).toBeTruthy();

    // Specifically wait for and verify the "Directorio" link, which comes from the API
    const directorioLink = page.locator('a:has-text("Directorio")');
    await expect(directorioLink).toBeVisible({ timeout: 20000 }); // Wait up to 20 seconds

    // Take a screenshot for visual confirmation
    await page.screenshot({ path: 'frontend/e2e/screenshots/menu-visible.png' });
  });
});
