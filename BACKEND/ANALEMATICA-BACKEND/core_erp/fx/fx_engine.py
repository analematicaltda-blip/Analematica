"""Legacy reference catalogue/conversion utility, never posting authorization.

The accounting ledger requires its own source-bound, valid, owner-reviewed quote.
A historical is_official flag in this catalogue does not certify its source.
"""
import logging,re
from datetime import datetime
from decimal import Decimal,ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone
from .models import Currency,FXRateTable
from apps.core_erp.accounting.validation import exact_arithmetic,money
from apps.core_erp.accounting.exceptions import AccountingError
logger=logging.getLogger(__name__)

def code(value):
    if not isinstance(value,str) or not re.fullmatch('[A-Z]{3}',value):raise ValueError('Registered uppercase three-letter currency required.')
    return value

def rate_value(value):
    if isinstance(value,bool) or not isinstance(value,(str,int,Decimal)):raise ValueError('Exact decimal rate required, never float.')
    try:
        value=Decimal(value)
        if not value.is_finite() or value<=0 or value>Decimal('999999999999.999999') or value!=value.quantize(Decimal('0.000001')):raise ValueError('Positive finite exact six-decimal rate required.')
    except ArithmeticError:raise ValueError('Invalid decimal rate.') from None
    return value

class FXEngine:
    @staticmethod
    @exact_arithmetic
    def get_rate(base_code,target_code,version=None,as_of=None):
        code(base_code);code(target_code)
        if version is not None and (type(version) is not int or version<1):raise ValueError('Positive integer version required.')
        cutoff=timezone.now() if as_of is None else as_of
        if not isinstance(cutoff,datetime) or not timezone.is_aware(cutoff) or cutoff>timezone.now():raise ValueError('Nonfuture aware observation cutoff required.')
        if Currency.objects.filter(code__in={base_code,target_code},is_active=True).count()!=len({base_code,target_code}):raise ValueError('Active registered currencies required.')
        if base_code==target_code:return Decimal('1.000000') # Identity, not a missing cross-rate fallback.
        query=FXRateTable.objects.filter(base_currency__code=base_code,target_currency__code=target_code,is_official=True,effective_from__lte=cutoff,rate__gt=0)
        if version is not None:query=query.filter(version=version)
        row=query.order_by('-effective_from','-version').first()
        if row is None:raise ValueError('No recorded reference rate for requested pair/version/cutoff.')
        if type(row.version) is not int or row.version<1:raise ValueError('Invalid recorded reference version.')
        return rate_value(row.rate)

    @staticmethod
    @exact_arithmetic
    def convert(amount,from_currency,to_currency,version=None):
        if isinstance(amount,bool) or not isinstance(amount,(str,int,Decimal)):raise ValueError('Exact monetary amount required, never float.')
        try:
            amount=Decimal(amount)
            if not amount.is_finite():raise ValueError('Finite amount required.')
            absolute=money(abs(amount));amount=-absolute if amount<0 else absolute
        except (AccountingError,ArithmeticError):raise ValueError('Exact monetary amount required.') from None
        rate=FXEngine.get_rate(from_currency,to_currency,version)
        converted=(amount*rate).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
        try:money(abs(converted))
        except AccountingError:raise ValueError('Converted amount exceeds ledger precision.') from None
        return converted

    @staticmethod
    @exact_arithmetic
    @transaction.atomic
    def update_rate(base_code,target_code,rate,user_id=None):
        code(base_code);code(target_code);rate=rate_value(rate)
        if base_code==target_code:raise ValueError('Identity rates do not require catalogue updates.')
        currencies=list(Currency.objects.select_for_update().filter(code__in=[base_code,target_code],is_active=True).order_by('pk'))
        if len(currencies)!=2:raise ValueError('Active registered currencies required.')
        by_code={row.code:row for row in currencies};base,target=by_code[base_code],by_code[target_code]
        previous=FXRateTable.objects.filter(base_currency=base,target_currency=target).order_by('-version').first()
        return FXRateTable.objects.create(base_currency=base,target_currency=target,rate=rate,effective_from=timezone.now(),version=previous.version+1 if previous else 1)
