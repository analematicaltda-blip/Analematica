from django.db import DatabaseError
from rest_framework import viewsets,permissions,mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Wallet,WalletTransaccion,WalletTransferIntent
from .serializers import (WalletAccountSerializer,WalletTransactionSerializer,TransferIntentSerializer,PrepareTransferSerializer,ReviewTransferSerializer,ExecuteTransferSerializer)
from .services.wallet_service import WalletOperationUnavailable
from .services import internal_transfer
from .services import device_approvals
from .serializers import DeviceChallengeSerializer,DeviceAttestationSerializer,DeviceCredentialSerializer
from .models import WalletDeviceCredential
from .services.access_policy import accessible_wallets,register_personal_profile,personal_signup
from rest_framework.exceptions import ValidationError
import base64

class PrivateWalletMixin:
    permission_classes=[permissions.IsAuthenticated]
    def finalize_response(self,request,response,*args,**kwargs):
        response=super().finalize_response(request,response,*args,**kwargs)
        response['Cache-Control']='no-store'
        return response
    def handle_exception(self,exception):
        if isinstance(exception,DatabaseError):
            exception=WalletOperationUnavailable('No se pudo confirmar el resultado. Consulte el estado de la intención antes de reintentar; conserve la misma clave de idempotencia.')
        return super().handle_exception(exception)

class WalletAccountViewSet(PrivateWalletMixin,viewsets.ReadOnlyModelViewSet):
    serializer_class=WalletAccountSerializer
    def get_queryset(self):
        return accessible_wallets(self.request.user)
    @action(detail=False,methods=['get','post'])
    def profile(self,request):
        if request.method=='POST':
            if request.data:raise ValidationError('El alta personal no acepta roles, titulares, empresa o saldos del cliente.')
            register_personal_profile(request.user)
        wallets=list(accessible_wallets(request.user))
        personal=[str(wallet.pk) for wallet in wallets if wallet.owner_type in {'TURISTA','EMPLEADO'}]
        corporate=[str(wallet.pk) for wallet in wallets if wallet.owner_type not in {'TURISTA','EMPLEADO'}]
        return Response({'user_id':request.user.pk,'username':request.user.get_username(),'wallet_registered':personal_signup(request.user),'personal_wallet_ids':personal,'company_wallet_ids':corporate,'company_panel_enabled':bool(corporate),'company_access_rule':'VERIFIED_COMPANY_ADMINISTRATOR_ONLY','financial_activation_automatic':False})
    @action(detail=True,methods=['post'])
    def deposit(self,request,pk=None):
        self.get_object();raise WalletOperationUnavailable()
    @action(detail=False,methods=['post'])
    def pay(self,request):raise WalletOperationUnavailable()
    @action(detail=True,methods=['post'])
    def liquidate(self,request,pk=None):
        self.get_object();raise WalletOperationUnavailable()
    @action(detail=True,methods=['post'])
    def freeze(self,request,pk=None):
        self.get_object();raise WalletOperationUnavailable()

class WalletTransactionViewSet(PrivateWalletMixin,viewsets.ReadOnlyModelViewSet):
    serializer_class=WalletTransactionSerializer
    def get_queryset(self):
        return WalletTransaccion.objects.filter(movimientos__wallet__in=accessible_wallets(self.request.user)).distinct()
    @action(detail=True,methods=['post'])
    def refund(self,request,pk=None):
        self.get_object();raise WalletOperationUnavailable()

class WalletTransferViewSet(PrivateWalletMixin,mixins.CreateModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    serializer_class=TransferIntentSerializer
    def get_queryset(self):return WalletTransferIntent.objects.filter(requested_by_id=self.request.user.pk,source__in=accessible_wallets(self.request.user)).order_by('-created_at')
    def create(self,request):
        form=PrepareTransferSerializer(data=request.data);form.is_valid(raise_exception=True)
        data=form.validated_data
        intent=internal_transfer.prepare(request.user,data['source'],data['destination'],data['amount'],data['idempotency_key'])
        return Response(self.get_serializer(intent).data,status=201)
    @action(detail=True,methods=['post'])
    def review(self,request,pk=None):
        self.get_object()
        form=ReviewTransferSerializer(data=request.data);form.is_valid(raise_exception=True)
        intent,token=internal_transfer.review(request.user,pk,form.validated_data['digest'],form.validated_data.get('device_proof'))
        return Response({'intent':self.get_serializer(intent).data,'confirmation':token})
    @action(detail=True,methods=['post'])
    def execute(self,request,pk=None):
        self.get_object()
        form=ExecuteTransferSerializer(data=request.data);form.is_valid(raise_exception=True)
        intent=internal_transfer.execute(request.user,pk,form.validated_data['digest'],form.validated_data['confirmation'],form.validated_data.get('device_proof'))
        return Response(self.get_serializer(intent).data)

    @action(detail=True,methods=['post'])
    def challenge(self,request,pk=None):
        self.get_object()
        form=DeviceChallengeSerializer(data=request.data);form.is_valid(raise_exception=True)
        challenge,message=device_approvals.issue(request.user,pk,form.validated_data['credential'],form.validated_data['phase'])
        return Response({'challenge':str(challenge.pk),'credential':str(challenge.credential_id),'payload':base64.b64encode(message).decode('ascii'),'expires_at':challenge.expires_at})

class WalletDeviceViewSet(PrivateWalletMixin,mixins.CreateModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    serializer_class=DeviceCredentialSerializer
    def get_queryset(self):return WalletDeviceCredential.objects.filter(user_id=self.request.user.pk).order_by('-created_at')
    def create(self,request):
        credential,nonce=device_approvals.begin_enrollment(request.user)
        return Response({'device':self.get_serializer(credential).data,'enrollment_challenge':nonce},status=201)
    @action(detail=True,methods=['post'])
    def attest(self,request,pk=None):
        self.get_object()
        form=DeviceAttestationSerializer(data=request.data);form.is_valid(raise_exception=True)
        device=device_approvals.attest(request.user,pk,form.validated_data['public_key'],form.validated_data['certificate_chain'],form.validated_data['enrollment_authorization'])
        return Response(self.get_serializer(device).data)
    @action(detail=True,methods=['post'])
    def revoke(self,request,pk=None):
        self.get_object();device=device_approvals.revoke(request.user,pk)
        return Response(self.get_serializer(device).data)
