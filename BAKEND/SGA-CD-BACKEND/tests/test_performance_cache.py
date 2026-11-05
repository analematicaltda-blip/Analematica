import time
import pytest
from app.core.cache import InMemoryCache, cache_service
from app.core.security import create_access_token
from app.models.dropdowns import TipoDocumento
from app.models.user import Usuario, RolesEnum

def test_cache_service_basic_and_ttl():
    cache = InMemoryCache(default_ttl=1)
    cache.set("key1", "val1")
    assert cache.get("key1") == "val1"

    # Invalidation
    cache.invalidate("key1")
    assert cache.get("key1") is None

    # Expiry
    cache.set("key2", "val2", ttl=1)
    time.sleep(1.1)
    assert cache.get("key2") is None

def test_cache_prefix_invalidation_and_tenant_isolation():
    cache = InMemoryCache(default_ttl=300)

    # Simulate tenant 1 and tenant 2 data
    cache.set("dropdown:tipos_documento:tenant:1:skip:0:limit:100", ["CC", "TI"])
    cache.set("dropdown:tipos_documento:tenant:2:skip:0:limit:100", ["Pasaporte", "CE"])

    assert cache.get("dropdown:tipos_documento:tenant:1:skip:0:limit:100") == ["CC", "TI"]
    assert cache.get("dropdown:tipos_documento:tenant:2:skip:0:limit:100") == ["Pasaporte", "CE"]

    # Invalidate tenant 1
    cache.invalidate_prefix("dropdown:tipos_documento:tenant:1")

    # Tenant 1 cache cleared, tenant 2 remains intact
    assert cache.get("dropdown:tipos_documento:tenant:1:skip:0:limit:100") is None
    assert cache.get("dropdown:tipos_documento:tenant:2:skip:0:limit:100") == ["Pasaporte", "CE"]

def test_dropdown_endpoint_caching_performance(client, db):
    # Create test user for auth
    user = Usuario(
        nombre_usuario="perf_user",
        correo="perf_user@example.com",
        password_hash="pw",
        rol=RolesEnum.admin_empresa,
        activo=True,
        inquilino_id=1
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Ensure test items exist
    item1 = TipoDocumento(nombre="Cédula Test Perf", inquilino_id=1)
    db.add(item1)
    db.commit()
    db.refresh(item1)

    # First call - cache miss
    cache_service.clear()
    t0 = time.time()
    response1 = client.get("/api/v1/dropdowns/tipos_documento/", headers=headers)
    t1 = time.time()
    dur1 = t1 - t0
    assert response1.status_code == 200

    # Second call - cache hit
    t2 = time.time()
    response2 = client.get("/api/v1/dropdowns/tipos_documento/", headers=headers)
    t3 = time.time()
    dur2 = t3 - t2
    assert response2.status_code == 200
    assert response1.json() == response2.json()

    # Cleanup DB
    db.delete(item1)
    db.delete(user)
    db.commit()

def test_static_files_cache_control_headers(client):
    import os
    test_file_path = "app/static/test_asset.txt"
    with open(test_file_path, "w") as f:
        f.write("static asset content")
    try:
        response = client.get("/static/test_asset.txt")
        assert response.status_code == 200
        assert "Cache-Control" in response.headers
        assert "max-age=31536000" in response.headers["Cache-Control"]
        assert "immutable" in response.headers["Cache-Control"]
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
