#!/usr/bin/env bash
set -euo pipefail

# Resuelve la ubicación del script para permitir ejecución desde cualquier directorio de trabajo
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/weights"
CHECKSUM_FILE="$SCRIPT_DIR/checksums.txt"
BASE_URL="https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-onnx/resolve/main/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4"

mkdir -p "$TARGET_DIR"

FILES=(
    "added_tokens.json"
    "config.json"
    "configuration_phi3.py"
    "genai_config.json"
    "phi3-mini-4k-instruct-cpu-int4-rtn-block-32-acc-level-4.onnx"
    "phi3-mini-4k-instruct-cpu-int4-rtn-block-32-acc-level-4.onnx.data"
    "special_tokens_map.json"
    "tokenizer.json"
    "tokenizer.model"
    "tokenizer_config.json"
)

# Modo verificación offline
if [ "${1:-}" = "--verify" ]; then
    echo "=== Verificando integridad de checksums (Rutas Relativas) ==="
    cd "$SCRIPT_DIR"
    if sha256sum -c "$CHECKSUM_FILE"; then
        echo "✅ Todos los archivos pasaron la verificación de integridad SHA-256."
        exit 0
    else
        echo "❌ Error de integridad en los archivos del modelo."
        exit 1
    fi
fi

echo "=== Descargando pesos y configuración de Phi-3 Mini (ONNX CPU INT4) ==="
echo "Directorio destino: $TARGET_DIR"

for file in "${FILES[@]}"; do
    if [ -f "$TARGET_DIR/$file" ] && [ -s "$TARGET_DIR/$file" ]; then
        echo "Archivo $file ya existe localmente. Omitiendo re-descarga..."
    else
        echo "Descargando $file..."
        curl -L -s --show-error --output "$TARGET_DIR/$file" "$BASE_URL/$file"
    fi
done

echo "=== Generando checksums SHA-256 con rutas relativas ==="
cd "$SCRIPT_DIR"
> "$CHECKSUM_FILE"

for file in "${FILES[@]}"; do
    if [ -f "weights/$file" ]; then
        sha256sum "weights/$file" >> "$CHECKSUM_FILE"
    fi
done

echo "Hashes guardados exitosamente en $CHECKSUM_FILE"
echo "Ejecutando verificación offline para validar el archivo de checksums recién generado..."
sha256sum -c "$CHECKSUM_FILE"
