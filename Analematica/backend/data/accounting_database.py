"""
Repositorio de Base de Datos Contable y Territorial Oficial (PUC y DIVIPOLA)
Analemática ERP Soberano - Doctrina DEAA-V2.1
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_FILE = Path(__file__).resolve().parent / "accounting_sovereign.db"

# Catálogo canónico PUC Colombia (Plan Único de Cuentas)
CANONICAL_PUC = [
    # CLASE 1: ACTIVO
    ("1", "ACTIVO", "ASSET", None),
    ("11", "DISPONIBLE", "ASSET", "1"),
    ("1105", "CAJA", "ASSET", "11"),
    ("110505", "CAJA GENERAL", "ASSET", "1105"),
    ("1110", "BANCOS", "ASSET", "11"),
    ("111005", "BANCOLOMBIA CUENTA CORRIENTE PRINCIPAL", "ASSET", "1110"),
    ("111010", "BANCO DE BOGOTA CUENTA RECAUDADORA", "ASSET", "1110"),
    ("13", "DEUDORES", "ASSET", "1"),
    ("1305", "CLIENTES", "ASSET", "13"),
    ("130505", "CLIENTES NACIONALES (VENTAS FACTURADAS)", "ASSET", "1305"),
    ("1355", "ANTICIPO DE IMPUESTOS Y CONTRIBUCIONES", "ASSET", "13"),
    ("135515", "ANTICIPO RETEFUENTE (2.5% / 3.5%)", "ASSET", "1355"),
    ("135517", "ANTICIPO RETEIVA (15%)", "ASSET", "1355"),
    ("135518", "ANTICIPO RETEICA TERRITORIAL", "ASSET", "1355"),
    ("14", "INVENTARIOS", "ASSET", "1"),
    ("1435", "MERCANCIAS NO FABRICADAS POR LA EMPRESA / PRODUCTOS", "ASSET", "14"),
    ("15", "PROPIEDADES PLANTA Y EQUIPO", "ASSET", "1"),
    ("1524", "EQUIPO DE OFICINA Y SERVIDORES", "ASSET", "15"),
    ("1528", "EQUIPO DE COMPUTACION Y COMUNICACION", "ASSET", "15"),
    ("1592", "DEPRECIACION ACUMULADA (CR)", "ASSET", "15"),

    # CLASE 2: PASIVO
    ("2", "PASIVO", "LIABILITY", None),
    ("21", "OBLIGACIONES FINANCIERAS", "LIABILITY", "2"),
    ("2105", "BANCOS NACIONALES", "LIABILITY", "21"),
    ("22", "PROVEEDORES", "LIABILITY", "2"),
    ("2205", "NACIONALES (COMPRAS Y SUMINISTROS)", "LIABILITY", "22"),
    ("23", "CUENTAS POR PAGAR", "LIABILITY", "2"),
    ("2365", "RETENCION EN LA FUENTE POR PAGAR", "LIABILITY", "23"),
    ("236540", "RETEFUENTE COMPRAS (2.5%)", "LIABILITY", "2365"),
    ("236525", "RETEFUENTE SERVICIOS (4%)", "LIABILITY", "2365"),
    ("2367", "IMPUESTO A LAS VENTAS RETENIDO (RETEIVA)", "LIABILITY", "23"),
    ("2368", "IMPUESTO DE INDUSTRIA Y COMERCIO RETENIDO (RETEICA)", "LIABILITY", "23"),
    ("24", "IMPUESTOS, GRAVAMENES Y TASAS", "LIABILITY", "2"),
    ("2408", "IMPUESTO SOBRE LAS VENTAS POR PAGAR (IVA)", "LIABILITY", "24"),
    ("240805", "IVA GENERADO EN VENTAS (19%)", "LIABILITY", "2408"),
    ("240810", "IVA DESCONTABLE EN COMPRAS (19%)", "LIABILITY", "2408"),
    ("26", "PASIVOS ESTIMADOS Y PROVISIONES", "LIABILITY", "2"),
    ("2615", "PROVISION PARA IMPUESTO DE RENTA Y COMPLEMENTARIOS (35%)", "LIABILITY", "26"),

    # CLASE 3: PATRIMONIO
    ("3", "PATRIMONIO", "EQUITY", None),
    ("31", "CAPITAL SOCIAL", "EQUITY", "3"),
    ("3105", "CAPITAL SUSCRITO Y PAGADO", "EQUITY", "31"),
    ("36", "RESULTADOS DEL EJERCICIO", "EQUITY", "3"),
    ("3605", "UTILIDAD DEL EJERCICIO", "EQUITY", "36"),

    # CLASE 4: INGRESOS
    ("4", "INGRESOS", "REVENUE", None),
    ("41", "OPERACIONALES", "REVENUE", "4"),
    ("4135", "COMERCIO AL POR MAYOR Y AL POR MENOR / SERVICIOS ERP", "REVENUE", "41"),

    # CLASE 5: GASTOS (EGRESOS)
    ("5", "GASTOS", "EXPENSE", None),
    ("51", "OPERACIONALES DE ADMINISTRACION", "EXPENSE", "5"),
    ("5105", "GASTOS DE PERSONAL Y NOMINA", "EXPENSE", "51"),
    ("5135", "SERVICIOS GENERALES Y TECNOLOGICOS", "EXPENSE", "51"),
    ("5160", "DEPRECIACIONES LINEAL PPE", "EXPENSE", "51"),

    # CLASE 6: COSTOS DE VENTAS
    ("6", "COSTOS DE VENTAS", "EXPENSE", None),
    ("61", "COSTO DE VENTAS Y DE PRESTACION DE SERVICIOS", "EXPENSE", "6"),
    ("6135", "COSTOS OPERATIVOS Y ADQUISICION DE INSUMOS", "EXPENSE", "61")
]

# Catálogo canónico territorial DIVIPOLA (DANE Colombia)
CANONICAL_DIVIPOLA = [
    # dept_code, dept_name, mun_code, mun_name, reteica_rate_mil
    ("11", "BOGOTA D.C.", "11001", "BOGOTA, D.C.", 9.66),
    ("05", "ANTIOQUIA", "05001", "MEDELLIN", 7.00),
    ("76", "VALLE DEL CAUCA", "76001", "CALI", 7.70),
    ("08", "ATLANTICO", "08001", "BARRANQUILLA", 8.00),
    ("50", "META", "50001", "VILLAVICENCIO", 6.00),
    ("50", "META", "50568", "PUERTO GAITAN", 5.00),
    ("68", "SANTANDER", "68001", "BUCARAMANGA", 7.00),
    ("13", "BOLIVAR", "13001", "CARTAGENA DE INDIAS", 7.50),
    ("25", "CUNDINAMARCA", "25754", "SOACHA", 6.50),
    ("17", "CALDAS", "17001", "MANIZALES", 6.00),
    ("66", "RISARALDA", "66001", "PEREIRA", 6.00),
    ("63", "QUINDIO", "63001", "ARMENIA", 6.00)
]

def init_accounting_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Tabla PUC
    cur.execute("""
    CREATE TABLE IF NOT EXISTS corporate_puc (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        account_type TEXT NOT NULL,
        parent_code TEXT
    )
    """)

    # Tabla DIVIPOLA
    cur.execute("""
    CREATE TABLE IF NOT EXISTS territorial_divipola (
        mun_code TEXT PRIMARY KEY,
        mun_name TEXT NOT NULL,
        dept_code TEXT NOT NULL,
        dept_name TEXT NOT NULL,
        reteica_rate_mil REAL NOT NULL
    )
    """)

    # Tabla de comprobantes integrados
    cur.execute("""
    CREATE TABLE IF NOT EXISTS journal_vouchers (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        concept TEXT NOT NULL,
        origin_module TEXT NOT NULL, -- VENTAS, COMPRAS, FINANZAS, OPERATIVO
        debits REAL NOT NULL,
        credits REAL NOT NULL,
        sha256_hash TEXT NOT NULL,
        trd_code TEXT NOT NULL
    )
    """)

    # Poblado idempotente de PUC
    for code, name, ac_type, parent in CANONICAL_PUC:
        cur.execute("INSERT OR REPLACE INTO corporate_puc (code, name, account_type, parent_code) VALUES (?, ?, ?, ?)",
                    (code, name, ac_type, parent))

    # Poblado idempotente de DIVIPOLA
    for dept_c, dept_n, mun_c, mun_n, rate in CANONICAL_DIVIPOLA:
        cur.execute("INSERT OR REPLACE INTO territorial_divipola (mun_code, mun_name, dept_code, dept_name, reteica_rate_mil) VALUES (?, ?, ?, ?, ?)",
                    (mun_c, mun_n, dept_c, dept_n, rate))

    conn.commit()
    conn.close()

def get_puc_catalog(search: str = "") -> List[Dict[str, Any]]:
    init_accounting_db()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if search:
        s = f"%{search.upper()}%"
        cur.execute("SELECT code, name, account_type, parent_code FROM corporate_puc WHERE code LIKE ? OR UPPER(name) LIKE ? ORDER BY code", (s, s))
    else:
        cur.execute("SELECT code, name, account_type, parent_code FROM corporate_puc ORDER BY code")
    rows = cur.fetchall()
    conn.close()
    return [{"code": r[0], "name": r[1], "type": r[2], "parent": r[3]} for r in rows]

def get_divipola_catalog(search: str = "") -> List[Dict[str, Any]]:
    init_accounting_db()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if search:
        s = f"%{search.upper()}%"
        cur.execute("SELECT mun_code, mun_name, dept_code, dept_name, reteica_rate_mil FROM territorial_divipola WHERE mun_code LIKE ? OR UPPER(mun_name) LIKE ? OR UPPER(dept_name) LIKE ? ORDER BY mun_name", (s, s, s))
    else:
        cur.execute("SELECT mun_code, mun_name, dept_code, dept_name, reteica_rate_mil FROM territorial_divipola ORDER BY mun_name")
    rows = cur.fetchall()
    conn.close()
    return [{"mun_code": r[0], "mun_name": r[1], "dept_code": r[2], "dept_name": r[3], "reteica_rate_mil": r[4]} for r in rows]

# Inicializar al importar
init_accounting_db()
