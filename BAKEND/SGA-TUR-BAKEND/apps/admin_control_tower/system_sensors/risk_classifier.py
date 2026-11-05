class RiskClassifier:
    """
    Clasifica riesgos sistémicos en niveles (LOW, MEDIUM, HIGH).
    """

    @staticmethod
    def classify(financial_anomalies, commercial_health):
        if len(financial_anomalies) > 0:
            return "HIGH"

        if commercial_health['churn_rate'] > 10:
            return "MEDIUM"

        return "LOW"
