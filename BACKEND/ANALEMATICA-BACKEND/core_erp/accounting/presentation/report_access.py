"""Fail-closed adapters for the older accounting report routes."""
from contextlib import contextmanager
from datetime import date
from decimal import Decimal,Context,localcontext
from uuid import UUID
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied,ValidationError
from ..exceptions import AccountingError
from ..validation import lock_company

class AccountingReportView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def handle_exception(self,exc):
        if isinstance(exc,AccountingError):
            exc=ValidationError({'code':'ACCOUNTING_REPORT_UNAVAILABLE','detail':'El libro requiere revisión antes de generar este informe.'})
        return super().handle_exception(exc)
    def finalize_response(self,request,response,*args,**kwargs):
        response=super().finalize_response(request,response,*args,**kwargs)
        response['Cache-Control']='no-store'
        return response

@contextmanager
def report_company(request):
    """A caller-supplied tenant UUID selects a scope; it never authorizes it."""
    try:
        raw=getattr(request,'tenant_id',None) or request.headers.get('X-Tenant-ID')
        identifier=str(UUID(str(raw)))
    except (TypeError,ValueError,AttributeError):
        raise PermissionDenied('Empresa contable no autorizada.') from None
    if (getattr(request,'tenant_id',None) is not None
            and request.headers.get('X-Tenant-ID') not in (None,identifier)):
        raise PermissionDenied('Empresa contable no autorizada.')
    from apps.turismo.models import VerifiedCompanyLink
    from apps.turismo.services.company_identity import resolve_company
    with transaction.atomic(),localcontext(Context(prec=50)):
        links=list(VerifiedCompanyLink.objects.filter(tenant_id=identifier,administrator_id=request.user.pk).values_list('provider_id',flat=True)[:2])
        if len(links)!=1:
            raise PermissionDenied('Empresa contable no autorizada.')
        company=lock_company(identifier)
        link=resolve_company(request.user,links[0])
        if link.tenant_id!=company.pk:
            raise PermissionDenied('Empresa contable no autorizada.')
        yield company
        if resolve_company(request.user,links[0]).tenant_id!=company.pk:
            raise PermissionDenied('Empresa contable no autorizada.')

def dates(request,interval=False):
    allowed={'start','end'} if interval else {'date'}
    if set(request.query_params)-allowed or any(len(request.query_params.getlist(k))!=1 for k in request.query_params):
        raise ValidationError('Parámetros de informe desconocidos o repetidos.')
    def parsed(key,default):
        raw=request.query_params.get(key)
        if raw is None:return default
        try:
            value=date.fromisoformat(raw)
            if value.isoformat()!=raw:raise ValueError()
            return value
        except (TypeError,ValueError):
            raise ValidationError('Fecha de informe inválida; usa AAAA-MM-DD.') from None
    if interval:
        end=parsed('end',timezone.localdate());start=parsed('start',end.replace(day=1))
        if start>end:raise ValidationError('Intervalo de informe inválido.')
        return start,end
    return parsed('date',timezone.localdate())

def wire(value):
    if isinstance(value,Decimal):return format(value,'f')
    if isinstance(value,(UUID,date)):return str(value)
    if isinstance(value,dict):return {key:wire(item) for key,item in value.items()}
    if isinstance(value,list):return [wire(item) for item in value]
    return value
