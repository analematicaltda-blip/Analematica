import uuid
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import CustomUser, Profile
from apps.turismo.models.divipola import Department, Municipality

class LocationAwareAuthTests(APITestCase):
    def setUp(self):
        self.dept = Department.objects.create(code="50", name="Meta")
        self.mun = Municipality.objects.create(code="50568", name="Puerto Gaitán", dept=self.dept)
        self.register_url = reverse('rest_register')

    def test_registration_with_location(self):
        data = {
            "email": "testuser@example.com",
            "password": "strong_password123",
            "password1": "strong_password123",
            "password2": "strong_password123",
            "dept_code": "50",
            "mun_code": "50568"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        user = CustomUser.objects.get(email="testuser@example.com")
        self.assertEqual(user.username, "testuser@example.com")

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.department, self.dept)
        self.assertEqual(profile.municipality, self.mun)

    def test_registration_with_invalid_location(self):
        data = {
            "email": "invalid@example.com",
            "password": "strong_password123",
            "password1": "strong_password123",
            "password2": "strong_password123",
            "dept_code": "99", # Invalid
            "mun_code": "50568"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verify the error is present in the enterprise error format
        errors = response.data.get("errors", [])
        field_errors = [e.get("field") for e in errors]
        self.assertIn("dept_code", field_errors)
