import io
import os
from typing import Tuple
from fastapi import HTTPException, status, UploadFile

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

def validate_and_sanitize_image_upload(
    file_bytes: bytes,
    filename: str,
    max_size_bytes: int = MAX_FILE_SIZE_BYTES
) -> Tuple[str, str]:
    """
    Validates uploaded image files by:
    1. Extension whitelist check
    2. File size limit (5MB)
    3. Real Magic Bytes MIME type check (PNG, JPEG, WebP)
    4. Malicious file execution prevention (.php, .sh, .exe, .html disguised)
    Returns sanitized filename and verified extension.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo subido está vacío."
        )

    if len(file_bytes) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamaño máximo permitido de {max_size_bytes // (1024*1024)} MB."
        )

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión de archivo '{ext}' no permitida. Formatos válidos: JPEG, PNG, WebP."
        )

    # Magic Bytes Validation
    # PNG: \x89PNG\r\n\x1a\n
    # JPEG: \xff\xd8\xff
    # WEBP: RIFF....WEBP
    is_png = file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    is_jpeg = file_bytes.startswith(b"\xff\xd8\xff")
    is_webp = file_bytes.startswith(b"RIFF") and b"WEBP" in file_bytes[:16]

    if not (is_png or is_jpeg or is_webp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido real del archivo no corresponde a una imagen válida (Magic Bytes mismatch)."
        )

    # Sanitize filename to prevent directory traversal and executable execution
    import re
    clean_filename = re.sub(r"[^a-zA-Z0-9_-]", "_", os.path.splitext(filename)[0])[:50] + ext

    return clean_filename, ext
