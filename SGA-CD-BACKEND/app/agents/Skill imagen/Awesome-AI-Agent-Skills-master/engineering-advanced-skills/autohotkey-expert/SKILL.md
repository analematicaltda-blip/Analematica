---
name: autohotkey-expert
description: >
  Expert AutoHotkey (AHK v1 and v2) developer. Use this skill whenever the user asks about
  AutoHotkey, AHK scripts, hotkeys, hotstrings, window automation, app launchers,
  macro creation, GUI dialogs, SendInput, WinMove, Run, ToolTip, SoundPlay, WinActivate,
  text expansion, keyboard remapping, mouse automation, or any Windows automation via AHK.
  Triggers on: "make an AHK script", "autohotkey shortcut for X", "hotkey to open X",
  "remap this key", "automate this in Windows", "ahk hotstring", "window snapping script",
  "AHK GUI", "reload my script", or any request implying AutoHotkey work.
  Context: user runs AHK v1, script at Startup folder, has Chrome/Brave/OperaGX,
  Ableton Live 11, Spotify, Stable Diffusion Forge, ComfyUI, and various web shortcuts.
---

# AutoHotkey Expert Skill

Eres un experto en AutoHotkey (v1 y v2). Tu trabajo es producir scripts **correctos, listos para pegar y usar** — sin errores de sintaxis y sin relleno genérico.

**Contexto del usuario:**
- Usa **AHK v1** (archivo principal: `misscripts.ahk` en Startup)
- Windows 11, RTX 4060, múltiples monitores
- Apps: Chrome, Brave, Opera GX, Ableton 11, Spotify, Stable Diffusion, ComfyUI, VS Code
- Shortcuts activos: `^#` (Ctrl+Win+letra), `^!` (Ctrl+Alt+letra), `#!` (Win+Alt+letra)

---

## Sintaxis Fundamental AHK v1

### Hotkeys — Modificadores
```
^   → Ctrl
!   → Alt
#   → Win (tecla Windows)
+   → Shift
*   → cualquier modificador adicional
~   → no suprimir la tecla original
$   → forzar uso de hook
```

### Combinaciones más comunes
```ahk
^#c::           ; Ctrl + Win + C
^!f::           ; Ctrl + Alt + F
#!t::           ; Win + Alt + T
+!g::           ; Shift + Alt + G
^+!MButton::    ; Ctrl + Shift + Alt + Botón central
```

### Estructura básica
```ahk
#NoEnv
#SingleInstance Force
SendMode Input
SetWorkingDir %A_ScriptDir%

F12::Reload      ; Recarga el script

^#c::
Run, "C:\Program Files\Google\Chrome\Application\chrome.exe"
Return
```

---

## Comandos Esenciales

### Lanzar aplicaciones
```ahk
; Por ejecutable
Run, notepad.exe

; Por ruta completa con espacios → comillas
Run, "C:\Program Files\App\app.exe"

; Por acceso directo (.lnk)
Run, "C:\Users\walva\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\App.lnk"

; Abrir URL directamente
Run, https://google.com

; Con directorio de trabajo
Run, "C:\app\app.exe", C:\app

; Con permisos de administrador
Run, *RunAs "C:\app\app.exe"
```

### Control de ventanas
```ahk
; Mover y redimensionar ventana activa
WinMove, A,, X, Y, Ancho, Alto

; Snapping mitad izquierda
#!Left::
WinMove, A,, 0, 0, A_ScreenWidth/2, A_ScreenHeight
Return

; Snapping mitad derecha
#!Right::
WinMove, A,, A_ScreenWidth/2, 0, A_ScreenWidth/2, A_ScreenHeight
Return

; Pantalla completa (sin barra de tareas)
^#Up::
WinMove, A,, 0, 0, A_ScreenWidth, A_ScreenHeight
Return

; Activar ventana por título
WinActivate, ahk_class Notepad
WinActivate, Nombre de la Ventana

; Minimizar / Maximizar / Restaurar
WinMinimize, A
WinMaximize, A
WinRestore, A

; Cerrar ventana
WinClose, A
WinKill, A   ; forzar cierre
```

### Enviar teclas y texto
```ahk
; Teclas especiales
Send, {Enter}
Send, {Tab}
Send, {Delete}
Send, {F5}
Send, {Home}
Send, {End}
Send, {PgUp}
Send, {PgDn}
Send, {Up}
Send, {Down}

; Combinaciones
Send, ^c         ; Ctrl+C (copiar)
Send, ^v         ; Ctrl+V (pegar)
Send, ^a         ; Ctrl+A (seleccionar todo)
Send, ^z         ; Ctrl+Z (deshacer)
Send, !{F4}      ; Alt+F4

; Texto literal (respeta caracteres especiales)
SendRaw, Este texto se envía tal cual: {sin} ^interpretar

; SendInput es más rápido y confiable
SendInput, {Ctrl Down}c{Ctrl Up}

; Escribir texto largo
Send, Hola mundo, este es un mensaje largo
```

### Mouse
```ahk
Click                    ; clic izquierdo en posición actual
Click, 500, 300          ; clic izquierdo en coordenadas absolutas
Click right              ; clic derecho
Click, 500, 300, 2       ; doble clic

; Mover sin clicar
MouseMove, 500, 300

; Clic y arrastrar
MouseClickDrag, Left, 100, 100, 500, 500

; Rueda del mouse
Send {WheelUp 3}
Send {WheelDown 3}

; CoordMode: Screen = coordenadas absolutas de pantalla
CoordMode, Mouse, Screen
Click, 1920, 500
```

### Clipboard (portapapeles)
```ahk
; Copiar texto al clipboard
clipboard := "Texto que quiero en el portapapeles"

; Leer desde clipboard
MsgBox, % clipboard

; Copiar selección actual
Send, ^c
ClipWait, 1   ; esperar hasta 1 segundo
texto := clipboard
```

---

## Hotstrings (Expansión de Texto)

```ahk
; Sintaxis básica: ::abreviatura::expansión
::hola::Hola, ¿cómo estás?

; No requiere espacio ni puntuación para activarse (*)
:*:grr::Gracias por tu tiempo

; SendRaw para caracteres especiales
::fiv1::
SendRaw Este texto puede tener {llaves} y ^símbolos sin problemas.
Return

; Con opción * (sin necesidad de terminator) y C (case-sensitive)
:*C:NPE::NullPointerException

; Ejemplo del usuario — snippets de trabajo
::traing::
Send traduce a inglés
Return

::traesp::
Send traduce a español
Return
```

---

## Control de Flujo

```ahk
; Variables
miVariable := "valor"
contador := 0

; If / Else
if (contador > 5) {
    MsgBox, Mayor que 5
} else {
    MsgBox, Menor o igual
}

; Forma clásica AHK v1
if contador > 5
    MsgBox, Mayor
else
    MsgBox, Menor

; Loop básico
Loop, 5 {
    Send, {Tab}
    Sleep, 100
}

; Loop infinito (usar con cuidado)
Loop {
    Sleep, 1000
    if (condicion)
        Break
}

; While
while (activo) {
    ; hacer algo
    Sleep, 500
}
```

---

## Condicionales de Ventana con #IfWinActive

```ahk
; Solo funciona cuando Chrome está activo
#IfWinActive, ahk_exe chrome.exe
^d::Send, ^+d    ; Ctrl+D → Ctrl+Shift+D solo en Chrome

; Solo cuando VS Code está activo
#IfWinActive, ahk_exe Code.exe
^Enter::Send, {F5}

; Restaurar comportamiento global
#IfWinActive
```

---

## Diálogos y Feedback Visual

```ahk
; Mensaje simple
MsgBox, Hola mundo

; Con título y botones
MsgBox, 4, Confirmar, ¿Deseas continuar?
IfMsgBox, Yes
    MsgBox, Elegiste Sí
    
; InputBox — pedir texto al usuario
InputBox, resultado, Título, Escribe algo:
MsgBox, Escribiste: %resultado%

; ToolTip — aparece cerca del cursor, sin interrumpir
ToolTip, Script ejecutado correctamente
Sleep, 2000
ToolTip   ; ocultar

; Notificación en bandeja del sistema
TrayTip, Mi Script, Acción completada, 3
```

---

## Funciones y Subrutinas

```ahk
; Subrutina (Gosub)
^!f::
Gosub, AbrirChrome
Return

AbrirChrome:
    Run, "C:\Program Files\Google\Chrome\Application\chrome.exe"
Return

; Función
AbrirApp(ruta) {
    if FileExist(ruta)
        Run, %ruta%
    else
        MsgBox, No encontré: %ruta%
}

; Llamar función
^!c::
AbrirApp("C:\Program Files\Google\Chrome\Application\chrome.exe")
Return
```

---

## Patrones de Uso Frecuente

### Snapping de ventanas (4 cuadrantes)
```ahk
#!Numpad7::  ; Win+Alt+7 → cuadrante superior izquierdo
WinMove, A,, 0, 0, A_ScreenWidth/2, A_ScreenHeight/2
Return

#!Numpad9::  ; Win+Alt+9 → cuadrante superior derecho
WinMove, A,, A_ScreenWidth/2, 0, A_ScreenWidth/2, A_ScreenHeight/2
Return

#!Numpad1::  ; Win+Alt+1 → cuadrante inferior izquierdo
WinMove, A,, 0, A_ScreenHeight/2, A_ScreenWidth/2, A_ScreenHeight/2
Return

#!Numpad3::  ; Win+Alt+3 → cuadrante inferior derecho
WinMove, A,, A_ScreenWidth/2, A_ScreenHeight/2, A_ScreenWidth/2, A_ScreenHeight/2
Return
```

### Lanzador de app con foco — si ya está abierta, la activa; si no, la abre
```ahk
^#c::
if WinExist("ahk_exe chrome.exe") {
    WinActivate, ahk_exe chrome.exe
} else {
    Run, "C:\Program Files\Google\Chrome\Application\chrome.exe"
}
Return
```

### Esperar que una app cargue antes de interactuar
```ahk
^#s::
Run, "D:\IA\ComfyUI\ComfyUI_windows_portable\ComfyUI_windows_portable_nvidia\run_nvidia_gpu.bat"
WinWait, ComfyUI,, 30   ; esperar hasta 30s
WinActivate
Return
```

### Macro de clic con delays (para flujos de UI)
```ahk
^+d::
CoordMode, Mouse, Screen
Click, 1801, 1054
Sleep, 500
Click, 1708, 830
Sleep, 300
Click, 1655, 895
Return
```

### Alternar entre dos estados
```ahk
global toggleActivo := false

^!q::
toggleActivo := !toggleActivo
if (toggleActivo)
    ToolTip, Modo ON
else
    ToolTip, Modo OFF
Sleep, 1500
ToolTip
Return
```

---

## Compatibilidad con AHK v1 vs v2

| Concepto | AHK v1 | AHK v2 |
|---|---|---|
| Variables en strings | `%variable%` | `%variable%` o `var` directo |
| Asignación | `var = valor` o `:=` | `:=` siempre |
| Run | `Run, programa` | `Run("programa")` |
| MsgBox | `MsgBox, texto` | `MsgBox("texto")` |
| Send | igual | igual |
| `#NoEnv` | recomendado | no existe |
| `#SingleInstance` | `Force` | `"Force"` |

**El usuario usa v1** — siempre generar sintaxis v1 salvo que pida v2 explícitamente.

---

## Recargar y Depurar

```ahk
F12::Reload          ; Recargar script completo (hotkey del usuario)
^F12::ExitApp        ; Salir del script

; Mostrar variables para debug
MsgBox, % "Valor: " . miVariable

; Log a archivo
FileAppend, %A_Now% - Evento registrado`n, C:\logs\ahk.log
```

---

## Estructura Recomendada para Scripts Grandes

```ahk
#NoEnv
#SingleInstance Force
SendMode Input
SetWorkingDir %A_ScriptDir%

; ===== RECARGA =====
F12::Reload

; ===== LANZADORES DE APPS =====
^#c::Run, "C:\Program Files\Google\Chrome\Application\chrome.exe"
^#b::Run, "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
^#n::Run, notepad.exe

; ===== WINDOW MANAGEMENT =====
#!Left::WinMove, A,, 0, 0, A_ScreenWidth/2, A_ScreenHeight
#!Right::WinMove, A,, A_ScreenWidth/2, 0, A_ScreenWidth/2, A_ScreenHeight

; ===== HOTSTRINGS / SNIPPETS =====
::saludar::Hola, ¿cómo estás?

; ===== MACROS COMPLEJAS =====
^+m::
; lógica aquí
Return
```

---

## Formato de Respuesta

Al responder una solicitud AHK, estructurar así:

1. **Código listo para pegar** — bloque AHK completo y funcional
2. **Hotkey usada** — explicar la combinación de teclas elegida y por qué no colisiona con shortcuts existentes del usuario
3. **Notas de instalación** — si hay que agregar al `misscripts.ahk` existente o crear script separado
4. **Variantes opcionales** — alternativas si el usuario quiere ajustar comportamiento

---

## Checklist Antes de Generar Código

- [ ] ¿Sintaxis AHK v1 (no v2)?
- [ ] ¿El hotkey elegido no colisiona con los activos del usuario (`^#`, `^!`, `#!`, `+!`)?
- [ ] ¿Rutas de archivo con comillas si tienen espacios?
- [ ] ¿`Return` al final de cada hotkey/subrutina?
- [ ] ¿`Sleep` adecuado si hay secuencias de UI con clics?
- [ ] ¿`#IfWinActive` si el atajo debe ser específico a una app?
