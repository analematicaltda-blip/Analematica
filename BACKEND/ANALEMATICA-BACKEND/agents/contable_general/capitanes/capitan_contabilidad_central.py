"""
contable_general -> capitanes: capitan_contabilidad_central.py
Doctrina Operativa DEAA-V2.1 - Enlace Integral Cruzado 1.000% con Ventas, Operativo/Compras, Finanzas y Archivo TRD
"""
import hashlib
import time
from typing import Dict, Any, List

class CapitanContabilidadCentral:
    def __init__(self, name: str = "capitan_contabilidad_central"):
        self.name = name

    def procesar_transaccion_cruzada(self, tipo: str, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el enlace cruzado de partidas dobles automáticas con las otras 4 divisiones.
        """
        asientos = []
        doc_ref = datos.get("doc_ref", f"DOC-{int(time.time())}")

        if tipo == "VENTA":
            # Cruce con División Comercial (Ventas):
            # Clientes Nacionales (130505) = Débito
            # Ingresos Operacionales (4135) = Crédito
            # IVA Generado (240805) = Crédito
            base = float(datos.get("base_cop", 1000000.0))
            iva = round(base * 0.19, 2)
            total = round(base + iva, 2)
            asientos.append({"cuenta": "130505", "nombre": "Clientes Nacionales", "debito": total, "credito": 0.0})
            asientos.append({"cuenta": "4135", "nombre": "Comercio / Servicios ERP", "debito": 0.0, "credito": base})
            asientos.append({"cuenta": "240805", "nombre": "IVA Generado 19%", "debito": 0.0, "credito": iva})

        elif tipo == "COMPRA_INSUMOS":
            # Cruce con División Operativa (Compras/SG-SST/Insumos):
            # Mercancías / Gastos (1435 / 5135) = Débito
            # IVA Descontable (240810) = Débito
            # ReteFuente Compras (236540) = Crédito (2.5%)
            # ReteICA Territorial (2368) = Crédito (0.7%)
            # Proveedores Nacionales (2205) = Crédito
            base = float(datos.get("base_cop", 500000.0))
            iva_desc = round(base * 0.19, 2)
            retefuente = round(base * 0.025, 2)
            reteica = round(base * 0.007, 2)
            proveedores = round(base + iva_desc - retefuente - reteica, 2)
            asientos.append({"cuenta": "5135", "nombre": "Insumos Operacionales ERP", "debito": base, "credito": 0.0})
            asientos.append({"cuenta": "240810", "nombre": "IVA Descontable en Compras", "debito": iva_desc, "credito": 0.0})
            asientos.append({"cuenta": "236540", "nombre": "ReteFuente Compras 2.5%", "debito": 0.0, "credito": retefuente})
            asientos.append({"cuenta": "2368", "nombre": "ReteICA Territorial Retenido", "debito": 0.0, "credito": reteica})
            asientos.append({"cuenta": "2205", "nombre": "Proveedores Nacionales", "debito": 0.0, "credito": proveedores})

        elif tipo == "RECAUDO_FINANCIERO":
            # Cruce con División Financiera (Tesorería):
            # Bancolombia (111005) = Débito
            # Clientes (130505) = Crédito
            monto = float(datos.get("monto_cop", 1190000.0))
            asientos.append({"cuenta": "111005", "nombre": "Bancolombia Cta Cte", "debito": monto, "credito": 0.0})
            asientos.append({"cuenta": "130505", "nombre": "Clientes Nacionales", "debito": 0.0, "credito": monto})

        tot_deb = round(sum(a["debito"] for a in asientos), 2)
        tot_cred = round(sum(a["credito"] for a in asientos), 2)
        cuadrado = abs(tot_deb - tot_cred) < 0.01

        # Enlace con Archivo TRD: Sello Criptográfico SHA-256
        raw_token = f"{doc_ref}-{tot_deb}-{tot_cred}-{time.time()}"
        sha_stamp = hashlib.sha256(raw_token.encode()).hexdigest()

        return {
            "unit": self.name,
            "status": "success",
            "doc_ref": doc_ref,
            "tipo_operacion": tipo,
            "asientos_puc": asientos,
            "total_debitos": tot_deb,
            "total_creditos": tot_cred,
            "partida_doble_cuadrada": cuadrado,
            "sello_archivo_trd": {
                "sha256_hash": sha_stamp,
                "trd_subserie": "110.02 - Comprobantes Contables Integrados",
                "inmutable": True
            }
        }

    def execute(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        params = payload or {}
        tipo = params.get("tipo", "VENTA")
        return self.procesar_transaccion_cruzada(tipo, params)

AgentUnit = CapitanContabilidadCentral
