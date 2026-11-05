import logging
logger = logging.getLogger(__name__)
class SargentoPerfil:
    @staticmethod
    def actualizar_datos_base(perfil_id, data):
        logger.info(f"SARGENTO: Actualizando perfil {perfil_id}")
