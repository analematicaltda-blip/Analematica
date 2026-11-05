import { test, expect } from '@playwright/test';

test('E2E Simulation: Comercial Flow', async ({ page }) => {
  test.setTimeout(120000); // 2 minutes
  await page.goto('http://localhost:3000/dashboard/login');
  await page.fill('input[name="email"]', 'prestador');
  await page.fill('input[name="password"]', 'prestador');
  await page.click('button:has-text("Iniciar Sesión")');

  await page.waitForURL(/.*dashboard/);

  // Go to Comercial
  await page.goto('http://localhost:3000/dashboard/prestador/mi-negocio/gestion-comercial');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/tmp/comercial-main.png', fullPage: true });

  // Try to find Marketing/Communication
  // Since it's not in page.tsx yet, I'll probably see the facturas table.
});
