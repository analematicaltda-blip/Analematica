"""RNT boundary: never infer official verification or identity from a submitted number."""
from rest_framework.exceptions import APIException

class RNTIntegrationUnavailable(APIException):
    status_code=503
    default_code='rnt_integration_unavailable'
    default_detail='Integración oficial RNT no configurada ni validada. No se verificó el registro ni se concedió acceso.'

class RNTIntegrationService:
    @classmethod
    def validate_rnt(cls,rnt_number,nit=None):
        raise RNTIntegrationUnavailable()

    @classmethod
    def sync_provider(cls,provider_id):
        raise RNTIntegrationUnavailable()

    @classmethod
    def login_via_rnt(cls,rnt_number,password_token):
        raise RNTIntegrationUnavailable()
