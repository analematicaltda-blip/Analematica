import logging
import json
import os
from datetime import timezone, datetime

logger = logging.getLogger(__name__)

class OperationalMemory:
    """MEMORIA OPERATIVA DE AGENTES (Persistencia en archivo JSON)"""
    def __init__(self, storage_path="backend/ai/memory/events.json"):
        self.storage_path = storage_path
        self.events = self._load_events()

    def _load_events(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando memoria: {e}")
        return []

    def _save_to_disk(self):
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.events, f)
        except Exception as e:
            logger.error(f"Error guardando memoria en disco: {e}")

    async def save_event(self, domain, event_type, payload, outcome):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": domain,
            "event_type": event_type,
            "data": payload,
            "outcome": outcome
        }
        self.events.append(event)
        self._save_to_disk()
        logger.info(f"Memoria Operativa: Registrado evento en dominio {domain}")
        return True

    async def retrieve_context(self, query):
        return [e for e in self.events if query in e['domain']][-5:]

memory_store = OperationalMemory()
