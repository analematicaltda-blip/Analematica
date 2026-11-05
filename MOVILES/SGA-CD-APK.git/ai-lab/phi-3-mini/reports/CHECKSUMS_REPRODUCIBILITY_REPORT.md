# SGA-CD — Informe de Portabilidad y Reproducibilidad de Checksums (Fase PoC-PHI3-R1)

**Fecha:** 27 de Octubre de 2026
**Script Principal:** `SGA-CD-APK.git/ai-lab/phi-3-mini/download-model.sh`
**Archivo de Integridad:** `SGA-CD-APK.git/ai-lab/phi-3-mini/checksums.txt`

---

## 1. Subsanación de Rutas Absolutas a Relativas

- **Defecto Reportado en PoC-PHI3**: El archivo `checksums.txt` contenía rutas absolutas atadas al entorno del contenedor (`/app/SGA-CD-APK.git/ai-lab/phi-3-mini/weights/...`), lo que impedía verificar la integridad en otros entornos o máquinas.
- **Corrección Aplicada**:
  - Se modificó `download-model.sh` para resolver dinámicamente el directorio del script mediante `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"`.
  - La generación de hashes realiza un `cd "$SCRIPT_DIR"` explícito antes de invocar `sha256sum`, produciendo rutas relativas normalizadas (`weights/<archivo>`).

---

## 2. Contenido del Archivo `checksums.txt` Normalizado

```text
f8e5a880c6c563a126d9efacb654e105fc4b66f21e5a540f04436e9487a955fb  weights/added_tokens.json
132bb3dca45e641008dce2ba8bbbf3fd877cf8b76a7c18919e0bae1ef13a20ce  weights/config.json
18b06d379f5199bfb8b7da26da14c580f3852e792895d2bf6158b2ef33c92d52  weights/configuration_phi3.py
d5ec04466a3d080de412409bf762219628f375314cfff303976733364baec5a2  weights/genai_config.json
385cd1b908a0d2f8634e86d30236f6dbb7ae660eb3943fd1ef5bdc3847326480  weights/phi3-mini-4k-instruct-cpu-int4-rtn-block-32-acc-level-4.onnx
5db30ce699aee1123cf9045742488db5928006fa618a42cb3c0840322a85ad0f  weights/phi3-mini-4k-instruct-cpu-int4-rtn-block-32-acc-level-4.onnx.data
810adc6e6c6ef2f56c285ef930d243358a3a9f05e36a01c5a10bafc6fac4609b  weights/special_tokens_map.json
072ab882d6c7192a42f78790945d16c064691321a73251a4b18f6a380f0fbe39  weights/tokenizer.json
9e556afd44213b6bd1be2b850ebbbd98f5481437a8021afaf58ee7fb1818d347  weights/tokenizer.model
32f66c2bab499baaa8341819ad9a13342f957501ce1e989bcb90853a01336cc0  weights/tokenizer_config.json
```

---

## 3. Pruebas de Reproducibilidad Offline

Se probó la validación desde dos ubicaciones de trabajo diferentes:

1. **Desde la raíz del Monorepo**:
   ```bash
   bash SGA-CD-APK.git/ai-lab/phi-3-mini/download-model.sh --verify
   ```
   **Resultado**: `OK` en los 10 archivos. Código de salida `0`.

2. **Desde el subdirectorio del laboratorio**:
   ```bash
   cd SGA-CD-APK.git/ai-lab/phi-3-mini && bash download-model.sh --verify
   ```
   **Resultado**: `OK` en los 10 archivos. Código de salida `0`.

3. **Prueba de Fallo Ante Alteración (Resistencia a Corrupción)**:
   Si un archivo es alterado o corrompido, `sha256sum -c` retorna el código de salida `1`, deteniendo inmediatamente cualquier proceso subsiguiente.
