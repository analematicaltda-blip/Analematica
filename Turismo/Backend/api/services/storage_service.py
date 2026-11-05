import boto3
import hashlib
import logging
from django.conf import settings
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def generate_file_hash(file):
    """
    Genera el hash SHA-256 de un archivo para integridad criptográfica.
    """
    sha256 = hashlib.sha256()
    for chunk in file.chunks():
        sha256.update(chunk)
    return sha256.hexdigest()

class StorageService:
    """
    Hallazgo 15: Integración de almacenamiento archivístico físico.
    Gestiona la subida de archivos a AWS S3 con validación de hash.
    """

    @staticmethod
    def upload_document(file, folder="archivistica"):
        """
        Sube un archivo a S3 y devuelve la storage_key y el hash.
        """
        file_hash = generate_file_hash(file)

        # En entornos de desarrollo sin AWS, simular subida
        if not getattr(settings, 'AWS_ACCESS_KEY_ID', None):
            logger.info(f"SARITA Storage (Simulado): Archivo subido con Hash {file_hash}")
            return f"simulated_path/{file.name}", file_hash

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        storage_key = f"{folder}/{file_hash}_{file.name}"

        try:
            s3_client.upload_fileobj(
                file,
                bucket_name,
                storage_key,
                ExtraArgs={'ContentType': file.content_type}
            )
            logger.info(f"SARITA Storage: Archivo subido exitosamente a S3: {storage_key}")
            return storage_key, file_hash
        except ClientError as e:
            logger.error(f"SARITA Storage Error: {str(e)}")
            raise e
