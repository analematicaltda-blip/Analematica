from langchain_core.tools import tool
from typing import Any, List, Dict

class InstitucionalSoldiers:
    """
    El arsenal de herramientas de ejecución para la escuadra de Gestión Institucional.
    Cada función es un Soldado-Administrador de la plataforma.
    """
    def __init__(self, api_client: Any):
        self.api = api_client

    @tool
    def crear_inquilino_nueva_sede(self, nombre_sede: str, pais: str, admin_email: str) -> Dict:
        """(SOLDADO SITIO WEB/INQUILINOS) Ejecuta la creación de un nuevo inquilino (sede o institución) en la plataforma."""
        print(f"--- 💥 SOLDADO (Institucional): ¡ACCIÓN! Creando inquilino '{nombre_sede}' en {pais}. ---")
        # return self.api.create_tenant(name=nombre_sede, country=pais, admin_email=admin_email)
        return {"status": "success", "tenant_id": "sede-col-001", "message": "Inquilino creado y aislado."}

    @tool
    def crear_nueva_area(self, nombre_area: str, descripcion: str, inquilino_id: str) -> Dict:
        """(SOLDADO ÁREAS) Ejecuta la creación de una nueva área cultural o deportiva dentro de un inquilino."""
        print(f"--- 💥 SOLDADO (Institucional): ¡ACCIÓN! Creando área '{nombre_area}' para inquilino {inquilino_id}. ---")
        # return self.api.create_area(name=nombre_area, description=descripcion, tenant_id=inquilino_id)
        return {"status": "success", "area_id": 15}

    @tool
    def registrar_personal_administrativo(self, nombre: str, email: str, rol: str, inquilino_id: str) -> Dict:
        """(SOLDADO PERSONAL) Ejecuta el registro de un nuevo miembro del personal administrativo en un inquilino."""
        print(f"--- 💥 SOLDADO (Institucional): ¡ACCIÓN! Registrando personal '{nombre}' con rol '{rol}'. ---")
        # return self.api.register_staff(name=nombre, email=email, role=rol, tenant_id=inquilino_id)
        return {"status": "success", "staff_id": 101}

    @tool
    def publicar_noticia_sitio_web(self, titulo: str, contenido_html: str) -> Dict:
        """(SOLDADO SITIO WEB) Publica una nueva noticia en la sección pública del sitio web."""
        print(f"--- 💥 SOLDADO (Institucional): ¡ACCIÓN! Publicando noticia en sitio web: '{titulo}'. ---")
        # return self.api.publish_website_news(title=titulo, content_html=contenido_html)
        return {"status": "success", "url": "/news/nueva-noticia"}

    def get_all_soldiers(self) -> List:
        """Recluta y devuelve la escuadra de Gestión Institucional completa."""
        return [
            self.crear_inquilino_nueva_sede,
            self.crear_nueva_area,
            self.registrar_personal_administrativo,
            self.publicar_noticia_sitio_web
        ]
