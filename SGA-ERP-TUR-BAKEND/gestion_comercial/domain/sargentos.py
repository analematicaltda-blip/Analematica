# backend/apps/prestadores/mi_negocio/gestion_comercial/domain/sargentos.py
import logging
from .models import OperacionComercial, ContratoComercial, OrdenOperativa, FacturaVenta
from django.utils import timezone
import uuid

logger = logging.getLogger(__name__)

class SargentoComercial:
    """
    Ejecutor de acciones mínimas indivisibles del dominio comercial.
    """

    @staticmethod
    def validar_precio(producto_id, precio_propuesto):
        # Lógica atómica: Comparar con lista de precios oficial
        logger.info(f"SARGENTO: Validando precio {precio_propuesto} para producto {producto_id}")
        return True # Siempre válido en esta fase

    @staticmethod
    def generar_contrato(operacion_id):
        try:
            operacion = OperacionComercial.objects.get(id=operacion_id)
            contrato, created = ContratoComercial.objects.get_or_create(
                operacion=operacion,
                defaults={
                    'perfil_ref_id': operacion.perfil_ref_id,
                    'cliente_ref_id': operacion.cliente_ref_id,
                    'terminos_y_condiciones': f"Términos estándar para la operación {operacion.id}",
                    'estado': 'BORRADOR'
                }
            )
            logger.info(f"SARGENTO: Contrato generado para operación {operacion_id}")

            # Activar misión de archivado legal vía agentes
            try:
                from apps.sarita_agents.orchestrator import sarita_orchestrator
                import json

                contract_content = {
                    "contrato_id": str(contrato.id),
                    "operacion_id": str(operacion.id),
                    "terminos": contrato.terminos_y_condiciones,
                    "fecha": str(timezone.now())
                }

                directive = {
                    "domain": "prestadores",
                    "mission": {"type": "ARCHIVE_LEAL_DOC"},
                    "parameters": {
                        "company_id": str(operacion.perfil_ref_id), # Simplificado para demo
                        "user_id": operacion.creado_por.id,
                        "process_type_code": 'LEGAL',
                        "process_code": 'CONT',
                        "document_type_code": 'CONTRATO',
                        "document_content": json.dumps(contract_content).encode('utf-8'),
                        "original_filename": f"CONTRATO-{contrato.id}.json",
                        "document_metadata": {'source_model': 'ContratoComercial', 'source_id': str(contrato.id)},
                    }
                }
                sarita_orchestrator.handle_directive(directive)
            except Exception as e:
                logger.error(f"SARGENTO: Error al delegar archivado de contrato: {e}")

            self.registrar_bitacora(operacion.creado_por.id, "CONTRACT_CREATED", {"contrato_id": str(contrato.id)})

            return contrato
        except Exception as e:
            logger.error(f"SARGENTO: Error al generar contrato: {e}")
            return None

    @staticmethod
    def registrar_bitacora(usuario_id, accion, detalles):
        from apps.audit.models import AuditLog
        try:
            from api.models import CustomUser
            user = CustomUser.objects.get(id=usuario_id)
            AuditLog.objects.create(
                user=user,
                username=user.username,
                action=accion,
                details=detalles
            )
            logger.info(f"SARGENTO: Acción '{accion}' registrada en bitácora para usuario {user.username}.")
        except Exception as e:
            logger.error(f"SARGENTO: Error al registrar bitácora: {e}")

    @staticmethod
    def generar_orden_operativa(contrato_id):
        try:
            contrato = ContratoComercial.objects.get(id=contrato_id)
            orden = OrdenOperativa.objects.create(
                contrato=contrato,
                perfil_ref_id=contrato.perfil_ref_id,
                descripcion_servicio=f"Servicio derivado del contrato {contrato.id}",
                fecha_programada=timezone.now() + timezone.timedelta(days=1),
                estado='PENDIENTE'
            )
            logger.info(f"SARGENTO: Orden operativa {orden.id} generada.")

            # Activar misión de ejecución operativa vía agentes
            try:
                from apps.sarita_agents.orchestrator import sarita_orchestrator
                directive = {
                    "domain": "prestadores",
                    "mission": {"type": "EXECUTE_OPERATIONAL_FLOW"},
                    "parameters": {
                        "orden_id": str(orden.id),
                        "perfil_id": str(orden.perfil_ref_id),
                        "descripcion": orden.descripcion_servicio
                    }
                }
                sarita_orchestrator.handle_directive(directive)
                logger.info(f"SARGENTO: Misión de ejecución operativa delegada para orden {orden.id}")
            except Exception as e:
                logger.error(f"SARGENTO: Error al delegar ejecución operativa: {e}")

            return orden
        except Exception as e:
            logger.error(f"SARGENTO: Error al generar orden: {e}")
            return None
