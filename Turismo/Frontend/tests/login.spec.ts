import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should allow a user to log in and redirect to the dashboard', async ({ page }) => {
    // Navigate to the login page
    await page.goto('http://localhost:3000/dashboard/login');

    // Get credentials from environment variables or use defaults
    const userEmail = process.env.E2E_TEST_USER_EMAIL || 'admin@example.com';
    const userPassword = process.env.E2E_TEST_USER_PASS || 'admin';

    // Fill in the email and password
    await page.fill('input[name="email"]', userEmail);
    await page.fill('input[name="password"]', userPassword);

    // Click the login button
    await page.click('button[type="submit"]');

    // Wait for navigation to the dashboard and verify an element
    // We expect to see the main content area after successful login.
    const mainContent = await page.waitForSelector('main.flex-1');
    expect(mainContent).toBeTruthy();

    // Verify the URL changed to the dashboard (or a sub-page)
    await expect(page).toHaveURL(/.*dashboard/);

    // Take a screenshot for visual confirmation
    await page.screenshot({ path: 'frontend/e2e/screenshots/login-success.png' });
  });
});
