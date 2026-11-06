from .models_intelligent import MissionHistory
import logging

logger = logging.getLogger(__name__)

class MissionScoring:
    """
    Hallazgo 20: Sistema de Scoring de Misiones para Coroneles.
    """

    @staticmethod
    def calculate_score(impact, success_rate, quality, efficiency):
        score = (impact * 0.35) + (success_rate * 0.30) + (quality * 0.20) + (efficiency * 0.15)
        return round(score, 2)

    @staticmethod
    def save_mission(mission_data):
        score = MissionScoring.calculate_score(
            mission_data['impact'],
            mission_data['success_rate'],
            mission_data['quality'],
            mission_data['efficiency']
        )

        return MissionHistory.objects.create(
            mission_id=mission_data['id'],
            mission_type=mission_data['type'],
            strategy=mission_data['strategy'],
            tenientes=mission_data['tenientes'],
            score=score,
            impact=mission_data['impact'],
            cost=mission_data['cost'],
            time=mission_data['time'],
            result=mission_data['result']
        )

    @staticmethod
    def recommend_strategy(mission_type):
        similar_missions = MissionHistory.objects.filter(mission_type=mission_type).order_by('-score')
        if similar_missions.exists():
            return similar_missions.first().strategy
        return "DEFAULT_STRATEGY"
