"""Explicit disabled-module boundary: no invented financial implementation."""
from rest_framework import permissions,status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

def unavailable(module,reason):
    return Response({'errors':[{'code':'module_not_enabled','message':reason}],'meta':{'module':module,'writes_enabled':False}},status=status.HTTP_503_SERVICE_UNAVAILABLE)

class PendingModuleView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    module=''
    blocker=''
    def unavailable(self,request,*args,**kwargs):return unavailable(self.module,self.blocker)
    get=post=put=patch=delete=unavailable

class PendingPurchasesViewSet(viewsets.ViewSet):
    permission_classes=[permissions.IsAuthenticated]
    def unavailable(self,request,*args,**kwargs):return unavailable('erp.compras','Implementación contable pendiente; no se realizó ninguna operación.')
    list=retrieve=create=update=partial_update=destroy=unavailable
    @action(detail=True,methods=['post'],url_path='pagar')
    def pagar_factura(self,request,pk=None):return self.unavailable(request)
