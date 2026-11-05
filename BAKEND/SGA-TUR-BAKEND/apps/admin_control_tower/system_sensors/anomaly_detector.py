import logging
from decimal import Decimal
from apps.admin_plataforma.gestion_contable.contabilidad.models import AdminJournalEntry

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Sensor sistémico para detectar inconsistencias en el ecosistema.
    """

    @staticmethod
    def check_unbalanced_entries():
        """
        Busca asientos contables que no cumplen el principio de partida doble.
        """
        unbalanced = []
        entries = AdminJournalEntry.objects.filter(is_posted=True)

        for entry in entries:
            transactions = entry.transactions.all()
            debit = sum(t.debit for t in transactions)
            credit = sum(t.credit for t in transactions)

            if debit != credit:
                unbalanced.append({
                    "id": str(entry.id),
                    "description": entry.description,
                    "diff": debit - credit
                })

        return unbalanced

    @staticmethod
    def detect_revenue_anomaly(current_mrr, previous_mrr, threshold=0.15):
        """
        Detecta caídas abruptas de ingresos.
        """
        if previous_mrr == 0:
            return False

        variation = (current_mrr - previous_mrr) / previous_mrr
        if variation < -threshold:
            logger.warning(f"ANOMALÍA DETECTADA: Caída del {variation*100}% en MRR.")
            return True
        return False
