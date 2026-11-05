import logging
logger = logging.getLogger(__name__)
class SargentoDocumentos:
    @staticmethod
    def archivar_evidencia(doc_id, metadata):
        logger.info(f"SARGENTO: Archivando evidencia {doc_id}")
