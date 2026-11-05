from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def enterprise_exception_handler(exc, context):
    """
    Fase 3: Enterprise API Contract Layer.
    Normaliza el manejo de errores para cumplir con el contrato estándar.
    """
    # Llamar al manejador por defecto de DRF primero para obtener el error estándar
    response = exception_handler(exc, context)

    if response is not None:
        # Mapear códigos de error de DRF a los códigos estándar de la Fase 3
        status_code = response.status_code
        error_code = "SERVER_ERROR"

        if status_code == status.HTTP_400_BAD_REQUEST:
            error_code = "INVALID_DATA"
        elif status_code == status.HTTP_401_UNAUTHORIZED:
            error_code = "UNAUTHORIZED"
        elif status_code == status.HTTP_403_FORBIDDEN:
            error_code = "FORBIDDEN"
        elif status_code == status.HTTP_404_NOT_FOUND:
            error_code = "NOT_FOUND"

        # Transformar el detalle del error en una lista normalizada de errores
        errors = []
        if isinstance(response.data, dict):
            for field, value in response.data.items():
                msg = value[0] if isinstance(value, list) else value
                errors.append({
                    "code": error_code,
                    "field": field if field != 'detail' else None,
                    "message": msg
                })
        else:
            errors.append({
                "code": error_code,
                "message": str(response.data)
            })

        # Sobrescribir data con la estructura que el Renderer usará
        response.data = {
            "errors": errors
        }

    return response
