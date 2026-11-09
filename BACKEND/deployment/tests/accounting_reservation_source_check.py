"""Real ORM reservation transition; no simulated booking, payment or fiscal document."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
from django.db import transaction
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('company_identity_check.py')),run_name='reservation_source_fixture')
from django.contrib.contenttypes.models import ContentType
from apps.domain_business.operativa.models import Reservation
from apps.core_erp.outbox_models import OutboxEvent
from apps.domain_business.operativa.sargentos import DomainSargentoReservas, RESERVATION_EVENT
from apps.application_services.reservation_service import ReservationApplicationService
from apps.application_services.domain_contracts.base import CreateReservationCommand,ConfirmReservationCommand
from apps.turismo.models import VerifiedCompanyLink
from rest_framework.exceptions import APIException
fixture['fixture']['create'](Reservation)
fixture['fixture']['create'](OutboxEvent)
class ReservationSourceTests(unittest.TestCase):
 def setUp(self):
  fixture['CompanyChecks'].setUp(self);fixture['CompanyChecks'].review(self,apply=True)
  self.actor=fixture['F'].owner
  content=ContentType.objects.get_for_model(Reservation)
  self.reservation=Reservation.plain_objects.create(tenant=self.tenant,customer_id=uuid.uuid4(),content_type=content,object_id=uuid.uuid4(),start_date=timezone.now(),end_date=timezone.now()+timedelta(days=1),total_price='100.00')
 def confirm(self,**overrides):
  args={'actor':self.actor,'provider_id':self.provider.pk};args.update(overrides)
  return DomainSargentoReservas.confirm_reservation(self.reservation.pk,**args)
 def test_owner_confirmation_and_replay(self):
  a=self.confirm();b=self.confirm();self.assertFalse(a['replayed']);self.assertTrue(b['replayed']);self.assertFalse(a['ledger_written']);self.assertFalse(a['fiscal_accepted'])
  self.assertTrue(a['confirmation_event_recorded']);self.assertEqual(a['confirmation_event_id'],b['confirmation_event_id'])
  self.assertEqual(OutboxEvent.objects.filter(aggregate_root=str(self.reservation.pk),event_type=RESERVATION_EVENT).count(),1)
  self.reservation.refresh_from_db();self.assertEqual(self.reservation.status,'CONFIRMED');self.assertEqual(str(self.reservation.total_price),'100.00')
 def test_missing_context_denied(self):
  with self.assertRaises(APIException):DomainSargentoReservas.confirm_reservation(self.reservation.pk)
 def test_other_owner_denied(self):
  with self.assertRaises(APIException):self.confirm(actor=fixture['F'].other)
 def test_revoked_link_denied(self):
  VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.confirm()
 def test_other_company_reservation_denied(self):
  other=fixture['Tenant'].objects.create(name='Other',tax_id=uuid.uuid4().hex,state='ACTIVE')
  Reservation.plain_objects.filter(pk=self.reservation.pk).update(tenant=other)
  with self.assertRaises(APIException):self.confirm()
 def test_cancelled_not_resurrected(self):
  Reservation.plain_objects.filter(pk=self.reservation.pk).update(status='CANCELLED')
  with self.assertRaises(APIException):self.confirm()
  self.reservation.refresh_from_db();self.assertEqual(self.reservation.status,'CANCELLED')
 def test_outer_rollback_preserves_pending(self):
  with self.assertRaises(RuntimeError):
   with transaction.atomic():self.confirm();raise RuntimeError('Producer failed')
  self.reservation.refresh_from_db();self.assertEqual(self.reservation.status,'PENDING')
  self.assertFalse(OutboxEvent.objects.filter(aggregate_root=str(self.reservation.pk)).exists())
 def test_event_failure_rolls_back_confirmation(self):
  with patch.object(OutboxEvent.objects,'create',side_effect=RuntimeError('Event persistence failed')):
   with self.assertRaises(RuntimeError):self.confirm()
  self.reservation.refresh_from_db();self.assertEqual(self.reservation.status,'PENDING')
  self.assertFalse(OutboxEvent.objects.filter(aggregate_root=str(self.reservation.pk)).exists())
 def test_legacy_confirmed_does_not_fabricate_historical_event(self):
  Reservation.plain_objects.filter(pk=self.reservation.pk).update(status='CONFIRMED')
  result=self.confirm();self.assertTrue(result['replayed']);self.assertFalse(result['confirmation_event_recorded'])
  self.assertIsNone(result['confirmation_event_id'])
 def test_conflicting_event_rejected_without_overwrite(self):
  result=self.confirm();OutboxEvent.objects.filter(pk=result['confirmation_event_id']).update(domain='unexpected')
  with self.assertRaises(APIException):self.confirm()
  self.assertEqual(OutboxEvent.objects.get(pk=result['confirmation_event_id']).domain,'unexpected')
 def test_application_service_no_simulated_ids_or_metadata_authority(self):
  service=ReservationApplicationService()
  result=service.execute(CreateReservationCommand());self.assertFalse(result['success']);self.assertNotIn('reservation_id',result)
  result=service.execute(ConfirmReservationCommand(reserva_id=str(self.reservation.pk),metadata={'actor':self.actor,'provider_id':str(self.provider.pk)}));self.assertFalse(result['success'])
  trusted=ReservationApplicationService(actor=self.actor,provider_id=self.provider.pk)
  self.assertTrue(trusted.execute(ConfirmReservationCommand(reserva_id=str(self.reservation.pk)))['success'])
if __name__=='__main__':unittest.main()
