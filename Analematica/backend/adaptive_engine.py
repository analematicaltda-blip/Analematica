import logging
from django.db.models import Avg, Count
from .models import DecisionHistory, AgentPerformance, AdaptiveProposal, GovernancePolicy

logger = logging.getLogger(__name__)

class AdaptiveEngine:
    """
    Motor de Inteligencia Adaptativa (AIM).
    Optimiza el comportamiento del sistema analizando el historial y el rendimiento.
    """

    def analyze_agent_performance(self):
        """
        Analiza si los agentes están alineados con los resultados exitosos.
        Genera propuestas de ajuste de pesos.
        """
        # En un sistema real, esto cruzaría votos individuales con resultados.
        # Aquí simulamos el análisis de tendencias.
        agents = AgentPerformance.objects.all()
        proposals = []

        for agent in agents:
            success_rate = agent.votes_in_consensus / agent.total_votes if agent.total_votes > 0 else 1.0

            if success_rate < 0.6 and agent.current_weight_multiplier > 0.5:
                # Sugerir reducción de peso
                new_multiplier = max(0.5, agent.current_weight_multiplier - 0.1)
                proposal = AdaptiveProposal.objects.create(
                    type='WEIGHT_ADJUST',
                    proposal_data={
                        "agent_id": agent.agent_id,
                        "old_multiplier": agent.current_weight_multiplier,
                        "new_multiplier": new_multiplier
                    },
                    reasoning=f"El agente {agent.agent_id} tiene una tasa de éxito de {success_rate:.2f}. Se sugiere reducir su influencia."
                )
                proposals.append(proposal)
                logger.warning(f"AIM: Sugerido ajuste de peso para {agent.agent_id} debido a bajo rendimiento.")

        return proposals

    def predict_command_risk(self, intention, params, historical_insights):
        """
        Calcula un Risk Score Predictivo basado en la memoria semántica.
        """
        is_dict = isinstance(historical_insights, dict)
        base_risk = historical_insights.get('predicted_failure_risk', 0.0) if is_dict else 0.0
        precedents = historical_insights.get('precedents_count', 0) if is_dict else 0

        # Ajuste por anomalías en parámetros
        if params.get('amount', 0) > 10000:
            base_risk += 0.2

        return {
            "predictive_score": min(1.0, base_risk),
            "confidence": 0.85,
            "justification": f"Basado en {precedents} casos similares."
        }

    def optimize_workflows(self):
        """
        Analiza fallos en WPA para sugerir cambios en las definiciones.
        """
        failed_workflows = DecisionHistory.objects.filter(was_compensated=True).values('intention').annotate(count=Count('id'))

        for fw in failed_workflows:
            if fw['count'] > 5:
                # Demasiados fallos para esta intención
                AdaptiveProposal.objects.create(
                    type='WORKFLOW_OPT',
                    proposal_data={"intention": fw['intention'], "action": "REVIEW_TIMEOUTS"},
                    reasoning=f"La intención {fw['intention']} ha fallado {fw['count']} veces. Se recomienda revisar tiempos de respuesta de servicios dependientes."
                )

    def generate_strategic_insights(self):
        """
        Bloque 5: Inteligencia Operativa Real.
        Analiza KPIs reales para generar propuestas estratégicas.
        """
        from apps.comercial.saas_metrics.revenue_metrics import RevenueMetrics
        from apps.comercial.saas_metrics.churn_analysis import ChurnAnalysis

        mrr = RevenueMetrics.calculate_mrr()
        churn = ChurnAnalysis.calculate_churn_rate()

        insights = []

        if churn > 5.0:
            insights.append({
                "type": "CHURN_ALERT",
                "severity": "HIGH",
                "message": f"Churn rate crítico detectado: {churn:.2f}%. Se requiere optimización de retención."
            })

        if mrr > 10000:
             insights.append({
                "type": "GROWTH_MILESTONE",
                "severity": "LOW",
                "message": "Objetivo de MRR mensual superado. Considerar expansión de SPV."
            })

        return insights
