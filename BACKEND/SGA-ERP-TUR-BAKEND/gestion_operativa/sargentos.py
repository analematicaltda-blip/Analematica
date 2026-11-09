# backend/apps/prestadores/mi_negocio/gestion_operativa/sargentos.py
import logging
import uuid
from django.utils import timezone
from .modulos_genericos.perfil.models import ProviderProfile
from apps.audit.models import AuditLog
from api.models import CustomUser

logger = logging.getLogger(__name__)

class SargentoOperativo:
    """
    Ejecutor de acciones mínimas e indivisibles del dominio operativo genérico.
    """

    @staticmethod
    def crear_orden_servicio(perfil_id, descripcion, parametros=None, *, usuario_id=None):
        from django.db import transaction
        from django.utils.dateparse import parse_datetime
        from rest_framework.exceptions import ValidationError
        from .sg_sst.sargentos import _context
        from .models import OrdenOperativa
        if not isinstance(parametros,dict) or not {'contrato_id','fecha_inicio','fecha_fin_estimada'}<=set(parametros):
            raise ValidationError('Contrato y fechas explícitas requeridos; no se inventan referencias.')
        if not isinstance(descripcion,str) or not 1<=len(descripcion.strip())<=2000:raise ValidationError('Descripción acotada requerida.')
        begin=parse_datetime(parametros['fecha_inicio']);end=parse_datetime(parametros['fecha_fin_estimada'])
        if begin is None or end is None or timezone.is_naive(begin) or timezone.is_naive(end) or end<=begin:raise ValidationError('Ventana prevista explícita y con zona requerida.')
        contract=uuid.UUID(str(parametros['contrato_id']))
        with transaction.atomic():
            user,provider=_context(usuario_id,perfil_id)
            orden=OrdenOperativa.objects.create(provider_id=provider.pk,contrato_ref_id=contract,
                descripcion_servicio=descripcion,fecha_inicio=begin,fecha_fin_estimada=end)
            AuditLog.objects.create(user=user,username=user.username,action='OPERATIONAL_DRAFT_CREATED',
                details={'provider_id':str(provider.pk),'operation_id':str(orden.pk),'kind':'OrdenOperativa'})
            return {'id':str(orden.pk),'status':'DRAFT_CREATED','service_started':False,
                    'contract_independently_verified':False,'ledger_written':False}

    @staticmethod
    def actualizar_estado(entidad_tipo, entidad_id, nuevo_estado, motivo="", agente_id=None,
                           *, provider_id=None, expected_state=None, confirmed=False):
        from .state_service import transition
        return transition(usuario_id=agente_id,provider_id=provider_id,kind=entidad_tipo,
            operation_id=entidad_id,expected_state=expected_state,new_state=nuevo_estado,
            reason=motivo,confirmed=confirmed)

    @staticmethod
    def registrar_ejecucion_tarea(tarea_id, operario_id, resultado):
        from rest_framework.exceptions import ValidationError
        raise ValidationError('Ejecución de tarea no cualificada: no se devuelve éxito sin persistencia y controles de despacho.')

    @staticmethod
    def registrar_costo_operativo(perfil_id, orden_id, concepto, monto):
        from .modulos_genericos.costos.models import Costo
        costo = Costo.objects.create(
            perfil_id=perfil_id,
            orden_operativa_ref_id=orden_id,
            concepto=concepto,
            monto=monto,
            fecha=timezone.now().date()
        )
        logger.info(f"SARGENTO: Costo {costo.id} registrado para orden {orden_id}.")
        return str(costo.id)

    @staticmethod
    def asignar_recurso(orden_id, item_id, cantidad):
        from .modulos_genericos.inventario.models import AsignacionRecurso, InventoryItem
        try:
            item = InventoryItem.objects.get(id=item_id)
            asignacion = AsignacionRecurso.objects.create(
                item=item,
                orden_operativa_ref_id=orden_id,
                cantidad_asignada=cantidad
            )
            item.cantidad -= cantidad
            item.save()
            logger.info(f"SARGENTO: Recurso {item_id} asignado a orden {orden_id}.")
            return str(asignacion.id)
        except InventoryItem.DoesNotExist:
            logger.error(f"SARGENTO: Item de inventario {item_id} no existe.")
            return None

    @staticmethod
    def registrar_bitacora_operativa(usuario_id, accion, detalles):
        try:
            user = CustomUser.objects.get(id=usuario_id)
            AuditLog.objects.create(
                user=user,
                username=user.username,
                action=f"OPERATIONAL_{accion}",
                details=detalles
            )
            logger.info(f"SARGENTO: Acción operativa '{accion}' registrada en bitácora.")
        except Exception as e:
            logger.error(f"SARGENTO: Error al registrar bitácora operativa: {e}")
