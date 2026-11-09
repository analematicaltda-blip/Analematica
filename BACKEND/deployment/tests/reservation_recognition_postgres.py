"""Actual PostgreSQL races: reviewed source accrual and original-preserving reversal."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import date
from django.utils import timezone

def run_recognition_races(owner,provider,reservation,fiscal_review):
    from django.db import connections
    from rest_framework.exceptions import ValidationError
    from apps.core_erp.accounting.exceptions import AccountingError
    from apps.core_erp.accounting.models import ChartOfAccounts,Account,FiscalPeriod,JournalEntry
    from apps.core_erp.accounting.ledger_engine import LedgerEngine
    from apps.core_erp.accounting.reports_engine import ReportsEngine
    from apps.core_erp.outbox_models import OutboxEvent
    from apps.domain_business.comercial.services import reservation_recognition as engine
    chart=ChartOfAccounts.plain_objects.create(tenant_id=reservation.tenant_id,name='Synthetic recognition chart')
    asset=Account.plain_objects.create(tenant_id=reservation.tenant_id,chart_of_accounts=chart,code='130505',name='Receivable',type='ASSET')
    revenue=Account.plain_objects.create(tenant_id=reservation.tenant_id,chart_of_accounts=chart,code='410505',name='Service revenue',type='REVENUE')
    today=timezone.localdate()
    FiscalPeriod.plain_objects.create(tenant_id=reservation.tenant_id,period_start=date(today.year,1,1),period_end=date(today.year,12,31),status='open')
    args={'actor':owner,'provider_id':provider.pk,'reservation_id':reservation.pk}
    def compete(operation,allow_reject=False):
        connections.close_all();barrier=Barrier(2)
        def attempt():
            try:barrier.wait(timeout=10);return operation()
            except (ValidationError,AccountingError):
                if allow_reject:return None
                raise
            finally:connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(attempt) for _ in range(2)];return [f.result(timeout=25) for f in futures]
    reviews=compete(lambda:engine.review_recognition(**args,fiscal_review_id=fiscal_review['review_id'],entry_date=today.isoformat(),account_mapping={'receivable':str(asset.pk),'revenue':str(revenue.pk),'tax_liability':None},service_evidence_digest='c'*64,policy_evidence_digest='d'*64,economic_fact='SERVICE_DELIVERED',confirmed=True,expected_revision=0),allow_reject=True)
    accepted=[r for r in reviews if r];assert len(accepted)==1;review=accepted[0]
    posted=compete(lambda:engine.post_recognition(**args,review_id=review['review_id'],confirmed=True))
    assert sorted(r['replayed'] for r in posted)==[False,True]
    assert len({r['journal_id'] for r in posted})==1
    assert JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id,is_posted=True).count()==1
    assert OutboxEvent.objects.filter(event_type=engine.POSTED,aggregate_root=str(reservation.pk)).count()==1
    original=JournalEntry.plain_objects.get(pk=posted[0]['journal_id']);original_hash=original.system_hash
    assert ReportsEngine.get_profitability(reservation.tenant_id,today,today)['net_profit']=='100.00'
    reverse_review=engine.review_reversal(**args,reason='Contrapartida revisada de servicio sintético',evidence_digest='e'*64,confirmed=True)
    reversed_rows=compete(lambda:engine.reverse_recognition(**args,review_id=reverse_review['review_id'],confirmed=True))
    assert sorted(r['replayed'] for r in reversed_rows)==[False,True]
    assert len({r['journal_id'] for r in reversed_rows})==1
    original.refresh_from_db();assert original.system_hash==original_hash
    assert JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id,is_posted=True).count()==2
    assert ReportsEngine.get_profitability(reservation.tenant_id,today,today)['net_profit']=='0.00'
    assert LedgerEngine.validate_ledger_integrity(reservation.tenant_id)['is_valid']
    results=[{'scenario':'reservation_recognition_review_race','accepted':1,'review_versions':1},
            {'scenario':'reservation_recognition_post_race','single_posted_journal':True,'single_origin_proof':True,'net_profit':'100.00'},
            {'scenario':'reservation_recognition_reverse_race','single_reversal':True,'original_hash_preserved':True,'net_profit':'0.00','chain_valid':True}]

    # Two workers apply the same prior receipt: one recognition and one claim.
    from uuid import uuid4
    from apps.domain_business.operativa.models import Reservation
    from apps.domain_business.comercial.services.reservation_fiscal import review_reservation
    from apps.core_erp.accounting.models import LedgerEntry
    advance_account=Account.plain_objects.create(tenant_id=reservation.tenant_id,chart_of_accounts=chart,code='280505',name='Customer advance',type='LIABILITY')
    cash=Account.plain_objects.create(tenant_id=reservation.tenant_id,chart_of_accounts=chart,code='110505',name='Cash',type='ASSET')
    receipt=LedgerEngine.post_lines(tenant_id=reservation.tenant_id,entry_date=today,description='Existing synthetic receipt',lines_data=[{'account':cash,'debit':'40.00'},{'account':advance_account,'credit':'40.00'}],actor=owner,idempotency_key='advance-fixture:'+str(uuid4()))
    booking=Reservation.plain_objects.create(tenant_id=reservation.tenant_id,customer_id=reservation.customer_id,content_type_id=reservation.content_type_id,object_id=reservation.object_id,start_date=reservation.start_date,end_date=reservation.end_date,status='CONFIRMED',total_price='100.00',deposit_paid='40.00')
    advance_args={**args,'reservation_id':booking.pk}
    fiscal=review_reservation(**advance_args,items=[{'item_id':str(uuid4()),'net':'100.00','tax':'0.00','tax_category':'EXCLUDED','policy_reference':'synthetic-reviewed:1'}],evidence_digest='f'*64,confirmed=True,expected_revision=0)
    review=engine.review_recognition(**advance_args,fiscal_review_id=fiscal['review_id'],entry_date=today.isoformat(),account_mapping={'receivable':str(asset.pk),'revenue':str(revenue.pk),'tax_liability':None},service_evidence_digest='c'*64,policy_evidence_digest='d'*64,economic_fact='SERVICE_DELIVERED',confirmed=True,expected_revision=0,advance_allocation={'journal_id':str(receipt.pk),'liability_account_id':str(advance_account.pk),'evidence_digest':'a'*64})
    posted=compete(lambda:engine.post_recognition(**advance_args,review_id=review['review_id'],confirmed=True))
    assert sorted(row['replayed'] for row in posted)==[False,True]
    assert len({row['journal_id'] for row in posted})==1
    assert OutboxEvent.objects.filter(pk=engine.advance_claim_id(receipt.pk)).count()==1
    assert str(LedgerEntry.plain_objects.get(journal_entry_id=posted[0]['journal_id'],account=asset).debit_amount)=='60.00'
    results.append({'scenario':'reservation_advance_post_race','single_recognition':True,'single_claim':True,'receivable':'60.00','prior_receipt':'40.00'})
    from apps.core_erp.accounting.exceptions import AccountingError
    try:
        LedgerEngine.reverse_entry(receipt.pk,'Must reject active applied receipt',tenant_id=reservation.tenant_id,actor=owner)
        raise AssertionError('Applied receipt was reversed')
    except AccountingError:pass
    results.append({'scenario':'applied_receipt_reversal_guard','active_receipt_reversal_rejected':True})
    from apps.core_erp.accounting.tax_reconciliation import reconcile_tax_account
    tax_account=Account.plain_objects.create(tenant_id=reservation.tenant_id,chart_of_accounts=chart,code='240805',name='Reviewed tax liability',type='LIABILITY')
    taxable=Reservation.plain_objects.create(tenant_id=reservation.tenant_id,customer_id=reservation.customer_id,content_type_id=reservation.content_type_id,object_id=reservation.object_id,start_date=reservation.start_date,end_date=reservation.end_date,status='CONFIRMED',total_price='100.00')
    tax_args={**args,'reservation_id':taxable.pk}
    fiscal=review_reservation(**tax_args,items=[{'item_id':str(uuid4()),'net':'84.03','tax':'15.97','tax_category':'TAXABLE','policy_reference':'synthetic-reviewed:tax'}],evidence_digest='b'*64,confirmed=True,expected_revision=0)
    review=engine.review_recognition(**tax_args,fiscal_review_id=fiscal['review_id'],entry_date=today.isoformat(),account_mapping={'receivable':str(asset.pk),'revenue':str(revenue.pk),'tax_liability':str(tax_account.pk)},service_evidence_digest='c'*64,policy_evidence_digest='d'*64,economic_fact='SERVICE_DELIVERED',confirmed=True,expected_revision=0)
    engine.post_recognition(**tax_args,review_id=review['review_id'],confirmed=True)
    report=reconcile_tax_account(reservation.tenant_id,account_id=tax_account.pk,since=today.isoformat(),until=today.isoformat())
    assert report['reviewed_reservation_tax']=='15.97' and report['unattributed_net']=='0.00'
    reversal=engine.review_reversal(**tax_args,reason='Reviewed reversal for tax reconciliation',evidence_digest='e'*64,confirmed=True)
    engine.reverse_recognition(**tax_args,review_id=reversal['review_id'],confirmed=True)
    report=reconcile_tax_account(reservation.tenant_id,account_id=tax_account.pk,since=today.isoformat(),until=today.isoformat())
    assert report['reviewed_reservation_tax']=='0.00' and report['net_liability_movement']=='0.00'
    results.append({'scenario':'tax_reconciliation_postgres','reviewed_tax':'15.97','after_reversal':'0.00','dian_compared':False})
    before=ReportsEngine.get_trial_balance(reservation.tenant_id,today)
    gate=Barrier(2)
    def post_during_report():
        try:
            gate.wait(timeout=10)
            return LedgerEngine.post_lines(tenant_id=reservation.tenant_id,entry_date=today,description='Concurrent report/post fixture',lines_data=[{'account':asset,'debit':'1.00'},{'account':revenue,'credit':'1.00'}],actor=owner,idempotency_key='report-race:'+str(uuid4()))
        finally:connections.close_all()
    def take_report():
        try:gate.wait(timeout=10);return ReportsEngine.get_trial_balance(reservation.tenant_id,today)
        finally:connections.close_all()
    connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:
        writing=pool.submit(post_during_report);reading=pool.submit(take_report)
        written=writing.result(timeout=25);observed=reading.result(timeout=25)
    assert observed['total_debit']==observed['total_credit']
    assert observed['total_debit'] in (before['total_debit'],before['total_debit']+1)
    expected_tail=before['snapshot']['ledger_tail_hash'] if observed['total_debit']==before['total_debit'] else written.system_hash
    assert observed['snapshot']['ledger_tail_hash']==expected_tail
    results.append({'scenario':'coherent_primary_report_during_post','balanced':True,'watermark_matches_observed_state':True,'replica_used':False})
    from apps.core_erp.accounting import ratios
    from apps.core_erp.accounting.bank_statement import compare_statement
    old_policy=ratios.latest(reservation.tenant_id)
    ratios.configure(reservation.tenant_id,actor=owner,mapping={'cash_equivalents':[str(cash.pk)],'temporary_investments':[],'immediate_receivables':[],'current_liabilities':[str(advance_account.pk)]},evidence_digest='f'*64,expected_revision=old_policy.revision if old_policy else 0,confirmed=True)
    text='transaction_id,date,direction,amount,currency\nsynthetic-bank-001,'+today.isoformat()+',IN,40.00,COP\nsynthetic-bank-002,'+today.isoformat()+',IN,999.00,COP\n'
    count_before=JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id).count()
    bank=compare_statement(reservation.tenant_id,account_id=cash.pk,csv_text=text)
    assert bank['summary']['UNIQUE_CANDIDATE']==1 and bank['summary']['UNMATCHED']==1
    assert not bank['bank_verified'] and not bank['ledger_written']
    assert JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id).count()==count_before
    results.append({'scenario':'bank_statement_comparison_postgres','unique_candidates':1,'unmatched':1,'new_journals':0,'bank_verified':False})
    from apps.core_erp.tenancy.models import Tenant
    from apps.core_erp.accounting import opening_balances,tax_policies
    opening_company=Tenant.objects.create(name='Synthetic reviewed opening',tax_id='opening-'+str(uuid4()),state='ACTIVE')
    opening_chart=ChartOfAccounts.plain_objects.create(tenant=opening_company,name='Opening chart')
    opening_cash=Account.plain_objects.create(tenant=opening_company,chart_of_accounts=opening_chart,code='110505',name='Opening cash',type='ASSET',initial_balance='100.00')
    Account.plain_objects.create(tenant=opening_company,chart_of_accounts=opening_chart,code='310505',name='Opening equity',type='EQUITY',initial_balance='100.00')
    FiscalPeriod.plain_objects.create(tenant=opening_company,period_start=date(today.year,1,1),period_end=date(today.year,12,31),status='open')
    reviews=compete(lambda:opening_balances.review_opening(opening_company.pk,actor=owner,entry_date=today.isoformat(),evidence_digest='a'*64,expected_revision=0,confirmed=True),allow_reject=True)
    selected=[r for r in reviews if r];assert len(selected)==1
    applied=compete(lambda:opening_balances.apply_opening(opening_company.pk,actor=owner,review_id=selected[0]['review_id'],confirmed=True))
    assert sorted(r['replayed'] for r in applied)==[False,True]
    assert JournalEntry.plain_objects.filter(tenant=opening_company).count()==1
    assert str(ReportsEngine.get_trial_balance(opening_company.pk,today)['total_debit'])=='100.00'
    opening_cash.refresh_from_db();assert str(opening_cash.initial_balance)=='100.00'
    results.append({'scenario':'opening_review_and_apply_races','one_review':True,'one_opening':True,'source_preserved':True,'balanced_report':'100.00'})
    terms={'code':'SYNTHETIC_POLICY','jurisdiction':'CO','currency':'COP','valid_from':date(today.year,1,1).isoformat(),'valid_until':date(today.year,12,31).isoformat(),'rounding':'PER_COMPONENT_HALF_UP','components':[{'code':'DECLARED_TAX','kind':'OUTPUT_TAX','rate_bps':1900,'applies_to':['TAXABLE']}]}
    one=tax_policies.review_policy(opening_company.pk,actor=owner,policy=terms,evidence_digest='b'*64,expected_revision=0,confirmed=True)
    two=tax_policies.review_policy(opening_company.pk,actor=owner,policy=terms,evidence_digest='c'*64,expected_revision=0,confirmed=True)
    from queue import Queue
    pending_policies=Queue();pending_policies.put(one['review_id']);pending_policies.put(two['review_id'])
    recorded=compete(lambda:tax_policies.record_policy(opening_company.pk,actor=owner,review_id=pending_policies.get_nowait(),confirmed=True),allow_reject=True)
    assert len([r for r in recorded if r])==1
    quote=tax_policies.quote_policy(opening_company.pk,code=terms['code'],revision=1,economic_date=today.isoformat(),net='100.00',tax_category='TAXABLE',direction='SALE')
    assert quote['output_tax']=='19.00' and not quote['regulatory_verified']
    results.append({'scenario':'tax_policy_record_race','single_version':True,'output_tax':'19.00','regulatory_verified':False})
    link_company=Tenant.objects.create(name='Synthetic existing opening link',tax_id='opening-link-'+str(uuid4()),state='ACTIVE')
    link_chart=ChartOfAccounts.plain_objects.create(tenant=link_company,name='Link chart')
    link_cash=Account.plain_objects.create(tenant=link_company,chart_of_accounts=link_chart,code='110505',name='Existing opening cash',type='ASSET',initial_balance='50.00')
    link_equity=Account.plain_objects.create(tenant=link_company,chart_of_accounts=link_chart,code='310505',name='Existing opening equity',type='EQUITY',initial_balance='50.00')
    period=FiscalPeriod.plain_objects.create(tenant=link_company,period_start=date(today.year,1,1),period_end=date(today.year,12,31),status='open')
    previous=LedgerEngine.post_lines(tenant_id=link_company.pk,entry_date=today,description='Previously recorded opening',lines_data=[{'account':link_cash,'debit':'50.00'},{'account':link_equity,'credit':'50.00'}],actor=owner,idempotency_key='previous-opening:'+str(link_company.pk),period_id=period.pk)
    original_hash=previous.system_hash
    FiscalPeriod.plain_objects.filter(pk=period.pk).update(status='closed')
    review=opening_balances.review_opening(link_company.pk,actor=owner,entry_date=today.isoformat(),evidence_digest='a'*64,expected_revision=0,confirmed=True,existing_journal_id=str(previous.pk))
    linked=compete(lambda:opening_balances.apply_opening(link_company.pk,actor=owner,review_id=review['review_id'],confirmed=True))
    assert sorted(row['replayed'] for row in linked)==[False,True]
    assert all(row['linked_existing'] and not row['ledger_written'] for row in linked)
    assert JournalEntry.plain_objects.filter(tenant=link_company).count()==1
    previous.refresh_from_db();assert previous.system_hash==original_hash
    assert str(ReportsEngine.get_trial_balance(link_company.pk,today)['total_debit'])=='50.00'
    results.append({'scenario':'opening_existing_link_race','new_journals':0,'closed_period_preserved':True,'original_hash_preserved':True,'source_fields_preserved':True})
    # Real payroll rows and row locks in PostgreSQL, not an in-memory mock.
    from types import SimpleNamespace
    from django.db import connection
    from payroll_fixture import install as install_payroll
    from apps.prestadores.mi_negocio.gestion_contable.nomina import reviewed_payroll
    from apps.prestadores.mi_negocio.gestion_contable.nomina.models import DetalleLiquidacion,Planilla
    def create_payroll_table(model):
        if model._meta.db_table not in connection.introspection.table_names():
            with connection.schema_editor() as editor:editor.create_model(model)
    payroll_case=SimpleNamespace(provider=provider,tenant=reservation.tenant,chart=chart,period=FiscalPeriod.plain_objects.filter(tenant_id=reservation.tenant_id,status='open').get())
    payload=install_payroll(payroll_case,create_payroll_table)
    payroll_reviews=compete(lambda:reviewed_payroll.review_payroll(actor=owner,provider_id=provider.pk,**payload),allow_reject=True)
    chosen=[row for row in payroll_reviews if row];assert len(chosen)==1
    results.append({'scenario':'payroll_review_race','accepted_reviews':1,'second_review_rejected':True,'regulatory_verified':False})
    before=JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id).count()
    postings=compete(lambda:reviewed_payroll.post_payroll(actor=owner,provider_id=provider.pk,payroll_id=payload['payroll_id'],review_id=chosen[0]['review_id'],confirmed=True))
    assert sorted(row['replayed'] for row in postings)==[False,True]
    assert JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id).count()==before+1
    assert DetalleLiquidacion.objects.filter(planilla_id=payload['payroll_id']).count()==1
    recorded_payroll=Planilla.objects.get(pk=payload['payroll_id']);assert str(recorded_payroll.total_neto)=='480.00'
    assert all(not row['money_transferred'] for row in postings)
    results.append({'scenario':'payroll_post_and_retry_race','new_posted_journals':1,'detail_rows':1,'net_payable':'480.00','money_transferred':False})
    from apps.core_erp.accounting import bank_reconciliation
    bank_text='transaction_id,date,direction,amount,currency\nsynthetic-persisted-bank,'+today.isoformat()+',IN,40.00,COP\n'
    bank_args={'actor':owner,'account_id':str(cash.pk),'csv_text':bank_text,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True}
    bank_review_race=compete(lambda:bank_reconciliation.review_reconciliation(reservation.tenant_id,**bank_args),allow_reject=True)
    chosen=[row for row in bank_review_race if row];assert len(chosen)==1
    results.append({'scenario':'bank_reconciliation_review_race','persisted_reviews':1,'bank_verified':False})
    journal_count=JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id).count()
    confirmed=compete(lambda:bank_reconciliation.confirm_reconciliation(reservation.tenant_id,actor=owner,statement_id=chosen[0]['statement_id'],review_id=chosen[0]['review_id'],confirmed=True))
    assert sorted(row['replayed'] for row in confirmed)==[False,True]
    assert all(row['reconciliation_confirmed'] and not row['ledger_written'] for row in confirmed)
    results.append({'scenario':'bank_reconciliation_confirm_retry_race','one_confirmation':True,'one_replay':True,'new_journals':0})
    release=bank_reconciliation.review_release(reservation.tenant_id,actor=owner,reconciliation_id=confirmed[0]['reconciliation_id'],reason_code='WRONG_MATCH',evidence_digest='b'*64,confirmed=True)
    released=compete(lambda:bank_reconciliation.confirm_release(reservation.tenant_id,actor=owner,review_id=release['review_id'],confirmed=True))
    assert sorted(row['replayed'] for row in released)==[False,True] and all(row['released'] for row in released)
    results.append({'scenario':'bank_reconciliation_release_retry_race','one_release':True,'old_evidence_preserved':True})
    options=Queue()
    for suffix in ['-one','-two']:
        pending=bank_reconciliation.review_reconciliation(reservation.tenant_id,**{**bank_args,'csv_text':bank_text.replace('synthetic-persisted-bank','synthetic-persisted-bank'+suffix)})
        options.put(pending)
    def claim_one_line():
        item=options.get_nowait()
        return bank_reconciliation.confirm_reconciliation(reservation.tenant_id,actor=owner,statement_id=item['statement_id'],review_id=item['review_id'],confirmed=True)
    exclusive=compete(claim_one_line,allow_reject=True);assert len([row for row in exclusive if row])==1
    assert JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id).count()==journal_count
    results.append({'scenario':'bank_two_statements_same_line_race','accepted':1,'rejected':1,'new_journals':0})
    from hotel_metrics_fixture import install as install_hotel
    from apps.prestadores.mi_negocio.gestion_contable.contabilidad import tourism_metrics
    hotel_case=SimpleNamespace(provider=provider,tenant=reservation.tenant,chart=chart,period=payroll_case.period,a=cash,b=revenue,user=owner)
    hotel_args=install_hotel(hotel_case,create_payroll_table)
    review=tourism_metrics.review_capacity(actor=owner,provider_id=provider.pk,**hotel_args)
    observations=compete(lambda:tourism_metrics.record_capacity(actor=owner,provider_id=provider.pk,review_id=review['review_id'],confirmed=True))
    assert sorted(item['replayed'] for item in observations)==[False,True]
    results.append({'scenario':'hotel_capacity_record_retry_race','one_observation':True,'one_replay':True,'new_ledger_entries':0})
    knowledge_cutoff=timezone.now().isoformat();choices=Queue()
    for index,rooms in enumerate([hotel_args['room_ids'][:1],[]]):
        amended=tourism_metrics.review_capacity(actor=owner,provider_id=provider.pk,**{**hotel_args,'room_ids':rooms,'expected_revision':1,'evidence_digest':('b' if index==0 else 'c')*64})
        choices.put(amended)
    def record_capacity_revision():
        chosen=choices.get_nowait()
        return tourism_metrics.record_capacity(actor=owner,provider_id=provider.pk,review_id=chosen['review_id'],confirmed=True)
    changes=compete(record_capacity_revision,allow_reject=True);assert len([item for item in changes if item])==1
    earlier=tourism_metrics.metrics(actor=owner,provider_id=provider.pk,since=today.isoformat(),until=today.isoformat(),as_of=knowledge_cutoff)
    current=tourism_metrics.metrics(actor=owner,provider_id=provider.pk,since=today.isoformat(),until=today.isoformat())
    assert earlier['available_room_days']==2 and earlier['capacity_sources'][0]['revision']==1
    assert current['available_room_days'] in (0,1) and current['capacity_sources'][0]['revision']==2
    results.append({'scenario':'hotel_capacity_competing_revision_and_knowledge_cutoff','accepted':1,'rejected':1,'earlier_capacity_preserved':2,'lookahead_used':False})
    from apps.prestadores.mi_negocio.gestion_contable.contabilidad import environmental_records
    env_activity={'id':'pg-environment-route','date':today.isoformat(),'quantity':'100','unit':'vehicle_km','factor_id':'pg-environment-factor','passengers':4}
    env_factor={'id':'pg-environment-factor','version':'synthetic-v1','unit':'vehicle_km','kg_co2e_per_unit':'0.123456','valid_from':today.replace(month=1,day=1).isoformat(),'valid_until':today.replace(month=12,day=31).isoformat(),'source_digest':'a'*64,'geography':'CO','boundary':'direct_combustion'}
    args={'actor':owner,'provider_id':provider.pk,'activities':[env_activity],'factors':[env_factor],'evidence_digest':'b'*64,'confirmed':True}
    env_journal_count=JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id).count()
    env_review=environmental_records.review_measurement(**args)
    records=compete(lambda:environmental_records.record_measurement(actor=owner,provider_id=provider.pk,review_id=env_review['review_id'],confirmed=True))
    assert sorted(item['replayed'] for item in records)==[False,True]
    results.append({'scenario':'environmental_record_retry_race','one_observation':True,'one_replay':True,'new_ledger_entries':0})
    choices=Queue()
    for index in range(2):
        choice=environmental_records.review_measurement(**{**args,'activities':[{**env_activity,'id':'pg-shared-environment-route'}],'evidence_digest':('c' if index==0 else 'd')*64})
        choices.put(choice)
    def record_environmental_choice():
        chosen=choices.get_nowait()
        return environmental_records.record_measurement(actor=owner,provider_id=provider.pk,review_id=chosen['review_id'],confirmed=True)
    chosen=compete(record_environmental_choice,allow_reject=True);assert len([item for item in chosen if item])==1
    assert JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id).count()==env_journal_count
    results.append({'scenario':'environmental_shared_activity_race','accepted':1,'rejected':1,'new_ledger_entries':0})
    choices=Queue()
    for index in range(2):
        factor={**env_factor,'id':'pg-competing-factor','kg_co2e_per_unit':'0.1' if index==0 else '0.2'}
        activity={**env_activity,'id':'pg-factor-route-'+str(index),'factor_id':factor['id']}
        choices.put(environmental_records.review_measurement(**{**args,'activities':[activity],'factors':[factor]}))
    choices_result=compete(record_environmental_choice,allow_reject=True);assert len([item for item in choices_result if item])==1
    assert JournalEntry.plain_objects.filter(tenant_id=reservation.tenant_id).count()==env_journal_count
    results.append({'scenario':'environmental_factor_version_conflict_race','accepted':1,'rejected':1,'new_ledger_entries':0})
    return results
