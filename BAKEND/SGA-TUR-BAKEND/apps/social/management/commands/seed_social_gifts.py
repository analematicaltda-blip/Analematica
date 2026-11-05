from django.core.management.base import BaseCommand
from apps.social.models import SocialGiftCatalog
from decimal import Decimal

class Command(BaseCommand):
    help = "Seeds the social gift catalog with the 20-tier tiers from 5,000 to 100,000 COP"

    def handle(self, *args, **options):
        # Multiples of 5,000 from 5k to 100k
        tiers = [5000 * i for i in range(1, 21)]

        icons = {
            5000: "🌸", 10000: "🍫", 15000: "☕", 20000: "🍕", 25000: "🍔",
            30000: "🍷", 35000: "🍰", 40000: "🎁", 45000: "🧸", 50000: "🌹",
            55000: "👗", 60000: "👔", 65000: "👠", 70000: "👜", 75000: "💍",
            80000: "📱", 85000: "🎧", 90000: "⌚", 95000: "✈️", 100000: "🌟"
        }

        created_count = 0
        for amount in tiers:
            code = f"gift_{amount}"
            name = f"Regalo de ${amount:,.0f}"
            icon = icons.get(amount, "🎁")

            obj, created = SocialGiftCatalog.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": f"Envía un detalle especial de ${amount:,.0f} COP",
                    "price": Decimal(str(amount)),
                    "icon_url": icon # Using emoji as placeholder icon
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {created_count} new gifts to the catalog (Total 20 tiers)."))
