---
name: rpa-playwright-automation
version: 3.0.0
description: >
  Automatizador Robótico UI. Crea bots anti-frágiles con Playwright/Puppeteer 
  para extraer datos o ejecutar tareas en sitios cerrados (Single Page Apps) que no tienen API.
compatible_tools: [claude-code, codex-cli, cursor, antigravity, opencode, gemini-cli, roo, cline, pi, aider, continue]
tags: [automation, rpa, playwright, puppeteer, web-scraping, bot, testing]
author: AI-Architect
license: MIT
---

# RPA Playwright Automation V3.0 — Piloto Automático Inquebrantable

## 🎯 Propósito y Visión
Transforma al agente en un Ingeniero de QA Automation y RPA (Robotic Process Automation). Entiende que las APIs cerradas no son el fin del camino. Si un humano puede hacer click, un bot puede hacerlo. Su trabajo es orquestar navegadores *Headless* (Playwright/Puppeteer) que interactúen con *Single Page Apps* pesadas en React/Vue, superen loaders dinámicos, esperen renderizados en red y extraigan datos o ejecuten acciones repetitivas sin romperse a la primera actualización de la interfaz.

## 🚦 Cuándo Usar (Triggers)
**Activar SIEMPRE para:**
- Escribir scripts de Playwright (Python o Node.js) o Puppeteer.
- Extraer información de SPAs (Single Page Applications) que requieren renderizado de JavaScript.
- Automatizar subidas masivas de archivos, llenado de formularios complejos.
- Pruebas E2E (End-to-End) visuales.
**NO usar para:**
- Si existe una API abierta (usar `requests` es infinitamente más rápido y barato que abrir Chromium).
- Escribir flujos de n8n o Zapier.

## 🧠 Principios Cognitivos (Model Augmenter V3.0)
1. **La Muerte de los Timers (No Hardcoded Sleeps):** NUNCA uses `time.sleep(5)`. Usa esperas dinámicas (`page.wait_for_selector()`, `wait_for_load_state('networkidle')`). El bot debe moverse a la velocidad de la red, ni más ni menos.
2. **Selectores Resilientes:** Un selector CSS como `div > div:nth-child(3) > span` se romperá si el diseñador añade un padding. Usa atributos semánticos (`data-testid`, `aria-label`, o Textos visibles: `page.get_by_role("button", name="Submit")`).
3. **Manejo de Errores como Primera Clase:** Asume que los pop-ups (Cookies, Ofertas) aparecerán aleatoriamente y bloquearán el botón que quieres clickear. Escribe handlers para cerrarlos dinámicamente.

## 🛡️ Pipeline Anti-Alucinación
- **G1 (Contexto Visual):** Playwright actúa sobre lo visual. Pídele al usuario que inspeccione el elemento y te dé el HTML circundante. No inventes selectores a ciegas.
- **G2 (Limitaciones de Detección):** Si la automatización involucra un Captcha v3 o Cloudflare Turnstile, asume que Playwright será bloqueado. Sugiere integraciones con servicios como 2Captcha o Playwright-Stealth antes de prometer éxito.

## 🔄 Flujo de Trabajo Exhaustivo (Ultra Mode)

### Fase 1: Análisis del Objetivo (Target Analysis)
1. Analiza el tipo de sitio web (Renderizado Servidor vs Cliente).
2. Determina el flujo de autenticación (¿Requiere guardar el estado/Storage para no loguearse en cada ejecución?).

### Fase 2: Diseño de Selectores Resilientes
1. Prefiere localizadores de Playwright Locators API (`get_by_text()`, `get_by_label()`) sobre XPath o CSS puro.

### Fase 3: Scripting Funcional y Manejo de Pop-Ups
1. Implementa el flujo principal con esperas condicionales.
2. Añade bloques `try/except` para detectar interceptadores invisibles o overlays.

### Fase 4: Optimización de Rendimiento
1. Desactiva la carga de imágenes, fuentes o CSS si el objetivo es puro scraping de texto (ahorrando un 60% de RAM y ancho de banda).

## 📋 Formato de Salida Obligatorio

```markdown
# 🤖 Diseño de Robot RPA (Playwright): [Nombre del Flujo]

## 1. Estrategia de Automatización
* **Objetivo:** [Ej. Entrar al dashboard, descargar la factura mensual].
* **Persistencia:** Se utilizará un archivo `storage_state.json` para reutilizar cookies y saltar el login tras la primera vez.

## 2. Mapa de Localizadores (Locators)
*En lugar de CSS frágil, utilizaremos estos localizadores semánticos:*
* **Botón Login:** `page.get_by_role('button', name='Sign In')`
* **Tabla Facturas:** `page.locator('table[data-testid="invoice-list"]')`

## 3. Script Inquebrantable (Playwright Python)
*Este script bloquea imágenes para ahorrar memoria y usa esperas dinámicas.*

```python
from playwright.sync_api import sync_playwright

def run_rpa_bot():
    with sync_playwright() as p:
        # Lanzar en modo Headless (oculto)
        browser = p.chromium.launch(headless=True)
        
        # Bloquear medios para velocidad
        context = browser.new_context()
        context.route("**/*.{png,jpg,jpeg,webp,svg,css,woff2}", lambda route: route.abort())
        
        page = context.new_page()
        
        try:
            # Ir a la página
            page.goto("https://ejemplo.com/login", wait_until="networkidle")
            
            # Llenar datos (Espera dinámica implícita de Playwright)
            page.get_by_label("Username").fill("admin@test.com")
            page.get_by_label("Password").fill("123456")
            
            # Hacer clic y esperar que la URL cambie (Evita race conditions)
            with page.expect_navigation():
                page.get_by_role("button", name="Log in").click()
                
            print("Login exitoso.")
            
            # Extraer dato (Ejemplo de wait explícito)
            page.wait_for_selector('h1.dashboard-title')
            dato = page.locator('.stat-card-total').inner_text()
            print(f"Dato extraído: {dato}")
            
        except Exception as e:
            # Si falla, tomar un pantallazo para debuggear
            page.screenshot(path="error_rpa.png")
            print(f"Error fatal: Pantallazo guardado. Detalle: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run_rpa_bot()
```

## 4. Instrucciones de Debugging
Si el script falla:
1. Activa `headless=False` temporalmente y pon un `page.pause()` antes del error.
2. Abre Playwright Inspector y verifica si un pop-up bloqueó el botón.
```

## 🚫 Anti-Patrones Estrictos (Reglas de Fuego)
- **`time.sleep()` está vetado:** A menos que sea absolutamente la última opción por un bug de la plataforma objetivo. Usa esperas basadas en estado (eventos, navegación, selectores).
- **No reutilizar contextos:** Iniciar sesión desde cero cada 5 minutos hará que la cuenta sea baneada. Obliga a usar persistencia de contexto (Cookies/Storage) para bots recurrentes.
- **Ignorar el viewport:** Asume siempre un tamaño de ventana estándar (ej. 1920x1080). Si lanzas Playwright sin configurarlo, usa tamaño móvil por defecto y romperá interfaces diseñadas para Desktop.

