import os
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')

import django
django.setup()

from rest_framework.test import APIClient
import json

def test_error_normalization():
    client = APIClient()

    # Test 401 (Unauthorized) on a protected endpoint that we know exists
    print("\nTesting 401 error response on /api/v1/sales/plans/...")
    response = client.get('/api/v1/sales/plans/')
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type')}")

    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        assert data['success'] is False
        assert data['data'] is None
        assert isinstance(data['errors'], list)
        assert data['errors'][0]['code'] == 'UNAUTHORIZED'
        print("✅ 401 normalization correct.")
    except Exception as e:
        print(f"❌ Error during 401 test: {e}")
        if hasattr(response, 'content'):
            print(f"Raw content: {response.content[:200]}")

if __name__ == "__main__":
    test_error_normalization()
