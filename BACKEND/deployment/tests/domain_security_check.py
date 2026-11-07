"""Scoped HTTP/ORM tests on a temporary SQLite schema; never a migration certificate."""
import os,runpy,unittest
from pathlib import Path
os.environ['CHECK_SERVICE']='turismo'
runpy.run_path(str(Path(__file__).with_name('tourism_runtime_check.py')),run_name='fixture_setup')
from django.db import connection
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIRequestFactory,APIClient,force_authenticate
from api.models import CustomUser,Entity,Profile,GovernmentProfile,AtractivoTuristico,RutaTuristica,HechoHistorico,ImagenAtractivo
from apps.turismo.models.divipola import Department,Municipality
from api.views import AtractivoTuristicoViewSet,RutaTuristicaViewSet,HechoHistoricoViewSet
from apps.turismo.models.provider_models import TourismProvider,TourismService
from apps.tourism_marketplace.models import TourismReview
from apps.tourism_marketplace.api.views import TourismReviewViewSet

# Actual declared tables, created only in the in-memory fixture, not via fake migrations.
created=set();visiting=set()
def create(model):
 model=model._meta.concrete_model
 if model._meta.db_table in created or model in visiting:return
 visiting.add(model)
 for field in model._meta.local_fields:
  if field.is_relation and field.remote_field and field.remote_field.model is not model:create(field.remote_field.model)
 for field in model._meta.local_many_to_many:create(field.remote_field.model)
 with connection.schema_editor() as editor:editor.create_model(model)
 created.add(model._meta.db_table);visiting.remove(model)

class DomainChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  for model in [CustomUser,Entity,Profile,GovernmentProfile,AtractivoTuristico,RutaTuristica,HechoHistorico,ImagenAtractivo,TourismProvider,TourismService,TourismReview]:create(model)
  cls.factory=APIRequestFactory()
  cls.dept=Department.objects.create(code='50',name='Synthetic department A');cls.otherdept=Department.objects.create(code='11',name='Synthetic department B')
  cls.town=Municipality.objects.create(code='50001',name='Synthetic town A',dept=cls.dept);cls.other=Municipality.objects.create(code='50002',name='Synthetic town B',dept=cls.dept)
  cls.entity=Entity.objects.create(name='Synthetic institution A',slug='test-a',type='municipal');cls.foreign=Entity.objects.create(name='Synthetic institution B',slug='test-b',type='municipal')
  def official(name,entity,town):
   # Seed fixture users without provisioning wallet/company side effects; signup is not under test.
   user=CustomUser(username=name,role='ADMIN_MUNICIPAL');CustomUser.objects.bulk_create([user])
   Profile.objects.create(user=user,entity=entity,department=cls.dept,municipality=town)
   GovernmentProfile.objects.create(user=user,entity=entity,nivel='MUNICIPAL',cargo='Synthetic test officer')
   content,_=ContentType.objects.get_or_create(app_label='api',model='atractivoturistico')
   for action in ['add','change','delete','view']:
    perm,_=Permission.objects.get_or_create(content_type=content,codename=action+'_atractivoturistico',defaults={'name':'Synthetic '+action});user.user_permissions.add(perm)
   return user
  cls.user=official('fixture-a',cls.entity,cls.town);cls.userb=official('fixture-b',cls.foreign,cls.other)
  cls.customer=CustomUser(username='customer-a',role='TURISTA');cls.customerb=CustomUser(username='customer-b',role='TURISTA');CustomUser.objects.bulk_create([cls.customer,cls.customerb])
  cls.draft=AtractivoTuristico.objects.create(nombre='Synthetic draft A',slug='draft-a',descripcion='test',como_llegar='test',categoria_color='BLANCO',entity=cls.entity,department=cls.dept,municipality=cls.town,autor=cls.user)
  cls.privateb=AtractivoTuristico.objects.create(nombre='Synthetic draft B',slug='draft-b',descripcion='test',como_llegar='test',categoria_color='BLANCO',entity=cls.foreign,department=cls.dept,municipality=cls.other,autor=cls.userb)
  cls.public=AtractivoTuristico.objects.create(nombre='Synthetic published',slug='published',descripcion='test',como_llegar='test',categoria_color='BLANCO',entity=cls.foreign,department=cls.dept,municipality=cls.other,autor=cls.userb,es_publicado=True)
  provider=TourismProvider.objects.create(name='Synthetic provider',provider_type='GUIDE',owner=cls.customerb)
  cls.service=TourismService.objects.create(provider=provider,service_type='TOUR',name='Synthetic service',description='test',price='10.00')
  cls.review=TourismReview.objects.create(customer=cls.customerb,service=cls.service,rating=4,comment='Synthetic original')
 def call(self,cls,action,method='get',pk=None,user=None,data=None):
  request=getattr(self.factory,method)('/isolated-domain/',data=data or {},format='json')
  if user:force_authenticate(request,user=user)
  return cls.as_view({method:action})(request,**({'pk':pk} if pk is not None else {}))
 def test_01_public_reads_only_published_records(self):
  response=self.call(AtractivoTuristicoViewSet,'list');self.assertEqual(response.status_code,200)
  rows=response.data.get('results',response.data) if isinstance(response.data,dict) else response.data;ids={r['id'] for r in rows};self.assertIn(self.public.pk,ids);self.assertNotIn(self.draft.pk,ids)
  self.assertEqual(self.call(AtractivoTuristicoViewSet,'retrieve',pk=self.draft.pk).status_code,404)
 def test_02_anonymous_and_customer_writes_denied_without_mutation(self):
  original=self.draft.nombre
  for user in [None,self.customer]:
   for method,action in [('patch','partial_update'),('delete','destroy')]:self.assertIn(self.call(AtractivoTuristicoViewSet,action,method,pk=self.draft.pk,user=user,data={'nombre':'MUTATED'}).status_code,[401,403])
  self.draft.refresh_from_db();self.assertEqual(self.draft.nombre,original)
 def test_03_officer_cannot_edit_another_municipality_even_if_published(self):
  for obj in [self.privateb,self.public]:self.assertEqual(self.call(AtractivoTuristicoViewSet,'partial_update','patch',obj.pk,self.user,{'nombre':'MUTATED'}).status_code,404)
 def test_04_scoped_officer_updates_own_draft(self):
  response=self.call(AtractivoTuristicoViewSet,'partial_update','patch',self.draft.pk,self.user,{'descripcion':'Synthetic updated'});self.assertEqual(response.status_code,200,response.data);self.draft.refresh_from_db();self.assertEqual(self.draft.descripcion,'Synthetic updated')
 def test_05_creation_binds_actor_and_jurisdiction(self):
  data={'nombre':'Synthetic new','slug':'new','descripcion':'test','como_llegar':'test','categoria_color':'BLANCO'}
  response=self.call(AtractivoTuristicoViewSet,'create','post',user=self.user,data=data);self.assertEqual(response.status_code,201,response.data)
  obj=AtractivoTuristico.objects.get(slug='new');self.assertEqual(obj.entity_id,self.entity.pk);self.assertEqual(obj.municipality_id,self.town.pk);self.assertEqual(obj.autor_id,self.user.pk)
 def test_06_territory_and_publication_tampering_denied(self):
  for data in [{'municipality':self.other.pk},{'entity':str(self.foreign.pk)},{'es_publicado':True}]:self.assertEqual(self.call(AtractivoTuristicoViewSet,'partial_update','patch',self.draft.pk,self.user,data).status_code,403)
  self.draft.refresh_from_db();self.assertFalse(self.draft.es_publicado)
 def test_07_coordinates_and_permissions_validated(self):
  self.assertEqual(self.call(AtractivoTuristicoViewSet,'partial_update','patch',self.draft.pk,self.user,{'latitud':91}).status_code,400)
  self.user.user_permissions.clear();self.user.__dict__.pop('_perm_cache',None);self.user.__dict__.pop('_user_perm_cache',None)
  try:self.assertEqual(self.call(AtractivoTuristicoViewSet,'partial_update','patch',self.draft.pk,self.user,{'descripcion':'MUTATED'}).status_code,403)
  finally:
   self.user.user_permissions.set(Permission.objects.filter(content_type__app_label='api',codename__in=['add_atractivoturistico','change_atractivoturistico','view_atractivoturistico','delete_atractivoturistico']));self.user.__dict__.pop('_perm_cache',None);self.user.__dict__.pop('_user_perm_cache',None)
 def test_08_unscoped_route_and_history_writes_are_unavailable(self):
  for cls in [RutaTuristicaViewSet,HechoHistoricoViewSet]:
   request=self.factory.post('/isolated/',{},format='json');self.assertEqual(cls.as_view({'get':'list'})(request).status_code,405)
  draft=HechoHistorico.objects.create(ano=2000,titulo='Synthetic draft',descripcion='test')
  published=HechoHistorico.objects.create(ano=2001,titulo='Synthetic public',descripcion='test',es_publicado=True)
  response=self.call(HechoHistoricoViewSet,'list');rows=response.data.get('results',response.data) if isinstance(response.data,dict) else response.data
  self.assertEqual({r['id'] for r in rows},{published.pk})
 def test_09_customer_cannot_change_or_delete_other_review(self):
  for method,action in [('patch','partial_update'),('delete','destroy')]:self.assertEqual(self.call(TourismReviewViewSet,action,method,self.review.pk,self.customer,{'rating':1}).status_code,404)
  self.review.refresh_from_db();self.assertEqual(self.review.rating,4)
 def test_10_review_author_and_verification_are_server_owned(self):
  response=self.call(TourismReviewViewSet,'create','post',user=self.customer,data={'service':str(self.service.pk),'rating':5,'comment':'Synthetic client review','customer':self.customerb.pk,'is_verified_purchase':True});self.assertEqual(response.status_code,201,response.data)
  review=TourismReview.objects.get(customer=self.customer,service=self.service);self.assertFalse(review.is_verified_purchase)
 def test_11_author_may_edit_own_review_and_rating_range_is_enforced(self):
  self.assertEqual(self.call(TourismReviewViewSet,'partial_update','patch',self.review.pk,self.customerb,{'comment':'Synthetic changed'}).status_code,200)
  self.assertEqual(self.call(TourismReviewViewSet,'partial_update','patch',self.review.pk,self.customerb,{'rating':6}).status_code,400)

 def test_12_duplicate_and_service_reassignment_are_rejected(self):
  response=self.call(TourismReviewViewSet,'create','post',user=self.customerb,data={'service':str(self.service.pk),'rating':3,'comment':'Duplicate fixture'});self.assertEqual(response.status_code,400,response.data)
  other=TourismService.objects.create(provider=self.service.provider,service_type='TOUR',name='Synthetic other service',description='test',price='5.00')
  self.assertEqual(self.call(TourismReviewViewSet,'partial_update','patch',self.review.pk,self.customerb,{'service':str(other.pk)}).status_code,400)
 def test_13_inactive_office_and_mismatched_role_cannot_write(self):
  government=self.user.government_profile;government.is_active=False;government.save(update_fields=['is_active'])
  self.assertEqual(self.call(AtractivoTuristicoViewSet,'partial_update','patch',self.draft.pk,self.user,{'descripcion':'MUTATED'}).status_code,403)
  government.is_active=True;government.save(update_fields=['is_active']);role=self.user.role;self.user.role='ADMIN_NACIONAL'
  try:self.assertEqual(self.call(AtractivoTuristicoViewSet,'partial_update','patch',self.draft.pk,self.user,{'descripcion':'MUTATED'}).status_code,403)
  finally:self.user.role=role
 def test_14_published_changes_require_separate_permission(self):
  self.draft.es_publicado=True;self.draft.save(update_fields=['es_publicado'])
  try:
   self.assertEqual(self.call(AtractivoTuristicoViewSet,'partial_update','patch',self.draft.pk,self.user,{'descripcion':'MUTATED'}).status_code,403)
   self.assertEqual(self.call(AtractivoTuristicoViewSet,'destroy','delete',self.draft.pk,self.user).status_code,403)
  finally:self.draft.es_publicado=False;self.draft.save(update_fields=['es_publicado'])
 def test_15_v1_detail_alias_uses_actual_integer_primary_key(self):
  from django.urls import resolve
  match=resolve('/api/v1/atractivos/'+str(self.public.pk)+'/');self.assertEqual(match.kwargs['pk'],self.public.pk)

 def test_16_publishing_works_only_with_explicit_functional_grant(self):
  content=ContentType.objects.get(app_label='api',model='atractivoturistico')
  permission,_=Permission.objects.get_or_create(content_type=content,codename='publish_atractivoturistico',defaults={'name':'Synthetic publication grant'})
  self.user.user_permissions.add(permission)
  for cache in ['_perm_cache','_user_perm_cache']:self.user.__dict__.pop(cache,None)
  try:
   response=self.call(AtractivoTuristicoViewSet,'partial_update','patch',self.draft.pk,self.user,{'es_publicado':True});self.assertEqual(response.status_code,200,response.data)
   self.draft.refresh_from_db();self.assertTrue(self.draft.es_publicado)
  finally:
   self.draft.es_publicado=False;self.draft.save(update_fields=['es_publicado']);self.user.user_permissions.remove(permission)
   for cache in ['_perm_cache','_user_perm_cache']:self.user.__dict__.pop(cache,None)
 def test_17_public_detail_omits_officer_login_and_department_scope_checks_locations(self):
  response=self.call(AtractivoTuristicoViewSet,'retrieve',pk=self.public.pk);self.assertEqual(response.status_code,200);self.assertNotIn('autor_username',response.data)
  user=CustomUser(username='fixture-department',role='ADMIN_DEPARTAMENTAL');CustomUser.objects.bulk_create([user])
  entity=Entity.objects.create(name='Synthetic department institution',slug='test-dept',type='departamental')
  Profile.objects.create(user=user,entity=entity,department=self.dept);GovernmentProfile.objects.create(user=user,entity=entity,nivel='DEPARTAMENTAL',cargo='Synthetic department officer')
  user.user_permissions.set(Permission.objects.filter(content_type__app_label='api',codename='add_atractivoturistico'))
  data={'nombre':'Synthetic department attraction','slug':'dept-new','descripcion':'test','como_llegar':'test','categoria_color':'BLANCO','municipality':self.other.pk}
  self.assertEqual(self.call(AtractivoTuristicoViewSet,'create','post',user=user,data=data).status_code,201)
  data.update(nombre='Synthetic rejected',slug='dept-bad',department=self.otherdept.pk)
  self.assertEqual(self.call(AtractivoTuristicoViewSet,'create','post',user=user,data=data).status_code,403)

 def test_18_full_url_and_middleware_preserve_public_read_and_protected_write(self):
  client=APIClient(HTTP_HOST='localhost')
  response=client.get('/api/v1/atractivos/');self.assertEqual(response.status_code,200)
  rows=response.json()['data'];ids={row['id'] for row in rows};self.assertIn(self.public.pk,ids);self.assertNotIn(self.draft.pk,ids)
  self.assertIn(client.post('/api/v1/atractivos/',{},format='json').status_code,[401,403])
  client.force_authenticate(self.user)
  response=client.patch('/api/v1/atractivos/'+str(self.draft.pk)+'/',{'descripcion':'Synthetic full middleware update'},format='json');self.assertEqual(response.status_code,200,response.content)
  self.draft.refresh_from_db();self.assertEqual(self.draft.descripcion,'Synthetic full middleware update')

if __name__=='__main__':unittest.main()
