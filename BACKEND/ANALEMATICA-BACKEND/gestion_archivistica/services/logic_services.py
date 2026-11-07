import base64
from typing import Dict, Any

from django.db import transaction

from apps.audit.services import AuditLogger
from apps.audit.models import AuditLog
from apps.domain_business.operativa.models import ProviderProfile
from ..models import Document, DocumentVersion, Process, DocumentType
from ..tasks.processing_tasks import start_file_processing_flow

class DocumentCoordinatorService:
    """
    Servicio de alto nivel para orquestar la lógica de negocio de documentos.
    Actúa como el "cerebro" para las operaciones complejas de documentos, asegurando
    la integridad de los datos a través de transacciones y una correcta orquestación.
    """
    @staticmethod
    def _get_next_sequence(company, process, doc_type) -> int:
        last_doc = Document.objects.select_for_update().filter(
            company=company, process=process, document_type=doc_type
        ).order_by('-sequence').first()
        return (last_doc.sequence + 1) if last_doc else 1

    @staticmethod
    def _generate_code(process: Process, doc_type: DocumentType, sequence: int) -> str:
        tp_code = process.process_type.code
        ppp_code = process.code
        dd_code = doc_type.code
        seq_padded = f"{sequence:02d}"
        return f"{tp_code}-{ppp_code}-{dd_code}-{seq_padded}"

    @classmethod
    @transaction.atomic
    def create_document_and_first_version(
        cls, *, data: Dict[str, Any], user: ProviderProfile, file_content: bytes, request
    ) -> DocumentVersion:
        """
        Crea un Documento "contenedor" y su primera versión de forma atómica.
        Orquesta la creación en la BD, la auditoría y el inicio del pipeline
        de procesamiento asíncrono.
        """
        company = user.company
        process = Process.objects.select_related('process_type').get(id=data['process_id'], company=company)
        doc_type = DocumentType.objects.get(id=data['document_type_id'], company=company)

        sequence = cls._get_next_sequence(company, process, doc_type)
        doc_code = cls._generate_code(process, doc_type, sequence)

        doc = Document.objects.create(
            company=company,
            process=process,
            document_type=doc_type,
            sequence=sequence,
            document_code=doc_code,
            created_by=user.usuario
        )

        initial_version = DocumentVersion.objects.create(
            document=doc,
            version_number=1,
            title=data['title'],
            validity_year=data['validity_year'],
            uploaded_by=user.usuario,
            original_filename=data['original_filename'],
            status='PENDING_UPLOAD'
        )

        file_content_b64 = base64.b64encode(file_content).decode('utf-8')
        start_file_processing_flow.delay(initial_version.id, file_content_b64)

        # AuditLogger.log(
        #     user=user.usuario,
        #     action=AuditLog.Action.DOCUMENT_CREATED,
        #     request=request,
        #     details={
        #         'document_id': str(doc.id),
        #         'document_code': doc.document_code,
        #         'version_id': initial_version.id,
        #         'title': initial_version.title
        #     }
        # )

        return initial_version

    @classmethod
    @transaction.atomic
    def create_new_version_for_document(
        cls, *, document: Document, data: Dict[str, Any], user: ProviderProfile, file_content: bytes, request
    ) -> DocumentVersion:
        """
        Crea una nueva versión para un documento ya existente de forma atómica.
        """
        latest_version = document.versions.select_for_update().latest('version_number')
        new_version_number = latest_version.version_number + 1

        new_version = DocumentVersion.objects.create(
            document=document,
            version_number=new_version_number,
            title=data['title'],
            validity_year=data['validity_year'],
            uploaded_by=user.usuario,
            original_filename=data['original_filename'],
            status='PENDING_UPLOAD'
        )

        file_content_b64 = base64.b64encode(file_content).decode('utf-8')
        start_file_processing_flow.delay(new_version.id, file_content_b64)

        # AuditLogger.log(
        #     user=user.usuario,
        #     action=AuditLog.Action.VERSION_UPLOADED,
        #     request=request,
        #     details={
        #         'document_id': str(document.id),
        #         'document_code': document.document_code,
        #         'new_version_id': new_version.id,
        #         'new_version_number': new_version.version_number,
        #         'title': new_version.title
        #     }
        # )

        return new_version
