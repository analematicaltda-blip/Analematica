import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import DigitalInfraBackup

logger = logging.getLogger(__name__)

class DigitalInfrastructureService:
    """
    Independent Digital Infrastructure Layer - Phase 19.3.
    Garantiza la continuidad operativa transnacional independiente de infraestructuras locales.
    Multi-cloud, Multi-región, Backups jurisdiccionales.
    """

    @staticmethod
    def calculate_technical_independence_index():
        """
        Métricas Clave: Independencia tecnológica %
        f(ProviderDiversity, RegionDiversity, RedundancyLevel)
        """
        backups = DigitalInfraBackup.objects.filter(sync_status='ACTIVE')
        providers_count = backups.values_list('provider', flat=True).distinct().count()
        regions_count = backups.values_list('jurisdiction', flat=True).distinct().count()

        # Independence Index based on 3 Providers and 3 Regions for 100% score
        independence_score = Decimal(str(min((providers_count * regions_count) / 9.0, 1.0))).quantize(Decimal('0.0001'))

        logger.info(f"Digital Infra: Technical Independence Index: {independence_score}")
        return independence_score

    @staticmethod
    @transaction.atomic
    def perform_systemic_redundancy_check():
        """
        Verifica el estado de sincronización y redundancia de datos a nivel global.
        Si RedundancyLevel < Threshold, dispara alerta crítica.
        """
        backups = DigitalInfraBackup.objects.all()
        failures_detected = 0

        for infra in backups:
            # Simulation: Check if sync is active and last health check is recent (within 1 hour)
            is_recent = infra.last_health_check and (timezone.now() - infra.last_health_check).seconds < 3600

            if infra.sync_status != 'ACTIVE' or not is_recent:
                infra.sync_status = 'ERROR'
                infra.save()
                failures_detected += 1
                logger.error(f"Digital Infra: Redundancy failure in {infra.name} ({infra.provider})")

                # Trigger Anomaly Alert to Control Tower (Phase C)
                from apps.control_tower.application.anomaly_service import AnomalyService
                AnomalyService.detect_anomaly(
                    metric="digital_infra_sync",
                    value=0.0,
                    threshold=1.0,
                    severity="HIGH",
                    description=f"Redundancy Failure detected in {infra.name} [{infra.jurisdiction}]"
                )

        return failures_detected

    @staticmethod
    def register_new_infra_node(name, provider, infra_type, jurisdiction):
        """
        Registra un nuevo nodo de infraestructura para redundancia corporativa.
        """
        infra = DigitalInfraBackup.objects.create(
            name=name,
            provider=provider,
            infra_type=infra_type,
            jurisdiction=jurisdiction,
            last_health_check=timezone.now()
        )

        logger.info(f"Digital Infra: Registered New Node {name} in {jurisdiction}")
        return infra
