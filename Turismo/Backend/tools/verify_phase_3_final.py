import os
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')

import django
django.setup()

from rest_framework.test import APIClient
from api.models import Entity, CustomUser
import json

def run_verification():
    client = APIClient()

    # 1. Test Success Response (Wrapped)
    print("Testing Successful response wrapping on /api/v1/public/publicaciones/...")
    response = client.get('/api/v1/public/publicaciones/')
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Keys: {list(data.keys())}")
    assert 'success' in data
    assert data['success'] is True
    assert 'data' in data
    assert 'meta' in data
    print("✅ Success wrap verified.")

    # 2. Test Error Response (Normalized)
    print("\nTesting Error response normalization (401) on /api/v1/governance/plataforma/planes/...")
    response = client.get('/api/v1/governance/plataforma/planes/')
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Errors: {json.dumps(data['errors'], indent=2)}")
    assert data['success'] is False
    assert data['errors'][0]['code'] == 'UNAUTHORIZED'
    print("✅ Error normalization verified.")

if __name__ == "__main__":
    run_verification()
