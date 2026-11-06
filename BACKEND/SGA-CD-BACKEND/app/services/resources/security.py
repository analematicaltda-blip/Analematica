"""Minimal same-user audit export for an independently deployed AiSOC; never transmit automatically."""
import hashlib
import json
from datetime import datetime,timezone
from app.models.assistance import ControlApproval,ControlJob
from app.services.assistance import control_crypto as crypto
from app.services.assistance.control import POLICY_DATA

def status():
    return {'integration':'aisoc','source_copied':True,'deployment':'not_verified','telemetry_transport':'manual_signed_export_only','outbound_requests':False,'automatic_response_enabled':False,'existing_control_authorizations':'two_same_requesting_admin_plus_impact_for_mutations','coverage':['control_approval_metadata_only'],'not_covered':['authentication_denials','host_intrusion','network_traffic','database_activity','mobile_os_telemetry'],'requirements':{'core_services_claim':16,'ram_gib_claim':8,'free_disk_gib_claim':20,'source':'SEGURIDAD/AiSOC/AGENTS.md'},'notice':'Copiar el SOC no significa que esté funcionando ni que exista protección activa. Un permiso normal es información de auditoría, no una amenaza.'}

def export(db,who,after_id=0,limit=100):
    rows=db.query(ControlApproval,ControlJob).join(ControlJob,ControlJob.id==ControlApproval.job_id).filter(ControlApproval.user_id==who.user_id,ControlApproval.tenant_id==who.tenant_id,ControlJob.user_id==who.user_id,ControlJob.tenant_id==who.tenant_id,ControlApproval.id>after_id).order_by(ControlApproval.id).limit(limit+1).all()
    more=len(rows)>limit;rows=rows[:limit];events=[]
    for approval,job in rows:
        intent=json.loads(crypto.decrypt(job.intent))
        # No destination URLs, message content, account names, prompts, tokens or device names.
        platform=intent.get('platform');operation=intent.get('operation')
        if platform not in POLICY_DATA['platform_hosts'] or operation not in POLICY_DATA['operations']:continue
        identifier=hashlib.sha256(('sgacd-approval:'+job.id+':'+str(approval.stage)).encode()).hexdigest()
        events.append({'id':identifier,'timestamp':datetime.fromtimestamp(approval.created_at,timezone.utc).isoformat().replace('+00:00','Z'),'severity':'info','title':'SGA-CD control authorization recorded','action':'control.authorize','outcome':'success','user_id':str(who.user_id),'resource_id':job.id,'authorization_stage':approval.stage,'required_authorizations':job.required,'platform':platform,'operation':operation,'plan_digest':approval.digest,'is_synthetic':False,'source_provenance':'sgacd_control_approval_database','is_security_finding':False})
    payload={'schema':'sgacd-aisoc-audit-export-v1','provenance':'database_snapshot_not_aisoc_investigation_ledger','scope':'requesting_user_and_tenant_only','source_tenant_id':who.tenant_id,'source_user_id':who.user_id,'after_id':after_id,'next_after_id':rows[-1][0].id if rows else after_id,'has_more':more,'transport':'manual_not_sent','ingest_batch':{'connector_id':'sgacd-control-audit','connector_type':'sgacd_control_audit','events':events}}
    return {**crypto.sign(payload),'algorithm':'Ed25519','public_key':crypto.public_key(),'notice':'Firma de exportación SGA-CD; no demuestra que AiSOC haya recibido eventos ni crea un ledger inmutable. Verifica con una clave pública confiada por separado. El token de ingestión AiSOC debe pertenecer al tenant de destino autorizado.'}
