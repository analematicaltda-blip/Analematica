# SGA-CD — Análisis de Viabilidad y Clasificación de Integración Android / Flet (PoC-PHI3-R1)

**Fecha:** 27 de Octubre de 2026
**Componente:** `SGA-CD-APK.git/`

---

## 1. Clasificación Transparente del Estado de las Pruebas

Para evitar interpretaciones ambiguas, se desglosa el estado real de cada nivel de evaluación:

| Nivel de Evaluación | Estado de Ejecución | Detalle de la Evidencia |
| :--- | :--- | :--- |
| **A. Viabilidad Teórica según Documentación** | **VERIFICADO** | Basado en la especificación oficial de Microsoft `onnxruntime-genai-android` y soporte ARM64. |
| **B. Inferencia Aislada en Servidor/Escritorio (Linux x86_64)** | **REPRODUCIDO CON ÉXITO** | Inferencia 100% offline completada (7/7 prompts) a ~6.5 tok/s con 3.17-3.71 GB RAM. |
| **C. Prueba en Dispositivo Android Físico / Emulador** | **NO EJECUTADO (PENDIENTE)** | Requiere dispositivo físico con Android NDK y >=8 GB RAM. Sin emulador ARM64 en el sandbox. |
| **D. Integración Funcional en la App Flet de Producción** | **NO EJECUTADO (BLOQUEADO)** | Preservada la aplicación `SGA-CD-APK.git/` sin modificaciones en producción conforme a la directriz. |

---

## 2. Requerimientos de Hardware en Dispositivos Móviles

- **Espacio en Disco**: 2.62 GB para los pesos cuantizados INT4.
- **Consumo de Memoria RAM**: 3.17 GB en carga inicial; pico de 3.71 GB durante inferencias largas.
- **Restricción de SO Android**:
  - Dispositivos de gama baja (4 GB RAM): **NO VIABLE** (Cierre forzado por el *Low Memory Killer* de Android).
  - Dispositivos de gama media-alta/alta (8 GB a 12 GB RAM): **VIABLE CON RESTRICCIONES** (requiere ejecución en proceso aislado de segundo plano).

---

## 3. Ruta de Integración Arquitectónica Recomendada (Futuro)

1. **Estrategia de Descarga Post-Instalación**: Los pesos de 2.62 GB **no deben incluirse dentro del APK**, sino descargarse como un *On-Demand Asset Pack* tras el primer inicio del usuario.
2. **Puente Nativo Kotlin / AAR**: Integrar la dependencia Maven `com.microsoft.onnxruntime:onnxruntime-genai-android` en la capa nativa Android de Flet para permitir aceleración NPU/GPU mediante NNAPI/QNN/OpenCL.
3. **Mantenimiento de Producción**: La APK de producción no ha sido alterada en esta fase de pruebas aisladas.
