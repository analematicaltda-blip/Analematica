from django.test import TestCase
from api.models import CustomUser
from apps.companies.models import Company
from apps.wallet.models import Wallet, WalletTransaccion
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel, AuthorityLevel
from decimal import Decimal

class WalletIntegrationTest(TestCase):
    databases = {'default', 'wallet_db'}

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin_test', email='admin_test@test.com', password='password'
        )
        self.company = Company.objects.create(name='Test Company Wallet', code='TCW')
        self.tourist_user = CustomUser.objects.create_user(
            username='tourist_test', email='tourist_test@test.com', password='password',
            role=CustomUser.Role.TURISTA
        )
        self.provider_user = CustomUser.objects.create_user(
            username='provider_test', email='provider_test@test.com', password='password',
            role=CustomUser.Role.PRESTADOR
        )

        # Get or create wallets (signals might have created them)
        self.tourist_wallet, _ = Wallet.objects.get_or_create(
            user_id=self.tourist_user.id,
            owner_id=str(self.tourist_user.id),
            defaults={
                'owner_type': Wallet.OwnerType.TURISTA,
                'saldo_disponible': Decimal('100.00')
            }
        )
        if self.tourist_wallet.saldo_disponible < Decimal('100.00'):
            self.tourist_wallet.saldo_disponible = Decimal('100.00')
            self.tourist_wallet.save()

        self.provider_wallet, _ = Wallet.objects.get_or_create(
            user_id=self.provider_user.id,
            owner_id='some-uuid-for-provider-test',
            defaults={
                'owner_type': Wallet.OwnerType.HOTEL,
                'saldo_disponible': Decimal('0.00')
            }
        )

    def test_governance_payment(self):
        kernel = GovernanceKernel(user=self.tourist_user)

        # Perform payment through kernel
        result = kernel.resolve_and_execute(
            intention_name="WALLET_PAY",
            parameters={
                "to_wallet_id": str(self.provider_wallet.id),
                "amount": 50.00,
                "description": "Test Payment"
            }
        )

        self.assertEqual(result['status'], 'SUCCESS')
        self.tourist_wallet.refresh_from_db()
        self.provider_wallet.refresh_from_db()

        self.assertEqual(self.tourist_wallet.saldo_disponible, Decimal('50.00'))
        # El prestador recibe el 90% (50 * 0.9 = 45)
        self.assertEqual(self.provider_wallet.saldo_disponible, Decimal('45.00'))

        # Check transaction
        tx = WalletTransaccion.objects.get(id=result['transaction_id'])
        # El monto_total registrado en la transaccion es la suma de los montos de movimientos PAGO e INGRESO
        # PAGO(50) + INGRESO(45) = 95
        self.assertEqual(tx.monto_total, Decimal('95.00'))

    def test_insufficient_funds(self):
        kernel = GovernanceKernel(user=self.tourist_user)

        with self.assertRaises(ValueError):
            kernel.resolve_and_execute(
                intention_name="WALLET_PAY",
                parameters={
                    "to_wallet_id": str(self.provider_wallet.id),
                    "amount": 150.00
                }
            )

    def test_freeze_wallet(self):
        kernel = GovernanceKernel(user=self.admin)

        result = kernel.resolve_and_execute(
            intention_name="WALLET_FREEZE",
            parameters={
                "wallet_id": str(self.tourist_wallet.id),
                "motivo": "Auditoria de seguridad"
            }
        )

        self.assertEqual(result['status'], 'SUCCESS')
        self.tourist_wallet.refresh_from_db()
        self.assertEqual(self.tourist_wallet.estado, Wallet.Status.BLOQUEADO)

        # Now payment should fail
        kernel_tourist = GovernanceKernel(user=self.tourist_user)
        # El Kernel lanza ValueError si el saldo es insuficiente o hay bloqueo
        with self.assertRaises(ValueError):
            kernel_tourist.resolve_and_execute(
                intention_name="WALLET_PAY",
                parameters={
                    "to_wallet_id": str(self.provider_wallet.id),
                    "amount": 10.00
                }
            )
