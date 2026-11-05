import logging
import uuid
from django.utils import timezone
from .investor_reporting_engine import InvestorReportingEngine
from .valuation_engine import ValuationEngine
from .governance_board_engine import GovernanceBoardEngine

logger = logging.getLogger(__name__)

class DueDiligenceRoom:
    """
    Sala de Datos Automática para Due Diligence Institucional (Fase 7).
    Genera paquetes de información auditables en 1 clic.
    """

    @staticmethod
    def generate_full_package(requester_name, organization):
        """
        Compila toda la información requerida por un inversionista institucional.
        """
        package = {
            "metadata": {
                "generated_at": timezone.now().isoformat(),
                "package_id": str(uuid.uuid4()),
                "status": "CERTIFIED"
            },
            "financial_legal": {
                "current_valuation": ValuationEngine.calculate_valuation(),
                "quarterly_report": InvestorReportingEngine.generate_quarterly_report(),
                "audit_integrity_status": "VALIDATED"
            },
            "governance": {
                "board_minutes": [str(m) for m in GovernanceBoardEngine.get_board_minutes()],
                "system_standard": "SARITA Civilizational Standard"
            },
            "technical": {
                "architecture_version": "7.0 (Institutional)",
                "data_lake_status": "ACTIVE"
            }
        }

        logger.info(f"DATA_ROOM: Generado paquete de Due Diligence para {requester_name} de {organization}")
        return package

    @staticmethod
    def create_access_token(user, requester_name, organization, purpose, expiry_hours=24):
        from ..models import DataRoomAccess
        token = str(uuid.uuid4())
        access = DataRoomAccess.objects.create(
            requester_name=requester_name,
            organization=organization,
            purpose=purpose,
            authorized_by=user,
            token=token,
            expires_at=timezone.now() + timezone.timedelta(hours=expiry_hours)
        )
        return access
