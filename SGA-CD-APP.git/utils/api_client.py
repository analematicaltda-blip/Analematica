import requests
import json
from typing import List, Dict, Any, Optional
from .security_shield import sanitize_input_for_flet, sanitize_dict_inputs, format_masked_error_code, mask_sensitive_token

class ApiClient:
    """
    Cliente para interactuar con el backend API del sistema SGA-CD.
    Soporta autenticación mediante JWT Bearer y X-API-KEY, e intercepta
    errores 401/403 ejecutando refrescos silenciosos o formateando trazas enmascaradas.
    """
    def __init__(self, base_url: str, tenant_api_key: str, access_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.tenant_api_key = tenant_api_key
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
            "X-API-KEY": tenant_api_key
        }
        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"

    def set_access_token(self, token: str):
        """Actualiza el token JWT de acceso en la cabecera."""
        self.access_token = token
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
            print(f"[ApiClient] JWT Token actualizado: {mask_sensitive_token(token)}")
        elif "Authorization" in self.headers:
            del self.headers["Authorization"]

    def _attempt_silent_refresh(self) -> bool:
        """
        Intenta un refresco silencioso del token JWT con el servidor antes de fallar.
        """
        try:
            refresh_url = f"{self.base_url}/api/v1/auth/refresh"
            resp = requests.post(
                refresh_url,
                headers={"X-API-KEY": self.tenant_api_key},
                json={},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                new_token = data.get("access_token")
                if new_token:
                    self.set_access_token(new_token)
                    print("[ApiClient] Refresco silencioso de JWT completado con éxito.")
                    return True
        except Exception as e:
            print(f"[ApiClient] Excepción en refresco silencioso: {e}")
        return False

    def _make_request(self, method: str, endpoint: str, headers: Dict = None, **kwargs) -> Dict | List | None:
        """Método de ayuda para realizar peticiones a la API con interceptor de errores."""
        url = f"{self.base_url}{endpoint}"

        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        # Sanitizar json payload si existe
        if "json" in kwargs and isinstance(kwargs["json"], dict):
            kwargs["json"] = sanitize_dict_inputs(kwargs["json"])

        try:
            response = requests.request(method, url, headers=request_headers, timeout=10, **kwargs)

            # Intercepción de respuestas HTTP 401 y 403
            if response.status_code in (401, 403):
                masked_code = format_masked_error_code(response.status_code)
                print(f"[ApiClient Interceptor] HTTP {response.status_code} detectado -> Código enmascarado: {masked_code}")

                # Intentar refresco silencioso
                if self._attempt_silent_refresh():
                    # Reintentar petición original con nuevo token
                    request_headers["Authorization"] = self.headers.get("Authorization", "")
                    response = requests.request(method, url, headers=request_headers, timeout=10, **kwargs)
                    if response.ok:
                        return response.json() if response.status_code != 204 else {}

                return {"error": True, "code": masked_code, "status_code": response.status_code}

            response.raise_for_status()

            if response.status_code == 204:
                return {}

            return response.json()
        except requests.exceptions.RequestException as e:
            status = getattr(e.response, 'status_code', 503) if hasattr(e, 'response') and e.response else 503
            masked_code = format_masked_error_code(status)
            print(f"Error de API en '{method} {endpoint}' [{masked_code}]: {e}")
            return {"error": True, "code": masked_code, "status_code": status}
        except json.JSONDecodeError:
            print(f"Error de decodificación JSON en '{method} {endpoint}'")
            return {"error": True, "code": "STD-ERR-500-INTERNAL-ERROR", "status_code": 500}

    # --- Métodos de API ---

    def get_user_context(self, user_id: int) -> Dict | None:
        """Obtiene el contexto de un usuario desde el backend."""
        headers = {"X-USER-ID": str(user_id)}
        return self._make_request("GET", "/api/user_context", headers=headers)

    def get_clases_profesor(self, profesor_id: int) -> List[Dict] | None:
        """Obtiene la lista de clases para un profesor específico."""
        params = {"profesor_id": profesor_id}
        return self._make_request("GET", "/api/clases", params=params)

    def create_alumno(self, alumno_data: Dict) -> Dict | None:
        """Crea un nuevo alumno."""
        return self._make_request("POST", "/api/alumnos", json=alumno_data)

    def get_llm_config(self) -> Dict | None:
        """Obtiene la configuración de LLM del inquilino desde el servidor."""
        return self._make_request("GET", "/api/config/llm")

    def set_llm_config(self, config_data: Dict) -> bool:
        """Guarda la configuración de LLM del inquilino en el servidor."""
        response = self._make_request("POST", "/api/config/llm", json=config_data)
        return isinstance(response, dict) and response.get("status") == "success"

    def pull_sync_data(self, last_sync_timestamp: str = None) -> Dict | None:
        """Obtiene los cambios del servidor para la sincronización."""
        params = {}
        if last_sync_timestamp:
            params['last_sync_timestamp'] = last_sync_timestamp
        return self._make_request("GET", "/api/sync/pull", params=params)

    def push_sync_data(self, data_batch: Dict) -> bool:
        """Envía los cambios locales al servidor para la sincronización."""
        response = self._make_request("POST", "/api/sync/push", json=data_batch)
        return isinstance(response, dict) and response.get("status") == "success"

    def post(self, endpoint: str, payload: Dict) -> Any:
        """Petición POST genérica con sanitización e intercepción."""
        return self._make_request("POST", endpoint, json=payload)
