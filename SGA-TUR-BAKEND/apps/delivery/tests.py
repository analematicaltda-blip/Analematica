from django.test import TestCase
from api.models import CustomUser
from apps.companies.models import Company
from apps.wallet.models import WalletAccount
from apps.delivery.models import DeliveryCompany, Driver, Vehicle, DeliveryService
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
from decimal import Decimal

class DeliveryIntegrationTest(TestCase):
    databases = {'default', 'wallet_db', 'delivery_db'}

    def setUp(self):
        self.company = Company.objects.create(name='Delivery Corp', code='DC')
        self.delivery_company = DeliveryCompany.objects.create(name='Logistics SARITA', company=self.company)

        self.tourist = CustomUser.objects.create_user(
            username='tourist_del', email='tourist_del@test.com', password='password',
            role=CustomUser.Role.TURISTA
        )
        self.driver_user = CustomUser.objects.create_user(
            username='driver_del', email='driver_del@test.com', password='password',
            role=CustomUser.Role.DELIVERY
        )

        self.driver = Driver.objects.create(user=self.driver_user, delivery_company=self.delivery_company, license_number='LIC-123')
        self.vehicle = Vehicle.objects.create(plate='XYZ-789', vehicle_type='MOTO', delivery_company=self.delivery_company, current_driver=self.driver)

        # Wallets (created via signal, but let's ensure balance)
        self.tourist_wallet = WalletAccount.objects.get(user_id=self.tourist.id)
        self.tourist_wallet.saldo_disponible = Decimal('50000.00')
        self.tourist_wallet.save()

        self.driver_wallet = WalletAccount.objects.get(user_id=self.driver_user.id)

    def test_full_delivery_flow(self):
        kernel = GovernanceKernel(user=self.tourist)

        # 1. Request Delivery
        res1 = kernel.resolve_and_execute("DELIVERY_REQUEST", {
            "origin_address": "Point A",
            "destination_address": "Point B",
            "estimated_price": 20000.00
        })
        self.assertEqual(res1['status'], 'SUCCESS')
        service_id = res1['service_id']

        # 2. Assign Driver (Admin)
        admin = CustomUser.objects.create_superuser('admin_del', 'admin_del@test.com', 'password')
        kernel_admin = GovernanceKernel(user=admin)
        res2 = kernel_admin.resolve_and_execute("DELIVERY_ASSIGN", {
            "service_id": service_id,
            "driver_id": str(self.driver.id),
            "vehicle_id": str(self.vehicle.id)
        })
        self.assertEqual(res2['status'], 'SUCCESS')

        # 3. Completar con Evidencia vía Kernel
        kernel_driver = GovernanceKernel(user=self.driver_user)
        res3 = kernel_driver.resolve_and_execute("DELIVERY_COMPLETE", {
            "service_id": service_id,
            "firma": "Firma Digital ABC",
            "observaciones": "Entregado en portería"
        })
        self.assertEqual(res3['status'], 'SUCCESS')

        # 4. Verify Payment in Wallet
        self.tourist_wallet.refresh_from_db()
        self.driver_wallet.refresh_from_db()

        self.assertEqual(self.tourist_wallet.saldo_disponible, Decimal('30000.00'))
        self.assertEqual(self.driver_wallet.saldo_disponible, Decimal('20000.00'))

        # 5. Verify Service Status
        service = DeliveryService.objects.get(id=service_id)
        self.assertEqual(service.status, DeliveryService.Status.ENTREGADO)
        self.assertIsNotNone(service.wallet_transaction)
