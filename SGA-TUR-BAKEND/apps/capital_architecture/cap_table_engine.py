import logging
from .models import Shareholder, ShareCertificate, EquityClass, SAFE, ConvertibleNote
from decimal import Decimal
from django.db.models import Sum

logger = logging.getLogger(__name__)

class CapTableEngine:
    """
    Manages equity ownership and simulates dilution scenarios.
    """

    @staticmethod
    def get_full_cap_table():
        total_shares = ShareCertificate.objects.aggregate(total=Sum('quantity'))['total'] or 0

        shareholders = Shareholder.objects.all()
        table = []

        for sh in shareholders:
            sh_shares = sh.certificates.aggregate(total=Sum('quantity'))['total'] or 0
            percentage = (Decimal(sh_shares) / Decimal(total_shares)) * 100 if total_shares > 0 else 0

            table.append({
                'name': sh.name,
                'shares': sh_shares,
                'percentage': round(percentage, 4),
                'type': sh.shareholder_type
            })

        return {'total_shares': total_shares, 'data': sorted(table, key=lambda x: x['shares'], reverse=True)}

    @staticmethod
    def simulate_dilution(new_investment, price_per_share):
        """
        Simulates impact of a new funding round.
        """
        current_total = ShareCertificate.objects.aggregate(total=Sum('quantity'))['total'] or 0
        new_shares = int(new_investment / price_per_share)
        post_money_total = current_total + new_shares

        dilution_factor = Decimal(current_total) / Decimal(post_money_total)

        return {
            'new_shares_issued': new_shares,
            'dilution_percentage': round((1 - dilution_factor) * 100, 2),
            'post_money_total_shares': post_money_total
        }
