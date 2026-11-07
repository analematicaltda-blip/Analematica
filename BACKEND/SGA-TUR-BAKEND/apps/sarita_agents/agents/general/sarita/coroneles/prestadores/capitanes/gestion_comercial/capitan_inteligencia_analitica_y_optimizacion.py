from apps.sarita_agents.agents.capitan_template import CapitanTemplate

class CapitanInteligenciaAnaliticaYOptimizacion(CapitanTemplate):
    def _get_tenientes(self) -> dict:
        return {"generico": "seo_technical"} # Fallback a teniente existente

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        p.pasos_del_plan = {"1": {"teniente": "generico", "descripcion": "Ejecución comercial", "parametros": {}}}
        p.save()
        return p
