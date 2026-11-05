import { test, expect } from '@playwright/test';

test.describe('E2E Simulation: Operador Turístico Integral - Gestión Comercial', () => {
  test.beforeEach(async ({ page }) => {
    // Login as Prestador
    await page.goto('http://localhost:3000/dashboard/login');
    await page.fill('input[name="email"]', 'prestador@example.com');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('Multichannel Communication Flow', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard/prestador/mi-negocio/gestion-comercial');

    // Navigate to Communication (Level 1)
    // Looking for the tab or component
    await page.click('text=Campañas'); // Assuming this text exists in Level1_Communication

    // Create a new campaign
    await page.fill('input[placeholder*="Lanzamiento"]', 'Campaña Expedición Amazonas');
    await page.click('text=WhatsApp');
    await page.fill('textarea', 'Hola! Tenemos una nueva oferta para ti.');
    await page.click('text=Crear Campaña');

    // Verify it appears in the list
    await expect(page.locator('text=Campaña Expedición Amazonas')).toBeVisible();
    await page.screenshot({ path: 'test-results/commercial-comm.png' });
  });

  test('Sales Funnel Architect', async ({ page }) => {
    // Navigate to Funnels (Level 3 or 5 depending on mapping)
    // Based on Sidebar.tsx: /dashboard/prestador/mi-negocio/gestion-comercial
    // The page.tsx of gestion-comercial probably has tabs

    // Let's explore the page first
    await page.goto('http://localhost:3000/dashboard/prestador/mi-negocio/gestion-comercial');
    await page.screenshot({ path: 'test-results/commercial-dashboard.png' });
  });
});
