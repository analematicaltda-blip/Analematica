import { test, expect } from '@playwright/test';

test('capture login', async ({ page }) => {
  await page.goto('http://localhost:3001/dashboard/login');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'snapshot-login.png' });
});

test('capture root', async ({ page }) => {
  await page.goto('http://localhost:3001/');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'snapshot-root.png' });
});
