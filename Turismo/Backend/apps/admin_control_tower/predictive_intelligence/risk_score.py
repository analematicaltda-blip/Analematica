from .churn_model import ChurnModel

class RiskScoreManager:
    """
    Clasifica el riesgo de churn y recomienda acciones estratégicas.
    """

    @staticmethod
    def evaluate_tenant(tenant_id):
        prob = ChurnModel.predict_churn(tenant_id)

        if prob > 0.7:
            level = "HIGH"
            action = "OFFER_PREVENTIVE_DOWNGRADE"
        elif prob > 0.4:
            level = "MEDIUM"
            action = "SEND_RETENTION_EMAIL"
        else:
            level = "LOW"
            action = "NONE"

        return {
            "tenant_id": tenant_id,
            "churn_probability": prob,
            "risk_level": level,
            "recommended_action": action
        }
