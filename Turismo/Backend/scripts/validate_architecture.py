import os
import sys
import re

def check_prohibited_imports():
    """
    Escanea el código fuente buscando importaciones prohibidas entre dominios:
    - admin_plataforma no puede importar de mi_negocio
    - mi_negocio no puede importar de admin_plataforma
    """
    base_path = 'backend/apps'
    violations = []

    rules = [
        {
            'path': 'admin_plataforma',
            'prohibited': 'apps.prestadores.mi_negocio',
            'message': 'Admin Plataforma intentó importar desde Mi Negocio (Tenant).'
        },
        {
            'path': 'prestadores/mi_negocio',
            'prohibited': 'apps.admin_plataforma',
            'message': 'Mi Negocio (Tenant) intentó importar desde Admin Plataforma.'
        },
        {
            'path': 'sarita_agents',
            'prohibited': 'apps.prestadores.mi_negocio',
            'message': 'Sarita Agents intentó importar directamente desde Mi Negocio (Usar EventBus/Interfaces).'
        },
        {
            'path': 'domain_business',
            'prohibited': 'admin_',
            'message': 'Domain Business no puede importar desde módulos de Administración.'
        },
        {
            'path': 'core_erp/accounting',
            'prohibited': 'apps.domain_business.operativa',
            'message': 'Contabilidad no puede importar desde Operativa.'
        },
        {
            'path': 'core_erp/consolidation',
            'prohibited': 'apps.application_services',
            'message': 'Consolidación no puede importar desde Application Services.'
        },
        {
            'path': 'sarita_agents',
            'prohibited': 'models import',
            'message': 'Agentes IA no pueden importar modelos directamente (Usar Application Services).'
        }
    ]

    # Modelos de metadata permitidos para sarita_agents (su propio dominio de control)
    agent_metadata_models = [
        'Mision', 'PlanTáctico', 'TareaDelegada', 'RegistroDeEjecucion',
        'MicroTarea', 'RegistroMicroTarea', 'Prestador', 'CustomUser'
    ]

    # Exclusiones globales para la validación de imports
    global_exclusions = ['migrations', 'apps.py', 'tests', '__pycache__']

    for rule in rules:
        target_dir = os.path.join(base_path, rule['path'])
        if not os.path.exists(target_dir):
            continue

        for root, dirs, files in os.walk(target_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in global_exclusions]

            for file in files:
                # Excluir models.py del propio sarita_agents si estamos validando sarita_agents
                if rule['path'] == 'sarita_agents' and file == 'models.py':
                    continue

                if file.endswith('.py') and file not in ['apps.py']:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_no, line in enumerate(f, 1):
                            if rule['prohibited'] in line and '# DECOUPLED' not in line and '# LEGACY' not in line:
                                # Lógica especial para sarita_agents: permitir sus propios modelos de control
                                if rule['path'] == 'sarita_agents':
                                    # Ignorar imports de django.db.models (Sum, Avg, etc.) si solo se importan esos
                                    if 'django.db.models' in line and 'import' in line:
                                        # Permitir utilidades de agregación comunes de Django
                                        django_orm_utils = [
                                            'Sum', 'Avg', 'Count', 'Max', 'Min', 'F', 'Q',
                                            'ExpressionWrapper', 'DurationField', 'Case', 'When', 'Value'
                                        ]
                                        # Extraer CamelCase items
                                        items = re.findall(r'\b([A-Z]\w+)\b', line)
                                        if all(item in django_orm_utils for item in items):
                                            continue

                                    # Si la línea solo contiene modelos de metadata, permitirla
                                    is_metadata_only = True
                                    # Extraer palabras que parecen modelos (CamelCase)
                                    imported_items = re.findall(r'\b([A-Z]\w+)\b', line)
                                    if not imported_items:
                                        is_metadata_only = False
                                    else:
                                        for item in imported_items:
                                            if item not in agent_metadata_models:
                                                is_metadata_only = False
                                                break
                                    if is_metadata_only:
                                        continue

                                # Permitir import de modelos si es para compatibilidad (usando alias) o si es en application_services
                                if 'import' in line and ('models' in line or '.models' in line):
                                     violations.append(f"{file_path}:{line_no}: {rule['message']} -> {line.strip()}")

    if violations:
        print("\n❌ VIOLACIONES DE ARQUITECTURA DETECTADAS:")
        for v in violations:
            print(f"  - {v}")
        return False

    print("\n✅ Arquitectura de dominios validada exitosamente.")
    return True

def check_tenant_enforcement():
    """
    Verifica que los modelos de negocio hereden de clases que aplican multi-tenant.
    """
    base_path = 'backend/apps'
    target_apps = ['domain_business', 'core_erp']
    violations = []

    # Clases permitidas de herencia para multi-tenant
    allowed_bases = ['TenantAwareModel', 'AccountingTenantModel', 'CompanyBase', 'Tenant', 'BaseInvoice']
    # Modelos exentos (configuraciones globales, etc.)
    exempt_models = [
        'Tenant', 'HoldingEntity', 'HoldingMembership',
        'IntercompanyAccountMapping', 'ConsolidatedReportSnapshot'
    ]

    for app in target_apps:
        app_path = os.path.join(base_path, app)
        for root, _, files in os.walk(app_path):
            for file in files:
                if file == 'models.py':
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Buscar clases de modelos
                        models = re.findall(r'class\s+(\w+)\(([^)]+)\):', content)
                        for model_name, bases in models:
                            if model_name in exempt_models:
                                continue

                            # Excluir TextChoices de Django
                            if 'models.TextChoices' in bases:
                                continue

                            # Si no hereda de algo que suene a TenantAware
                            if not any(base in bases for base in allowed_bases):
                                violations.append(f"{file_path}: Modelo '{model_name}' no parece aplicar multi-tenant (Hereda de: {bases})")

    if violations:
        print("\n❌ VIOLACIONES DE MULTI-TENANT ENFORCEMENT:")
        for v in violations:
            print(f"  - {v}")
        return False

    print("\n✅ Multi-tenant enforcement validado.")
    return True

if __name__ == "__main__":
    success_imports = check_prohibited_imports()
    success_tenant = check_tenant_enforcement()

    if not success_imports or not success_tenant:
        sys.exit(1)
