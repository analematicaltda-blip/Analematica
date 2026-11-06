import os
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')

import django
django.setup()

from rest_framework.test import APIClient
from rest_framework import status
import json

def test_api_normalization():
    client = APIClient()

    # 1. Test an error (unauthorized) - Should follow the errors format
    print("Testing Unauthorized error response on normalized route...")
    # Using a route that is definitely in urlpatterns
    error_response = client.get('/api/v1/sales/')
    print(f"Status Code: {error_response.status_code}")

    try:
        error_data = error_response.json()
        print(f"Response: {json.dumps(error_data, indent=2)}")

        # Assertions for error structure
        assert error_data['success'] is False
        assert error_data['data'] is None
        assert isinstance(error_data['errors'], list)
        assert any(e['code'] == 'UNAUTHORIZED' for e in error_data['errors'])
        print("✅ Error structure is correct.")
    except Exception as e:
        print(f"❌ Error during unauthorized test: {e}")

    # 2. Test a successful response
    print("\nTesting departments for successful wrap...")
    response = client.get('/api/departments/')

    try:
        data = response.json()
        print(f"Status Code: {response.status_code}")
        if 'success' in data:
            print(f"Response structure: {list(data.keys())}")
            assert data['success'] is True
            assert 'data' in data
            assert 'meta' in data
            print("✅ Success structure is correct (Global Renderer active).")
        else:
            print("❌ Renderer did not wrap the response.")
    except Exception as e:
        print(f"❌ Error during success test: {e}")

if __name__ == "__main__":
    test_api_normalization()
