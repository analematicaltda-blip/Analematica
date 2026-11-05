from cryptography.fernet import Fernet
import jwt
from django.conf import settings

class SaritaDRMService:
    @staticmethod
    def encrypt_file(file_content, prestador_id):
        key = settings.SARITA_ARCHIVE_KEY.encode()
        f = Fernet(key)
        encrypted = f.encrypt(file_content)
        return encrypted

    @staticmethod
    def generate_drm_token(prestador_id, ip):
        token = jwt.encode({
            'prestador_id': prestador_id,
            'ip': ip,
            'system': 'SARITA',
            'exp': jwt.time() + 3600  # 1h
        }, settings.SARITA_JWT_SECRET, algorithm='HS256')
        return token

    @staticmethod
    def upload_onedrive(file, email):
        # MS Graph API call to prestador Drive/OneDrive
        # OAuth via prestador MS account
        pass  # Impl Graph API

