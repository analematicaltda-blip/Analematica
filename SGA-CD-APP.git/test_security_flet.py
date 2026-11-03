"""
Test Script for Flet Security Shield, API Interceptor, and Dark Metallic Blue Banners
"""
import unittest
from unittest.mock import MagicMock, patch
import requests

from utils.security_shield import (
    sanitize_input_for_flet,
    sanitize_dict_inputs,
    mask_sensitive_token,
    format_masked_error_code
)
from utils.api_client import ApiClient
from utils.sync_manager import SyncManager


class TestFletSecurityShieldAndAPI(unittest.TestCase):

    def test_sanitize_input_for_flet(self):
        malicious_input = "<script>alert('xss')</script>Hello <b>World</b><iframe src='bad.com'></iframe>"
        clean = sanitize_input_for_flet(malicious_input)
        self.assertNotIn("<script>", clean)
        self.assertNotIn("<iframe>", clean)
        self.assertIn("Hello", clean)

    def test_format_masked_error_code(self):
        self.assertEqual(format_masked_error_code(401), "STD-ERR-401-UNAUTHORIZED")
        self.assertEqual(format_masked_error_code(403), "STD-ERR-403-FORBIDDEN")
        self.assertEqual(format_masked_error_code(500), "STD-ERR-500-INTERNAL-ERROR")

    def test_mask_sensitive_token(self):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature"
        masked = mask_sensitive_token(token)
        self.assertTrue(masked.startswith("eyJh..."))
        self.assertTrue(masked.endswith("ture"))

    @patch('requests.request')
    def test_api_client_intercepts_403(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_request.return_value = mock_response

        client = ApiClient(base_url="http://localhost:8000", tenant_api_key="test_key")
        result = client._make_request("GET", "/api/v1/protected")

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("error"))
        self.assertEqual(result.get("code"), "STD-ERR-403-FORBIDDEN")

    def test_sync_manager_attendance_payload_taxonomy(self):
        payload = SyncManager.format_attendance_payload(
            actividad="Disciplinas Deportivas - Fútbol",
            ubicacion="Cancha Municipal"
        )
        self.assertEqual(payload["actividad"], "Disciplinas Deportivas - Fútbol")
        self.assertIn("timestamp", payload)


if __name__ == '__main__':
    unittest.main()
