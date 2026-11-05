import os
import re
import json

def audit_soldiers_deep():
    base_path = "backend/apps/sarita_agents/agents/general/sarita/coroneles/"
    results = []

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and "soldados" in file:
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()

                    # Regex to find classes and their methods
                    classes = re.findall(r'class (\w+)\((SoldadoN6OroV2|SoldierTemplate|SoldadoTemplate)\):', content)

                    # Split content by classes to analyze each one
                    class_blocks = re.split(r'class \w+\(', content)[1:]

                    for i, (class_name, base_class) in enumerate(classes):
                        block = class_blocks[i]

                        has_todo = "TODO" in block or "FIXME" in block
                        # Return empty or static dicts
                        is_anemic = re.search(r'return \{["\']\w+["\']: ["\']\w+["\']\}', block) is not None
                        if "status" in block and "SUCCESS" in block and len(re.findall(r'["\']', block)) < 10:
                            is_anemic = True

                        has_orm = "objects.create" in block or "save()" in block or ".objects." in block
                        has_event = "EventBus.emit" in block or "OutboxEvent" in block

                        # Check if it uses the new Oro V2 method or the old one
                        uses_atomic = "def perform_atomic_action" in block
                        uses_action = "def perform_action" in block

                        risk = "Bajo"
                        if any(kw in class_name.lower() for kw in ["nomina", "fiscal", "contable", "asiento", "pago", "credito"]):
                            risk = "Alto"
                        elif any(kw in class_name.lower() for kw in ["inventario", "stock", "comision", "lead"]):
                            risk = "Medio"

                        results.append({
                            "name": class_name,
                            "module": root.split('/')[-2],
                            "is_anemic": is_anemic,
                            "has_todo": has_todo,
                            "has_orm": has_orm,
                            "has_event": has_event,
                            "uses_atomic": uses_atomic,
                            "uses_action": uses_action,
                            "risk": risk,
                            "file": path
                        })

    # Print summary table
    print(f"{'Soldado':<40} | {'Módulo':<15} | Anémico | ORM | Event | Risk")
    print("-" * 95)
    for r in results:
        print(f"{r['name']:<40} | {r['module']:<15} | {str(r['is_anemic']):<7} | {str(r['has_orm']):<3} | {str(r['has_event']):<5} | {r['risk']}")

    return results

if __name__ == "__main__":
    audit_soldiers_deep()
