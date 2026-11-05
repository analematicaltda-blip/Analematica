from .feature_extractor import FeatureExtractor

class ChurnModel:
    """
    Motor Predictivo de Churn (Fase 4).
    Calcula la probabilidad de que un tenant cancele su suscripción.
    """

    @staticmethod
    def predict_churn(tenant_id):
        features = FeatureExtractor.get_tenant_features(tenant_id)

        probability = 0.0

        # Heurística 1: Inactividad prolongada
        if features['inactivity_period'] > 30:
            probability += 0.6
        elif features['inactivity_period'] > 15:
            probability += 0.3

        # Heurística 2: Problemas de pago
        if features['payment_friction'] > 0:
            probability += 0.2 * features['payment_friction']

        # Heurística 3: Salud del sistema
        if features['health_score'] < 0.5:
            probability += 0.4

        # Caping
        probability = min(0.99, probability)

        return probability
