import logging
import random
from .models import Experiment
from django.utils import timezone

logger = logging.getLogger(__name__)

class ExperimentEngine:
    """
    Manages A/B tests for autonomous optimizations.
    """

    @staticmethod
    def create_pricing_experiment(name, entity_ids):
        # Divide into control and test
        random.shuffle(entity_ids)
        split = len(entity_ids) // 2

        control = entity_ids[:split]
        test = entity_ids[split:]

        return Experiment.objects.create(
            name=name,
            control_group=control,
            test_group=test,
            metrics_to_track=['gross_margin', 'churn_rate']
        )

    @staticmethod
    def get_group_for_entity(entity_id):
        experiments = Experiment.objects.filter(is_active=True)
        for exp in experiments:
            if str(entity_id) in exp.control_group:
                return 'CONTROL', exp.id
            if str(entity_id) in exp.test_group:
                return 'TEST', exp.id
        return 'NORMAL', None
