import os
import hashlib
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePaymentGatewayAdapter(ABC):
    @abstractmethod
    def generar_link_pago(self, monto: float, moneda: str, referencia: str, cliente_info: Dict[str, Any], concepto: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def validar_webhook_confirmacion(self, payload: Dict[str, Any], firma_seguridad: str) -> Dict[str, Any]:
        pass

from app.commercial.pool08.bold_gateway import BoldGateway,GatewayError
class BoldPaymentGateway(BasePaymentGatewayAdapter):
    """Compatibility facade; transport errors never produce an invented link."""
    def __init__(self,identity_key,secret_key):
        self.gateway=BoldGateway(identity_key,secret_key)
    def generar_hash_integridad(self,order_id,monto,moneda):
        return self.gateway.integrity(order_id,monto,moneda)
    def generar_link_pago(self,monto,moneda,referencia,cliente_info,concepto):
        result=self.gateway.create(referencia,monto,moneda,concepto)
        return {'status':'LINK_CREATED','pasarela':'BOLD_COLOMBIA',**result}
    def validar_webhook_confirmacion(self,payload,firma_seguridad):
        return self.gateway.verify_webhook(payload,firma_seguridad)

# Environment keys override the recovered, ignored local configuration as a pair.
# No value is logged; a deployment without this local file must supply its secrets.
def _bold_credentials():
    identity=os.environ.get('BOLD_IDENTITY_KEY','');secret=os.environ.get('BOLD_SECRET_KEY','')
    if identity or secret:
        if not identity or not secret:raise ValueError('Configura ambas variables Bold del mismo comercio.')
        return identity,secret
    from pathlib import Path
    import stat
    path=Path(__file__).resolve().parents[4]/'.runtime/bold-test.env'
    if not path.exists():return '', ''
    info=path.lstat()
    if path.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid!=os.getuid() or info.st_size>4096:raise ValueError('Configuración Bold local requiere archivo privado del proceso.')
    values={}
    for line in path.read_text().splitlines():
        key,value=line.split('=',1)
        if key in values or key not in {'BOLD_IDENTITY_KEY','BOLD_SECRET_KEY'}:raise ValueError('Configuración Bold local inválida.')
        values[key]=json.loads(value)
    if set(values)!={'BOLD_IDENTITY_KEY','BOLD_SECRET_KEY'} or any(not isinstance(v,str) or not v for v in values.values()):raise ValueError('Par de claves Bold requerido.')
    return values['BOLD_IDENTITY_KEY'],values['BOLD_SECRET_KEY']

_bold_identity,_bold_secret=_bold_credentials()
payment_gateway=BoldPaymentGateway(identity_key=_bold_identity,secret_key=_bold_secret)
del _bold_identity,_bold_secret
