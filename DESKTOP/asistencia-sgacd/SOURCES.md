# Fuentes investigadas (2026-11-06)

| Proyecto | Uso y decisión |
|---|---|
| [Open Duet](https://github.com/Anil-matcha/open-duet) | Copia completa de 1.172 archivos, Apache-2.0, commit `6ec8e0c8360c8f8b6cc282b9d6ec5f563d351b56`; manifiesto de hashes incluido. Perfil de planificación separado; backend upstream requiere Python 3.14+. |
| [agent-desktop](https://github.com/vercel-labs/agent-desktop) | Copia existente completa en `DESKTOP/agent-desktop`, conector existente en `DESKTOP/agent-desktop-sgacd`; su runtime es local al host. |
| [Appium UiAutomator2](https://github.com/appium/appium-uiautomator2-driver) | Adaptador nativo Android seleccionado. HEAD consultado `262c6f3a0c43f84f5087873e1ddaade2a33a1526` ya requiere Appium 4; pin compatible seleccionado `8.7.3` con Appium `3.9.0`. Android 8/API 26 o posterior según driver. Apache-2.0. |
| [Appium XCUITest](https://github.com/appium/appium-xcuitest-driver) | Adaptador iOS seleccionado. HEAD consultado `cd2efd3fa4e58cf50a2b37dc38b2a2de5de9a635` requiere Appium 4; pin compatible seleccionado `12.22.8` con Appium `3.9.0`. Mac/Xcode y firma WDA para iPhone real. Apache-2.0. |
| [Mobile MCP](https://github.com/mobile-next/mobile-mcp) | Evaluado en `57efc27d96971f96caba69b62665fa057ebc65ac`. No se expone su servidor genérico directamente al modelo: los permisos se verifican en nuestro ejecutor limitado. |
| [Maestro](https://github.com/mobile-dev-inc/maestro) | Evaluado en `aaa248d7fd4ca4924444dc027af9c7a62a9be348`; su README consultado excluye iOS físico, por lo que se prefirió Appium para ese objetivo. |

Appium/driver son dependencias que instala el operador en el host autorizado, no nuevas copias vendorizadas. Playwright y fast-xml-parser están fijados con lockfile. Se mantienen licencias de los proyectos copiados; una copia no transfiere titularidad ni elimina obligaciones de licencia.
