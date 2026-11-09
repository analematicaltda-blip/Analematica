"""Synthetic payroll setup shared by loopback tests; never production data."""
def install(case,create):
    from datetime import timedelta
    from django.utils import timezone
    from apps.prestadores.mi_negocio.gestion_contable.nomina import models as payroll
    from apps.prestadores.mi_negocio.gestion_contable.nomina.reviewed_payroll import ACCOUNT_TYPES
    from apps.core_erp.accounting.models import Account
    from uuid import uuid4
    for name in ('Empleado','Contrato','Planilla','ConceptoNomina','NovedadNomina','DetalleLiquidacion','Ausencia','IncapacidadLaboral'):
        create(getattr(payroll,name))
    day=timezone.localdate();start=day-timedelta(days=14)
    if case.period.period_start>start:
        case.period.period_start=start;case.period.save()
    token=uuid4().hex
    employee=payroll.Empleado.objects.create(perfil_id=case.provider.pk,nombre='Synthetic',apellido='Payroll worker',identificacion=token,fecha_nacimiento=day.replace(year=1990,day=1),direccion='Synthetic',telefono='Synthetic',email=token+'@example.test',estado='ACTIVO',centro_costo='SYNTHETIC_ROUTE')
    contract=payroll.Contrato.objects.create(empleado=employee,fecha_inicio=start,salario='1000.00',cargo='Synthetic',tipo_contrato='TERMINO_INDEFINIDO',activo=True)
    source=payroll.Planilla.objects.create(perfil_id=case.provider.pk,periodo_inicio=start,periodo_fin=day)
    mapping={}
    for i,(key,kind) in enumerate(ACCOUNT_TYPES.items()):
        account=Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='PAYROLL-FIX-'+str(i),name='Synthetic '+key,type=kind);mapping[key]=str(account.pk)
    return {'payroll_id':str(source.pk),'policy':{'code':'DECLARED_BASE','revision':1,'valid_from':start.isoformat(),'valid_until':day.isoformat(),'divisor_days':30,'evidence_digest':'a'*64,'components':[{'code':'DECLARED_DEDUCTION','kind':'EMPLOYEE_DEDUCTION','rate_bps':400},{'code':'DECLARED_EMPLOYER','kind':'EMPLOYER_CONTRIBUTION','rate_bps':1200},{'code':'DECLARED_PROVISION','kind':'PROVISION','rate_bps':800}]},'workers':[{'employee_id':str(employee.pk),'contract_id':str(contract.pk),'worked_days':15}],'account_mapping':mapping,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True}
