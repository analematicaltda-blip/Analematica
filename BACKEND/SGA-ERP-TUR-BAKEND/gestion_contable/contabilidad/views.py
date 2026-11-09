"""Account catalog bound to the requesting owner's verified accounting company."""
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from ...web_session import ErpSessionAuthentication
from ...company_scope import owned_provider
from apps.turismo.services.company_identity import resolve_company
from apps.core_erp.accounting.models import Account
from apps.core_erp.accounting.validation import lock_company
from .serializers import PlanCuentaSerializer
from apps.core_erp.accounting.fiscal_envelope_parser import FiscalEnvelopeJSONParser
from apps.core_erp.accounting.query_parser import AccountingQueryJSONParser

from apps.core_erp.accounting.http_privacy import PrivateAccountingResponseMixin

class AccountingCatalogPagination(PageNumberPagination):
    page_size_query_param='page_size'
    max_page_size=100

class PlanCuentaViewSet(PrivateAccountingResponseMixin,viewsets.ModelViewSet):
    pagination_class=AccountingCatalogPagination
    queryset=Account.plain_objects.none()
    serializer_class=PlanCuentaSerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
    filter_backends=[DjangoFilterBackend]
    filterset_fields=['code','type','is_active']

    def company(self):
        user=get_user_model().objects.filter(pk=self.request.user.pk,is_active=True).first()
        if user is None:raise PermissionDenied('Se requiere un titular activo.')
        self.request.user=user
        return resolve_company(user,owned_provider(self.request).pk).tenant

    def get_queryset(self):
        return Account.plain_objects.filter(tenant_id=self.company().pk).select_related('parent_account').order_by('code','pk')

    def get_serializer_context(self):
        return {**super().get_serializer_context(),'accounting_tenant_id':self.company().pk}

    @transaction.atomic
    def perform_create(self,serializer):
        company=self.company();lock_company(company.pk)
        if self.company().pk!=company.pk:raise PermissionDenied("La identidad empresarial cambió.")
        checked=self.get_serializer(data=serializer.initial_data)
        checked.is_valid(raise_exception=True)
        serializer.instance=checked.save(tenant=company)

    @transaction.atomic
    def perform_update(self,serializer):
        company=self.company();lock_company(company.pk)
        # Recheck authoritative ownership/state after taking the accounting lock.
        if self.company().pk!=company.pk:raise PermissionDenied('La identidad empresarial cambió.')
        fresh=Account.plain_objects.get(pk=serializer.instance.pk,tenant=company)
        checked=self.get_serializer(fresh,data=serializer.initial_data,partial=serializer.partial)
        checked.is_valid(raise_exception=True)
        serializer.instance=checked.save()

    def destroy(self,request,*args,**kwargs):
        self.get_object()
        raise ValidationError('Conserva el catálogo histórico; desactiva la cuenta en lugar de eliminarla.')

    @action(detail=False,methods=['get'],url_path='identidad-contable')
    def accounting_identity(self,request):
        company=self.company()
        return Response({'company_id':str(company.pk),'provider_id':str(owned_provider(request).pk),'actor_id':str(request.user.pk),'read_only':True})

    @action(detail=False,methods=['get'],url_path='conciliacion-tributaria')
    def tax_reconciliation(self,request):
        from apps.core_erp.accounting.tax_reconciliation import reconcile_tax_account
        from apps.core_erp.accounting.exceptions import AccountingError
        if set(request.query_params)-{'provider_id','cuenta_id','desde','hasta'}:raise ValidationError('Parámetros de conciliación no admitidos.')
        company=self.company()
        try:result=reconcile_tax_account(company.pk,account_id=request.query_params.get('cuenta_id'),since=request.query_params.get('desde'),until=request.query_params.get('hasta'))
        except (ValueError,TypeError,AccountingError):raise ValidationError('Revisa cuenta, fechas, valoración y evidencias tributarias.') from None
        return Response(result)

    @action(detail=False,methods=['get'],url_path='conciliacion-tributaria-integral')
    def tax_register(self,request):
        from apps.core_erp.accounting.tax_register import reconcile_tax_register
        from apps.core_erp.accounting.exceptions import AccountingError
        allowed={'provider_id','cuenta_id','desde','hasta'}
        if set(request.query_params)!=allowed or any(len(request.query_params.getlist(k))!=1 for k in allowed):raise ValidationError('Cuenta, fechas y proveedor únicos requeridos.')
        company=self.company()
        try:result=reconcile_tax_register(company.pk,account_id=request.query_params['cuenta_id'],since=request.query_params['desde'],until=request.query_params['hasta'])
        except (AccountingError,ValueError,TypeError,KeyError):raise ValidationError('No se pudo verificar la conciliación integral. Revisa fuente, fechas y cuentas.') from None
        return Response(result)

    @action(detail=False,methods=['get'],url_path='diagnostico-dian')
    def dian_readiness(self,request):
        from django.conf import settings
        from apps.core_erp.accounting.dian_readiness import inspect_readiness
        company=self.company()
        profiles=getattr(settings,'ACCOUNTING_DIAN_PUBLIC_PROFILES',{})
        profile=profiles.get(str(company.pk)) if isinstance(profiles,dict) else None
        return Response(inspect_readiness(company.pk,profile))

    @action(detail=False,methods=['post'],url_path='estimar-impacto-ambiental',parser_classes=[AccountingQueryJSONParser])
    def environmental_estimate(self,request):
        from apps.core_erp.accounting.environmental import estimate
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company()
        if not isinstance(request.data,dict) or set(request.data)!={'activities','factors'}:raise ValidationError('Contrato ambiental inválido.')
        try:result=estimate(company_id=company.pk,**request.data)
        except (AccountingError,ValueError,TypeError):raise ValidationError('Revisa cantidades, unidades, vigencias, límites y fuentes explícitas. No se certifican factores ni obligaciones contables.') from None
        return Response(result)

    def _environmental_command(self,request,operation,fields):
        from . import environmental_records
        from apps.core_erp.accounting.exceptions import AccountingError
        self.company()
        values={k:request.query_params[k] for k in request.query_params if k!='provider_id'} if request.method=='GET' else request.data
        if not isinstance(values,dict) or set(values)!=fields:raise ValidationError('Contrato de medición ambiental inválido.')
        try:result=getattr(environmental_records,operation)(actor=request.user,provider_id=owned_provider(request).pk,**values)
        except (AccountingError,ValueError,TypeError):raise ValidationError('Revisa actividad, versión del factor, soporte, titular y confirmaciones. Una actividad confirmada no puede reutilizarse.') from None
        return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-medicion-ambiental',parser_classes=[AccountingQueryJSONParser])
    def review_environmental(self,request):
        return self._environmental_command(request,'review_measurement',{'activities','factors','evidence_digest','confirmed'})

    @action(detail=False,methods=['post'],url_path='registrar-medicion-ambiental',parser_classes=[AccountingQueryJSONParser])
    def record_environmental(self,request):
        return self._environmental_command(request,'record_measurement',{'review_id','confirmed'})

    @action(detail=False,methods=['get'],url_path='estado-medicion-ambiental')
    def environmental_state(self,request):
        return self._environmental_command(request,'measurement_state',{'review_id'})

    def _environmental_correction_command(self,request,operation,fields):
        from . import environmental_corrections
        from apps.core_erp.accounting.exceptions import AccountingError
        self.company()
        values={k:request.query_params[k] for k in request.query_params if k!='provider_id'} if request.method=='GET' else request.data
        if not isinstance(values,dict) or set(values)!=fields:raise ValidationError('Contrato de corrección ambiental inválido.')
        try:result=getattr(environmental_corrections,operation)(actor=request.user,provider_id=owned_provider(request).pk,**values)
        except (AccountingError,ValueError,TypeError):raise ValidationError('Revisa observación, historia, factores, versión y confirmaciones. El original se conserva.') from None
        return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-correccion-ambiental',parser_classes=[AccountingQueryJSONParser])
    def review_environmental_correction(self,request):
        return self._environmental_correction_command(request,'review_correction',{'observation_id','expected_revision','activities','factors','evidence_digest','reason_code','confirmed'})

    @action(detail=False,methods=['post'],url_path='registrar-correccion-ambiental',parser_classes=[AccountingQueryJSONParser])
    def record_environmental_correction(self,request):
        return self._environmental_correction_command(request,'record_correction',{'observation_id','review_id','confirmed'})

    @action(detail=False,methods=['get'],url_path='historia-correccion-ambiental')
    def environmental_correction_state(self,request):
        return self._environmental_correction_command(request,'correction_state',{'observation_id'})

    def _hotel_command(self,request,operation,fields,optional=frozenset()):
        from . import tourism_metrics
        from apps.core_erp.accounting.exceptions import AccountingError
        self.company()
        values={k:request.query_params[k] for k in request.query_params if k!='provider_id'} if request.method=='GET' else request.data
        if not isinstance(values,dict) or not fields<=set(values) or set(values)-fields-set(optional):raise ValidationError('Contrato de indicadores hoteleros inválido.')
        try:result=getattr(tourism_metrics,operation)(actor=request.user,provider_id=owned_provider(request).pk,**values)
        except (AccountingError,ValueError,TypeError):raise ValidationError('Revisa inventario físico, fecha actual, clasificación, ventana y evidencia; no se reconstruye capacidad histórica inexistente.') from None
        return Response(result)

    @action(detail=False,methods=['get'],url_path='fuentes-indicadores-hoteleros')
    def hotel_sources(self,request):
        return self._hotel_command(request,'sources',set())

    @action(detail=False,methods=['post'],url_path='revisar-capacidad-hotelera',parser_classes=[AccountingQueryJSONParser])
    def review_hotel_capacity(self,request):
        return self._hotel_command(request,'review_capacity',{'day','room_ids','mapping','evidence_digest','expected_revision','confirmed'})

    @action(detail=False,methods=['post'],url_path='registrar-capacidad-hotelera',parser_classes=[AccountingQueryJSONParser])
    def record_hotel_capacity(self,request):
        return self._hotel_command(request,'record_capacity',{'review_id','confirmed'})

    @action(detail=False,methods=['get'],url_path='indicadores-hoteleros')
    def hotel_metrics(self,request):
        return self._hotel_command(request,'metrics',{'since','until'},{'as_of'})

    def _operational_payroll_cost_command(self,request,operation,fields):
        from ..nomina import operational_costs
        from apps.core_erp.accounting.exceptions import AccountingError
        from django.core.exceptions import ValidationError as ModelValidationError
        if set(request.query_params)!={'provider_id'} or len(request.query_params.getlist('provider_id'))!=1:raise ValidationError('Proveedor único requerido.')
        self.company()
        if not isinstance(request.data,dict) or set(request.data)!=fields:raise ValidationError('Contrato de atribución de nómina inválido.')
        try:result=getattr(operational_costs,operation)(actor=request.user,provider_id=owned_provider(request).pk,**request.data)
        except (AccountingError,ValueError,TypeError,KeyError,ModelValidationError):raise ValidationError('Revisa nómina contabilizada, jornadas, capacidad declarada, centros y confirmaciones; no se deduce tiempo trabajado ni se causa otro gasto.') from None
        return Response(result)

    @action(detail=False,methods=['post'],url_path='fuentes-costos-operativos-nomina',parser_classes=[AccountingQueryJSONParser])
    def payroll_cost_sources(self,request):
        return self._operational_payroll_cost_command(request,'cost_sources',{'payroll_id'})

    @action(detail=False,methods=['post'],url_path='revisar-costos-operativos-nomina',parser_classes=[AccountingQueryJSONParser])
    def review_payroll_costs(self,request):
        return self._operational_payroll_cost_command(request,'review_costs',{'payroll_id','capacities','operation_centers','evidence_digest','reason_code','expected_revision','confirmed'})

    @action(detail=False,methods=['post'],url_path='registrar-costos-operativos-nomina',parser_classes=[AccountingQueryJSONParser])
    def record_payroll_costs(self,request):
        return self._operational_payroll_cost_command(request,'record_costs',{'payroll_id','review_id','confirmed'})

    @action(detail=False,methods=['post'],url_path='estado-costos-operativos-nomina',parser_classes=[AccountingQueryJSONParser])
    def payroll_cost_state(self,request):
        return self._operational_payroll_cost_command(request,'cost_state',{'payroll_id'})

    @action(detail=False,methods=['post'],url_path='costos-laborales-operacion',parser_classes=[AccountingQueryJSONParser])
    def operation_labor_costs(self,request):
        return self._operational_payroll_cost_command(request,'operation_cost_report',{'order_id','since','until'})

    def _payroll_command(self,request,operation,fields):
        from ..nomina import reviewed_payroll
        from apps.core_erp.accounting.exceptions import AccountingError
        self.company()
        values=dict(request.query_params) if operation in {'payroll_state','payroll_sources'} else request.data
        if operation in {'payroll_state','payroll_sources'}:values={k:request.query_params[k] for k in request.query_params if k!='provider_id'}
        if not isinstance(values,dict) or set(values)!=fields:raise ValidationError('Contrato de nómina revisada inválido.')
        try:result=getattr(reviewed_payroll,operation)(actor=request.user,provider_id=owned_provider(request).pk,**values)
        except (AccountingError,ValueError,TypeError):raise ValidationError('Revisa fuente laboral, días, vigencia, cuentas, período y revisión persistida. No se presume validación normativa.') from None
        return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-nomina',parser_classes=[AccountingQueryJSONParser])
    def review_payroll(self,request):
        return self._payroll_command(request,'review_payroll',{'payroll_id','policy','workers','account_mapping','evidence_digest','expected_revision','confirmed'})

    @action(detail=False,methods=['post'],url_path='contabilizar-nomina-revisada',parser_classes=[AccountingQueryJSONParser])
    def post_payroll(self,request):
        return self._payroll_command(request,'post_payroll',{'payroll_id','review_id','confirmed'})

    @action(detail=False,methods=['get'],url_path='fuentes-nomina-revisada')
    def payroll_sources(self,request):
        return self._payroll_command(request,'payroll_sources',set())

    @action(detail=False,methods=['get'],url_path='estado-nomina-revisada')
    def payroll_state(self,request):
        return self._payroll_command(request,'payroll_state',{'payroll_id'})

    @action(detail=False,methods=['get'],url_path='cuentas-compras-nativas')
    def native_purchase_accounts(self,request):
        from apps.core_erp.accounting.catalog import purchase_catalog
        from apps.core_erp.accounting.exceptions import AccountingError
        allowed={'provider_id','paged','despues_id','buscar'}
        if set(request.query_params)-allowed or any(len(request.query_params.getlist(k))!=1 for k in request.query_params):raise ValidationError('Parámetros de catálogo inválidos.')
        try:result=purchase_catalog(self.company(),paged=request.query_params.get('paged'),after=request.query_params.get('despues_id'),search=request.query_params.get('buscar'))
        except (AccountingError,ValueError,TypeError):raise ValidationError('Catálogo de cuentas de compra no disponible.') from None
        return Response(result)

    def _native_purchase_command(self,request,operation,fields):
        from apps.prestadores.mi_negocio.gestion_contable.compras import native_purchase
        from apps.core_erp.accounting.exceptions import AccountingError
        from django.core.exceptions import ValidationError as ModelValidationError
        allowed={'provider_id'}
        if set(request.query_params)!=allowed or len(request.query_params.getlist('provider_id'))!=1:raise ValidationError('Proveedor único requerido.')
        with transaction.atomic():
            company=self.company();lock_company(company.pk)
            if self.company().pk!=company.pk:raise PermissionDenied('La empresa cambió.')
            if not isinstance(request.data,dict) or set(request.data)!=fields:raise ValidationError('Contrato nativo de compras inválido.')
            try:result=getattr(native_purchase,operation)(actor=request.user,provider_id=request.query_params['provider_id'],**request.data)
            except (AccountingError,ValueError,TypeError,KeyError,ModelValidationError):raise ValidationError('Revisa fuente nativa, proveedor, factura, reglas, período y confirmaciones; no se presume aceptación fiscal.') from None
            return Response(result)

    @action(detail=False,methods=['post'],url_path='registrar-proveedor-nativo',parser_classes=[AccountingQueryJSONParser])
    def record_native_supplier(self,request):
        return self._native_purchase_command(request,'record_supplier',{'request_id','name','identification','evidence_digest','confirmed'})

    @action(detail=False,methods=['post'],url_path='registrar-factura-compra-nativa',parser_classes=[AccountingQueryJSONParser])
    def record_native_purchase(self,request):
        return self._native_purchase_command(request,'record_invoice',{'request_id','supplier_id','number','issue_date','due_date','subtotal','tax','gross','document_digest','evidence_digest','confirmed'})

    @action(detail=False,methods=['post'],url_path='revisar-compra-nativa',parser_classes=[AccountingQueryJSONParser])
    def review_native_purchase(self,request):
        return self._native_purchase_command(request,'review_purchase',{'invoice_id','selection','settlement_account_id','economic_fact','evidence_digest','expected_revision','confirmed'})

    @action(detail=False,methods=['post'],url_path='contabilizar-compra-nativa',parser_classes=[AccountingQueryJSONParser])
    def post_native_purchase(self,request):
        return self._native_purchase_command(request,'post_purchase',{'invoice_id','review_id','confirmed'})

    @action(detail=False,methods=['post'],url_path='estado-compra-nativa',parser_classes=[AccountingQueryJSONParser])
    def native_purchase_state(self,request):
        return self._native_purchase_command(request,'purchase_state',{'invoice_id'})

    @action(detail=False,methods=['post'],url_path='fuentes-compras-nativas',parser_classes=[AccountingQueryJSONParser])
    def native_purchase_sources(self,request):
        return self._native_purchase_command(request,'purchase_sources',{'after_id'})

    @action(detail=False,methods=['post'],url_path='revisar-contrapartida-compra-nativa',parser_classes=[AccountingQueryJSONParser])
    def review_native_purchase_reversal(self,request):
        return self._native_purchase_command(request,'review_purchase_reversal',{'invoice_id','reason_code','evidence_digest','confirmed'})

    @action(detail=False,methods=['post'],url_path='contrapartida-compra-nativa',parser_classes=[AccountingQueryJSONParser])
    def reverse_native_purchase(self,request):
        return self._native_purchase_command(request,'reverse_purchase',{'invoice_id','review_id','confirmed'})

    @action(detail=False,methods=['post'],url_path='proveedores-compras-nativas',parser_classes=[AccountingQueryJSONParser])
    def native_supplier_sources(self,request):
        return self._native_purchase_command(request,'supplier_sources',{'after_id'})

    def _commercial_tax_command(self,request,operation,fields):
        from apps.core_erp.accounting import commercial_tax_posting
        from apps.core_erp.accounting.exceptions import AccountingError
        with transaction.atomic():
            company=self.company();lock_company(company.pk)
            if self.company().pk!=company.pk:raise PermissionDenied('La empresa cambió.')
            if not isinstance(request.data,dict) or set(request.data)!=fields:raise ValidationError('Contrato comercial tributario inválido.')
            try:result=getattr(commercial_tax_posting,operation)(company.pk,actor=request.user,**request.data)
            except (AccountingError,ValueError,TypeError,KeyError):raise ValidationError('Revisa fuente, cuentas, política vigente y confirmaciones; no se presume aceptación tributaria.') from None
            return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-hecho-tributario',parser_classes=[AccountingQueryJSONParser])
    def review_commercial_tax(self,request):
        return self._commercial_tax_command(request,'review_fact',{'fact','evidence_digest','expected_revision','confirmed'})

    @action(detail=False,methods=['post'],url_path='contabilizar-hecho-tributario',parser_classes=[AccountingQueryJSONParser])
    def post_commercial_tax(self,request):
        return self._commercial_tax_command(request,'post_fact',{'document_id','review_id','confirmed'})

    @action(detail=False,methods=['post'],url_path='estado-hecho-tributario',parser_classes=[AccountingQueryJSONParser])
    def commercial_tax_state(self,request):
        return self._commercial_tax_command(request,'fact_state',{'document_id'})

    @action(detail=False,methods=['post'],url_path='revisar-contrapartida-tributaria',parser_classes=[AccountingQueryJSONParser])
    def review_commercial_tax_reversal(self,request):
        return self._commercial_tax_command(request,'review_reversal',{'document_id','reason_code','evidence_digest','confirmed'})

    @action(detail=False,methods=['post'],url_path='contrapartida-tributaria',parser_classes=[AccountingQueryJSONParser])
    def reverse_commercial_tax(self,request):
        return self._commercial_tax_command(request,'reverse_fact',{'document_id','review_id','confirmed'})

    def _tax_policy_command(self,request,operation,fields):
        from apps.core_erp.accounting import tax_policies
        from apps.core_erp.accounting.exceptions import AccountingError
        with transaction.atomic():
            company=self.company();lock_company(company.pk)
            if self.company().pk!=company.pk:raise PermissionDenied('La empresa cambió.')
            if not isinstance(request.data,dict) or set(request.data)!=fields:raise ValidationError('Contrato de política tributaria inválido.')
            extra={} if operation=='quote_policy' else {'actor':request.user}
            try:result=getattr(tax_policies,operation)(company.pk,**extra,**request.data)
            except (AccountingError,ValueError,TypeError):raise ValidationError('Revisa código, versión, vigencia, categorías, tasas y evidencia; no se presume normativa vigente.') from None
            return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-politica-tributaria',parser_classes=[AccountingQueryJSONParser])
    def review_tax_policy(self,request):
        return self._tax_policy_command(request,'review_policy',{'policy','evidence_digest','expected_revision','confirmed'})

    @action(detail=False,methods=['post'],url_path='registrar-politica-tributaria',parser_classes=[AccountingQueryJSONParser])
    def record_tax_policy(self,request):
        return self._tax_policy_command(request,'record_policy',{'review_id','confirmed'})

    @action(detail=False,methods=['post'],url_path='calcular-politica-tributaria',parser_classes=[AccountingQueryJSONParser])
    def quote_tax_policy(self,request):
        return self._tax_policy_command(request,'quote_policy',{'code','revision','economic_date','net','tax_category','direction'})

    @action(detail=False,methods=['get'],url_path='politicas-tributarias')
    def tax_policy_history(self,request):
        from apps.core_erp.accounting.tax_policies import policy_history
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company()
        if set(request.query_params)-{'provider_id','code','before_revision'}:raise ValidationError('Parámetros no admitidos.')
        try:result=policy_history(company.pk,code=request.query_params.get('code'),before_revision=request.query_params.get('before_revision'))
        except (AccountingError,ValueError,TypeError):raise ValidationError('Código o cursor inválido.') from None
        return Response(result)

    @action(detail=False,methods=['get'],url_path='estado-apertura')
    def opening_state(self,request):
        from apps.core_erp.accounting.opening_balances import opening_state
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company()
        try:result=opening_state(company.pk,actor=request.user)
        except AccountingError:raise ValidationError('Los saldos legados requieren conciliación profesional.') from None
        return Response(result)

    def _financial_rehearsal_command(self,request,operation,fields):
        from apps.core_erp.accounting import financial_orchestration
        from apps.core_erp.accounting.exceptions import AccountingError
        with transaction.atomic():
            company=self.company();lock_company(company.pk)
            if self.company().pk!=company.pk:raise PermissionDenied('La empresa cambió.')
            if not isinstance(request.data,dict) or set(request.data)!=fields:
                raise ValidationError('Contrato de simulación financiera inválido.')
            try:
                result=getattr(financial_orchestration,operation)(company.pk,actor=request.user,
                    provider_id=owned_provider(request).pk,**request.data)
            except (AccountingError,ValueError,TypeError):
                raise ValidationError('Revisa intención, confirmaciones, importe, destino y vigencia. No se ejecutó un pago.') from None
            return Response(result)

    @action(detail=False,methods=['post'],url_path='preparar-simulacion-financiera',parser_classes=[AccountingQueryJSONParser])
    def prepare_financial_rehearsal(self,request):
        return self._financial_rehearsal_command(request,'prepare',{'intent','confirmed'})

    @action(detail=False,methods=['post'],url_path='confirmar-simulacion-financiera',parser_classes=[AccountingQueryJSONParser])
    def confirm_financial_rehearsal(self,request):
        return self._financial_rehearsal_command(request,'confirm',{'request_id','plan_digest','step','confirmed'})

    @action(detail=False,methods=['post'],url_path='simular-orden-financiera',parser_classes=[AccountingQueryJSONParser])
    def simulate_financial_rehearsal(self,request):
        return self._financial_rehearsal_command(request,'simulate',{'request_id','plan_digest','impact_confirmation','confirmed'})

    @action(detail=False,methods=['post'],url_path='cancelar-simulacion-financiera',parser_classes=[AccountingQueryJSONParser])
    def cancel_financial_rehearsal(self,request):
        return self._financial_rehearsal_command(request,'cancel',{'request_id','plan_digest','confirmed'})

    def _opening_command(self,request,operation,fields):
        from apps.core_erp.accounting import opening_balances
        from apps.core_erp.accounting.exceptions import AccountingError
        with transaction.atomic():
            company=self.company();lock_company(company.pk)
            if self.company().pk!=company.pk:raise PermissionDenied('La empresa cambió.')
            optional={'existing_journal_id'} if operation=='review_opening' else set()
            if not isinstance(request.data,dict) or not fields<=set(request.data) or set(request.data)-fields-optional:raise ValidationError('Contrato de apertura inválido.')
            try:result=getattr(opening_balances,operation)(company.pk,actor=request.user,**request.data)
            except (AccountingError,ValueError,TypeError):raise ValidationError('Revisa saldos, evidencia, fecha y periodo; libros existentes o FX requieren otra conciliación.') from None
            return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-apertura',parser_classes=[AccountingQueryJSONParser])
    def review_opening(self,request):
        return self._opening_command(request,'review_opening',{'entry_date','evidence_digest','expected_revision','confirmed'})

    @action(detail=False,methods=['post'],url_path='aplicar-apertura',parser_classes=[AccountingQueryJSONParser])
    def apply_opening(self,request):
        return self._opening_command(request,'apply_opening',{'review_id','confirmed'})

    def _bank_reconciliation_command(self,request,operation,fields):
        from apps.core_erp.accounting import bank_reconciliation
        from apps.core_erp.accounting.exceptions import AccountingError
        with transaction.atomic():
            company=self.company();lock_company(company.pk)
            if self.company().pk!=company.pk:raise PermissionDenied('La identidad empresarial cambió.')
            values={k:request.query_params[k] for k in request.query_params if k!='provider_id'} if operation in {'reconciliation_state','reconciliation_sources'} else request.data
            optional={'resolutions','period'} if operation=='review_reconciliation' else set()
            if not isinstance(values,dict) or not fields<=set(values) or set(values)-fields-optional:raise ValidationError('Contrato de conciliación revisada inválido.')
            try:result=getattr(bank_reconciliation,operation)(company.pk,actor=request.user,**values)
            except (AccountingError,ValueError,TypeError):raise ValidationError('Revisa origen, coincidencias, clasificación, reservas activas y revisión persistida; no se presume conexión bancaria.') from None
            return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-conciliacion-bancaria',parser_classes=[AccountingQueryJSONParser])
    def review_bank_reconciliation(self,request):
        return self._bank_reconciliation_command(request,'review_reconciliation',{'account_id','csv_text','evidence_digest','expected_revision','confirmed'})

    @action(detail=False,methods=['post'],url_path='confirmar-conciliacion-bancaria',parser_classes=[AccountingQueryJSONParser])
    def confirm_bank_reconciliation(self,request):
        return self._bank_reconciliation_command(request,'confirm_reconciliation',{'statement_id','review_id','confirmed'})

    @action(detail=False,methods=['get'],url_path='fuentes-conciliacion-bancaria')
    def bank_reconciliation_sources(self,request):
        return self._bank_reconciliation_command(request,'reconciliation_sources',set())

    @action(detail=False,methods=['get'],url_path='estado-conciliacion-bancaria')
    def bank_reconciliation_state(self,request):
        return self._bank_reconciliation_command(request,'reconciliation_state',{'account_id','source_digest'})

    @action(detail=False,methods=['post'],url_path='revisar-liberacion-bancaria',parser_classes=[AccountingQueryJSONParser])
    def review_bank_release(self,request):
        return self._bank_reconciliation_command(request,'review_release',{'reconciliation_id','reason_code','evidence_digest','confirmed'})

    @action(detail=False,methods=['post'],url_path='confirmar-liberacion-bancaria',parser_classes=[AccountingQueryJSONParser])
    def confirm_bank_release(self,request):
        return self._bank_reconciliation_command(request,'confirm_release',{'review_id','confirmed'})

    @action(detail=False,methods=['post'],url_path='comparar-extracto',parser_classes=[AccountingQueryJSONParser])
    @transaction.atomic
    def bank_statement_comparison(self,request):
        from apps.core_erp.accounting.bank_statement import compare_statement
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company();lock_company(company.pk)
        if self.company().pk!=company.pk:raise PermissionDenied('La empresa cambió.')
        if not isinstance(request.data,dict) or set(request.data)!={'account_id','csv_text'}:raise ValidationError('Contrato de extracto inválido.')
        try:result=compare_statement(company.pk,account_id=request.data['account_id'],csv_text=request.data['csv_text'])
        except (AccountingError,ValueError,TypeError):raise ValidationError('Revisa el formato CSV, fechas, importes y clasificación de la cuenta.') from None
        return Response(result)

    @action(detail=False,methods=['get'],url_path='estado-reconocimiento')
    def reservation_recognition_status(self,request):
        from apps.domain_business.comercial.services.reservation_recognition import recognition_status
        from apps.core_erp.accounting.exceptions import AccountingError
        self.company()
        if set(request.query_params)-{'provider_id','reservation_id','before_revision'}:raise ValidationError('Consulta de estado inválida.')
        try:result=recognition_status(actor=request.user,provider_id=owned_provider(request).pk,reservation_id=request.query_params.get('reservation_id'),before_revision=request.query_params.get('before_revision'))
        except (ValueError,TypeError,AccountingError):raise ValidationError('No se pudo verificar el estado de esta reserva.') from None
        return Response(result)

    @action(detail=False,methods=['get'],url_path='cuentas-reconocimiento')
    def recognition_accounts(self,request):
        from apps.core_erp.accounting.catalog import recognition_catalog
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company()
        if set(request.query_params)-{'provider_id','paged','despues_id','buscar'}:raise ValidationError('Parámetros de catálogo no admitidos.')
        try:result=recognition_catalog(company,paged=request.query_params.get('paged'),after=request.query_params.get('despues_id'),search=request.query_params.get('buscar'))
        except (AccountingError,ValueError,TypeError):raise ValidationError('Usa paginación explícita y cursores/búsqueda válidos.') from None
        return Response(result)

    def _recognition_command(self,request,operation,fields):
        from apps.domain_business.comercial.services import reservation_recognition as recognition
        from apps.core_erp.accounting.exceptions import AccountingError
        self.company()
        optional={'advance_allocation'} if operation=='review_recognition' else set()
        if not isinstance(request.data,dict) or not set(fields)<=set(request.data) or set(request.data)-set(fields)-optional:raise ValidationError('Contrato de reconocimiento inválido.')
        try:result=getattr(recognition,operation)(actor=request.user,provider_id=owned_provider(request).pk,**request.data)
        except (ValueError,TypeError,AccountingError):raise ValidationError('Revisa la fuente, cuentas, fecha y periodo contable antes de confirmar.') from None
        return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-reconocimiento-reserva',parser_classes=[AccountingQueryJSONParser])
    def review_reservation_recognition(self,request):
        return self._recognition_command(request,'review_recognition',{'reservation_id','fiscal_review_id','entry_date','account_mapping','service_evidence_digest','policy_evidence_digest','economic_fact','confirmed','expected_revision'})

    @action(detail=False,methods=['post'],url_path='contabilizar-reserva',parser_classes=[AccountingQueryJSONParser])
    def post_reservation_recognition(self,request):
        return self._recognition_command(request,'post_recognition',{'reservation_id','review_id','confirmed'})

    @action(detail=False,methods=['post'],url_path='revisar-contrapartida-reserva',parser_classes=[AccountingQueryJSONParser])
    def review_reservation_reversal(self,request):
        return self._recognition_command(request,'review_reversal',{'reservation_id','reason','evidence_digest','confirmed'})

    @action(detail=False,methods=['post'],url_path='contrapartida-reserva',parser_classes=[AccountingQueryJSONParser])
    def reverse_reservation_recognition(self,request):
        return self._recognition_command(request,'reverse_recognition',{'reservation_id','review_id','confirmed'})

    @action(detail=False,methods=['get'],url_path='fuentes-reserva-fiscal')
    def reservation_fiscal_sources(self,request):
        from apps.domain_business.comercial.services.reservation_fiscal import list_reservation_sources
        self.company()
        try:result=list_reservation_sources(actor=request.user,provider_id=owned_provider(request).pk,after=request.query_params.get('despues_id'))
        except (ValueError,TypeError):raise ValidationError('Cursor de reservas inválido.') from None
        return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-reserva-con-politica',parser_classes=[AccountingQueryJSONParser])
    def review_reservation_policy(self,request):
        from apps.domain_business.comercial.services.reservation_tax_policy import review_with_policy
        from apps.core_erp.accounting.exceptions import AccountingError
        self.company()
        fields={'reservation_id','selection','economic_date','evidence_digest','confirmed','expected_revision'}
        if not isinstance(request.data,dict) or set(request.data)!=fields:raise ValidationError('Contrato de selección tributaria inválido.')
        try:result=review_with_policy(actor=request.user,provider_id=owned_provider(request).pk,**request.data)
        except (ValueError,TypeError,AccountingError):raise ValidationError('Revisa versión, vigencia, desglose y total. Este flujo no contabiliza retenciones ni emite factura.') from None
        return Response(result)

    @action(detail=False,methods=['post'],url_path='revisar-reserva-fiscal',parser_classes=[AccountingQueryJSONParser])
    def review_reservation_fiscal(self,request):
        from apps.domain_business.comercial.services.reservation_fiscal import review_reservation
        from apps.core_erp.accounting.exceptions import AccountingError
        self.company()
        expected={'reservation_id','items','evidence_digest','confirmed','expected_revision'}
        if not isinstance(request.data,dict) or set(request.data)!=expected:raise ValidationError('Contrato de revisión inválido.')
        try:result=review_reservation(actor=request.user,provider_id=owned_provider(request).pk,**request.data)
        except (ValueError,TypeError,AccountingError):raise ValidationError('Revisión no válida para esta reserva.') from None
        return Response(result,status=201)

    @action(detail=False,methods=['post'],url_path='solicitar-factura-reserva',parser_classes=[AccountingQueryJSONParser])
    def request_reservation_invoice(self,request):
        from apps.domain_business.comercial.services.reservation_fiscal import request_reservation_invoice
        from apps.core_erp.accounting.exceptions import AccountingError
        self.company()
        if not isinstance(request.data,dict) or set(request.data)!={'reservation_id','review_id','confirmed'}:raise ValidationError('Contrato de solicitud inválido.')
        try:result=request_reservation_invoice(actor=request.user,provider_id=owned_provider(request).pk,**request.data)
        except (ValueError,TypeError,AccountingError):raise ValidationError('Solicitud no válida para esta reserva.') from None
        return Response(result,status=200 if result['replayed'] else 201)

    @action(detail=False,methods=['post'],url_path='consulta-contable',parser_classes=[AccountingQueryJSONParser])
    def accounting_query(self,request):
        from apps.core_erp.accounting.query_assistant import answer_query
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company()
        try:result=answer_query(company.pk,request.data)
        except (ValueError,TypeError,AccountingError):
            raise ValidationError('Consulta no disponible: usa una pregunta soportada y un intervalo válido para rentabilidad.') from None
        return Response(result)

    @action(detail=False,methods=['get'],url_path='estado-cola-comercial')
    def commercial_outbox_status(self,request):
        from apps.core_erp.accounting.commercial_outbox_status import inspect_commercial_outbox
        return Response(inspect_commercial_outbox(self.company().pk))

    @action(detail=False,methods=['get'],url_path='estado-proyeccion')
    def projection_status(self,request):
        from apps.core_erp.accounting.delivery import status
        return Response(status(self.company().pk))

    @action(detail=False,methods=['get'],url_path='balance-prueba')
    def trial_balance(self,request):
        from datetime import date
        from decimal import Decimal
        from django.utils import timezone
        from apps.core_erp.accounting.reports_engine import ReportsEngine
        try:cutoff=date.fromisoformat(request.query_params.get('fecha_corte',timezone.localdate().isoformat()))
        except (TypeError,ValueError):raise ValidationError('Fecha de corte inválida.') from None
        company=self.company()
        from apps.core_erp.accounting.exceptions import AccountingError
        try:report=ReportsEngine.get_trial_balance(company.pk,cutoff)
        except AccountingError:raise ValidationError('El corte requiere una empresa activa y conciliación de saldos/monedas.') from None
        for line in report['lines']:
            for key in ('debit','credit','balance'):line[key]=format(line[key],'.2f')
        for key in ('total_debit','total_credit'):report[key]=format(report[key],'.2f')
        report['currency']=company.currency
        return Response(report)

    @action(detail=False,methods=['get'],url_path='rentabilidad')
    def profitability(self,request):
        from datetime import date
        from django.utils import timezone
        from apps.core_erp.accounting.reports_engine import ReportsEngine
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company()
        try:
            end=date.fromisoformat(request.query_params.get('hasta',timezone.localdate().isoformat()))
            start=date.fromisoformat(request.query_params.get('desde',end.replace(day=1).isoformat()))
            report=ReportsEngine.get_profitability(company.pk,start,end)
        except (TypeError,ValueError,AccountingError):
            raise ValidationError('Intervalo inválido o saldos pendientes de conciliación contable.') from None
        return Response(report)

    @action(detail=False,methods=['post'],url_path='validar-sobre-fiscal',parser_classes=[FiscalEnvelopeJSONParser])
    def validate_fiscal_envelope(self,request):
        from apps.core_erp.accounting.fiscal_envelope import inspect_envelope
        company=self.company()
        try:report=inspect_envelope(request.data,company.pk)
        except (ValueError,TypeError):raise ValidationError('Sobre fiscal inválido o fuera del alcance empresarial. No se almacenó el documento.') from None
        return Response(report)

    @action(detail=False,methods=['get'],url_path='diagnostico-conciliacion')
    def reconciliation_diagnostic(self,request):
        from apps.core_erp.accounting.reconciliation import inspect_company
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company()
        try:
            raw=request.query_params.get('limite','20')
            if not raw.isascii() or not raw.isdecimal() or len(raw)>2:raise ValueError('Invalid limit.')
            return Response(inspect_company(company.pk,after_id=request.query_params.get('despues_id'),limit=int(raw)))
        except (ValueError,AccountingError):raise ValidationError('Cursor, límite o empresa no válidos para el diagnóstico.') from None

    @action(detail=False,methods=['post'],url_path='simulacion-caja')
    def cash_simulation(self,request):
        from apps.core_erp.intelligence.cash_simulation import simulate
        company=self.company()
        try:result=simulate(request.data)
        except ValueError as exc:raise ValidationError(str(exc)) from None
        return Response({**result,'tenant_id':str(company.pk),'currency':company.currency})

    @action(detail=False,methods=['post'],url_path='backtest-caja')
    def cash_backtest(self,request):
        from apps.core_erp.intelligence.cash_simulation import backtest
        company=self.company()
        try:result=backtest(request.data)
        except ValueError as exc:raise ValidationError(str(exc)) from None
        return Response({**result,'tenant_id':str(company.pk),'currency':company.currency})

    @action(detail=False,methods=['post'],url_path='backtest-ventanas-caja')
    def cash_backtest_windows(self,request):
        from apps.core_erp.intelligence.cash_simulation import backtest_windows
        company=self.company()
        try:result=backtest_windows(request.data)
        except ValueError as exc:raise ValidationError(str(exc)) from None
        return Response({**result,'tenant_id':str(company.pk),'currency':company.currency})

    @action(detail=False,methods=['post'],url_path='sensibilidad-caja')
    def cash_sensitivity(self,request):
        from apps.core_erp.intelligence.cash_simulation import sensitivity
        company=self.company()
        try:result=sensitivity(request.data)
        except ValueError as exc:raise ValidationError(str(exc)) from None
        return Response({**result,'tenant_id':str(company.pk),'currency':company.currency})

    @action(detail=False,methods=['get','post'],url_path='clasificacion-liquidez')
    @transaction.atomic
    def liquidity_classification(self,request):
        from apps.core_erp.accounting import ratios
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company();lock_company(company.pk)
        if self.company().pk!=company.pk:raise PermissionDenied('La identidad empresarial cambió.')
        try:
            if request.method=='GET':return Response(ratios.describe(ratios.latest(company.pk)))
            if not isinstance(request.data,dict) or set(request.data)!={'mapping','evidence_digest','expected_revision','confirmed'}:
                raise ValidationError('Se requiere clasificación, evidencia, revisión esperada y confirmación explícita.')
            return Response(ratios.configure(company.pk,actor=request.user,**request.data),status=201)
        except AccountingError as exc:raise ValidationError(str(exc)) from None

    @action(detail=False,methods=['get'],url_path='historial-liquidez')
    def liquidity_history(self,request):
        from apps.core_erp.accounting import ratios
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company()
        try:
            def positive(name,default=None):
                value=request.query_params.get(name)
                if value is None:return default
                if not value.isascii() or not value.isdecimal() or len(value)>9 or int(value)<1:
                    raise ValueError('Invalid cursor.')
                return int(value)
            return Response(ratios.history(company.pk,before_revision=positive('antes_revision'),limit=positive('limite',20)))
        except (ValueError,AccountingError):
            raise ValidationError('Cursor, límite o integridad de historial inválidos; requiere revisión.') from None

    @action(detail=False,methods=['get'],url_path='liquidez-acida')
    def liquidity_ratio(self,request):
        from datetime import date
        from django.utils import timezone
        from apps.core_erp.accounting import ratios
        from apps.core_erp.accounting.exceptions import AccountingError
        company=self.company()
        try:
            cutoff=date.fromisoformat(request.query_params.get('fecha_corte',timezone.localdate().isoformat()))
            revision=request.query_params.get('revision')
            if revision is not None:
                if not revision.isascii() or not revision.isdecimal() or len(revision)>9 or int(revision)<1:raise ValueError('Invalid revision.')
                revision=int(revision)
            return Response(ratios.quick_ratio(company.pk,cutoff,policy_revision=revision))
        except (TypeError,ValueError,AccountingError):
            raise ValidationError('Fecha, clasificación o saldos pendientes de revisión contable.') from None

    @action(detail=False,methods=['get'])
    def tree(self,request):
        accounts=list(self.get_queryset().order_by('code','pk'))
        by_id={row.pk:row for row in accounts};children={row.pk:[] for row in accounts}
        for row in accounts:
            if row.parent_account_id in children:children[row.parent_account_id].append(row.pk)
        def node(identifier,ancestors):
            if identifier in ancestors or len(ancestors)>100:raise ValidationError('Jerarquía contable cíclica o demasiado profunda.')
            row=by_id[identifier]
            return {'id':str(row.pk),'code':row.code,'name':row.name,'type':row.type,
                    'children':[node(pk,ancestors|{identifier}) for pk in children[identifier]]}
        roots=[row.pk for row in accounts if row.parent_account_id is None]
        reachable=set()
        def walk(identifier):
            if identifier in reachable:return
            reachable.add(identifier)
            for child in children[identifier]:walk(child)
        result=[node(identifier,set()) for identifier in roots]
        for identifier in roots:walk(identifier)
        if len(reachable)!=len(accounts):raise ValidationError('Existen cuentas con jerarquía inválida.')
        return Response(result)
