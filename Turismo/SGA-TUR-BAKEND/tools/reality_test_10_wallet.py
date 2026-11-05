import os
import django
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.wallet.models import Wallet, WalletTransaccion
from apps.wallet.services import WalletService

def run_test():
    print("🚀 INICIANDO PRUEBA REAL DE BILLETERA (Escrow Flow)")
    user, _ = CustomUser.objects.get_or_create(username="tester", defaults={"email": "tester@sarita.com"})
    wallet, _ = Wallet.objects.get_or_create(user=user, defaults={"saldo_disponible": Decimal("1000.00")})

    ws = WalletService(user)
    print(f"Saldo inicial: {wallet.saldo_disponible}")

    # 1. Autorizar (Bloqueo)
    print("Ejecutando bloqueo de 500...")
    tx = ws.authorize_payment(to_wallet_id=None, amount=500, related_service_id="SERV-001")
    wallet.refresh_from_db()
    print(f"Saldo tras bloqueo: Disponible={wallet.saldo_disponible}, Bloqueado={wallet.saldo_bloqueado}")

    # 2. Liberar
    print(f"Liberando pago TX {tx.id}...")
    ws.release_payment(tx.id)
    wallet.refresh_from_db()
    print(f"Saldo final: Disponible={wallet.saldo_disponible}, Bloqueado={wallet.saldo_bloqueado}")

    if wallet.saldo_bloqueado == 0:
        print("✅ PRUEBA EXITOSA: Flujo de custodia validado.")
    else:
        print("❌ FALLO: El saldo bloqueado no se liberó.")

if __name__ == "__main__":
    run_test()
