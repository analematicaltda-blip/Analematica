import base64
import logging
from celery import shared_task, chain

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from ..models import DocumentVersion
from ..services.crypto_service import CryptoService
from ..services.file_service import StorageCoordinator

logger = logging.getLogger(__name__)

# ==============================================================================
# TAREA PRINCIPAL (ORQUESTADOR DEL FLUJO)
# ==============================================================================
@shared_task(name="start_file_processing_flow")
def start_file_processing_flow(version_id: int, file_content_b64: str):
    """
    Orquesta la cadena de tareas de procesamiento para un nuevo archivo.
    """
    logger.info(f"Initiating file processing pipeline for DocumentVersion ID: {version_id}")

    processing_pipeline = chain(
        hash_and_encrypt_task.s(version_id, file_content_b64),
        upload_task.s(),
        # prepare_for_notarization_task.s() # Se añadirá más adelante
    )

    processing_pipeline.apply_async()

# ==============================================================================
# TAREAS INDIVIDUALES DEL PIPELINE
# ==============================================================================
@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def hash_and_encrypt_task(self, version_id: int, file_content_b64: str) -> tuple:
    """
    Tarea #1 del pipeline: Calcula el hash y cifra el archivo.
    """
    try:
        # ... (el resto de la función se mantiene igual, se omite por brevedad)
        with transaction.atomic():
            version = DocumentVersion.objects.select_for_update().get(id=version_id)
            if version.status != DocumentVersion.ProcessingStatus.PENDING_UPLOAD:
                logger.warning(f"Skipping hash_and_encrypt for Version {version_id}, status is already '{version.status}'.")
                return (version_id, None)

        file_content = base64.b64decode(file_content_b64)
        crypto_service = CryptoService()
        file_hash = crypto_service.calculate_hash(file_content)
        encryption_key = crypto_service.derive_company_key(version.document.company)
        encrypted_content = crypto_service.encrypt(file_content, encryption_key)

        version.file_hash_sha256 = file_hash
        version.save(update_fields=['file_hash_sha256'])

        logger.info(f"Successfully hashed and encrypted Version ID: {version_id}.")
        encrypted_content_b64 = base64.b64encode(encrypted_content).decode('utf-8')
        return (version_id, encrypted_content_b64)

    except ObjectDoesNotExist:
        logger.error(f"Version ID {version_id} not found in hash_and_encrypt_task. Aborting pipeline.")
    except Exception as exc:
        logger.exception(f"Error in hash_and_encrypt_task for Version {version_id}. Attempt {self.request.retries + 1}.")
        raise exc

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def upload_task(self, prev_task_result: tuple) -> int:
    """
    Tarea #2 del pipeline: Sube el contenido cifrado al almacenamiento en la nube.
    """
    version_id, encrypted_content_b64 = prev_task_result
    if not encrypted_content_b64:
        logger.warning(f"Skipping upload for Version {version_id} as previous task returned no content.")
        return version_id

    try:
        version = DocumentVersion.objects.get(id=version_id)
        encrypted_content = base64.b64decode(encrypted_content_b64)
        storage_coordinator = StorageCoordinator()

        external_id = storage_coordinator.upload(encrypted_content, version)

        version.external_file_id = external_id
        version.save(update_fields=['external_file_id'])

        logger.info(f"Successfully uploaded Version ID: {version_id}. External ID: {external_id}")
        return version_id

    except ObjectDoesNotExist:
        logger.error(f"Version ID {version_id} not found in upload_task. Aborting pipeline.")
    except Exception as exc:
        logger.exception(f"Error in upload_task for Version {version_id}. Attempt {self.request.retries + 1}.")
        raise exc

@shared_task(bind=True)
def prepare_for_notarization_task(self, version_id: int) -> str:
    """
    Tarea final del pipeline de subida. Marca la versión como lista para notarización.
    """
    try:
        version = DocumentVersion.objects.get(id=version_id)
        if version.file_hash_sha256 and version.external_file_id:
            version.status = DocumentVersion.ProcessingStatus.PENDING_CONFIRMATION
            version.save(update_fields=['status'])
            logger.info(f"Version {version_id} is now ready for notarization.")
            return f"Success: Version {version_id} queued for notarization."
        else:
            logger.error(f"Cannot queue Version {version_id}, previous step failed.")
            return f"Failed: Version {version_id} could not be queued."
    except ObjectDoesNotExist:
        logger.error(f"Version ID {version_id} not found in prepare_for_notarization_task.")
        return f"Failed: Version {version_id} not found."
