import logging
logger = logging.getLogger(__name__)
class DocumentoService:
    @staticmethod
    def log_document_action(doc_id, action):
        logger.info(f"Documento {doc_id}: {action}")
