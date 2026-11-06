import json
import hashlib
from datetime import datetime
from django.core.files.base import ContentFile
from ..models import LegacyMilestone

class BundleService:
    @staticmethod
    def generate_evidence_bundle(title: str, description: str, data: dict) -> LegacyMilestone:
        """
        Genera un paquete de evidencia inmutable para el legado histórico.
        """
        timestamp = datetime.now().isoformat()
        bundle_content = {
            "title": title,
            "description": description,
            "data": data,
            "timestamp": timestamp,
            "version": "1.0-LEGACY"
        }

        bundle_json = json.dumps(bundle_content, indent=4)
        integrity_hash = hashlib.sha256(bundle_json.encode()).hexdigest()

        milestone = LegacyMilestone.objects.create(
            title=title,
            description=description,
            integrity_hash=integrity_hash
        )

        # En una implementación real, esto se guardaría en un almacenamiento persistente/WORM
        milestone.evidence_bundle_path = f"legacy/bundles/bundle_{milestone.id}_{integrity_hash[:8]}.json"
        milestone.save()

        return milestone
