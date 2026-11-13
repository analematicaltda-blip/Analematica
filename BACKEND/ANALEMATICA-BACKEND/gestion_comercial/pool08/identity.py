"""Native roles stay local. Verified company ownership never comes from a role label."""
from django.contrib.auth import get_user_model
from api.models import BusinessUserProfile
from apps.turismo.models import VerifiedCompanyLink
from apps.core_erp.accounting.agent_army_runtime import authority,identifier
from .access_protocol import AccessFault,NON_DELEGABLE,digest,person
from .access_service import AccessService
from apps.core_erp.accounting.exceptions import AccountingError
from .identity_store import Store
from .contract import SYSTEM,capabilities

BUSINESS_ROLES={'PRESTADOR','BUSINESS_OWNER','BUSINESS_ADMIN','BUSINESS_OPERATOR','BUSINESS_EMPLOYEE','ARTESANO','EVENT_MANAGER'}
def resolve_access(user,provider_id):
    provider_id=identifier(provider_id)
    link=VerifiedCompanyLink.objects.select_related('provider','administrator').filter(provider_id=provider_id).first()
    if link is None:raise AccessFault('VERIFIED_LOCAL_COMPANY_REQUIRED',403)
    try:company,owner,provider=authority(link.administrator,provider_id)
    except AccountingError:raise AccessFault('ACTIVE_LOCAL_ADMINISTRATOR_REQUIRED',403) from None
    User=get_user_model();ids={row['id'] for row in capabilities()['capabilities']}
    def actor(ref):
        ref=person(str(ref));target=User.objects.filter(pk=int(ref),is_active=True,is_agent=False).first()
        if target is None:raise AccessFault('ACTIVE_PERSONAL_ACCOUNT_REQUIRED',403)
        if target.pk!=owner.pk:
            if target.role not in BUSINESS_ROLES or not BusinessUserProfile.objects.filter(user_id=target.pk,provider_id=provider_id).exists():
                raise AccessFault('SCOPED_LOCAL_BUSINESS_MEMBERSHIP_REQUIRED',403)
        return target
    def describe(target):
        owner_now=target.pk==owner.pk
        roles=[{'id':str(target.role),'name':str(target.get_role_display())}]
        global_roles=list(target.global_roles.order_by('pk').values('id','name'))
        for role in global_roles:roles.append({'id':str(role['id']),'name':role['name']})
        signature=digest({'namespace':SYSTEM+':api.CustomUser','role':target.role,'global_roles':roles,'provider':provider_id,'tenant':str(company.pk)})
        return {'tenant_ref':str(company.pk),'actor_ref':str(target.pk),'identity_namespace':SYSTEM+':api.CustomUser/local_global_roles','local_roles':roles,'local_role_scope':'owned_company' if owner_now else 'explicit_provider_membership','role_fingerprint':signature,'is_manager':owner_now,'capability_floor':sorted(ids if owner_now else ids-NON_DELEGABLE),'legacy_permissions_authoritative':False,'company_name':company.name}
    current=actor(user.pk)
    def subject(ref):return describe(actor(ref))
    def team():
        members=list(BusinessUserProfile.objects.filter(provider_id=provider_id,user__is_active=True,user__is_agent=False).order_by('user_id').values_list('user_id',flat=True)[:101])
        refs=[owner.pk]+[key for key in members if key!=owner.pk]
        rows=[]
        for ref in refs[:100]:
            try:value=describe(actor(ref))
            except AccessFault:continue
            rows.append({key:value[key] for key in ('actor_ref','local_roles','role_fingerprint','is_manager','capability_floor')})
        return rows,len(refs)>100
    def grantor_valid(ref):
        if str(ref)!=str(owner.pk):return False
        try:authority(User.objects.get(pk=owner.pk),provider_id);return True
        except Exception as error:
            from rest_framework.exceptions import APIException
            if isinstance(error,(APIException,AccountingError,User.DoesNotExist)):return False
            raise
    return AccessService(Store(),describe(current),subject,team,grantor_valid,SYSTEM,ids)
