"""Eight independent rule workers, offline and without payment/approval tools.
Open Duet planning and agent-desktop control use the existing gated engine.
"""
from dataclasses import dataclass
import time
from .workspace import transfer_fields,digest,canonical_uuid,WalletLocalError
from .readiness import pending
ENGINE_SUPPORT={'planner':'Open Duet','device_engine':'agent-desktop','bridge':'DESKTOP/asistencia-sgacd','approval_policy':'existing_control_engine','minimum_human_approvals':2,'offline_money_execution':False}

@dataclass(frozen=True)
class Context:
    draft: dict
    actor: str

class Custodian:
    id='custodio';name='Custodio local';task='Revisa el ámbito del almacén cifrado'
    def run(self,context):
        canonical_uuid(context.actor);canonical_uuid(context.draft['id'])
        return 'LOCAL_ACTOR_FORMAT_VALID'
class CryptographyGuard:
    id='criptografia';name='Guardián criptográfico';task='Comprueba el resumen del borrador sin acceder a privadas'
    def run(self,context):
        if digest(transfer_fields(**context.draft['fields']))!=context.draft['digest']:raise WalletLocalError('DRAFT_INTEGRITY_FAILED')
        return 'DRAFT_DIGEST_MATCHES'
class IntegritySentinel:
    id='integridad';name='Centinela de integridad';task='Exige validación vigente del dispositivo en línea'
    def run(self,context):return 'DEVICE_ATTESTATION_REQUIRED'
class OriginGuard:
    id='antiphishing';name='Vigilante de origen';task='Exige TLS y origen aprobado al reconectar'
    def run(self,context):return 'PINNED_SERVER_ORIGIN_REQUIRED'
class ApprovalCoordinator:
    id='aprobaciones';name='Coordinador de revisiones';task='Verifica dos revisiones locales del mismo solicitante'
    def run(self,context):
        acks=context.draft['acks']
        valid=context.draft['expires_at']>int(time.time()) and len(acks)==2 and all(ack.get('actor')==context.actor and ack.get('digest')==context.draft['digest'] and ack.get('stage')==index+1 for index,ack in enumerate(acks))
        return 'TWO_LOCAL_REVIEWS' if valid else 'LOCAL_REVIEW_PENDING'
class ReconciliationScout:
    id='conciliacion';name='Analista de conciliación';task='Impide confundir borradores con movimientos confirmados'
    def run(self,context):
        if context.draft['state'] not in {'DRAFT','REVIEWED_LOCALLY','READY_FOR_SERVER_REVIEW'}:raise WalletLocalError('OFFLINE_SETTLEMENT_NOT_SUPPORTED')
        return 'NO_SETTLEMENT_AUTHORITY'
class ContinuityWorker:
    id='continuidad';name='Soldado de continuidad';task='Prepara trabajo local sin liquidación desconectada'
    def run(self,context):return 'LOCAL_REVIEW_EXPIRED' if context.draft['expires_at']<=int(time.time()) else 'DRAFT_ONLY_OFFLINE'
class ProductionAuditor:
    id='produccion';name='Inspector de pendientes';task='Mantiene visibles las validaciones reales pendientes'
    def run(self,context):return 'PRODUCTION_BLOCKED' if pending() else 'RELEASE_REVIEW_REQUIRED'
SOLDIERS=(Custodian(),CryptographyGuard(),IntegritySentinel(),OriginGuard(),ApprovalCoordinator(),ReconciliationScout(),ContinuityWorker(),ProductionAuditor())

def catalog():
    return [{'id':worker.id,'name':worker.name,'task':worker.task,'engine_support':dict(ENGINE_SUPPORT),'mode':'local_rules_and_gated_planning','can_approve':False,'can_execute_payments':False} for worker in SOLDIERS]

def review_draft(draft,local_actor):
    context=Context(draft,local_actor)
    # Only fixed findings leave workers; no notes, account IDs, amounts or secrets.
    return {'agents':[{'id':worker.id,'status':worker.run(context)} for worker in SOLDIERS],
            'requires_fresh_server_intent':True,'requires_two_hardware_approvals':True,'settled':False,'automatic_dispatch':False}
