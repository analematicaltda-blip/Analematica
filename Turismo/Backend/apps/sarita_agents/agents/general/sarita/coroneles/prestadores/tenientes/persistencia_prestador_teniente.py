# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/tenientes/persistencia_prestador_teniente.py
import logging
from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from apps.sarita_agents.models import Prestador

logger = logging.getLogger(__name__)

class TenientePersistenciaPrestador(TenienteTemplate):
    """
    Teniente responsable de persistir un nuevo prestador en la base de datos.
    """
    def perform_action(self, parametros: dict) -> dict:
        """
        Crea un nuevo registro de Prestador en la base de datos.
        """
        logger.info(f"TENIENTE (PersistenciaPrestador): Creando registro para -> {parametros}")

        nombre = parametros.get("nombre")
        email = parametros.get("email")

        # Se asume que los datos ya fueron validados por el teniente anterior.

        try:
            prestador = Prestador.objects.create(
                nombre=nombre,
                email=email,
                activo=True # Activamos el prestador como parte del proceso.
            )

            logger.info(f"TENIENTE (PersistenciaPrestador): Prestador creado con ID {prestador.id}")
            return {
                "status": "SUCCESS",
                "message": "Prestador creado exitosamente.",
                "prestador_id": str(prestador.id)
            }
        except Exception as e:
            # Captura posibles errores de unicidad de email u otros errores de BD.
            raise ValueError(f"Error de base de datos al crear el prestador: {str(e)}")
