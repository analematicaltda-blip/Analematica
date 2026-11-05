from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken

# Inicializa Fernet con la clave de la configuración
# Es importante que la clave sea un objeto de bytes
key = settings.FIELD_ENCRYPTION_KEY
fernet = Fernet(key)

class EncryptedTextField(models.TextField):
    """
    Un campo de texto personalizado que encripta su valor antes de guardarlo
    en la base de datos y lo desencripta al leerlo.
    """

    def from_db_value(self, value, expression, connection):
        """
        Convierte un valor de la base de datos a un valor de Python.
        En este caso, desencripta el valor.
        """
        if value is None:
            return value
        try:
            # Desencripta el valor usando la clave
            decrypted_value = fernet.decrypt(value.encode('utf-8')).decode('utf-8')
            return decrypted_value
        except InvalidToken:
            # Si el token no es válido (por ejemplo, datos no encriptados o corruptos),
            # devuelve el valor original para evitar que la aplicación se rompa.
            return value

    def to_python(self, value):
        """
        Convierte el valor a un objeto Python.
        Se asegura de que si ya es una cadena, no se procese de nuevo.
        """
        if isinstance(value, str):
            return value
        if value is None:
            return value
        try:
            decrypted_value = fernet.decrypt(value.encode('utf-8')).decode('utf-8')
            return decrypted_value
        except InvalidToken:
            return value

    def get_prep_value(self, value):
        """
        Prepara el valor para ser guardado en la base de datos.
        En este caso, encripta el valor.
        """
        if value is None:
            return value
        # Encripta el valor y lo convierte a una cadena para guardarlo
        encrypted_value = fernet.encrypt(value.encode('utf-8')).decode('utf-8')
        return encrypted_value