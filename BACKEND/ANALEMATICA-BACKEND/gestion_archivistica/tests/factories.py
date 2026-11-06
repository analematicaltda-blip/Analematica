import factory
from factory.django import DjangoModelFactory
import uuid

from apps.companies.models import Company
from apps.api.models import CustomUser
from ..models import Document, DocumentVersion, Process, DocumentType, ProcessType
from apps.domain_business.operativa.models import Perfil

# --- FÁBRICAS DE ENTIDADES BASE ---
class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company
        django_get_or_create = ('name',)

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker('company')
    code = factory.Sequence(lambda n: f"C{n:03d}")
    is_active = True

class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser
        django_get_or_create = ('username',)

    id = factory.LazyFunction(uuid.uuid4)
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')

class PerfilFactory(DjangoModelFactory):
    class Meta:
        model = Perfil

    usuario = factory.SubFactory(UserFactory)
    company = factory.SubFactory(CompanyFactory)
    nombre_comercial = factory.Faker('company')

# --- FÁBRICAS DE CATÁLOGOS DE GESTIÓN ARCHIVÍSTICA ---
class ProcessTypeFactory(DjangoModelFactory):
    class Meta:
        model = ProcessType
    company = factory.SubFactory(CompanyFactory)
    name = factory.Faker('bs')
    code = factory.Sequence(lambda n: f"PT{n}")

class ProcessFactory(DjangoModelFactory):
    class Meta:
        model = Process
    company = factory.SubFactory(CompanyFactory)
    process_type = factory.SubFactory(ProcessTypeFactory, company=factory.SelfAttribute('..company'))
    name = factory.Faker('catch_phrase')
    code = factory.Sequence(lambda n: f"PRC{n}")

class DocumentTypeFactory(DjangoModelFactory):
    class Meta:
        model = DocumentType
    company = factory.SubFactory(CompanyFactory)
    name = factory.Faker('word')
    code = factory.Sequence(lambda n: f"DT{n}")

# --- FÁBRICAS DE DOCUMENTOS Y VERSIONES ---
class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document

    company = factory.SubFactory(CompanyFactory)
    created_by = factory.SubFactory(UserFactory)
    process = factory.SubFactory(ProcessFactory, company=factory.SelfAttribute('..company'))
    document_type = factory.SubFactory(DocumentTypeFactory, company=factory.SelfAttribute('..company'))

class DocumentVersionFactory(DjangoModelFactory):
    class Meta:
        model = DocumentVersion

    document = factory.SubFactory(DocumentFactory)
    uploaded_by = factory.SubFactory(UserFactory)

    version_number = 1
    title = factory.Faker('sentence', nb_words=5)
    validity_year = 2024
    original_filename = factory.LazyAttribute(lambda o: f"{o.title.replace(' ', '_')}.pdf")
    status = DocumentVersion.ProcessingStatus.VERIFIED
    file_hash_sha256 = factory.Faker('sha256')
    external_file_id = factory.LazyFunction(lambda: f"s3-key/{uuid.uuid4()}.enc")
    blockchain_transaction = factory.Faker('sha256', raw_output=False)
