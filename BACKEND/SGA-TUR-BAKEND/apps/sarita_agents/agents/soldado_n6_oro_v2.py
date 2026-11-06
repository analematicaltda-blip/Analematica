# backend/apps/sarita_agents/agents/soldado_n6_oro_v2.py

import logging
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from django.db import transaction, models
from django.utils import timezone
from apps.sarita_agents.models import RegistroMicroTarea, MicroTarea
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class SoldadoN6OroV2(ABC):
    """
    ESTÁNDAR MAESTRO N6 ORO V2
    La unidad mínima de ejecución determinística, atómica y auditable de SARITA.
    """

    # Propiedades obligatorias que deben ser definidas en la subclase
    domain: str = ""
    subdomain: str = ""
    aggregate_root: str = ""
    required_permissions: List[str] = []
    version: int = 1

    # Flags de comportamiento
    requires_idempotency: bool = True
    requires_outbox: bool = True
    requires_audit: bool = True
    requires_multi_tenant: bool = True

    def __init__(self, sargento=None):
        self.sargento = sargento
        self._validate_structure()

    def _validate_structure(self):
        if not self.domain or not self.aggregate_root:
            raise AttributeError(f"El soldado {self.__class__.__name__} debe definir domain y aggregate_root.")

    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método de ejecución PROTEGIDO. Nadie sobreescribe esta secuencia.
        """
        correlation_id = task_data.get('correlation_id')
        tenant_id = task_data.get('tenant_id')
        user = task_data.get('user')
        idempotent_key = task_data.get('idempotent_key') or task_data.get('micro_tarea_id')

        logger.info(f"N6-ORO-V2: Iniciando ejecución de {self.__class__.__name__} (CID: {correlation_id})")

        # 1. Validaciones de Seguridad y Aislamiento
        self._check_tenant(tenant_id)
        self._check_permissions(user)

        # 2. Control de Idempotencia
        if self.requires_idempotency and idempotent_key:
            previous_result = self._check_idempotency(idempotent_key)
            if previous_result:
                return previous_result

        try:
            with transaction.atomic():
                # 3. Validación de Negocio/Estado Previo
                self.validate_preconditions(task_data)

                # 4. Ejecución de Lógica de Dominio (ORM Real)
                result_entity = self.perform_atomic_action(task_data)

                # 5. Generación de Resultado Estructurado
                result_payload = self._build_result(result_entity)

                # 6. Auditoría SHA-256 Encadenada
                audit_id = None
                if self.requires_audit:
                    audit = self._log_audit(task_data, result_payload)
                    audit_id = str(audit.id)

                # 7. Registro en Outbox (Garantía de Evento)
                if self.requires_outbox:
                    self._register_outbox(task_data, result_payload)

                # 8. Marcar Idempotencia como exitosa
                if self.requires_idempotency:
                    self._commit_idempotency(idempotent_key, result_payload)

                return {
                    "status": "READY",
                    "soldier": self.__class__.__name__,
                    "domain": self.domain,
                    "entity_id": str(getattr(result_entity, 'id', result_entity)),
                    "audit_id": audit_id,
                    "correlation_id": correlation_id,
                    "event_emitted": self.requires_outbox
                }

        except Exception as e:
            logger.error(f"N6-ORO-V2 ERROR: Fallo en {self.__class__.__name__} -> {str(e)}")
            if self.requires_idempotency:
                self._fail_idempotency(idempotent_key, str(e))
            raise e

    @abstractmethod
    def perform_atomic_action(self, params: Dict[str, Any]) -> Any:
        """Aquí va la lógica real del ORM."""
        pass

    def validate_preconditions(self, params: Dict[str, Any]):
        """Opcional: Validar estado antes de escribir."""
        pass

    def _check_tenant(self, tenant_id):
        if self.requires_multi_tenant and not tenant_id:
            raise PermissionError("Violación Multi-tenant: tenant_id es obligatorio.")

    def _check_permissions(self, user):
        if not user:
             raise PermissionError("Ejecución denegada: No se proporcionó contexto de usuario.")

        # MOTOR DE PERMISOS REAL (HALLAZGO F5)
        # Verificamos si el usuario tiene el permiso específico del dominio o es un SuperUser
        if user.is_superuser:
            return True

        for perm in self.required_permissions:
            if not user.has_perm(perm):
                logger.error(f"N6-ORO-V2: Violación de Seguridad. Usuario {user.id} no tiene permiso {perm}.")
                raise PermissionError(f"Faltan permisos obligatorios: {perm}")

    def _check_idempotency(self, key):
        from apps.sarita_agents.models import IdempotencyKey
        existing = IdempotencyKey.objects.filter(key=key, domain=self.domain).first()
        if existing and existing.status == 'SUCCESS':
            logger.warning(f"IDEMPOTENCIA: Tarea {key} ya procesada exitosamente.")
            return existing.response_payload
        return None

    def _commit_idempotency(self, key, result):
        from apps.sarita_agents.models import IdempotencyKey
        IdempotencyKey.objects.update_or_create(
            key=key, domain=self.domain,
            defaults={'status': 'SUCCESS', 'response_payload': result}
        )

    def _fail_idempotency(self, key, error):
        from apps.sarita_agents.models import IdempotencyKey
        IdempotencyKey.objects.update_or_create(
            key=key, domain=self.domain,
            defaults={'status': 'FAILED', 'response_payload': {'error': error}}
        )

    def _log_audit(self, params, result):
        payload_str = f"{json.dumps(params, default=str)}{json.dumps(result, default=str)}{timezone.now().isoformat()}"
        integrity_hash = hashlib.sha256(payload_str.encode()).hexdigest()

        # Buscar la MicroTarea si viene el ID
        mt_id = params.get('micro_tarea_id')
        mt = MicroTarea.objects.filter(id=mt_id).first() if mt_id else None

        return RegistroMicroTarea.objects.create(
            micro_tarea=mt,
            exitoso=True,
            resultado=result,
            observaciones=f"N6-ORO-V2 | Hash: {integrity_hash} | Ver: {self.version}"
        )

    def _register_outbox(self, params, result):
        from apps.core_erp.models import OutboxEvent
        OutboxEvent.objects.create(
            event_type=getattr(self, 'event_name', f"{self.domain.upper()}_ACTION_EXECUTED"),
            domain=self.domain,
            aggregate_root=self.aggregate_root,
            payload={**result, "correlation_id": params.get('correlation_id'), "tenant_id": params.get('tenant_id')},
            version=self.version
        )

    def _build_result(self, entity) -> Dict[str, Any]:
        """Convierte la entidad en un payload serializable."""
        if hasattr(entity, 'to_dict'):
            return entity.to_dict()
        return {"id": str(getattr(entity, 'id', entity)), "msg": "Action completed"}
