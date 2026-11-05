from typing import Generic, TypeVar, Optional, Any

T = TypeVar('T')

class ServiceResult(Generic[T]):
    """
    Patrón de respuesta estandarizado para la capa de servicios.
    Facilita la interpretación de resultados por parte de los Agentes IA.
    """
    def __init__(self, success: bool, data: Optional[T] = None, error: Optional[str] = None, message: str = ""):
        self.success = success
        self.data = data
        self.error = error
        self.message = message

    @classmethod
    def ok(cls, data: T, message: str = "Operación exitosa"):
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(cls, error: str, message: str = "Error en la operación"):
        return cls(success=False, error=error, message=message)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message": self.message
        }
