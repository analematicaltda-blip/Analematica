import logging
import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base import BaseStorageAdapter

logger = logging.getLogger(__name__)

class S3StorageAdapter(BaseStorageAdapter):
    """
    Adaptador de almacenamiento para interactuar con Amazon S3.
    """
    def __init__(self):
        """
        Inicializa el cliente de Boto3 para S3.
        """
        required_settings = ['AWS_STORAGE_BUCKET_NAME', 'AWS_S3_REGION_NAME']
        for setting in required_settings:
            if not getattr(settings, setting, None):
                raise ImproperlyConfigured(f"S3StorageAdapter requires '{setting}' to be set.")

        self.s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def upload(self, encrypted_content: bytes, cloud_filename: str) -> str:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=cloud_filename,
                Body=encrypted_content,
                ServerSideEncryption='AES256'
            )
            logger.info(f"Successfully uploaded to S3: s3://{self.bucket_name}/{cloud_filename}")
            return cloud_filename
        except ClientError as e:
            logger.exception(f"Failed to upload file to S3. Bucket: {self.bucket_name}, Key: {cloud_filename}")
            raise IOError(f"Could not upload file to S3: {e}")

    def download(self, external_id: str) -> bytes:
        try:
            logger.info(f"Downloading from S3: s3://{self.bucket_name}/{external_id}")
            s3_object = self.s3_client.get_object(Bucket=self.bucket_name, Key=external_id)
            return s3_object['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File with key '{external_id}' not found in S3 bucket.")
            else:
                raise IOError(f"Could not download file from S3: {e}")

    def delete(self, external_id: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=external_id)
            logger.info(f"Successfully deleted from S3: s3://{self.bucket_name}/{external_id}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Attempted to delete non-existent key from S3: {external_id}")
                return True
            logger.exception(f"Failed to delete file from S3. Key: {external_id}")
            return False
