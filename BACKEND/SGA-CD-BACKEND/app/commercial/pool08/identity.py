"""SGA-CD preserves its educational/administrative roles and existing plan permissions."""
from app.models.user import Usuario
from app.models.corporate import CorporateOwner
from app.services.workspace_service import access_for,roles_of
from app.services.role_contracts import ADMIN_TEAM,NAMES
from .access_protocol import AccessFault,NON_DELEGABLE,digest,person
from .access_service import AccessService
from .identity_store import Store
from .contract import capabilities,SYSTEM

GROUPS={
 'crm':{'crm.prospect.manage','quote.prepare','booking.availability.read','landing.lead.capture'},
 'media':{'media.image.generate','media.reel.render','media.image.resize','media.video.resize','landing.page.manage'},
 'publish':{'channel.video.publish','campaign.email.bulk.send','campaign.sms_mms.send','campaign.whatsapp.multimedia.send','ads.campaign.manage'},
 'inbox':{'channel.private_message.reply','channel.public_comment.reply','channel.email.reply'},
}
def resolve_access(db,user):
    ids={row['id'] for row in capabilities()['capabilities']}
    def actor(ref):
        ref=person(str(ref));db.expire_all()
        result=db.query(Usuario).populate_existing().filter_by(id=int(ref),activo=True).first()
        if result is None:raise AccessFault('ACTIVE_LOCAL_ACCOUNT_REQUIRED',403)
        return result
    current=actor(user.id);access=access_for(db,current)
    if access.owner:
        owner=db.get(CorporateOwner,1)
        if not owner or owner.user_id!=current.id:raise AccessFault('PLATFORM_OWNER_BINDING_REQUIRED',403)
    tenant_id=access.tenant.id;scope=access.scope
    def describe(target):
        local=access_for(db,target)
        if local.tenant.id!=tenant_id:raise AccessFault('FOREIGN_LOCAL_ACCOUNT',403)
        roles=roles_of(target);role_rows=[{'id':code,'name':NAMES.get(code,'Administrador general' if code=='admin_general' else code)} for code in sorted(roles)]
        area_ids=sorted(str(item.id) for item in target.areas)
        fingerprint=digest({'namespace':'sga-cd:Usuario/RolesEnum','roles':sorted(roles),'primary_role':getattr(target.rol,'value',str(target.rol)),'tenant':tenant_id,'areas':area_ids,'superior':target.reporta_a_usuario_id})
        manager=bool(local.full and (local.owner or 'admin_empresa' in roles))
        floor=set(ids) if manager else set().union(*(values for key,values in GROUPS.items() if local.permissions.get(key)))
        if not manager:floor-=NON_DELEGABLE
        return {'tenant_ref':scope,'actor_ref':str(target.id),'local_roles':role_rows,'role_fingerprint':fingerprint,'identity_namespace':'sga-cd:Usuario/RolesEnum','local_role_scope':'company' if manager else 'area' if roles&ADMIN_TEAM else 'personal','is_manager':manager,'capability_floor':sorted(floor),'legacy_permissions_authoritative':True,'company_name':local.tenant.nombre_empresa}
    principal=describe(current)
    def subject(ref):
        target=actor(ref)
        if target.inquilino_id!=tenant_id or (not roles_of(target)&(ADMIN_TEAM|{'admin_empresa','admin_general'})):raise AccessFault('LOCAL_TEAM_MEMBER_REQUIRED',403)
        return describe(target)
    def team():
        rows=db.query(Usuario).filter_by(inquilino_id=tenant_id,activo=True).order_by(Usuario.id).limit(101).all()
        eligible=[describe(item) for item in rows if roles_of(item)&(ADMIN_TEAM|{'admin_empresa','admin_general'})]
        return [{'actor_ref':item['actor_ref'],'local_roles':item['local_roles'],'role_fingerprint':item['role_fingerprint'],'is_manager':item['is_manager'],'capability_floor':item['capability_floor']} for item in eligible[:100]],len(rows)>100
    def grantor_valid(ref):
        try:
            target=actor(ref)
            if target.inquilino_id!=tenant_id:return False
            local=describe(target)
            if 'admin_general' in roles_of(target):
                binding=db.get(CorporateOwner,1)
                return bool(binding and binding.user_id==target.id and local['is_manager'])
            return local['is_manager']
        except AccessFault:return False
    return AccessService(Store(db),principal,subject,team,grantor_valid,SYSTEM,ids)
