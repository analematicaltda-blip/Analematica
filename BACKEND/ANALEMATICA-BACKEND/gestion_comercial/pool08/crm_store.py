"""Owned CRM persistence; existing Cliente records are reused, never copied on read."""
from contextlib import contextmanager
from datetime import datetime,timezone
from django.db import transaction,IntegrityError,OperationalError,connection
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.core_erp.tenancy.models import Tenant
from .crm_models import CRMContact,CRMEvent
from .crm import CRMError,digest

from .contract import SYSTEM

class Store:
    system=SYSTEM
    def __init__(self,company,provider,actor):
        self.scope,self.provider,self.actor=str(company.pk),str(provider.pk),str(actor.pk)
        self.company_name=provider.name
        with connection.cursor() as cursor:
            tables=set(connection.introspection.table_names(cursor))
            for model in (CRMContact,CRMEvent):
                if model._meta.db_table not in tables:raise CRMError('CRM_SCHEMA_INSTALL_REQUIRED',503)
                columns={column.name for column in connection.introspection.get_table_description(cursor,model._meta.db_table)}
                if not {field.column for field in model._meta.local_fields}<=columns:raise CRMError('CRM_SCHEMA_INSTALL_REQUIRED',503)
    @contextmanager
    def transaction(self):
        try:
            with transaction.atomic():yield
        except (IntegrityError,OperationalError):raise CRMError('CRM_WRITE_CONFLICT',409) from None
    def lock(self):
        # UPDATE acquires a write lock on SQLite too; no reliance on ignored FOR UPDATE.
        from django.db.models import F
        if Tenant.objects.filter(pk=self.scope).update(name=F('name'))!=1:raise CRMError('COMPANY_NOT_AVAILABLE',403)
    def customers(self):return Cliente.objects.filter(perfil_id=self.provider)
    def snapshot(self,row):return dict(name=row.nombre,email=row.email,phone=row.telefono or '')
    def from_customer(self,row):
        return dict(id='customer:'+str(row.pk),name=row.nombre,email=row.email.strip().casefold(),phone=row.telefono or '',origin='EXISTING_CUSTOMER',responsible_ref=self.actor,notes='',stage='ganado',revision=0,status='CUSTOMER',consents={},tasks=[],duplicate_review=None,customer_ref=str(row.pk))
    def get(self,cid):
        meta=CRMContact.objects.filter(pk=cid,scope=self.scope,provider_ref=self.provider).first()
        if meta:
            if meta.customer_ref:
                row=self.customers().filter(pk=meta.customer_ref).first()
                if row is None or digest(self.snapshot(row))!=meta.base_fingerprint:raise CRMError('LEGACY_CUSTOMER_CHANGED_REVIEW_REQUIRED',409)
            return meta.document
        if cid.startswith('customer:') and cid[9:].isdigit():
            row=self.customers().filter(pk=int(cid[9:])).first()
            if row:
                # A converted prospect keeps its CRM ID; aliases never create a second wrapper.
                existing=CRMContact.objects.filter(scope=self.scope,customer_ref=row.pk).first()
                return self.get(existing.pk) if existing else self.from_customer(row)
        return None
    def iter_contacts(self,query=''):
        from django.db.models import Q,CharField,Value
        from django.db.models.functions import Cast,Concat
        from heapq import merge
        metas=CRMContact.objects.filter(scope=self.scope,provider_ref=self.provider)
        known=metas.exclude(customer_ref=None).values_list('customer_ref',flat=True)
        legacy=self.customers().exclude(pk__in=known)
        if query:
            metas=metas.filter(Q(document__name__icontains=query)|Q(document__email__icontains=query)|Q(document__phone__icontains=query))
            legacy=legacy.filter(Q(nombre__icontains=query)|Q(email__icontains=query)|Q(telefono__icontains=query))
        existing=(self.get(row.pk) for row in metas.order_by('pk').iterator(chunk_size=100))
        legacy=legacy.annotate(crm_sort=Concat(Value('customer:'),Cast('pk',output_field=CharField())))
        customers=(self.from_customer(row) for row in legacy.order_by('crm_sort').iterator(chunk_size=100))
        yield from merge(existing,customers,key=lambda value:value['id'])
    def list(self,query,offset,limit):
        from itertools import islice
        rows=list(islice(self.iter_contacts(query),offset,offset+limit+1))
        return rows[:limit],len(rows)>limit
    def duplicates(self,email,phone,excluding):
        result=[]
        for value in self.iter_contacts():
            normalized_phone=''.join(c for c in value['phone'] if c not in ' ()-')
            if value['id']!=excluding and ((email and email==value['email']) or (phone and phone==normalized_phone)):
                result.append(value['id'])
                if len(result)>1000:raise CRMError('DUPLICATE_REVIEW_LIMIT',409)
        return sorted(result)
    def save(self,item,revision):
        meta=CRMContact.objects.filter(pk=item['id'],scope=self.scope,provider_ref=self.provider).first()
        if meta and meta.revision!=revision:raise CRMError('REVISION_CONFLICT',409)
        row=None
        if item['customer_ref']:
            row=self.customers().filter(pk=int(item['customer_ref'])).first()
            if row is None:raise CRMError('CUSTOMER_NOT_FOUND',404)
        elif item['status']=='CUSTOMER':
            # Cliente requires a unique email. Empty/fabricated email is never manufactured.
            if not item['email']:raise CRMError('CUSTOMER_EMAIL_REQUIRED')
            if self.customers().filter(email__iexact=item['email']).exists():raise CRMError('CUSTOMER_EMAIL_EXISTS',409)
            import uuid
            row=Cliente(perfil=ProviderProfile.objects.get(pk=self.provider),id_publico=uuid.uuid4())
        if row:
            row.nombre,row.email,row.telefono=item['name'],item['email'],item['phone'];row.save()
            item['customer_ref']=str(row.pk)
        fingerprint=digest(self.snapshot(row)) if row else digest({})
        if meta is None:meta=CRMContact(id=item['id'],scope=self.scope,provider_ref=self.provider)
        meta.revision=item['revision'];meta.customer_ref=int(item['customer_ref']) if item['customer_ref'] else None
        meta.document=item;meta.base_fingerprint=fingerprint;meta.save()
    def event(self,rid):
        row=CRMEvent.objects.filter(id=rid).first();return row.document if row else None
    def append(self,rid,actor,operation,contact,fingerprint,receipt,data):
        CRMEvent.objects.create(id=rid,scope=self.scope,contact=contact,document=dict(scope=self.scope,actor=actor,operation=operation,contact_id=contact,fingerprint=fingerprint,receipt=receipt,data=data,created_at=datetime.now(timezone.utc).isoformat()))
    def history(self,contact,offset,limit):
        return list(CRMEvent.objects.filter(scope=self.scope,contact=contact).order_by('sequence').values_list('document',flat=True)[offset:offset+limit])
