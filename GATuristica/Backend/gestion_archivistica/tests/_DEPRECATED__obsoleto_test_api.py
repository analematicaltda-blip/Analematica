import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from .factories import PerfilFactory, DocumentFactory, ProcessFactory, DocumentTypeFactory
from ..models import Document, DocumentVersion

# Todas las pruebas en este archivo necesitan acceso a la base de datos.
pytestmark = pytest.mark.django_db

class TestDocumentAPI:

    def setup_method(self):
        """Este método se ejecuta antes de cada prueba en esta clase."""
        self.client = APIClient()
        self.perfil = PerfilFactory()
        self.user = self.perfil.usuario
        self.client.force_authenticate(user=self.user)

    def test_list_documents_returns_only_own_company_docs(self):
        """
        Prueba que el endpoint de lista SOLO devuelva documentos de la compañía del usuario.
        """
        # Crea 3 documentos para la compañía de nuestro usuario
        DocumentFactory.create_batch(3, company=self.perfil.company)

        # Crea 2 documentos para otra compañía
        DocumentFactory.create_batch(2)

        response = self.client.get('/api/v1/mi-negocio/archivistica/documents/')

        assert response.status_code == status.HTTP_200_OK
        # La API devuelve datos paginados, por lo que verificamos el 'count'
        assert response.data['count'] == 3

        # Verifica que todos los documentos devueltos pertenezcan a la compañía correcta
        for doc in response.data['results']:
            retrieved_doc = Document.objects.get(id=doc['id'])
            assert retrieved_doc.company == self.perfil.company

    def test_retrieve_document_from_other_company_fails(self):
        """
        Prueba de seguridad Multi-Tenancy: Un usuario no puede ver un documento
        de otra compañía, incluso si conoce su UUID.
        """
        other_company_doc = DocumentFactory()

        url = f'/api/v1/mi-negocio/archivistica/documents/{other_company_doc.id}/'
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_editor_can_create_document(self, mocker):
        """
        Prueba el flujo feliz de creación de un documento.
        Usa 'mocker' para simular la tarea de Celery y evitar su ejecución real.
        """
        mock_task = mocker.patch('apps.prestadores.mi_negocio.gestion_archivistica.services.logic_services.start_file_processing_flow.delay')

        process = ProcessFactory(company=self.perfil.company)
        doc_type = DocumentTypeFactory(company=self.perfil.company)

        test_file = SimpleUploadedFile("report.docx", b"word file content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        data = {
            'title': 'New Report',
            'validity_year': 2024,
            'process_id': str(process.id),
            'document_type_id': str(doc_type.id),
            'file': test_file,
        }

        response = self.client.post('/api/v1/mi-negocio/archivistica/documents/', data=data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert Document.objects.count() == 1
        assert Document.objects.first().versions.count() == 1

        mock_task.assert_called_once()

        call_args = mock_task.call_args[0]
        version_id_sent_to_task = call_args[0]
        file_content_b64_sent = call_args[1]

        new_version = Document.objects.first().versions.first()
        assert version_id_sent_to_task == new_version.id
        import base64
        assert base64.b64decode(file_content_b64) == b"word file content"
