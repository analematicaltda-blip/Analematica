"""Legacy viewset compatibility, deliberately unmounted and read-only.

Core/native report URLs remain unchanged. Registering this adapter must not add
an alternative write/reversal path around the existing reviewed commands.
"""
from rest_framework import viewsets,filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Account,JournalEntry
from .serializers import AccountSerializer,JournalEntrySerializer
from .report_access import AccountingReportView,report_company

class BaseAccountingViewSet(viewsets.ReadOnlyModelViewSet,AccountingReportView):
    filter_backends=[DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    ordering_fields=('id',)
    def get_queryset(self):
        company=getattr(self,'authorized_company',None)
        if company is None:raise PermissionDenied('Empresa contable no autorizada.')
        return self.model.plain_objects.filter(tenant_id=company.pk).order_by('pk')
    def scoped(self,request,operation,*args,**kwargs):
        with report_company(request) as company:
            self.authorized_company=company
            try:return operation(request,*args,**kwargs)
            finally:del self.authorized_company
    def list(self,request,*args,**kwargs):
        return self.scoped(request,super().list,*args,**kwargs)
    def retrieve(self,request,*args,**kwargs):
        return self.scoped(request,super().retrieve,*args,**kwargs)

class AccountViewSet(BaseAccountingViewSet):
    model=Account
    serializer_class=AccountSerializer
    filterset_fields=('type','is_active','parent_account')
    search_fields=('code','name')
    ordering_fields=('id','code','name')

class JournalEntryViewSet(BaseAccountingViewSet):
    model=JournalEntry
    serializer_class=JournalEntrySerializer
    filterset_fields=('date','is_posted','period')
    search_fields=('reference','description')
    ordering_fields=('id','date')
    def get_queryset(self):
        return super().get_queryset().filter(is_posted=True)
    @action(detail=True,methods=['post'])
    def reverse(self,request,pk=None):
        with report_company(request) as company:
            self.authorized_company=company
            try:self.get_object()
            finally:del self.authorized_company
            return Response({'code':'USE_REVIEWED_REVERSAL_WORKFLOW',
                             'detail':'Utiliza el flujo contable revisado para solicitar una contrapartida.'},status=409)
