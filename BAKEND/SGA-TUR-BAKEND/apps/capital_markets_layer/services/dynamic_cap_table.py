from .capital_structure_engine import CapitalStructureEngine
from ..models import ShareIssuance, EquityRound

class DynamicCapTable:
    """
    Cap Table en tiempo real con versionado y simulación (Fase 8).
    """

    @staticmethod
    def get_full_cap_table():
        """
        Retorna la tabla de capitalización detallada.
        """
        ownership = CapitalStructureEngine.calculate_current_ownership()

        return {
            "summary": {
                "total_holders": len(ownership),
                "fully_diluted_shares": sum(o['shares'] for o in ownership)
            },
            "table": ownership
        }

    @staticmethod
    def create_snapshot():
        """
        Captura el estado actual para histórico.
        """
        # Implementación de persistencia de snapshot si se requiere
        return DynamicCapTable.get_full_cap_table()

    @staticmethod
    def simulate_esop_expansion(pool_percentage):
        """
        Simula la creación o expansión de un pool de opciones para empleados.
        """
        ownership = CapitalStructureEngine.calculate_current_ownership()
        dilution_factor = Decimal('1') - (Decimal(str(pool_percentage)) / 100)

        simulated = []
        for entry in ownership:
            simulated.append({
                "shareholder": entry['shareholder'],
                "new_percentage": entry['percentage'] * dilution_factor
            })

        simulated.append({
            "shareholder": "ESOP Pool (Simulado)",
            "new_percentage": pool_percentage
        })

        return simulated

from decimal import Decimal
