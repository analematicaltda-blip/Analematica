# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/tenientes/validacion_prestador_teniente.py
import logging
from apps.sarita_agents.agents.teniente_template import TenienteTemplate

logger = logging.getLogger(__name__)

class TenienteValidacionPrestador(TenienteTemplate):
    """
    Teniente responsable de validar los datos básicos de un nuevo prestador.
    """
    def perform_action(self, parametros: dict) -> dict:
        """
        Realiza una validación simple de los datos del prestador.
        """
        logger.info(f"TENIENTE (ValidacionPrestador): Validando datos -> {parametros}")

        nombre = parametros.get("nombre")
        email = parametros.get("email")

        if not nombre or not email:
            raise ValueError("El 'nombre' y el 'email' del prestador son campos obligatorios.")

        if "@" not in email:
            raise ValueError("El formato del 'email' no es válido.")

        logger.info(f"TENIENTE (ValidacionPrestador): Los datos básicos son válidos.")
        return {"status": "SUCCESS", "message": "Datos básicos validados correctamente."}
