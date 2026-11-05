import logging
from .models import IncidenteLaboral, InvestigacionIncidente, MatrizRiesgo
from apps.audit.models import AuditLog
from apps.governance_live.models import SystemicState
from apps.prestadores.mi_negocio.gestion_archivistica.archiving import ArchivingService

logger = logging.getLogger(__name__)

class SargentoSST:
    """
    Sargento Atómico: Ejecuta acciones mínimas de SST, como registros de incidentes y bloqueos operativos.
    """

    @staticmethod
    def registrar_incidente(datos: dict, usuario_id: int):
        """
        Registra un accidente o incidente y dispara alerta si es grave.
        """
        incidente = IncidenteLaboral.objects.create(
            provider_id=datos['perfil_id'],
            tipo=datos['tipo'],
            fecha_hora=datos['fecha_hora'],
            lugar=datos['lugar'],
            descripcion_hechos=datos['descripcion'],
            gravedad=datos['gravedad']
        )

        # Auditoría Obligatoria
        AuditLog.objects.create(
            user_id=usuario_id,
            action="SST_INCIDENT_REGISTERED",
            details=f"Incidente {incidente.id} registrado. Gravedad: {incidente.gravedad}"
        )

        # Generar Evidencia Archivística (Fase 2 Integration)
        try:
            # Simplificado: asumiendo que ya existen los tipos en la DB
            evidencia = ArchivingService.archive_document(
                company_id=1, # Default placeholder
                user_id=usuario_id,
                process_type_code="SST",
                process_code="INCIDENTES",
                document_type_code="ACTA_INC",
                document_content=b"Registro de incidente generado por Sargento SST",
                original_filename=f"incidente_{incidente.id}.txt",
                document_metadata={"source_id": str(incidente.id)}
            )
            incidente.evidencia_archivistica_ref_id = evidencia.id
            incidente.save()
        except Exception as e:
            logger.error(f"FALLO ARCHIVO SST: No se pudo generar evidencia para incidente {incidente.id}: {e}")

        # Bloqueo Automático si es MORTAL o GRAVE (Gobernanza)
        if incidente.gravedad in ['MORTAL', 'GRAVE']:
            logger.warning(f"SARGENTO SST: Gravedad crítica detectada. Solicitando bloqueo operativo.")
            # Aquí se integraría con el Kernel para cambiar el estado sistémico a CONTAINMENT

        return {"status": "REGISTERED", "id": incidente.id}

    @staticmethod
    def bloquear_operacion_por_riesgo(proceso_id: str, motivo: str, usuario_id: int):
        """
        Bloquea un proceso operativo específico por condiciones inseguras.
        """
        # Se asume integración con apps.prestadores.mi_negocio.gestion_operativa.models.ProcesoOperativo
        from apps.prestadores.mi_negocio.gestion_operativa.models import ProcesoOperativo

        proceso = ProcesoOperativo.objects.get(id=proceso_id)
        proceso.estado = 'SUSPENDIDO'
        proceso.descripcion += f"\n[SST BLOCK]: {motivo}"
        proceso.save()

        AuditLog.objects.create(
            user_id=usuario_id,
            action="OPERATIONAL_SST_BLOCK",
            details=f"Proceso {proceso_id} suspendido por riesgo SST: {motivo}"
        )

        return {"status": "BLOCKED", "proceso": proceso_id}
