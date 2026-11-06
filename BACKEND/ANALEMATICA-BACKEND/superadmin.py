from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.social.models import SocialConversation, SocialGiftCatalog, SocialGiftTransaction
from apps.turismo.models.divipola import Department, Municipality
from apps.core_erp.accounting.models import Account
from apps.admin_plataforma.permissions import IsSuperAdmin

class SuperAdminSystemAuditViewSet(viewsets.ViewSet):
    """
    Controlador Maestro para el Super Admin.
    Gestión unificada de componentes transversales: Chat, Video, Regalos, DIVIPOLA y Contabilidad.
    """
    permission_classes = [IsSuperAdmin]

    # --- Gestión de Chat y Video ---
    @action(detail=False, methods=['get'], url_path='social/active-rooms')
    def active_rooms(self, request):
        rooms = SocialConversation.objects.filter(conversation_type__in=['public_room', 'private_room'])
        return Response([
            {
                "id": r.id,
                "title": r.title,
                "type": r.conversation_type,
                "entry_fee": r.entry_fee,
                "adult_only": r.is_adult_only,
                "created_at": r.created_at,
                "members_count": r.memberships.count()
            } for r in rooms
        ])

    # --- Gestión de Regalos y Comisiones ---
    @action(detail=False, methods=['get'], url_path='financial/gift-catalog')
    def gift_catalog(self, request):
        catalog = SocialGiftCatalog.objects.all()
        return Response([
            {
                "id": g.id,
                "code": g.code,
                "name": g.name,
                "price": g.price,
                "active": g.active
            } for g in catalog
        ])

    @action(detail=False, methods=['get'], url_path='financial/gift-audit')
    def gift_audit(self, request):
        txs = SocialGiftTransaction.objects.all().order_by('-created_at')[:50]
        return Response([
            {
                "id": t.id,
                "sender": t.sender.username,
                "receiver": t.receiver.username,
                "amount": t.amount,
                "commission_2pct": float(t.amount) * 0.02,
                "status": t.status,
                "timestamp": t.created_at
            } for t in txs
        ])

    # --- Gestión DIVIPOLA ---
    @action(detail=False, methods=['get'], url_path='territorial/depts')
    def list_departments(self, request):
        depts = Department.objects.all()
        return Response([{"code": d.code, "name": d.name} for d in depts])

    @action(detail=False, methods=['post'], url_path='territorial/muns/create')
    def create_municipality(self, request):
        data = request.data
        dept = Department.objects.get(code=data['dept_code'])
        mun = Municipality.objects.create(
            code=data['code'],
            name=data['name'],
            dept=dept
        )
        return Response({"status": "Created", "id": mun.code}, status=status.HTTP_201_CREATED)

    # --- Gestión de Configuraciones Globales ---
    @action(detail=False, methods=['get', 'patch'], url_path='settings/global')
    def global_settings(self, request):
        from .models import PlatformGlobalSettings
        obj, _ = PlatformGlobalSettings.objects.get_or_create(id='00000000-0000-0000-0000-000000000001') # Singleton placeholder
        if request.method == 'PATCH':
            # Update settings (simplified)
            for key, value in request.data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            obj.save()
            return Response({"status": "Updated"})

        return Response({
            "social_gift_commission_pct": obj.social_gift_commission_pct,
            "room_entry_commission_pct": obj.room_entry_commission_pct,
            "max_gift_amount": obj.max_gift_amount,
            "maintenance_mode": obj.maintenance_mode
        })

    # --- Gestión de Cuentas (PUC Global) ---
    @action(detail=False, methods=['get'], url_path='accounting/global-ledger')
    def global_ledger_overview(self, request):
        # Muestra un resumen de cuentas activas en todo el sistema (cross-tenant)
        from django.db.models import Count
        ledger_stats = Account.plain_objects.values('type').annotate(count=Count('id'))
        return Response({
            "total_accounts_system_wide": Account.plain_objects.count(),
            "distribution": ledger_stats
        })
