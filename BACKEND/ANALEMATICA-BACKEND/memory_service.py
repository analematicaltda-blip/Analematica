import json
import logging
import uuid
import numpy as np
from django.utils import timezone
from .models import DecisionHistory

logger = logging.getLogger(__name__)

class SemanticMemory:
    """
    Gestiona la memoria semántica del sistema mediante embeddings.
    Permite la recuperación de casos pasados por similitud de intención y contexto.
    """

    def store_decision(self, intention, input_params, result):
        """
        Crea un registro en la memoria histórica con su representación vectorial.
        """
        # Simulación de generación de embedding (En prod usaría OpenAI o SADI)
        content_str = f"{intention} {json.dumps(input_params)}"
        simulated_embedding = self._generate_simulated_embedding(content_str)

        DecisionHistory.objects.create(
            intention=intention,
            input_params=input_params,
            risk_score=result.risk_score,
            consensus_score=0.9, # Simulado
            final_status=result.status,
            was_compensated=(result.status == 'ROLLED_BACK'),
            embedding=simulated_embedding.tobytes()
        )
        logger.info(f"Memoria: Decisión {intention} indexada semánticamente.")

    def find_similar_cases(self, intention, input_params, limit=3):
        """
        Busca casos similares en el pasado para predecir comportamiento.
        """
        content_str = f"{intention} {json.dumps(input_params)}"
        query_embedding = self._generate_simulated_embedding(content_str)

        all_histories = DecisionHistory.objects.all()
        results = []

        for hist in all_histories:
            if hist.embedding:
                hist_embedding = np.frombuffer(hist.embedding, dtype=np.float32)
                # Cálculo de similitud coseno simple
                similarity = np.dot(query_embedding, hist_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(hist_embedding)
                )
                if similarity > 0.8: # Umbral de similitud
                    results.append({
                        "id": hist.id,
                        "intention": hist.intention,
                        "status": hist.final_status,
                        "similarity": float(similarity)
                    })

        # Ordenar por similitud
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]

    def _generate_simulated_embedding(self, text):
        """
        Genera un vector determinista basado en el texto para propósitos de simulación.
        """
        seed = hash(text) % (2**32)
        np.random.seed(seed)
        return np.random.rand(128).astype(np.float32)

class MemoryService:
    """
    Punto de entrada único para todos los niveles de memoria.
    """
    def __init__(self):
        self.semantic = SemanticMemory()

    def record_execution(self, correlation_id, intention, params, result):
        # Memoria Estratégica y Semántica
        self.semantic.store_decision(intention, params, result)

    def get_contextual_insights(self, intention, params):
        """
        Extrae lecciones aprendidas de casos similares.
        """
        similars = self.semantic.find_similar_cases(intention, params)
        if not similars:
            return "No hay precedentes directos."

        fail_rate = len([c for c in similars if c['status'] != 'EXECUTED']) / len(similars)
        return {
            "precedents_count": len(similars),
            "predicted_failure_risk": fail_rate,
            "lesson": "Alta probabilidad de éxito" if fail_rate < 0.3 else "Precaución: Casos similares fallaron"
        }
