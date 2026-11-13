"""Adapter to the existing ACID ledger, without payment or fiscal issuance."""
from datetime import date
from decimal import Decimal
from .crm import CRMError,digest
from .opportunities import uuid_ref
class Ledger:
    def __init__(self,crm):self.crm=crm;self.company=crm.store.scope;self.actor=crm.actor
    def policy(self):
        import json,os,re
        from django.conf import settings
        from django.contrib.auth import get_user_model
        policies=getattr(settings,'COMMERCIAL_SALE_ACCOUNT_POLICIES',None)
        if policies is None:
            try:policies=json.loads(os.environ.get('COMMERCIAL_SALE_ACCOUNT_POLICIES','{}'))
            except (ValueError,TypeError):raise CRMError('SALE_ACCOUNT_POLICY_REQUIRED',503) from None
        p=policies.get(self.company) if isinstance(policies,dict) else None
        if not isinstance(p,dict) or set(p)!={'version','valid_from','valid_until','reviewer_ref','support_digest','roles'}:raise CRMError('SALE_ACCOUNT_POLICY_REQUIRED',503)
        from .crm import moment
        from datetime import datetime,timezone
        now=datetime.now(timezone.utc)
        if not moment(p['valid_from'])<=now<moment(p['valid_until']) or not isinstance(p['support_digest'],str) or not re.fullmatch('[a-f0-9]{64}',p['support_digest']):raise CRMError('SALE_ACCOUNT_POLICY_EXPIRED',409)
        if not isinstance(p['reviewer_ref'],str) or not p['reviewer_ref'].isascii() or not p['reviewer_ref'].isdecimal() or not get_user_model().objects.filter(pk=p['reviewer_ref'],is_active=True).exists():raise CRMError('SALE_ACCOUNT_POLICY_REVIEWER_REQUIRED',409)
        if not isinstance(p['roles'],dict) or set(p['roles'])!={'receivable','revenue','contract_liability','tax_liability'} or any(not isinstance(v,list) for v in p['roles'].values()):raise CRMError('INVALID_SALE_ACCOUNT_POLICY')
        return p
    def user(self):
        from django.contrib.auth import get_user_model
        row=get_user_model().objects.filter(pk=self.actor,is_active=True).first()
        if row is None or getattr(row,'is_agent',False):raise CRMError('HUMAN_OWNER_REQUIRED',403)
        return row
    def account(self,ref,kind):
        from apps.core_erp.accounting.models import Account
        uuid_ref(ref);row=Account.plain_objects.filter(pk=ref,tenant_id=self.company,chart_of_accounts__tenant_id=self.company,is_active=True,type=kind).first()
        if row is None:raise CRMError('SCOPED_ACCOUNT_REQUIRED')
        return row
    def catalog(self):
        if not self.crm.authorize().principal['is_manager']:raise CRMError('LOCAL_ADMINISTRATOR_REQUIRED',403)
        from apps.core_erp.accounting.models import Account,FiscalPeriod
        policy=self.policy()
        return {'policy_version':policy['version'],'policy_digest':digest(policy),'professional_review_independently_verified':False,'accounts':[{'id':str(x.pk),'code':x.code,'name':x.name,'type':x.type,'roles':[role for role,ids in policy['roles'].items() if str(x.pk) in ids]} for x in Account.plain_objects.filter(tenant_id=self.company,chart_of_accounts__tenant_id=self.company,is_active=True).order_by('code')[:200]],'periods':[{'id':str(x.pk),'start':x.period_start.isoformat(),'end':x.period_end.isoformat(),'status':x.status} for x in FiscalPeriod.plain_objects.filter(tenant_id=self.company,status='open').order_by('-period_start')[:20]],'company_ref':self.company}
    def preview(self,source,terms):
        from apps.core_erp.accounting.models import FiscalPeriod
        from apps.core_erp.tenancy.models import Tenant
        from apps.core_erp.accounting.validation import money
        e=source['content']['estimate'];company=Tenant.objects.get(pk=self.company)
        if e['currency']!='COP' or company.currency!='COP':raise CRMError('SALE_REVIEWED_FX_REQUIRED',409)
        gross,base,tax=money(e['total']),money(e['subtotal'])-money(e['discount']),money(e['tax'])
        if gross<=0 or gross!=base+tax:raise CRMError('SALE_TOTALS_INVALID')
        accounts=terms['accounts']
        if not isinstance(accounts,dict) or set(accounts)!={'receivable','contra','tax_liability'}:raise CRMError('SALE_ACCOUNT_MAPPING_REQUIRED')
        policy=self.policy();selected={'receivable':accounts['receivable'],'contract_liability' if terms['economic_fact']=='UNCONDITIONAL_RECEIVABLE' else 'revenue':accounts['contra']}
        if accounts['tax_liability'] is not None:selected['tax_liability']=accounts['tax_liability']
        if any(ref not in policy['roles'][role] for role,ref in selected.items()):raise CRMError('SALE_ACCOUNT_ROLE_NOT_REVIEWED')
        receivable=self.account(accounts['receivable'],'ASSET');contra=self.account(accounts['contra'],'LIABILITY' if terms['economic_fact']=='UNCONDITIONAL_RECEIVABLE' else 'REVENUE');tax_account=None
        if terms['economic_fact']=='SERVICE_DELIVERED' and tax>0:tax_account=self.account(accounts['tax_liability'],'LIABILITY')
        elif accounts['tax_liability'] is not None:raise CRMError('UNEXPECTED_TAX_ACCOUNT')
        ids=[str(x.pk) for x in (receivable,contra,tax_account) if x is not None]
        if len(set(ids))!=len(ids):raise CRMError('DISTINCT_SALE_ACCOUNTS_REQUIRED')
        day=date.fromisoformat(terms['entry_date'])
        from django.utils.timezone import localdate
        if day>localdate():raise CRMError('FUTURE_SALE_ACCOUNTING_NOT_ALLOWED')
        periods=list(FiscalPeriod.plain_objects.filter(tenant_id=self.company,status='open',period_start__lte=day,period_end__gte=day)[:2])
        if len(periods)!=1:raise CRMError('SALE_OPEN_PERIOD_REQUIRED',409)
        lines=[{'account_id':str(receivable.pk),'debit':format(gross,'.2f'),'credit':'0.00'},{'account_id':str(contra.pk),'debit':'0.00','credit':format(gross if terms['economic_fact']=='UNCONDITIONAL_RECEIVABLE' else base,'.2f')}]
        if tax_account:lines.append({'account_id':str(tax_account.pk),'debit':'0.00','credit':format(tax,'.2f')})
        return {'account_policy_digest':digest(policy),'company_id':self.company,'currency':'COP','period_id':str(periods[0].pk),'entry_date':day.isoformat(),'lines':lines,'total_debit':format(gross,'.2f'),'total_credit':format(gross,'.2f'),'revenue_recognized':terms['economic_fact']=='SERVICE_DELIVERED','invoice_issued':False,'money_transferred':False}
    def post(self,item):
        from apps.core_erp.accounting.ledger_engine import LedgerEngine
        from apps.core_erp.accounting.models import Account
        from apps.core_erp.accounting.commercial_sales_guard import permit
        p=item['review']['preview'];rows=[]
        for line in p['lines']:
            account=Account.plain_objects.get(pk=line['account_id'],tenant_id=self.company);rows.append({'account':account,'debit':line['debit'],'credit':line['credit'],'description':'Venta revisada '+item['id']})
        with permit(self.company,item['id']):entry=LedgerEngine.post_lines(tenant_id=self.company,entry_date=date.fromisoformat(p['entry_date']),description='Venta comercial revisada '+item['id'],lines_data=rows,actor=self.user(),idempotency_key='commercial-sale:'+item['id'],period_id=p['period_id'])
        return {'id':str(entry.pk),'hash':entry.system_hash,'company_id':str(entry.tenant_id),'posted':entry.is_posted}
    def verify(self,item):
        from apps.core_erp.accounting.models import JournalEntry
        from apps.core_erp.accounting.ledger_engine import LedgerEngine
        row=JournalEntry.plain_objects.filter(pk=item['journal']['id'],tenant_id=self.company,is_posted=True,financial_event_id='commercial-sale:'+item['id']).first()
        if row is None or row.system_hash!=item['journal']['hash'] or LedgerEngine.calculate_hash(row)!=row.system_hash:raise CRMError('SALE_JOURNAL_INTEGRITY_REQUIRED',503)
        return row
    def reverse(self,item):
        from apps.core_erp.accounting.models import JournalEntry
        from apps.core_erp.accounting.ledger_engine import LedgerEngine
        from apps.core_erp.accounting.commercial_sales_guard import permit
        original=self.verify(item);prior=JournalEntry.plain_objects.filter(tenant_id=self.company,reversed_entry_id=original.pk,is_posted=True).first()
        if prior:raise CRMError('UNRECONCILED_SALE_REVERSAL',409)
        with permit(self.company,item['id']):row=LedgerEngine.reverse_entry(original.pk,reason=item['reversal_review']['reason'],tenant_id=self.company,actor=self.user())
        return {'id':str(row.pk),'hash':row.system_hash,'company_id':str(row.tenant_id),'posted':row.is_posted,'original_id':str(original.pk)}
