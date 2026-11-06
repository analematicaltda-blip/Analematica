# backend/apps/prestadores/mi_negocio/gestion_archivistica/sargentos.py
import logging
import hashlib
from django.utils import timezone
from .models import Document, DocumentVersion
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)

class SargentoArchivistico:
    """
    Ejecutor de acciones mínimas e indivisibles del dominio archivístico.
    """

    @staticmethod
    def generar_hash_sha256(content: bytes) -> str:
        hash_val = hashlib.sha256(content).hexdigest()
        logger.info(f"SARGENTO: Hash SHA-256 generado: {hash_val[:16]}...")
        return hash_val

    @staticmethod
    def registrar_acceso(document_id, user_id, action="READ"):
        from api.models import CustomUser
        try:
            user = CustomUser.objects.get(id=user_id)
            AuditLog.objects.create(
                user=user,
                username=user.username,
                action=f"DOCUMENT_ACCESS_{action}",
                details={"document_id": str(document_id)}
            )
            logger.info(f"SARGENTO: Acceso {action} registrado para documento {document_id} por usuario {user.username}.")
            return True
        except Exception as e:
            logger.error(f"SARGENTO: Error al registrar acceso archivístico: {e}")
            return False

    @staticmethod
    def aplicar_sello_temporal(version_id):
        try:
            version = DocumentVersion.objects.get(id=version_id)
            # Simulación de sellado de tiempo institucional
            version.status = DocumentVersion.ProcessingStatus.VERIFIED
            version.save()
            logger.info(f"SARGENTO: Sello temporal institucional aplicado a versión {version_id}.")
            return True
        except Exception as e:
            logger.error(f"SARGENTO: Error al aplicar sello temporal: {e}")
            return False

    @staticmethod
    def archivar_documento(parametros: dict):
        from .archiving import ArchivingService
        try:
            doc_version = ArchivingService.archive_document(**parametros)
            logger.info(f"SARGENTO: Documento archivado exitosamente. Versión ID: {doc_version.id}")
            return str(doc_version.id)
        except Exception as e:
            logger.error(f"SARGENTO: Error al archivar documento: {e}")
            return None

    @staticmethod
    def validar_integridad(version_id, current_content: bytes):
        try:
            version = DocumentVersion.objects.get(id=version_id)
            current_hash = hashlib.sha256(current_content).hexdigest()
            if current_hash == version.file_hash_sha256:
                logger.info(f"SARGENTO: Integridad verificada para versión {version_id}.")
                return True
            else:
                logger.warning(f"SARGENTO: ¡VIOLACIÓN DE INTEGRIDAD! en versión {version_id}.")
                version.status = DocumentVersion.ProcessingStatus.COMPROMISED
                version.save()
                return False
        except Exception as e:
            logger.error(f"SARGENTO: Error en validación de integridad: {e}")
            return False
