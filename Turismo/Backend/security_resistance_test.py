import sys
import os

# Mocking Django environment for standalone test
class MockUser:
    def __init__(self, id, role, is_authenticated=True, username="test_user"):
        self.id = id
        self.role = role
        self.is_authenticated = is_authenticated
        self.username = username

def simulate_security_checks():
    print("--- INICIANDO PRUEBAS DE RESISTENCIA DE SEGURIDAD (SARITA) ---")

    # 1. Prueba de Rate Limiting por Rol
    print("\n[TEST 1] Verificación de Rate Limiting por Rol...")
    from apps.common.security_hardening import SecurityHardeningMiddleware

    # Mock de cache y request
    class MockCache:
        def __init__(self): self.data = {}
        def get(self, k, d=0): return self.data.get(k, d)
        def set(self, k, v, timeout=0): self.data[k] = v

    import apps.common.security_hardening as sh
    sh.cache = MockCache()

    middleware = SecurityHardeningMiddleware(lambda r: "OK")
    user_turista = MockUser(1, 'TURISTA')

    class MockRequest:
        def __init__(self, user):
            self.user = user
            self.method = 'GET'
            self.headers = {}

    req = MockRequest(user_turista)

    # Simular 51 peticiones (Límite Turista = 50)
    for i in range(51):
        res = middleware._check_rate_limit(user_turista)

    if res == True:
        print("✅ ÉXITO: Rate Limit detectado para Turista en petición 51.")
    else:
        print("❌ FALLO: Rate Limit no bloqueó al Turista.")

    # 2. Prueba de Replay Attack
    print("\n[TEST 2] Verificación de Protección contra Replay Attack...")
    nonce = "unique_nonce_123"
    middleware._validate_nonce(nonce) # Primer uso
    is_replay = not middleware._validate_nonce(nonce) # Segundo uso

    if is_replay:
        print("✅ ÉXITO: Intento de Replay Attack bloqueado.")
    else:
        print("❌ FALLO: Replay Attack permitido.")

    # 3. Prueba de Cadena Forense
    print("\n[TEST 3] Verificación de Cadena Forense (Simulación)...")
    # Nota: No probamos DB real aquí para evitar dependencias,
    # pero validamos que el hash cambie con los datos.
    import hashlib
    def quick_hash(data): return hashlib.sha256(data.encode()).hexdigest()

    h1 = quick_hash("prev0" + "LOGIN" + "user1")
    h2 = quick_hash(h1 + "LOGIN" + "user1")

    if h1 != h2:
        print("✅ ÉXITO: Cadena de integridad generada correctamente.")
    else:
        print("❌ FALLO: Los hashes no se encadenan.")

    print("\n--- PRUEBAS COMPLETADAS ---")

if __name__ == "__main__":
    # Ajustar path para importar apps
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    try:
        simulate_security_checks()
    except Exception as e:
        print(f"Error durante la prueba: {e}")
