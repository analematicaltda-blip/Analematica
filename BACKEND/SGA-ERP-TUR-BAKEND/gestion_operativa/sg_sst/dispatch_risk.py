"""Explicit server-provisioned order risk approval; no inferred legal qualification.

This evaluates recorded controls, not physical implementation or ARL authenticity.
No medical diagnoses enter its snapshot or operational response.
"""
import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError,PermissionDenied
from apps.core_erp.accounting.integrity import fingerprint
from .access import require_clinical_permission

def raw_assessment(order):
    catalog=getattr(settings,'OPERATIONAL_RISK_ASSESSMENTS',{})
    if not isinstance(catalog,dict):raise ValidationError('Catálogo de riesgos inválido.')
    company=catalog.get(str(order.provider_id),{})
    if not isinstance(company,dict):raise ValidationError('Catálogo de riesgos de empresa inválido.')
    return company.get(str(order.pk))

def digest(order):
    # Reading a completed operation remains possible after risk expiry/revocation.
    return fingerprint(raw_assessment(order))

def evaluate(order,terms,crew):
    from ..dispatch_authorization import stamp,sha
    raw=raw_assessment(order)
    fields={'approved','version','reviewer_id','valid_from','valid_until','evidence_digest','hazards','required_ppe','worker_risk_classes'}
    if not isinstance(raw,dict) or set(raw)!=fields or raw['approved'] is not True:raise ValidationError('Evaluación de riesgo aprobada específica de la orden requerida.')
    if not isinstance(raw['version'],str) or not re.fullmatch('[A-Za-z0-9_.-]{1,40}',raw['version']):raise ValidationError('Versión de riesgo explícita requerida.')
    sha(raw['evidence_digest'])
    if not stamp(raw['valid_from'])<=order.fecha_inicio<=timezone.now()<order.fecha_fin_estimada<=stamp(raw['valid_until']):raise ValidationError('La evaluación de riesgo no cubre la operación.')
    if not isinstance(raw['reviewer_id'],str) or raw['reviewer_id'] not in terms['reviewer_ids']:raise PermissionDenied('Revisor de riesgo no provisionado.')
    reviewer=get_user_model().objects.filter(pk=raw['reviewer_id'],is_active=True).first()
    if reviewer is None or getattr(reviewer,'is_agent',False):raise PermissionDenied('Revisor de riesgo activo requerido.')
    require_clinical_permission(reviewer,'create')
    hazards=raw['hazards']
    if not isinstance(hazards,list) or not 1<=len(hazards)<=30:raise ValidationError('Peligros y controles explícitos requeridos.')
    codes=set()
    for hazard in hazards:
        if not isinstance(hazard,dict) or set(hazard)!={'code','controlled','evidence_digest'} or not isinstance(hazard['code'],str) or not re.fullmatch('[A-Z0-9_-]{1,40}',hazard['code']) or hazard['code'] in codes or hazard['controlled'] is not True:raise ValidationError('Peligro duplicado o sin control acreditado.')
        sha(hazard['evidence_digest']);codes.add(hazard['code'])
    ppe=raw['required_ppe']
    if not isinstance(ppe,list) or len(ppe)>20 or any(not isinstance(c,str) or not re.fullmatch('[A-Z0-9_-]{1,30}',c) for c in ppe) or len(set(ppe))!=len(ppe):raise ValidationError('EPP de riesgo inválido.')
    classes=raw['worker_risk_classes'];expected={entry['employee_id'] for entry in crew}
    if not isinstance(classes,dict) or set(classes)!=expected or any(type(v) is not int or not 1<=v<=5 for v in classes.values()):raise ValidationError('Clase de riesgo explícita para cada trabajador requerida; no se infiere afiliación ARL.')
    return sorted(set(terms['required_ppe'])|set(ppe))
