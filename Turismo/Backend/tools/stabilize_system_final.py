import os
import re

def fix_capitan_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Fix absolute import
        content = content.replace('from .coronel_template import CoronelTemplate', 'from apps.sarita_agents.agents.coronel_template import CoronelTemplate')
        content = content.replace('from ..coronel_template import CoronelTemplate', 'from apps.sarita_agents.agents.coronel_template import CoronelTemplate')

        # 2. Fix __init__ signature
        old_init = r'def __init__\(self, mision_id: str, objective: str, parametros: Dict\[str, Any\]\):'
        new_init = 'def __init__(self, coronel):'
        content = re.sub(old_init, new_init, content)

        old_super = r'super\(\)\.__init__\(mision_id=mision_id, objective=objective, parametros=parametros\)'
        new_super = 'super().__init__(coronel=coronel)'
        content = re.sub(old_super, new_super, content)

        # 3. Remove self.logger.info from __init__ (causes attribute error)
        content = re.sub(r'self\.logger\.info\(f"CAPITÁN.*?\)\n', '', content)
        content = re.sub(r'self\.logger\.info\("CAPITÁN.*?"\)\n', '', content)

        # 4. Inject _get_tenientes if missing
        if 'def _get_tenientes(self)' not in content:
            method_body = """
    def _get_tenientes(self) -> Dict:
        return {}
"""
            if 'def plan(self' in content:
                content = re.sub(r'(    def plan\(self.*?\):)', method_body + r'\1', content, flags=re.DOTALL)
            else:
                # Append at the end of class
                content += method_body

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")

def fix_urls(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            c = f.read()
        if 'urlpatterns' not in c:
            with open(filepath, 'w') as f:
                f.write("from django.urls import path\n\nurlpatterns = []\n")
            print(f"Fixed urls.py in {filepath}")

def run_stabilization():
    root_dir = 'apps/sarita_agents/agents/general/sarita/coroneles'
    count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.startswith('capitan_') and file.endswith('.py'):
                fix_capitan_file(os.path.join(root, file))
                count += 1
    print(f"Fixed {count} capitanes.")

    # Fix app_labels in models
    model_files = [
        'apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/hoteles/models.py',
        'apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/restaurantes/models.py',
        'apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/transporte/models.py'
    ]
    for mf in model_files:
        if os.path.exists(mf):
            with open(mf, 'r') as f:
                c = f.read()
            c = c.replace("app_label = 'mi_negocio'", "app_label = 'prestadores'")
            with open(mf, 'w') as f:
                f.write(c)
            print(f"Fixed app_label in {mf}")

    # Fix empty urls.py
    spec_dir = 'apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados'
    for root, dirs, files in os.walk(spec_dir):
        if 'urls.py' in files:
            fix_urls(os.path.join(root, 'urls.py'))

if __name__ == "__main__":
    run_stabilization()
