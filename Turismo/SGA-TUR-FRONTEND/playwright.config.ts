import { defineConfig, devices } from '@playwright/test';

/**
 * Configuración general de Playwright
 * Documentación: https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  /* Ejecutar los tests en paralelo */
  fullyParallel: true,

  /* Evitar dejar test.only en CI */
  forbidOnly: !!process.env.CI,

  /* Reintentos automáticos solo en CI */
  retries: process.env.CI ? 2 : 0,

  /* Limitar workers en CI */
  workers: process.env.CI ? 1 : undefined,

  /* Reporter */
  reporter: 'html',

  /* Configuración compartida */
  use: {
    trace: 'on-first-retry',
    baseURL: 'http://localhost:3000',
    headless: true,
  },

  /* Proyectos para diferentes navegadores */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Puedes añadir firefox o webkit si lo deseas
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
  ],

  /**
   * Configuración del servidor web.
   * - En entornos CI → no se levanta el servidor.
   * - En desarrollo → usa `npm run dev`.
   * - En producción → usa `npm run preview`.
   *
   * NOTA: Si las pruebas fallan por timeout al iniciar el servidor,
   * una estrategia es iniciar el servidor manualmente en una terminal
   * (`npm run dev &`) y luego comentar toda esta sección `webServer`
   * antes de ejecutar `npx playwright test`.
   */
  // webServer: (() => {
  //   if (process.env.CI) {
  //     console.log('⚙️  Entorno CI detectado: se omite el arranque automático del servidor.');
  //     return undefined;
  //   }

  //   const isProduction = process.env.NODE_ENV === 'production';

  //   return {
  //     command: isProduction ? 'npm run preview' : 'npm run dev',
  //     url: 'http://localhost:3000',
  //     reuseExistingServer: true,
  //     timeout: 120 * 1000,
  //   };
  // })(),
});