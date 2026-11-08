from uuid import UUID
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..web_session import ErpSessionAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from apps.turismo.models import QuotationDraft
from apps.turismo.services.company_identity import resolve_company
from .quote_drafts import create_draft,get_draft,present,withdraw

class PrivateDraftView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
    def finalize_response(self,request,response,*args,**kwargs):
        response=super().finalize_response(request,response,*args,**kwargs)
        response['Cache-Control']='no-store'
        return response

class QuotationDraftCollection(PrivateDraftView):
    def post(self,request):
        draft,created=create_draft(request.user,request.data)
        return Response(present(draft),status=201 if created else 200)
    def get(self,request):
        try:provider=UUID(request.query_params.get('provider_id',''))
        except (ValueError,TypeError,AttributeError):raise ValidationError('Seleccione un prestador propio.')
        link=resolve_company(request.user,provider)
        query=QuotationDraft.objects.filter(provider_id=provider,tenant_id=link.tenant_id,requested_by_id=request.user.pk).order_by('-created_at','-pk')
        paginator=PageNumberPagination();paginator.page_size=20
        page=paginator.paginate_queryset(query,request)
        return paginator.get_paginated_response([present(item) for item in page])

class QuotationDraftDetail(PrivateDraftView):
    def get(self,request,pk):return Response(present(get_draft(request.user,pk)))

class QuotationDraftWithdraw(PrivateDraftView):
    def post(self,request,pk):
        if not isinstance(request.data,dict) or set(request.data)!={'digest'}:raise ValidationError('Se requiere el resumen del borrador.')
        return Response(present(withdraw(request.user,pk,request.data['digest'])))

class QuotationOptions(PrivateDraftView):
    def get(self,request):
        from apps.turismo.models import VerifiedCompanyLink
        from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
        from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
        from rest_framework.exceptions import PermissionDenied
        raw=request.query_params.get('provider_id')
        if not raw:
            result=[]
            links=VerifiedCompanyLink.objects.filter(administrator_id=request.user.pk,revoked_at__isnull=True,valid_until__gt=timezone.now()).select_related('provider')[:100]
            for link in links:
                try:resolve_company(request.user,link.provider_id)
                except PermissionDenied:continue
                result.append({'provider_id':str(link.provider_id),'name':link.provider.name})
            return Response({'companies':result})
        try:provider=UUID(raw)
        except (ValueError,TypeError,AttributeError):raise ValidationError('Prestador inválido.')
        link=resolve_company(request.user,provider)
        customers=Cliente.objects.filter(perfil_id=provider)
        products=Product.objects.filter(provider_id=provider,is_active=True,base_price_currency=link.tenant.currency)
        customer_search=request.query_params.get('customer_search','')[:100]
        product_search=request.query_params.get('product_search','')[:100]
        if customer_search:customers=customers.filter(nombre__icontains=customer_search)
        if product_search:products=products.filter(nombre__icontains=product_search)
        customers=list(customers.order_by('nombre','pk')[:101]);products=list(products.order_by('nombre','pk')[:101])
        return Response({'currency':link.tenant.currency,'customers':[{'id':c.pk,'name':c.nombre} for c in customers[:100]],'products':[{'id':str(p.pk),'name':p.nombre,'unit_price':str(p.base_price.amount)} for p in products[:100]],'customers_truncated':len(customers)>100,'products_truncated':len(products)>100,'availability_checked':False})

class CompanyScopeOptions(PrivateDraftView):
    def get(self,request):
        from ..company_scope import company_options
        return Response(company_options(request))
