# backend/apps/prestadores/mi_negocio/gestion_archivistica/services.py
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date
from typing import Dict, Any, Union
import io
import hashlib

from .models import ProcessType, Process, DocumentType, Document, DocumentVersion
from apps.companies.models import Company

User = get_user_model()

class ArchivingService:
    @staticmethod
    @transaction.atomic
    def archive_document(
        *,
        company_id: int,
        user_id: int,
        process_type_code: str,
        process_code: str,
        document_type_code: str,
        document_content: Union[bytes, io.BytesIO],
        original_filename: str,
        document_metadata: Dict[str, Any],
        requires_blockchain_notarization: bool = False
    ) -> DocumentVersion:
        """
        Método principal para archivar un nuevo documento.
        """
        try:
            company = Company.objects.get(id=company_id)
            user = User.objects.get(id=user_id)

            # 1. Obtener o crear la taxonomía
            process_type = ProcessType.objects.get(company=company, code=process_type_code)
            process = Process.objects.get(company=company, process_type=process_type, code=process_code)
            doc_type = DocumentType.objects.get(company=company, code=document_type_code)

            # 2. Calcular hash
            content_bytes = document_content.read() if isinstance(document_content, io.BytesIO) else document_content
            file_hash = hashlib.sha256(content_bytes).hexdigest()

            # 3. Crear o obtener el Documento maestro
            # Usamos el source_id de los metadatos para vincularlo unívocamente.
            source_id = document_metadata.get('source_id')
            if not source_id:
                raise ValidationError("source_id es requerido en document_metadata.")

            document_code = f"{doc_type.code}-{source_id}"

            document, created = Document.objects.get_or_create(
                company=company,
                process=process,
                document_type=doc_type,
                document_code=document_code,
                defaults={
                    'sequence': 0, # Secuencia se actualizará abajo
                    'created_by': user
                }
            )

            # 4. Crear la nueva DocumentVersion
            version_number = (document.versions.order_by('-version_number').first().version_number + 1) if document.versions.exists() else 1

            # Actualizar la secuencia del documento maestro
            document.sequence = version_number
            document.save()

            doc_version = DocumentVersion.objects.create(
                document=document,
                version_number=version_number,
                title=original_filename,
                validity_year=date.today().year,
                uploaded_by=user,
                original_filename=original_filename,
                status=DocumentVersion.ProcessingStatus.PENDING_CONFIRMATION,
                file_hash_sha256=file_hash,
                # Simulación de subida a almacenamiento externo
                external_file_id=f"s3://{company.code.lower()}/{doc_type.code.lower()}/{original_filename}"
            )

            # Lógica futura para notarización en blockchain aquí

            return doc_version

        except (Company.DoesNotExist, User.DoesNotExist, ProcessType.DoesNotExist, Process.DoesNotExist, DocumentType.DoesNotExist) as e:
            raise ValidationError(f"Configuración de archivado inválida: {e}")
