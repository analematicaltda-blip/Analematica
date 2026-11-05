# backend/apps/sarita_agents/agents/marketing/coronel_marketing.py
import logging
from apps.sarita_agents.agents.coronel_template import CoronelTemplate
from .capitan_embudo import CapitanEmbudo

logger = logging.getLogger(__name__)

class CoronelMarketing(CoronelTemplate):
    """
    Coronel de Marketing Conversacional: Supervisa la adquisición y coordina capitanes.
    """
    def _get_capitanes(self) -> dict:
        return {
            "embudo": CapitanEmbudo(coronel=self)
        }

    def _select_capitan(self, mission: dict):
        # Todo lo relacionado con marketing por ahora va al Capitán de Embudo
        return self.capitanes["embudo"]
