# DIRECTRIZ TÉCNICA: IA LOCAL Y RESILIENCIA TOTAL (HYBRID EDGE AI)

Esta directriz establece el protocolo para garantizar que SARITA funcione al 100% en zonas sin cobertura mediante inteligencia artificial local y sincronización diferida.

## 1. DETECCIÓN AUTOMÁTICA DE CAPACIDAD (HARDWARE INTELLIGENCE)
- **Desktop:** Al instalar, el sistema ejecuta `getHardwareSpecs` para identificar la RAM y CPU disponibles.
- **Mobile:** El APK utiliza `getMobileIntelligence` para categorizar el dispositivo.
- **Asignación de Modelo:**
  - **Alta Gama (>=16GB RAM):** llama3:8b.
  - **Media Gama (>=8GB RAM):** mistral o phi3.
  - **Baja Gama (<8GB RAM):** tinyllama o phi3-mini.

## 2. PROTOCOLO OLLAMA (INTEGRACIÓN LOCAL)
- El instalador de SARITA debe verificar o descargar la instancia de **Ollama** en el equipo local.
- Se pre-descarga el LM (Model) compatible determinado por el paso de detección.
- El servicio IA del SDK se configura mediante `setLocalConfig` para apuntar al puerto local `11434`.

## 3. FLUJO DE INTELIGENCIA HÍBRIDA (REMOTE-FIRST / LOCAL-FALLBACK)
1. El usuario envía una orden o consulta.
2. El SDK intenta contactar al **General SARITA** en el Backend central.
3. Si hay falla de red (timeout), se activa automáticamente el **Motor Híbrido (HybridAIEngine)**.
4. El LM local procesa la orden y genera una respuesta inmediata al humano.
5. La orden procesada se marca con el tag `LOCAL_IA_PROCESSED`.

## 4. MOTOR DE SINCRONIZACIÓN (SYNC SARGENTO)
- Toda acción procesada localmente se encola en la base de datos **SQLite**.
- Al detectar el regreso de la conexión (vía `flush`), el sistema envía el lote de acciones al Backend.
- El Backend valida los hashes locales y actualiza el Libro Mayor y los registros operativos con la marca de tiempo original.

## 5. SEGURIDAD Y PRIVACIDAD LOCAL
- Los datos procesados localmente por Ollama nunca salen del dispositivo hasta la sincronización cifrada.
- Se mantiene el estándar de inmutabilidad SHA-256 incluso en modo offline.
