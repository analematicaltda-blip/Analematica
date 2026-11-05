import hashlib
from datetime import date
from cryptography.fernet import Fernet

from apps.companies.models import Company
from apps.companies.services.key_derivation_service import KeyDerivationService

class CryptoService:
    """
    Servicio para manejar todas las operaciones criptográficas:
    - Derivación de claves por compañía.
    - Cifrado y descifrado de contenido.
    - Cálculo de hashes.
    """

    def derive_company_key(self, company: Company) -> bytes:
        """
        Orquesta la derivación de la clave de cifrado para una compañía.
        """
        # Usamos la fecha actual. En un sistema con rotación de claves,
        # la fecha provendría de la DocumentVersion.
        key = KeyDerivationService.derive_encryption_key(company, for_date=date.today())
        return KeyDerivationService.urlsafe_b64encode_key(key)

    def encrypt(self, content: bytes, key: bytes) -> bytes:
        """
        Cifra el contenido de un archivo usando la clave proporcionada.
        """
        f = Fernet(key)
        return f.encrypt(content)

    def decrypt(self, encrypted_content: bytes, key: bytes) -> bytes:
        """
        Descifra el contenido de un archivo usando la clave proporcionada.
        """
        f = Fernet(key)
        return f.decrypt(encrypted_content)

    def calculate_hash(self, content: bytes) -> str:
        """
        Calcula el hash SHA-256 del contenido de un archivo.
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(content)
        return sha256_hash.hexdigest()
