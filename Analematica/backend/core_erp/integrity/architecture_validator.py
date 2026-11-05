# backend/apps/core_erp/integrity/architecture_validator.py
import os
import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ArchitectureValidator:
    """
    Regla 1: Ningún dominio puede importar directamente otro dominio.
    Solo comunicación vía EventBus.
    """

    OFFICIAL_DOMAINS = [
        'finanzas', 'ventas', 'inventario', 'nomina', 'sgsst', 'marketing',
        'comercial', 'contabilidad', 'prestadores', 'admin_plataforma'
    ]

    def __init__(self, root_path: str = "apps"):
        self.root_path = root_path
        self.violations: List[Dict] = []

    def validate(self) -> Dict:
        """
        Escanea el código fuente buscando imports cruzados prohibidos.
        """
        logger.info("Iniciando auditoría de aislamiento de dominios...")

        # Obtener ruta absoluta del directorio apps
        base_dir = os.path.join(os.getcwd(), "backend", self.root_path)
        if not os.path.exists(base_dir):
            base_dir = os.path.join(os.getcwd(), self.root_path)

        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._check_file_imports(file_path)

        status = "PASSED" if not self.violations else "FAILED"
        score = 100 if not self.violations else max(0, 100 - (len(self.violations) * 5))

        return {
            "component": "DomainIsolation",
            "status": status,
            "score": score,
            "violations": self.violations
        }

    def _check_file_imports(self, file_path: str):
        # Determinar el dominio del archivo actual
        current_domain = self._get_domain_from_path(file_path)
        if not current_domain or current_domain not in self.OFFICIAL_DOMAINS:
            return

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                # Regex para capturar 'import apps.dominio' o 'from apps.dominio import ...'
                match = re.search(r'(?:from|import)\s+apps\.([\w_]+)', line)
                if match:
                    imported_domain = match.group(1)
                    if imported_domain in self.OFFICIAL_DOMAINS and imported_domain != current_domain:
                        # Excepción: core_erp y common son compartidos
                        if imported_domain in ['core_erp', 'common']:
                            continue

                        self.violations.append({
                            "file": os.path.relpath(file_path),
                            "line": i + 1,
                            "offending_import": imported_domain,
                            "current_domain": current_domain,
                            "message": f"Violación de aislamiento: {current_domain} importa directamente a {imported_domain}"
                        })

    def _get_domain_from_path(self, file_path: str) -> str:
        parts = file_path.split(os.sep)
        try:
            apps_idx = parts.index("apps")
            if len(parts) > apps_idx + 1:
                return parts[apps_idx + 1]
        except ValueError:
            pass
        return None
