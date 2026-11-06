import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class ChartOfAccountsManager:
    """
    Gestiona la estructura lógica del Plan de Cuentas (PUC).
    Centraliza la validación de códigos y naturalezas contables.
    """

    # Definición de Naturalezas (Debito/Credito) por Clase de Cuenta
    CLASS_NATURES = {
        '1': 'DEBIT',  # Activo
        '2': 'CREDIT', # Pasivo
        '3': 'CREDIT', # Patrimonio
        '4': 'CREDIT', # Ingresos
        '5': 'DEBIT',  # Gastos
        '6': 'DEBIT',  # Costos de Venta
        '7': 'DEBIT',  # Costos de Producción
    }

    # Cuentas mandatorias para la operación SaaS
    MANDATORY_ACCOUNTS = {
        'ASSETS': {'code': '1', 'name': 'Activos', 'type': 'asset'},
        'LIABILITIES': {'code': '2', 'name': 'Pasivos', 'type': 'liability'},
        'EQUITY': {'code': '3', 'name': 'Patrimonio', 'type': 'equity'},
        'INCOME_SAAS': {'code': '413501', 'name': 'Ingresos SaaS Suscripciones', 'type': 'income'},
        'INCOME_USAGE': {'code': '413502', 'name': 'Ingresos por Uso API/IA', 'type': 'income'},
        'DEFERRED_INCOME': {'code': '270505', 'name': 'Ingresos Diferidos SaaS', 'type': 'liability'},
        'TAXES_PAYABLE': {'code': '240805', 'name': 'Impuestos por Pagar (IVA)', 'type': 'liability'},
        'COSTS_IA': {'code': '519501', 'name': 'Costos Operación IA', 'type': 'expense'},
        'COSTS_INFRA': {'code': '519502', 'name': 'Costos Infraestructura Cloud', 'type': 'expense'},
        'BANK_FEES': {'code': '530505', 'name': 'Gastos Bancarios y Comisiones', 'type': 'expense'},
    }

    @staticmethod
    def validate_account_code(code):
        if not code or not code.replace('.', '').isdigit():
            raise ValidationError(f"Código de cuenta inválido: {code}. Debe ser numérico.")

        first_digit = code[0]
        if first_digit not in ChartOfAccountsManager.CLASS_NATURES:
            raise ValidationError(f"Clase de cuenta no reconocida: {first_digit}")

    @staticmethod
    def get_account_nature(code):
        first_digit = code[0]
        return ChartOfAccountsManager.CLASS_NATURES.get(first_digit, 'DEBIT')

    @staticmethod
    def is_debit_increase(code):
        return ChartOfAccountsManager.get_account_nature(code) == 'DEBIT'

    @staticmethod
    def get_mandatory_accounts():
        return ChartOfAccountsManager.MANDATORY_ACCOUNTS
