# funnels/tests_runtime.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from infrastructure.models import Tenant
from .models import Funnel, FunnelVersion, FunnelPublication, Lead, LeadEvent, LeadState

User = get_user_model()

class FunnelRuntimeEngineTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Runtime Tenant")
        self.user = User.objects.create_user(email='runtime@example.com', password='password', tenant=self.tenant)
        self.client.force_authenticate(user=self.user)

        # Crear la estructura de un embudo de prueba
        self.funnel = Funnel.objects.create(tenant=self.tenant, name="Runtime Test Funnel")
        self.version = FunnelVersion.objects.create(
            funnel=self.funnel,
            version_number=1,
            schema_json={
                "pages": [
                    {"id": "page-1", "type": "offer"},
                    {"id": "page-2", "type": "thankyou"}
                ]
            }
        )
        self.publication = FunnelPublication.objects.create(funnel=self.funnel, version=self.version)
        self.events_url = reverse('runtime-event')

    def test_process_form_submit_event_creates_lead(self):
        self.assertEqual(Lead.objects.count(), 0)

        event_data = {
            "publication_slug": str(self.publication.public_url_slug),
            "event_type": "FORM_SUBMIT",
            "payload": {
                "page_id": "page-1",
                "form_data": {"email": "lead@example.com"}
            }
        }

        response = self.client.post(self.events_url, event_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Lead.objects.count(), 1)

        lead = Lead.objects.first()
        self.assertEqual(lead.form_data['email'], 'lead@example.com')
        self.assertEqual(lead.funnel, self.funnel)
        self.assertEqual(lead.initial_version, self.version)

        # Verificar estado y evento
        self.assertEqual(LeadState.objects.count(), 1)
        self.assertEqual(LeadEvent.objects.count(), 1)
        self.assertEqual(lead.state.current_page_id, "page-1")

    def test_unsupported_event_type_fails(self):
        event_data = {
            "publication_slug": str(self.publication.public_url_slug),
            "event_type": "UNSUPPORTED_EVENT",
            "payload": {}
        }
        response = self.client.post(self.events_url, event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lead.objects.count(), 0)

    def test_invalid_publication_slug_fails(self):
        event_data = {
            "publication_slug": "invalid-slug",
            "event_type": "FORM_SUBMIT",
            "payload": {}
        }
        response = self.client.post(self.events_url, event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lead.objects.count(), 0)

    def test_get_lead_details(self):
        # Primero, crear un lead para poder consultarlo
        lead = Lead.objects.create(
            tenant=self.tenant,
            funnel=self.funnel,
            initial_version=self.version,
            form_data={"email": "details@example.com"}
        )
        LeadState.objects.create(lead=lead, current_page_id="page-1", version=self.version)

        url = reverse('runtime-lead-detail', kwargs={'lead_id': lead.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(lead.id))
        self.assertEqual(response.data['form_data']['email'], 'details@example.com')
        self.assertEqual(response.data['state']['current_page_id'], 'page-1')
