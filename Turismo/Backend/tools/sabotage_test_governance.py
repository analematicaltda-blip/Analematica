# backend/sabotage_test_governance.py
import os
import django
import logging

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel, AuthorityLevel
from apps.wallet.models import WalletAccount
from apps.wallet.services import WalletService
from apps.companies.models import Company

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_sabotage_test():
    print("🕵️ INICIANDO PRUEBA DE SABOTAJE - GOBERNANZA SOBERANA")

    # 1. Setup
    admin = CustomUser.objects.filter(is_superuser=True).first()
    attacker = CustomUser.objects.create_user(username="malicious_agent", email="attack@dev.null", password="pass", role="TURISTA")
    company = Company.objects.first()

    # Wallet victima
    victim, _ = CustomUser.objects.get_or_create(username="victim", defaults={"email":"v@v.com", "role":"TURISTA"})
    w_victim, _ = WalletAccount.objects.get_or_create(
        user=victim, owner_type="TOURIST", owner_id=str(victim.id),
        defaults={"company": company, "balance": 500000}
    )

    kernel = GovernanceKernel(attacker)

    # --- INTENTO 1: Inyectar intención no registrada ---
    print("\n--- INTENTO 1: Inyectar intención ilegal ---")
    try:
        kernel.resolve_and_execute("DRAIN_ALL_WALLETS", {"confirm": True})
    except Exception as e:
        print(f"✅ BLOQUEO EXITOSO: {e}")

    # --- INTENTO 2: Escalar autoridad (Ejecutar acción de SuperAdmin como Turista) ---
    print("\n--- INTENTO 2: Escalar autoridad (WALLET_FREEZE como Turista) ---")
    try:
        kernel.resolve_and_execute("WALLET_FREEZE", {"wallet_id": str(w_victim.id), "motivo": "I hate you"})
    except Exception as e:
        print(f"✅ BLOQUEO EXITOSO: {e}")

    # --- INTENTO 3: Violar dominio (Agente IA operando fuera de su mandato) ---
    print("\n--- INTENTO 3: Violación de Dominio (Agente de Marketing en Finanzas) ---")
    attacker.is_agent = True
    attacker.agent_domain = "marketing"
    attacker.save()

    try:
        kernel.resolve_and_execute("WALLET_DEPOSIT", {"wallet_id": str(w_victim.id), "amount": 1000})
    except Exception as e:
        print(f"✅ BLOQUEO EXITOSO: {e}")

    # --- INTENTO 4: MODO ATAQUE ACTIVADO (Bloqueo Total) ---
    print("\n--- INTENTO 4: Sistema en MODO ATAQUE ---")
    from apps.admin_plataforma.models import GovernancePolicy
    GovernancePolicy.objects.create(name="SYSTEM_ATTACK_MODE", type="BLOCK", is_active=True, domain="global")

    try:
        # Incluso una intención permitida para el rol debería fallar si el sistema está congelado
        kernel.resolve_and_execute("WALLET_PAY", {"to_wallet_id": "any", "amount": 10})
    except Exception as e:
        print(f"✅ BLOQUEO EXITOSO (SISTEMA CONGELADO): {e}")

    print("\n🏁 PRUEBA DE SABOTAJE FINALIZADA.")

if __name__ == "__main__":
    run_sabotage_test()
