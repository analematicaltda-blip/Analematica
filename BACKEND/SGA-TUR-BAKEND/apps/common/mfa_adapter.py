"""Versioned encryption for newly enrolled allauth factors, preserving legacy reads."""
from allauth.mfa.adapter import DefaultMFAAdapter
from cryptography.fernet import Fernet
from django.conf import settings
PREFIX='sgacd-mfa1:'
class EncryptedMFAAdapter(DefaultMFAAdapter):
    def encrypt(self,text):
        return PREFIX+Fernet(settings.FIELD_ENCRYPTION_KEY).encrypt(text.encode()).decode()
    def decrypt(self,text):
        if text.startswith(PREFIX):
            return Fernet(settings.FIELD_ENCRYPTION_KEY).decrypt(text[len(PREFIX):].encode()).decode()
        # Other historical allauth flows remain readable; ERP explicitly rejects unsealed TOTP.
        return text
