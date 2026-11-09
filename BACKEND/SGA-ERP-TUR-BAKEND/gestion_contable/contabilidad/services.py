"""Tourism accounting adapter: verified company identity, never provider UUID aliasing."""
from django.db import transaction
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.models import Account
from apps.core_erp.accounting.validation import current_actor, lock_company
from apps.core_erp.accounting.exceptions import AccountingError
from apps.turismo.models import TourismProvider, VerifiedCompanyLink
from apps.turismo.services.company_identity import resolve_company

class ContabilidadService:
    @staticmethod
    @transaction.atomic
    def crear_asiento_completo(provider,date,description,periodo,creado_por,transacciones_data,*,idempotency_key=None):
        user=current_actor(creado_por)
        hint=VerifiedCompanyLink.objects.filter(provider_id=provider.pk).values_list('tenant_id',flat=True).first()
        if hint is None:raise AccountingError('A verified accounting company link is required.')
        lock_company(hint)
        TourismProvider.objects.select_for_update().get(pk=provider.pk)
        VerifiedCompanyLink.objects.select_for_update().get(provider_id=provider.pk)
        link=resolve_company(user,provider.pk)
        if link.tenant_id!=hint:raise AccountingError('Accounting identity changed; repeat review.')
        lines=[]
        for row in transacciones_data:
            account=Account.plain_objects.filter(pk=row.get('cuenta_id'),tenant_id=link.tenant_id).first()
            if account is None:raise AccountingError('Account is not available in the verified company.')
            lines.append({'account':account,'debit':row.get('debit',0),'credit':row.get('credit',0),
                          'description':row.get('description',description)})
        return LedgerEngine.post_lines(tenant_id=link.tenant_id,entry_date=date,description=description,
            lines_data=lines,actor=user,period_id=getattr(periodo,'pk',periodo),idempotency_key=idempotency_key)
