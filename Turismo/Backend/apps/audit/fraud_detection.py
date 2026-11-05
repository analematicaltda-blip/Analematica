import logging
from .models import FraudEvent
from django.utils import timezone

logger = logging.getLogger(__name__)

class FraudDetectionService:
    @staticmethod
    def analyze_transaction(user, amount, ip_address, metadata=None):
        score = 0
        reasons = []

        # 1. Unusual Amount check
        if amount > 5000000: # 5M
            score += 40
            reasons.append("High amount threshold")

        # 2. Velocity check (Simulated)
        # In real life: query recent FraudEvents for this user

        # 3. Geo change (Simulated)
        if metadata and metadata.get('country_change'):
            score += 50
            reasons.append("Sudden geo location change")

        # Record event
        FraudEvent.objects.create(
            user=user,
            event_type="TRANSACTION_ANALYSIS",
            score=score,
            ip_address=ip_address,
            metadata={"reasons": reasons, "amount": float(amount)}
        )

        if score >= 61:
            return "BLOCK", score
        if score >= 31:
            return "WARNING", score
        return "NORMAL", score
