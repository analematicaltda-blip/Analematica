"""Compatibility entry point; no fabricated KPIs or unscoped scenario persistence."""
from .cash_simulation import simulate

class SimulationEngine:
    @staticmethod
    def simulate_scenario(name,parameters):
        if not isinstance(name,str) or not 1<=len(name.strip())<=255:
            raise ValueError('An explicit scenario name is required.')
        return {'scenario_name':name.strip(),**simulate(parameters)}
