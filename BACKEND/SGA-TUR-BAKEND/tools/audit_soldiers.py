import os
import re

def audit_soldiers():
    base_path = "backend/apps/sarita_agents/agents/general/sarita/coroneles/"
    soldiers = []

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and "soldados" in file:
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()

                    # Find classes inheriting from SoldadoN6OroV2 or similar
                    classes = re.findall(r'class (\w+)\((SoldadoN6OroV2|SoldierTemplate|SoldadoTemplate)\)', content)
                    for class_name, base_class in classes:
                        has_todo = "TODO" in content or "FIXME" in content
                        has_return_zero = "return 0" in content or "return []" in content
                        has_perform_atomic = "def perform_atomic_action" in content
                        has_perform_action = "def perform_action" in content

                        soldiers.append({
                            "name": class_name,
                            "file": path,
                            "base": base_class,
                            "has_todo": has_todo,
                            "has_return_zero": has_return_zero,
                            "has_perform_atomic": has_perform_atomic,
                            "has_perform_action": has_perform_action
                        })

    print(f"{'Name':<35} | {'Base':<15} | TODO | R0 | Atomic | Action")
    print("-" * 85)
    for s in soldiers:
        print(f"{s['name']:<35} | {s['base']:<15} | {str(s['has_todo']):<4} | {str(s['has_return_zero']):<2} | {str(s['has_perform_atomic']):<6} | {str(s['has_perform_action'])}")

if __name__ == "__main__":
    audit_soldiers()
