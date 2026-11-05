"""
Servicio Maestro de Enlace Contable Multimódulo (GATuristica ERP)
Interconecta Ventas, Archivo, Finanzas y Operaciones con la Suite Contable.
Cumple con partida doble, causación de impuestos (IVA, Retención, Renta), activos y pasivos.
"""

from decimal import Decimal
import uuid
from typing import Dict, Any, List

class MultiModuleAccountingBridge:
    """
    Motor determinístico de causación y registro contable entre módulos del ERP.
    """

    @staticmethod
    def balance_entry(lines: List[Dict[str, Any]]) -> bool:
        """Verifica que la suma de débitos sea igual a la suma de créditos."""
        total_debit = sum(Decimal(str(line.get('debit', 0))) for line in lines)
        total_credit = sum(Decimal(str(line.get('credit', 0))) for line in lines)
        return total_debit == total_credit

    @classmethod
    def bridge_venta(cls, venta_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Causación contable de venta de productos o servicios turísticos:
        - Débito: Clientes (130505) o Caja/Bancos (110505 / 111005)
        - Crédito: Ingresos Operacionales (413505 / 414005)
        - Crédito: IVA Generado 19% (240801)
        - Débito: Retención en la fuente a favor (135515) si aplica
        """
        subtotal = Decimal(str(venta_data.get('subtotal', 0)))
        tasa_iva = Decimal(str(venta_data.get('tasa_iva', '0.19')))
        iva = (subtotal * tasa_iva).quantize(Decimal('0.01'))

        tasa_rete = Decimal(str(venta_data.get('tasa_retefuente', '0.00')))
        retefuente = (subtotal * tasa_rete).quantize(Decimal('0.01'))

        total_cobrar = subtotal + iva - retefuente

        lines = [
            {
                'account_code': '130505',
                'account_name': 'Clientes Nacionales',
                'debit': total_cobrar,
                'credit': Decimal('0.00'),
                'description': f"Cuentas por cobrar factura {venta_data.get('numero', '')}"
            },
            {
                'account_code': '414005' if venta_data.get('es_turismo') else '413505',
                'account_name': 'Ingresos Operacionales',
                'debit': Decimal('0.00'),
                'credit': subtotal,
                'description': f"Venta de bienes/servicios - {venta_data.get('concepto', '')}"
            },
            {
                'account_code': '240801',
                'account_name': 'IVA Generado en Ventas (19%)',
                'debit': Decimal('0.00'),
                'credit': iva,
                'description': "IVA generado facturación"
            }
        ]

        if retefuente > 0:
            lines.append({
                'account_code': '135515',
                'account_name': 'Anticipo Retención en la Fuente',
                'debit': retefuente,
                'credit': Decimal('0.00'),
                'description': "Retención en la fuente practicada por cliente"
            })

        assert cls.balance_entry(lines), "El asiento contable de ventas no cumple partida doble"

        return {
            'module': 'VENTAS',
            'reference_id': venta_data.get('id', str(uuid.uuid4())),
            'lines': lines,
            'is_balanced': True
        }

    @classmethod
    def bridge_compra(cls, compra_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Causación contable de compra o gasto operacional:
        - Débito: Inventario (1435) o Gasto Operacional (5105 / 5115)
        - Débito: IVA Descontable (240802)
        - Crédito: Retención en la fuente por pagar (236540 / 236525)
        - Crédito: Proveedores / Cuentas por pagar (220505)
        """
        subtotal = Decimal(str(compra_data.get('subtotal', 0)))
        tasa_iva = Decimal(str(compra_data.get('tasa_iva', '0.19')))
        iva = (subtotal * tasa_iva).quantize(Decimal('0.01'))

        tasa_rete = Decimal(str(compra_data.get('tasa_retefuente', '0.025')))
        retefuente = (subtotal * tasa_rete).quantize(Decimal('0.01'))

        total_pagar = subtotal + iva - retefuente

        lines = [
            {
                'account_code': '1435' if compra_data.get('es_inventario') else '5135',
                'account_name': 'Inventarios o Gasto',
                'debit': subtotal,
                'credit': Decimal('0.00'),
                'description': f"Compra factura {compra_data.get('numero', '')}"
            },
            {
                'account_code': '240802',
                'account_name': 'IVA Descontable en Compras',
                'debit': iva,
                'credit': Decimal('0.00'),
                'description': "IVA descontable"
            },
            {
                'account_code': '236540',
                'account_name': 'Retención en la Fuente por Pagar',
                'debit': Decimal('0.00'),
                'credit': retefuente,
                'description': "Retención en la fuente practicada a proveedor"
            },
            {
                'account_code': '220505',
                'account_name': 'Proveedores Nacionales',
                'debit': Decimal('0.00'),
                'credit': total_pagar,
                'description': f"Cuenta por pagar proveedor {compra_data.get('proveedor', '')}"
            }
        ]

        assert cls.balance_entry(lines), "El asiento contable de compras no cumple partida doble"

        return {
            'module': 'COMPRAS',
            'reference_id': compra_data.get('id', str(uuid.uuid4())),
            'lines': lines,
            'is_balanced': True
        }

    @classmethod
    def bridge_conciliacion_bancaria(cls, tesoreria_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Causación contable de recaudos, cobro de pasarela o conciliación financiera:
        - Débito: Bancos (111005)
        - Débito: Gasto Comisiones Bancarias / Pasarela (530515)
        - Crédito: Clientes / Monedero (130505 / 2380)
        """
        monto_bruto = Decimal(str(tesoreria_data.get('monto_bruto', 0)))
        comision = Decimal(str(tesoreria_data.get('comision', 0)))
        neto_banco = monto_bruto - comision

        lines = [
            {
                'account_code': '111005',
                'account_name': 'Bancos Moneda Nacional',
                'debit': neto_banco,
                'credit': Decimal('0.00'),
                'description': "Ingreso neto a cuenta bancaria"
            },
            {
                'account_code': '530515',
                'account_name': 'Gastos Financieros - Comisiones',
                'debit': comision,
                'credit': Decimal('0.00'),
                'description': "Comisión de intermediación o pasarela"
            },
            {
                'account_code': '130505',
                'account_name': 'Clientes Nacionales',
                'debit': Decimal('0.00'),
                'credit': monto_bruto,
                'description': f"Pago recibido referencia {tesoreria_data.get('referencia', '')}"
            }
        ]

        assert cls.balance_entry(lines), "El asiento contable de conciliación no cumple partida doble"

        return {
            'module': 'FINANZAS',
            'reference_id': tesoreria_data.get('id', str(uuid.uuid4())),
            'lines': lines,
            'is_balanced': True
        }

    @classmethod
    def bridge_reserva_operativa(cls, reserva_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Causación contable de reserva confirmada desde el módulo operativo/turismo:
        - Débito: Anticipos de Clientes / Clientes (130505)
        - Crédito: Ingresos Hotelería y Turismo (414005)
        - Crédito: IVA Generado (240801)
        """
        return cls.bridge_venta({
            'id': reserva_data.get('id'),
            'numero': f"RES-{reserva_data.get('codigo_reserva', '000')}",
            'concepto': f"Reserva de servicio turístico {reserva_data.get('servicio', '')}",
            'subtotal': reserva_data.get('valor_total', 0),
            'tasa_iva': reserva_data.get('tasa_iva', '0.19'),
            'tasa_retefuente': '0.00',
            'es_turismo': True
        })
