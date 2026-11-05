# backend/apps/prestadores/mi_negocio/gestion_archivistica/services.py
import base64
import hashlib
from datetime import date
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.fernet import Fernet
from django.db import transaction

import boto3
from botocore.exceptions import ClientError

from .models import Document, DocumentVersion, Process, DocumentType
from api.models import CustomUser
from apps.audit.services import AuditLogger
from .tasks.processing_tasks import start_file_processing_flow
from .storage_adapters.s3 import S3StorageAdapter

# ==========================================================
# Crypto Service
# ==========================================================
class CryptoService:
    ITERATIONS = 260000
    @staticmethod
    def calculate_hash(file_content: bytes) -> str:
        return hashlib.sha256(file_content).hexdigest()
    @classmethod
    def derive_company_key(cls, company) -> bytes:
        if not hasattr(settings, 'GLOBAL_ENCRYPTION_PEPPER'):
            raise ImproperlyConfigured("GLOBAL_ENCRYPTION_PEPPER must be set in settings.")
        # La lógica real dependería de cómo el modelo `Company` almacena su `key_salt`.
        # Esto es un placeholder funcional.
        # if not hasattr(company, 'encryption_key') or not hasattr(company.encryption_key, 'key_salt'):
        #      raise ValueError(f"Company '{company.name}' does not have a valid encryption key setup.")
        # salt = company.encryption_key.key_salt.encode('utf-8')
        salt = b'a-secure-random-salt-per-company'
        pepper = settings.GLOBAL_ENCRYPTION_PEPPER.encode('utf-8')
        password = date.today().isoformat().encode('utf-8')
        combined_salt = salt + pepper
        key = hashlib.pbkdf2_hmac('sha256', password, combined_salt, cls.ITERATIONS, dklen=32)
        return base64.urlsafe_b64encode(key)
    @staticmethod
    def encrypt(file_content: bytes, key: bytes) -> bytes:
        return Fernet(key).encrypt(file_content)
    @staticmethod
    def decrypt(encrypted_content: bytes, key: bytes) -> bytes:
        return Fernet(key).decrypt(encrypted_content)

# ==========================================================
# File Coordinator
# ==========================================================
class FileCoordinator:
    def __init__(self):
        self.crypto_service = CryptoService()
        self.storage_adapter = S3StorageAdapter()
    def upload_and_process(self, file_content: bytes, version: DocumentVersion) -> tuple[str, str]:
        file_hash = self.crypto_service.calculate_hash(file_content)
        company = version.document.company
        encryption_key = self.crypto_service.derive_company_key(company)
        encrypted_content = self.crypto_service.encrypt(file_content, encryption_key)
        cloud_filename = f"{company.id}/{version.document.id}/{version.id}.enc"
        external_id = self.storage_adapter.upload(encrypted_content, cloud_filename)
        return file_hash, external_id
    def download_and_decrypt(self, version: DocumentVersion) -> bytes:
        encrypted_content = self.storage_adapter.download(version.external_file_id)
        company = version.document.company
        encryption_key = self.crypto_service.derive_company_key(company)
        return self.crypto_service.decrypt(encrypted_content, encryption_key)

# ==========================================================
# Document Coordinator
# ==========================================================
class DocumentCoordinatorService:
    @staticmethod
    @transaction.atomic
    def _get_next_sequence(company, process, doc_type) -> int:
        last_doc = Document.objects.select_for_update().filter(company=company, process=process, document_type=doc_type).order_by('-sequence').first()
        return (last_doc.sequence + 1) if last_doc else 1
    @staticmethod
    def _generate_code(process: Process, doc_type: DocumentType, sequence: int) -> str:
        return f"{process.process_type.code}-{process.code}-{doc_type.code}-{sequence:02d}"
    @classmethod
    @transaction.atomic
    def create_document_and_first_version(cls, *, data, user, file_content, request) -> DocumentVersion:
        process = data['process']
        doc_type = data['document_type']
        company = user.company
        if not company: raise ValueError("User must have a company.")
        sequence = cls._get_next_sequence(company, process, doc_type)
        doc_code = cls._generate_code(process, doc_type, sequence)
        doc = Document.objects.create(company=company, process=process, document_type=doc_type, sequence=sequence, document_code=doc_code, created_by=user)
        initial_version = DocumentVersion.objects.create(document=doc, version_number=1, title=data['title'], validity_year=data['validity_year'], uploaded_by=user, original_filename=data['original_filename'], status=DocumentVersion.ProcessingStatus.PENDING_UPLOAD)
        file_content_b64 = base64.b64encode(file_content).decode('utf-8')
        start_file_processing_flow.delay(initial_version.id, file_content_b64)
        AuditLogger.log(user=user, action="DOCUMENT_CREATED", request=request, details={'document_id': str(doc.id)})
        return initial_version
    @classmethod
    @transaction.atomic
    def create_new_version_for_document(cls, *, document, data, user, file_content, request) -> DocumentVersion:
        latest_version = document.versions.select_for_update().latest('version_number')
        new_version_number = latest_version.version_number + 1
        new_version = DocumentVersion.objects.create(document=document, version_number=new_version_number, title=data['title'], validity_year=data['validity_year'], uploaded_by=user, original_filename=data['original_filename'], status=DocumentVersion.ProcessingStatus.PENDING_UPLOAD)
        file_content_b64 = base64.b64encode(file_content).decode('utf-8')
        start_file_processing_flow.delay(new_version.id, file_content_b64)
        AuditLogger.log(user=user, action="VERSION_UPLOADED", request=request, details={'document_id': str(document.id)})
        return new_version
