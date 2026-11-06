from django.core.management.base import BaseCommand
from apps.sadi_agent.models import SemanticDomain, Intent

class Command(BaseCommand):
    help = 'Pobla la base de datos con las intenciones operativas de la Fase 6.'

    def handle(self, *args, **options):
        # 1. Dominios
        d_contable, _ = SemanticDomain.objects.get_or_create(name='contable', defaults={'description': 'Gestión de libros y asientos'})
        d_comercial, _ = SemanticDomain.objects.get_or_create(name='comercial', defaults={'description': 'Ventas y CRM'})
        d_nomina, _ = SemanticDomain.objects.get_or_create(name='nomina', defaults={'description': 'Pagos laborales'})
        d_financiero, _ = SemanticDomain.objects.get_or_create(name='financiero', defaults={'description': 'Tesorería y flujos'})
        d_marketing, _ = SemanticDomain.objects.get_or_create(name='marketing', defaults={'description': 'Embudo de ventas y prospección'})

        # 2. Intenciones
        Intent.objects.get_or_create(domain=d_contable, name='ERP_CREATE_VOUCHER', defaults={'description': 'Crear un asiento contable o comprobante'})
        Intent.objects.get_or_create(domain=d_contable, name='CHECK_ACCOUNT_BALANCE', defaults={'description': 'Consultar el saldo de una cuenta'})
        Intent.objects.get_or_create(domain=d_comercial, name='CREATE_SALE', defaults={'description': 'Registrar una venta nueva'})
        Intent.objects.get_or_create(domain=d_nomina, name='RUN_PAYROLL', defaults={'description': 'Liquidar la nómina del periodo'})
        Intent.objects.get_or_create(domain=d_financiero, name='ERP_VIEW_CASH_FLOW', defaults={'description': 'Ver el estado de tesorería y bancos'})

        # Marketing Funnel Intents
        Intent.objects.get_or_create(domain=d_marketing, name='QUIERO_VENDER_TURISMO', defaults={'description': 'Prospecto interesado en vender servicios turísticos'})
        Intent.objects.get_or_create(domain=d_marketing, name='SOY_GOBIERNO', defaults={'description': 'Prospecto interesado en gestión gubernamental/territorial'})
        Intent.objects.get_or_create(domain=d_marketing, name='QUIERO_PRECIO', defaults={'description': 'Prospecto pregunta por costos o ROI'})
        Intent.objects.get_or_create(domain=d_marketing, name='EXPLORAR_PLATAFORMA', defaults={'description': 'Prospecto desea conocer funcionalidades generales'})

        self.stdout.write(self.style.SUCCESS('Catálogo de intenciones SADI Fase 6 inicializado.'))
