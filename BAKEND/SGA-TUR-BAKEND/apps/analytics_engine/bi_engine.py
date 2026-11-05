class AnalyticsEngine:
    """
    Hallazgo 18: Business Intelligence Comparativo.
    Calcula KPIs de crecimiento interanual e intermensual.
    """

    @staticmethod
    def calculate_yoy(current_value, previous_year_value):
        if not previous_year_value or previous_year_value == 0:
            return 0
        return ((current_value - previous_year_value) / previous_year_value) * 100

    @staticmethod
    def calculate_mom(current_month_value, previous_month_value):
        if not previous_month_value or previous_month_value == 0:
            return 0
        return ((current_month_value - previous_month_value) / previous_month_value) * 100

    @staticmethod
    def get_trend(values: list):
        """Calcula el promedio móvil de 3 períodos."""
        if len(values) < 3:
            return sum(values) / len(values) if values else 0
        return sum(values[-3:]) / 3
