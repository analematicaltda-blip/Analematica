"""Own CRM after-sales boundary over the existing reviewed cancellation/refund engine.
No customer/reservation IDs are equated, no bank refund or consent is inferred.
"""
from .crm import CRMError,text

def execute(crm,user,operation,data):
    from apps.prestadores.mi_negocio.gestion_comercial.cancellation_views import OPERATIONS
    from apps.prestadores.mi_negocio.gestion_comercial import cancellation_policies as engine
    from apps.core_erp.accounting.exceptions import AccountingError
    access=crm.authorize()
    if not access.principal['is_manager']:raise CRMError('LOCAL_ADMINISTRATOR_REQUIRED',403)
    if operation=='followup':
        if not isinstance(data,dict) or set(data)!={'request_id','contact_id','expected_revision','reservation_id','title','due_at','responsible_ref'}:raise CRMError('INVALID_AFTER_SALES_FIELDS')
        try:engine.case_state(actor=user,provider_id=crm.store.provider,reservation_id=data['reservation_id'])
        except (AccountingError,ValueError,TypeError,KeyError):raise CRMError('AFTER_SALES_REVIEW_REQUIRED',409) from None
        from .after_sales_followup import record_followup
        result=record_followup(crm,data)
        return {'result':result,'reservation_ref':data['reservation_id'],'customer_binding_verified':False,'outbound_message_sent':False}
    if not isinstance(operation,str) or operation not in OPERATIONS or not isinstance(data,dict):raise CRMError('INVALID_AFTER_SALES_OPERATION')
    expected=OPERATIONS[operation];variants=(expected,expected|{'cancellation_at'}) if operation=='review_case' else (expected,)
    if set(data) not in variants:raise CRMError('INVALID_AFTER_SALES_FIELDS')
    # Actor/company/provider come only from freshly authenticated native context.
    try:result=getattr(engine,operation)(actor=user,provider_id=crm.store.provider,**data)
    except AccountingError:raise CRMError('AFTER_SALES_REVIEW_REQUIRED',409) from None
    except (ValueError,TypeError,KeyError):raise CRMError('INVALID_AFTER_SALES_DATA') from None
    return {'result':result,'context':{'system':crm.store.system,'company_ref':crm.store.scope,'provider_ref':crm.store.provider,'actor_ref':crm.actor},'crm_customer_binding_inferred':False}
