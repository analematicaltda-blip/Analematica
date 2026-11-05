import base64
import hashlib
from datetime import date

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from ..models import Company

class KeyDerivationService:
    """
    Servicio estático para la derivación de claves de cifrado deterministas y seguras
    por cada compañía (inquilino). Esta es la implementación central de nuestra
    estrategia de seguridad de 'conocimiento cero' (zero-knowledge).
    """
    ITERATIONS = 260000

    @classmethod
    def derive_encryption_key(cls, company: Company, for_date: date) -> bytes:
        """
        Deriva una clave de cifrado de 32 bytes para una compañía en una fecha específica.
        La clave es determinista: las mismas entradas siempre producen la misma salida.

        Args:
            company (Company): La instancia de la compañía para la que se derivará la clave.
            for_date (date): La fecha para la cual se generará la clave. Usar la fecha
                             permite una futura estrategia de rotación de claves.

        Returns:
            bytes: La clave de cifrado de 32 bytes, lista para ser usada por Fernet.

        Raises:
            ImproperlyConfigured: Si el GLOBAL_ENCRYPTION_PEPPER no está configurado.
            ObjectDoesNotExist: Si la compañía no tiene una encryption_key asociada.
        """
        if not hasattr(settings, 'GLOBAL_ENCRYPTION_PEPPER'):
            raise ImproperlyConfigured("GLOBAL_ENCRYPTION_PEPPER must be set in settings.")

        try:
            salt = company.encryption_key.key_salt.encode('utf-8')
            pepper = settings.GLOBAL_ENCRYPTION_PEPPER.encode('utf-8')
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Company '{company.name}' does not have an associated encryption key.")

        password = for_date.isoformat().encode('utf-8')
        combined_salt = salt + pepper

        key = hashlib.pbkdf2_hmac(
            'sha256',
            password,
            combined_salt,
            cls.ITERATIONS,
            dklen=32
        )
        return key

    @staticmethod
    def urlsafe_b64encode_key(key: bytes) -> bytes:
        """
        Codifica la clave de 32 bytes en formato URL-safe base64, que es
        el formato requerido por la librería 'cryptography.fernet'.
        """
        return base64.urlsafe_b64encode(key)
