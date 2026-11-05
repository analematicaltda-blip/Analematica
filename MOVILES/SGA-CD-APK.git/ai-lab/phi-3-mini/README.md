# SGA-CD — PoC Phi-3 Mini (ONNX Runtime GenAI)

## 1. Objetivo y Alcance
Este laboratorio aislado (`SGA-CD-APK.git/ai-lab/phi-3-mini/`) tiene como finalidad validar la viabilidad técnica y operativa de descargar, verificar la integridad y ejecutar inferencias locales offline del modelo **Phi-3 Mini 4K Instruct (ONNX INT4)** en el entorno de servidor/escritorio, identificando los requerimientos de integración futura para la APK Android basada en Flet.

## 2. Variante Seleccionada
- **Repositorio HF**: `https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-onnx`
- **Subdirectorio**: `cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4`
- **Tamaño Total**: ~2.72 GB (2,725,565,620 bytes)
- **Licencia**: MIT License (Microsoft Corporation)

## 3. Estrategia de Almacenamiento e Aislamiento
- El código de prueba, scripts de descarga, configuración y reportes de ejecución residen bajo control de versiones Git en `SGA-CD-APK.git/ai-lab/phi-3-mini/`.
- Los pesos binarios del modelo se descargan exclusivamente en `weights/` (o un directorio local fuera de Git) y están explícitamente ignorados mediante `.gitignore` para evitar contaminar el historial o los repositorios remotos.

## 4. Instrucciones de Uso
1. Ejecutar descarga e integridad:
   ```bash
   bash SGA-CD-APK.git/ai-lab/phi-3-mini/download-model.sh
   ```
2. Instalar dependencias de prueba:
   ```bash
   pip install -r SGA-CD-APK.git/ai-lab/phi-3-mini/requirements-test.txt
   ```
3. Ejecutar prueba de inferencia offline:
   ```bash
   python3 SGA-CD-APK.git/ai-lab/phi-3-mini/test_inference.py
   ```
