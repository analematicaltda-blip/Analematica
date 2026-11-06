# Escritorio local para Analemática y SGA-CD

El código completo de Vercel Labs está incorporado en `../agent-desktop`: 3746
entradas versionadas, commit `b43ac4f6e892ef608f8851428613c4009f0e84c7`.
No es un submódulo ni un enlace al repositorio. La licencia Apache 2.0 permite
usarlo, modificarlo y redistribuirlo conservando licencia y avisos; la autoría
original permanece en sus titulares. `upstream.json` registra origen e integridad.
El único enlace simbólico interno, `.claude → .agents`, viene del proyecto original.
La regla de .gitattributes conserva los bytes del origen incluso en Windows.

Esta carpeta contiene el conector de SGA-CD; no modifica las fuentes originales.
No incorpora un LLM. El agente de Codex u otro cliente MCP decide las acciones.

## Instalar en tu computador

Necesitas Node.js 18 o posterior, además de curl y tar. Windows 11 incluye estas
últimas herramientas. No necesitas WSL ni Docker para este conector.
Desde una copia **local** del repositorio, en PowerShell o terminal:

```powershell
node DESKTOP/agent-desktop-sgacd/install.mjs
node DESKTOP/agent-desktop-sgacd/run.mjs doctor
node DESKTOP/agent-desktop-sgacd/run.mjs status
```

El instalador usa el empaquetador copiado del proyecto para descargar el runtime
oficial 1.2.0 de tu sistema y verificar sus checksums. Lo instala solo dentro de
`.runtime`, sin servicios del sistema ni instalación global. Guarda y comprueba
la integridad del ejecutable y sus helpers; `--repair` reinstala explícitamente.
No prueba ni controla aplicaciones durante la instalación.

El proceso opera el equipo donde se ejecuta. Abrirlo en Codespaces opera el
contenedor remoto, no el escritorio de Windows. Para trabajar en tu portátil,
abre la copia local con VS Code/Codex y usa la sesión gráfica de tu usuario.
Las aplicaciones elevadas y escritorios protegidos siguen sujetos al sistema
operativo; instalar este código no concede privilegios administrativos.

## Conectar el agente

VS Code tiene una entrada `sgacd-desktop` en `.vscode/mcp.json`. Instala primero
el runtime y después inicia ese servidor MCP desde VS Code local. El transporte
es stdio: no abre puertos ni publica una API de control remoto.

Para obtener la configuración con la ruta absoluta de tu equipo:

```powershell
node DESKTOP/agent-desktop-sgacd/config.mjs vscode
node DESKTOP/agent-desktop-sgacd/config.mjs codex
```

El segundo comando imprime el bloque para la configuración MCP de Codex. No
modifica tu cuenta ni tus configuraciones privadas automáticamente. Configurar un
servidor en el repositorio no añade herramientas a una sesión de chat ya abierta.

Antes de operar aplicaciones, lee las guías que corresponden al binario instalado:

```powershell
node DESKTOP/agent-desktop-sgacd/run.mjs skills get desktop
node DESKTOP/agent-desktop-sgacd/run.mjs skills get platform
```

Las acciones requieren elementos observados y referencias actuales. Las reglas
de entrega/reintento y los permisos de accesibilidad los aplica agent-desktop;
el conector no añade `--headed`, no cambia permisos ni reintenta acciones.

## Capacidades y límites

Puede observar árboles de accesibilidad, localizar controles, escribir, pulsar,
gestionar ventanas y ofrecer esas operaciones como herramientas MCP. Algunas
aplicaciones no exponen un árbol utilizable. Los permisos y funciones disponibles
se comprueban con `status` en cada equipo.

No automatiza páginas web. Para Meta se mantienen las integraciones oficiales,
OAuth y sesiones autorizadas; esto no concede acceso a la infraestructura interna
de Meta ni elimina restricciones del negocio. Tampoco establece SSH ni conexión
con tu portátil por sí solo. No se añadió un endpoint de control al SaaS.

Los snapshots y sesiones se guardan en `.runtime/state`, aislados mediante
`AGENT_DESKTOP_HOME`. `.runtime` está excluido de Git: no publiques estados,
capturas, portapapeles ni sesiones. HOME/USERPROFILE y credenciales de red se
conservan; no hay acciones gráficas automáticas al arrancar el servidor MCP.

## Modificar o compilar tus fuentes

Para compilar la copia necesitas Rust 1.89 y las herramientas nativas del sistema:

```powershell
cd DESKTOP/agent-desktop
cargo build --release -p agent-desktop
```

No ejecutes `cargo test --workspace`: cada adaptador solo compila en su sistema.
Las instrucciones por plataforma están en el AGENTS.md y CONTRIBUTING.md del origen.
En esta entrega no se compiló Rust: se verificó el runtime oficial precompilado.

## Verificación de la entrega

```powershell
node DESKTOP/agent-desktop-sgacd/verify-source.mjs
node --test DESKTOP/agent-desktop-sgacd/tests/runtime.test.mjs
```

Para incluir pruebas del runtime instalado y su servidor MCP, establece
`SGACD_DESKTOP_TEST_NATIVE=1` en el entorno del proceso de pruebas.

Se comprobaron 81 pruebas originales de empaquetado/distribución y seis del
conector, incluida inicialización MCP y listado de herramientas reales sin
invocarlas. La versión Linux se ejecuta en el entorno de validación; `status`
reporta accesibilidad denegada por ausencia de sesión D-Bus gráfica. No se validó
control de aplicaciones reales ni el runtime Windows/macOS en este entorno.
