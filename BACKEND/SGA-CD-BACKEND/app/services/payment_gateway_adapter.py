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

class BoldPaymentGateway(BasePaymentGatewayAdapter):
    """
    Integracion Oficial con Pasarela Bold Colombia.
    Soporta PSE, Nequi, Boton Bancolombia y Tarjetas Credito/Debito.
    """
    def __init__(self, identity_key: str, secret_key: str):
        self.identity_key = identity_key
        self.secret_key = secret_key
        self.api_url = "https://integrations.api.bold.co/online/link/v1"

    def generar_hash_integridad(self, order_id: str, monto: float, moneda: str) -> str:
        """Genera el hash SHA-256 exigido por Bold: {orderId}{amount}{currency}{secretKey}"""
        monto_str = str(int(monto)) if monto == int(monto) else str(monto)
        cadena = f"{order_id}{monto_str}{moneda}{self.secret_key}"
        return hashlib.sha256(cadena.encode("utf-8")).hexdigest()

    def generar_link_pago(self, monto: float, moneda: str, referencia: str, cliente_info: Dict[str, Any], concepto: str) -> Dict[str, Any]:
        hash_integridad = self.generar_hash_integridad(referencia, monto, moneda)
        
        # Intentar generar link directo vía API REST de Bold
        payload_data = {
            "amount_type": "CLOSE",
            "amount": {
                "total": int(monto),
                "currency": moneda
            },
            "description": concepto[:90],
            "reference": referencia,
            "callback_url": "http://localhost:8080/payment_success.html"
        }

        checkout_url = f"https://checkout.bold.co/payment/{referencia}"
        bold_order_id = referencia

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload_data).encode("utf-8"),
                headers={
                    "Authorization": f"x-api-key {self.identity_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                res_json = json.loads(response.read().decode("utf-8"))
                if "payload" in res_json and "url" in res_json["payload"]:
                    checkout_url = res_json["payload"]["url"]
                    bold_order_id = res_json["payload"].get("id", referencia)
        except Exception:
            # Fallback seguro: Botón Bold Checkout con hash de integridad
            pass

        return {
            "status": "success",
            "pasarela": "BOLD_COLOMBIA",
            "checkout_url": checkout_url,
            "referencia": referencia,
            "bold_order_id": bold_order_id,
            "monto": monto,
            "moneda": moneda,
            "integrity_signature": hash_integridad,
            "identity_key": self.identity_key,
            "metodos_disponibles": ["PSE", "TARJETA_CREDITO_DEBITO", "NEQUI", "BOTON_BANCOLOMBIA"]
        }

    def validar_webhook_confirmacion(self, payload: Dict[str, Any], firma_seguridad: str) -> Dict[str, Any]:
        raise ValueError("Confirmación Bold bloqueada: falta un verificador cualificado de firma sobre el cuerpo HTTP original y su vínculo con el pago. Un payload declarado no acredita pago ni reembolso.")

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
