"""Fixed shared-ledger commands: two owner reviews, no provider/URL override.

Authorization is checked again immediately before dispatch. The two databases do
not share a transaction: a timeout after dispatch has an unknown outcome and must
be retried with the same persisted review, never a new fabricated confirmation.
"""
import json,re,hashlib
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import Usuario
from app.services import corporate_ledger as ledger

READS={'purchase_accounts':'cuentas-compras-nativas/','environmental_corrections':'historia-correccion-ambiental/','environmental_state':'estado-medicion-ambiental/','hotel_sources':'fuentes-indicadores-hoteleros/','hotel_metrics':'indicadores-hoteleros/','bank_sources':'fuentes-conciliacion-bancaria/','bank_reconciliation_state':'estado-conciliacion-bancaria/','payroll_sources':'fuentes-nomina-revisada/','payroll_status':'estado-nomina-revisada/','opening':'estado-apertura/','tax_policy_history':'politicas-tributarias/','status':'estado-reconocimiento/','dian':'diagnostico-dian/','sources':'fuentes-reserva-fiscal/','accounts':'cuentas-reconocimiento/'}
COST_COMMANDS={'operation_labor_costs', 'payroll_cost_state', 'record_payroll_costs', 'payroll_cost_sources', 'review_payroll_costs'}
COMMANDS={
 'payroll_cost_sources':('fuentes-costos-operativos-nomina/',{'payroll_id'},set()),
 'review_payroll_costs':('revisar-costos-operativos-nomina/',{'expected_revision', 'reason_code', 'capacities', 'confirmed', 'operation_centers', 'payroll_id', 'evidence_digest'},set()),
 'record_payroll_costs':('registrar-costos-operativos-nomina/',{'review_id', 'payroll_id', 'confirmed'},set()),
 'payroll_cost_state':('estado-costos-operativos-nomina/',{'payroll_id'},set()),
 'operation_labor_costs':('costos-laborales-operacion/',{'until', 'order_id', 'since'},set()),

 'native_supplier_sources':('proveedores-compras-nativas/',{'after_id'},set()),
 'record_native_supplier':('registrar-proveedor-nativo/',{'evidence_digest', 'confirmed', 'request_id', 'name', 'identification'},set()),
 'record_native_purchase':('registrar-factura-compra-nativa/',{'evidence_digest', 'subtotal', 'gross', 'number', 'confirmed', 'issue_date', 'document_digest', 'request_id', 'due_date', 'tax', 'supplier_id'},set()),
 'review_native_purchase':('revisar-compra-nativa/',{'evidence_digest', 'selection', 'economic_fact', 'invoice_id', 'expected_revision', 'confirmed', 'settlement_account_id'},set()),
 'post_native_purchase':('contabilizar-compra-nativa/',{'confirmed', 'invoice_id', 'review_id'},set()),
 'native_purchase_state':('estado-compra-nativa/',{'invoice_id'},set()),
 'native_purchase_sources':('fuentes-compras-nativas/',{'after_id'},set()),
 'review_native_purchase_reversal':('revisar-contrapartida-compra-nativa/',{'evidence_digest', 'confirmed', 'invoice_id', 'reason_code'},set()),
 'reverse_native_purchase':('contrapartida-compra-nativa/',{'confirmed', 'invoice_id', 'review_id'},set()),

 'review_commercial_tax_reversal':('revisar-contrapartida-tributaria/',{'document_id','reason_code','evidence_digest','confirmed'},set()),
 'reverse_commercial_tax':('contrapartida-tributaria/',{'document_id','review_id','confirmed'},set()),
 'review_commercial_tax':('revisar-hecho-tributario/',{'fact','evidence_digest','expected_revision','confirmed'},set()),
 'post_commercial_tax':('contabilizar-hecho-tributario/',{'document_id','review_id','confirmed'},set()),
 'commercial_tax_state':('estado-hecho-tributario/',{'document_id'},set()),
 'review_reservation_policy':('revisar-reserva-con-politica/',{'reservation_id','selection','economic_date','evidence_digest','confirmed','expected_revision'},set()),
 'review_environmental_correction':('revisar-correccion-ambiental/',{'observation_id','expected_revision','activities','factors','evidence_digest','reason_code','confirmed'},set()),
 'record_environmental_correction':('registrar-correccion-ambiental/',{'observation_id','review_id','confirmed'},set()),
 'prepare_financial_rehearsal':('preparar-simulacion-financiera/',{'intent','confirmed'},set()),
 'confirm_financial_rehearsal':('confirmar-simulacion-financiera/',{'request_id','plan_digest','step','confirmed'},set()),
 'simulate_financial_rehearsal':('simular-orden-financiera/',{'request_id','plan_digest','impact_confirmation','confirmed'},set()),
 'cancel_financial_rehearsal':('cancelar-simulacion-financiera/',{'request_id','plan_digest','confirmed'},set()),
 'review_environmental':('revisar-medicion-ambiental/',{'activities','factors','evidence_digest','confirmed'},set()),
 'record_environmental':('registrar-medicion-ambiental/',{'review_id','confirmed'},set()),
 'estimate_environmental':('estimar-impacto-ambiental/',{'activities','factors'},set()),
 'review_hotel_capacity':('revisar-capacidad-hotelera/',{'day','room_ids','mapping','evidence_digest','expected_revision','confirmed'},set()),
 'record_hotel_capacity':('registrar-capacidad-hotelera/',{'review_id','confirmed'},set()),
 'compare_bank_statement':('comparar-extracto/',{'account_id','csv_text'},set()),
 'review_bank_reconciliation':('revisar-conciliacion-bancaria/',{'account_id','csv_text','evidence_digest','expected_revision','confirmed'},{'resolutions','period'}),
 'confirm_bank_reconciliation':('confirmar-conciliacion-bancaria/',{'statement_id','review_id','confirmed'},set()),
 'review_bank_release':('revisar-liberacion-bancaria/',{'reconciliation_id','reason_code','evidence_digest','confirmed'},set()),
 'confirm_bank_release':('confirmar-liberacion-bancaria/',{'review_id','confirmed'},set()),
 'review_payroll':('revisar-nomina/',{'payroll_id','policy','workers','account_mapping','evidence_digest','expected_revision','confirmed'},set()),
 'post_payroll':('contabilizar-nomina-revisada/',{'payroll_id','review_id','confirmed'},set()),
 'review_opening':('revisar-apertura/',{'entry_date','evidence_digest','expected_revision','confirmed'},{'existing_journal_id'}),
 'apply_opening':('aplicar-apertura/',{'review_id','confirmed'},set()),
 'review_tax_policy':('revisar-politica-tributaria/',{'policy','evidence_digest','expected_revision','confirmed'},set()),
 'record_tax_policy':('registrar-politica-tributaria/',{'review_id','confirmed'},set()),
 'quote_tax_policy':('calcular-politica-tributaria/',{'code','revision','economic_date','net','tax_category','direction'},set()),
 'query':('consulta-contable/',{'question'},{'since','until'}),
 'review_recognition':('revisar-reconocimiento-reserva/',{'reservation_id','fiscal_review_id','entry_date','account_mapping','service_evidence_digest','policy_evidence_digest','economic_fact','confirmed','expected_revision'},{'advance_allocation'}),
 'post_recognition':('contabilizar-reserva/',{'reservation_id','review_id','confirmed'},set()),
 'review_reversal':('revisar-contrapartida-reserva/',{'reservation_id','reason','evidence_digest','confirmed'},set()),
 'reverse_recognition':('contrapartida-reserva/',{'reservation_id','review_id','confirmed'},set()),
}
NATIVE_COMMANDS={'native_supplier_sources','record_native_supplier', 'record_native_purchase', 'reverse_native_purchase', 'post_native_purchase', 'review_native_purchase_reversal', 'native_purchase_sources', 'review_native_purchase', 'native_purchase_state'}
FIELDS=['owner_id','reviewer_id','ledger_actor_id','provider_id','tenant_id','evidence_digest','valid_until']

def context(db,user,session_cookie):
    link=ledger.require_binding(db,user)
    if not isinstance(session_cookie,str) or not re.fullmatch('[a-z0-9]{32}',session_cookie):raise HTTPException(403,'Se requiere sesión contable vigente del titular.')
    return {k:getattr(link,k) for k in FIELDS}

def recheck(db,user,selected):
    with Session(bind=db.get_bind(),autoflush=False) as fresh_db:
        fresh=fresh_db.get(Usuario,user.id)
        if fresh is None:raise HTTPException(403,'Titular corporativo no vigente.')
        link=ledger.require_binding(fresh_db,fresh)
        if any(getattr(link,k)!=v for k,v in selected.items()):raise HTTPException(403,'El vínculo cambió; vuelve a revisar la operación.')

def identity(transport,target,cookie,selected):
    found=ledger.fetch(transport,target+ledger.BASE+'identidad-contable/',cookie,{'provider_id':selected['provider_id']})
    if not isinstance(found,dict) or any(str(found.get(k))!=selected[v] for k,v in [('company_id','tenant_id'),('provider_id','provider_id'),('actor_id','ledger_actor_id')]):
        raise HTTPException(403,'La sesión ERP no corresponde al vínculo corporativo.')

def read_sources(db,*,user,session_cookie,resource,parameters=None):
    if resource not in READS:raise HTTPException(422,'Consulta contable no admitida.')
    parameters=parameters or {}
    allowed={'observation_id'} if resource=='environmental_corrections' else {'review_id'} if resource=='environmental_state' else {'since','until','as_of'} if resource=='hotel_metrics' else {'account_id','source_digest'} if resource=='bank_reconciliation_state' else {'payroll_id'} if resource=='payroll_status' else {'code','before_revision'} if resource=='tax_policy_history' else {'reservation_id','before_revision'} if resource=='status' else ({'despues_id'} if resource=='sources' else {'paged','despues_id','buscar'} if resource in {'accounts','purchase_accounts'} else set())
    if (resource=='environmental_corrections' and set(parameters)!={'observation_id'}) or (resource=='environmental_state' and set(parameters)!={'review_id'}) or (resource=='hotel_metrics' and not {'since','until'}<=set(parameters)) or (resource=='bank_reconciliation_state' and set(parameters)!={'account_id','source_digest'}) or set(parameters)-allowed or (resource=='status' and 'reservation_id' not in parameters) or (resource=='payroll_status' and 'payroll_id' not in parameters):raise HTTPException(422,'Parámetros de fuente inválidos.')
    selected=context(db,user,session_cookie);target=ledger.origin()
    try:
        with ledger.client() as transport:
            identity(transport,target,session_cookie,selected)
            data=ledger.fetch(transport,target+ledger.BASE+READS[resource],session_cookie,{'provider_id':selected['provider_id'],**parameters})
    except ledger.httpx.HTTPError:raise HTTPException(503,'No se pudo consultar la fuente contable.') from None
    recheck(db,user,selected)
    if not isinstance(data,dict) or data.get('company_id')!=selected['tenant_id'] or data.get('read_only') is not True:raise HTTPException(503,'Fuente contable incompatible.')
    if resource=='environmental_corrections':
        flags=['ledger_written','money_transferred','liability_recognized','carbon_credit_issued','independently_verified','esg_certified','confirmations_restored']
        if data.get('observation_id')!=parameters['observation_id'] or any(data.get(k) is not False for k in flags) or data.get('original_preserved') is not True or data.get('effective_total_replaces_original') is not True or type(data.get('revision')) is not int or not 0<=data['revision']<=100 or not isinstance(data.get('history'),list) or len(data['history'])!=data['revision']:
            raise HTTPException(503,'Historia ambiental incompatible.')
    if resource=='bank_reconciliation_state' and data.get('applied') is not None:
        from app.services.bank_resolution_contract import result as validate_bank
        try:validate_bank(data['applied'])
        except (ValueError,TypeError,KeyError):raise HTTPException(503,'Cobertura bancaria recuperada incompatible.') from None
    return data

def dispatch(db,*,user,session_cookie,operation,payload):
    if operation not in COMMANDS:raise HTTPException(422,'Operación contable no admitida.')
    path,required,optional=COMMANDS[operation]
    if not isinstance(payload,dict) or not required<=set(payload) or set(payload)-required-optional or (operation not in {'query','quote_tax_policy','compare_bank_statement','estimate_environmental','commercial_tax_state','native_purchase_state','native_purchase_sources','native_supplier_sources','payroll_cost_sources','payroll_cost_state','operation_labor_costs'} and payload.get('confirmed') is not True):
        raise HTTPException(422,'Contrato o confirmación contable inválidos.')
    selected=context(db,user,session_cookie);target=ledger.origin()
    try:
        with ledger.client() as transport:
            identity(transport,target,session_cookie,selected)
            # CSRF is obtained only from the fixed ERP origin; never from callers.
            session=ledger.fetch(transport,target+'/api/v1/erp-session/',session_cookie,{})
            if not isinstance(session,dict) or session.get('authenticated') is not True or str((session.get('user') or {}).get('id'))!=selected['ledger_actor_id'] or not re.fullmatch('[a-zA-Z0-9]{64}',session.get('csrf_token','')):
                raise HTTPException(403,'La sesión contable requiere autenticación vigente.')
            csrf_cookie=transport.cookies.get('sgacd_erp_tur_csrf')
            if not isinstance(csrf_cookie,str) or not re.fullmatch('[a-zA-Z0-9]{32}',csrf_cookie):raise HTTPException(503,'No se pudo verificar la protección CSRF del ERP.')
            recheck(db,user,selected)
            headers={'Cookie':ledger.COOKIE+'='+session_cookie+'; sgacd_erp_tur_csrf='+csrf_cookie,'X-CSRFToken':session['csrf_token'],'Origin':target,'Referer':target+'/','Accept-Encoding':'identity'}
            with transport.stream('POST',target+ledger.BASE+path,params={'provider_id':selected['provider_id']},json=payload,headers=headers) as response:
                if response.status_code in (400,401,403,409,422):raise HTTPException(409,'El ERP rechazó la operación. Revisa fuente, identidad, periodo y aprobaciones.')
                if response.status_code!=200:raise HTTPException(503,'Resultado no confirmado. Consulta y reintenta la misma revisión; no crees otra operación.')
                if response.headers.get('content-encoding','identity')!='identity':raise HTTPException(503,'Resultado no verificable; consulta la revisión original.')
                chunks=[];size=0
                for chunk in response.iter_bytes(chunk_size=8192):
                    size+=len(chunk)
                    if size>ledger.MAX_RESPONSE:raise HTTPException(503,'Resultado demasiado grande; consulta la revisión original.')
                    chunks.append(chunk)
            raw=json.loads(b''.join(chunks));data=raw['data'] if isinstance(raw,dict) and raw.get('success') is True else raw
    except (ledger.httpx.HTTPError,ValueError):raise HTTPException(503,'Resultado no confirmado. Reintenta con la misma revisión persistida para evitar duplicados.') from None
    if not isinstance(data,dict):raise HTTPException(503,'Resultado contable incompatible; consulta la revisión original.')
    if operation in COST_COMMANDS:
        from app.services.payroll_cost_contract import validate as validate_cost
        try:validate_cost(operation,data,payload,selected)
        except (ValueError,TypeError,KeyError,AttributeError):raise HTTPException(503,'Resultado de costos incompatible; consulta la misma revisión.') from None
        return {'schema':'sgacd-corporate-ledger-command-v1','company_id':selected['tenant_id'],'operation':operation,'source':'authenticated_shared_ledger','data':data,'dispatch_authorized':True,'cross_database_atomic':False}
    if operation in NATIVE_COMMANDS:
        from app.services.native_purchase_contract import validate as validate_native
        try:validate_native(operation,data,payload,selected)
        except (ValueError,TypeError,KeyError):raise HTTPException(503,'Resultado nativo de compra incompatible; consulta la misma fuente.') from None
        return {'schema':'sgacd-corporate-ledger-command-v1','company_id':selected['tenant_id'],'operation':operation,'source':'authenticated_shared_ledger','data':data,'dispatch_authorized':True,'cross_database_atomic':False}
    if operation in {'review_commercial_tax','post_commercial_tax','commercial_tax_state','review_commercial_tax_reversal','reverse_commercial_tax'}:
        if data.get('company_id')!=selected['tenant_id']:raise HTTPException(503,'Empresa tributaria incompatible.')
        if operation=='commercial_tax_state':
            if data.get('document_id')!=payload['document_id'] or data.get('read_only') is not True or data.get('confirmations_restored') is not False:raise HTTPException(503,'Recuperación tributaria incompatible.')
            return {'schema':'sgacd-corporate-ledger-command-v1','company_id':selected['tenant_id'],'operation':operation,'source':'authenticated_shared_ledger','data':data,'dispatch_authorized':True,'cross_database_atomic':False}
        if data.get('regulatory_verified') is not False or data.get('money_transferred') is not False:raise HTTPException(503,'Aceptación o pago no acreditados.')
        if operation in {'post_commercial_tax','reverse_commercial_tax'} and (data.get('document_id')!=payload['document_id'] or data.get('fiscal_document_created') is not False):raise HTTPException(503,'Documento tributario incompatible.')
    if operation=='review_reservation_policy':
        preview=data.get('preview',{})
        flags=['ledger_written','fiscal_accepted','fiscal_document_created','money_transferred','regulatory_verified','withholding_posted']
        if data.get('company_id')!=selected['tenant_id'] or data.get('reservation_id')!=payload['reservation_id'] or any(data.get(k) is not False for k in flags) or data.get('stored_policy_link_verified') is not True or preview.get('selection')!=sorted(payload['selection'],key=lambda row:row['item_id']) or preview.get('economic_date')!=payload['economic_date'] or preview.get('fiscal_review_id')!=data.get('review_id') or preview.get('company_id')!=selected['tenant_id']:
            raise HTTPException(503,'Desglose tributario sin correspondencia verificable.')
        if not re.fullmatch('[0-9a-f]{64}',str(data.get('policy_link_digest',''))):raise HTTPException(503,'Falta evidencia del vínculo tributario.')
    if operation in {'review_bank_reconciliation','confirm_bank_reconciliation'}:
        from app.services.bank_resolution_contract import preview as validate_bank_preview,result as validate_bank_result
        try:
            if operation=='review_bank_reconciliation' and payload.get('resolutions') is not None:validate_bank_preview(data['preview'],payload['resolutions'])
            if operation=='review_bank_reconciliation' and payload.get('period') is not None:
                from app.services.bank_resolution_contract import period as validate_period
                validate_period(data['preview']['period_assessment'],payload['period'])
            if operation=='confirm_bank_reconciliation':validate_bank_result(data)
        except (ValueError,TypeError,KeyError):raise HTTPException(503,'Cobertura o resoluciones bancarias incompatibles.') from None
    if operation=='estimate_environmental':
        flags=['ledger_written','money_transferred','liability_recognized','carbon_credit_issued','esg_certified','factor_sources_independently_verified']
        if data.get('schema')!='sgacd-environmental-estimate-v1' or data.get('company_id')!=selected['tenant_id'] or data.get('read_only') is not True or any(data.get(k) is not False for k in flags) or not re.fullmatch('[0-9a-f]{64}',str(data.get('assessment_digest',''))):raise HTTPException(503,'Estimación ambiental sin alcance verificable.')
        try:
            snapshot=data['snapshot']
            digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
            if snapshot.get('company_id')!=selected['tenant_id'] or snapshot.get('activities')!=sorted(payload['activities'],key=lambda a:a['id']) or snapshot.get('factors')!=sorted(payload['factors'],key=lambda f:f['id']) or digest!=data['assessment_digest']:raise ValueError('Environmental source mismatch')
        except (KeyError,TypeError,ValueError,AttributeError):raise HTTPException(503,'La estimación no corresponde a las fuentes solicitadas.') from None
    if operation=='query':
        if data.get('schema')!='sgacd-accounting-query-v1' or data.get('company_id')!=selected['tenant_id'] or data.get('read_only') is not True or any(data.get(k) is not False for k in ['generated_sql','external_model_used','financial_action_authorized','ledger_written']):raise HTTPException(503,'Consulta sin alcance verificable.')
    if operation=='quote_tax_policy' and (data.get('schema')!='sgacd-tax-quote-v1' or data.get('read_only') is not True or data.get('fiscal_document_created') is not False):raise HTTPException(503,'Cotización tributaria incompatible.')
    if operation in {'review_payroll','post_payroll','review_tax_policy','record_tax_policy','quote_tax_policy'} and data.get('regulatory_verified') is not False:raise HTTPException(503,'No se acredita validación normativa.')
    if operation in {'review_payroll','post_payroll','review_opening','apply_opening','review_tax_policy','record_tax_policy','quote_tax_policy'} and data.get('company_id')!=selected['tenant_id']:raise HTTPException(503,'Contexto de resultado incompatible.')
    if operation in {'review_payroll','post_payroll'}:
        try:payroll_id=str(UUID(str(payload['payroll_id'])))
        except (ValueError,TypeError):raise HTTPException(503,'Identidad de nómina incompatible.') from None
        if operation=='review_payroll' and (data.get('preview',{}).get('snapshot',{}).get('payroll_id')!=payroll_id or data.get('preview',{}).get('snapshot',{}).get('company_id')!=selected['tenant_id']):raise HTTPException(503,'La propuesta no corresponde a la nómina solicitada.')
        if operation=='post_payroll' and (data.get('payroll_id')!=payroll_id or data.get('money_transferred') is not False):raise HTTPException(503,'El resultado no corresponde a una causación de nómina sin pago.')
    if operation in {'compare_bank_statement','review_bank_reconciliation','confirm_bank_reconciliation','review_bank_release','confirm_bank_release'}:
        if data.get('company_id')!=selected['tenant_id'] or data.get('bank_verified') is not False or data.get('ledger_written') is not False or data.get('money_transferred') is not False:raise HTTPException(503,'Resultado bancario sin alcance verificable.')
        try:
            if operation=='compare_bank_statement' and (data.get('schema')!='sgacd-bank-comparison-v1' or data.get('read_only') is not True or data.get('account_id')!=str(UUID(payload['account_id'])) or data.get('source_digest')!=hashlib.sha256(payload['csv_text'].encode()).hexdigest()):raise ValueError('Comparison identity mismatch')
            if operation=='review_bank_reconciliation' and (data.get('preview',{}).get('account_id')!=str(UUID(payload['account_id'])) or data.get('preview',{}).get('source_digest')!=hashlib.sha256(payload['csv_text'].encode()).hexdigest()):raise ValueError('Statement identity mismatch')
            if operation=='confirm_bank_reconciliation' and data.get('statement_id')!=str(UUID(payload['statement_id'])):raise ValueError('Statement identity mismatch')
            if operation=='review_bank_release' and data.get('reconciliation_id')!=str(UUID(payload['reconciliation_id'])):raise ValueError('Reconciliation identity mismatch')
        except (ValueError,TypeError,AttributeError):raise HTTPException(503,'El resultado no corresponde a la fuente bancaria solicitada.') from None
    if operation in {'review_environmental','record_environmental'}:
        if data.get('company_id')!=selected['tenant_id'] or any(data.get(k) is not False for k in ['ledger_written','money_transferred','liability_recognized','carbon_credit_issued','independently_verified']):raise HTTPException(503,'Medición ambiental sin alcance verificable.')
        if operation=='review_environmental':
            snapshot=data.get('preview',{}).get('assessment',{}).get('snapshot',{})
            if snapshot.get('company_id')!=selected['tenant_id'] or snapshot.get('activities')!=sorted(payload['activities'],key=lambda a:a['id']) or snapshot.get('factors')!=sorted(payload['factors'],key=lambda f:f['id']):raise HTTPException(503,'Fuentes ambientales incompatibles.')
        elif data.get('review_id')!=payload['review_id']:raise HTTPException(503,'Revisión ambiental incompatible.')
    if operation in {'review_hotel_capacity','record_hotel_capacity'}:
        if data.get('company_id')!=selected['tenant_id'] or data.get('ledger_written') is not False or data.get('independently_verified') is not False:raise HTTPException(503,'Capacidad hotelera sin alcance verificable.')
        if operation=='review_hotel_capacity' and (data.get('preview',{}).get('snapshot',{}).get('company_id')!=selected['tenant_id'] or data.get('preview',{}).get('snapshot',{}).get('provider_id')!=selected['provider_id'] or data.get('preview',{}).get('snapshot',{}).get('day')!=payload['day']):raise HTTPException(503,'La propuesta no corresponde a la capacidad solicitada.')
    if operation in {'review_environmental_correction','record_environmental_correction'}:
        flags=['ledger_written','money_transferred','liability_recognized','carbon_credit_issued','independently_verified','esg_certified']
        if data.get('company_id')!=selected['tenant_id'] or data.get('observation_id')!=payload.get('observation_id') or any(data.get(k) is not False for k in flags):
            raise HTTPException(503,'Corrección ambiental sin alcance verificable.')
        if operation=='review_environmental_correction':
            preview=data.get('preview',{});snapshot=preview.get('assessment',{}).get('snapshot',{})
            if preview.get('revision')!=payload['expected_revision']+1 or preview.get('reason_code')!=payload['reason_code'] or preview.get('evidence_digest')!=payload['evidence_digest'] or snapshot.get('company_id')!=selected['tenant_id'] or snapshot.get('activities')!=sorted(payload['activities'],key=lambda a:a['id']) or snapshot.get('factors')!=sorted(payload['factors'],key=lambda f:f['id']):
                raise HTTPException(503,'Corrección de fuentes distintas a las revisadas.')
        elif data.get('review_id')!=payload['review_id'] or data.get('original_preserved') is not True:
            raise HTTPException(503,'Registro de corrección incompatible.')
    if operation.endswith('_financial_rehearsal'):
        flags=['payment_executed','bank_destination_verified','source_independently_verified',
               'network_called','desktop_job_created','ledger_written','usable_as_payment_authorization']
        if data.get('schema')!='sgacd-financial-rehearsal-result-v1' or data.get('company_id')!=selected['tenant_id'] or any(data.get(k) is not False for k in flags):
            raise HTTPException(503,'Simulación financiera sin alcance verificable.')
        intent=payload.get('intent') if operation=='prepare_financial_rehearsal' else None
        if intent is not None:
            expected_digest=hashlib.sha256(json.dumps(intent,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
            if data.get('intent')!=intent or intent.get('company_id')!=selected['tenant_id'] or data.get('request_id')!=intent.get('request_id') or data.get('plan_digest')!=expected_digest:
                raise HTTPException(503,'La intención financiera no corresponde a la revisión.')
        elif data.get('request_id')!=payload.get('request_id') or data.get('plan_digest')!=payload.get('plan_digest'):
            raise HTTPException(503,'Resultado de otra intención financiera.')
        status={'prepare_financial_rehearsal':'PREPARED','confirm_financial_rehearsal':'CONFIRMED_'+str(payload.get('step')),'simulate_financial_rehearsal':'SIMULATED_ONLY','cancel_financial_rehearsal':'CANCELLED'}[operation]
        if data.get('status')!=status:raise HTTPException(503,'Estado de simulación incompatible.')
    field='correction_id' if operation=='record_environmental_correction' else 'observation_id' if operation in {'record_hotel_capacity','record_environmental'} else 'reconciliation_id' if operation in {'confirm_bank_reconciliation','confirm_bank_release'} else 'policy_id' if operation in {'record_tax_policy','quote_tax_policy'} else 'review_id' if operation.startswith('review_') else 'request_id' if operation.endswith('_financial_rehearsal') else 'journal_id'
    if operation not in {'query','compare_bank_statement','estimate_environmental'}:
        try:UUID(data[field])
        except (ValueError,KeyError,TypeError):raise HTTPException(503,'Falta evidencia del resultado; consulta la revisión original.') from None
    expected_write=operation in {'post_payroll','post_recognition','reverse_recognition','apply_opening','post_commercial_tax','reverse_commercial_tax'}
    if operation=='apply_opening' and data.get('linked_existing') is True and data.get('metadata_recorded') is True:expected_write=False
    if data.get('ledger_written') is not expected_write:raise HTTPException(503,'Estado contable incompatible; consulta la revisión original.')
    return {'schema':'sgacd-corporate-ledger-command-v1','company_id':selected['tenant_id'],'operation':operation,'source':'authenticated_shared_ledger','data':data,'dispatch_authorized':True,'cross_database_atomic':False}
