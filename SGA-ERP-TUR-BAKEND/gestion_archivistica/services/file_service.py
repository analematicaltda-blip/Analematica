from ..storage_adapters.s3 import S3StorageAdapter
from ..storage_adapters.base import BaseStorageAdapter
from ..models import DocumentVersion
from .crypto_service import CryptoService

class StorageCoordinator:
    """
    Coordina las operaciones de almacenamiento, seleccionando el adaptador
    adecuado (S3, Google Drive, etc.) según la configuración.
    """
    def get_adapter(self) -> BaseStorageAdapter:
        return S3StorageAdapter()

    def upload(self, encrypted_content: bytes, version: DocumentVersion) -> str:
        adapter = self.get_adapter()
        cloud_filename = f"{version.document.company.id}/{version.document.id}/{version.id}.enc"
        return adapter.upload(encrypted_content, cloud_filename)

    def download(self, version: DocumentVersion) -> bytes:
        adapter = self.get_adapter()
        return adapter.download(version.external_file_id)

class FileCoordinator:
    """
    Coordina las operaciones de alto nivel sobre archivos,
    combinando almacenamiento y criptografía.
    """
    def __init__(self):
        self.storage = StorageCoordinator()
        self.crypto = CryptoService()

    def download(self, version: DocumentVersion) -> bytes:
        """
        Descarga un archivo de forma segura: lo obtiene del almacenamiento
        en la nube y lo descifra.
        """
        # 1. Descargar el contenido CIFRADO
        encrypted_content = self.storage.download(version)

        # 2. Derivar la clave de cifrado para esta compañía
        key = self.crypto.derive_company_key(version.document.company)

        # 3. Descifrar el contenido
        decrypted_content = self.crypto.decrypt(encrypted_content, key)

        return decrypted_content
