import subprocess
import json
import sys
import os

def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def hybrid_search(query, mode="text", lang=None, path="."):
    """
    Motor Híbrido:
    - mode="text": Usa ripgrep (rg)
    - mode="structural": Usa ast-grep (sg)
    """
    print(f"🔍 Buscando en modo {mode}...")
    
    if mode == "structural":
        # Comando para ast-grep
        # Ejemplo: sg -p 'func $NAME($$$)' -l py
        lang_flag = f"-l {lang}" if lang else ""
        cmd = f"sg -p '{query}' {lang_flag} --json"
        stdout, stderr = run_command(cmd)
        
        try:
            results = json.loads(stdout)
            count = len(results)
            print(f"✅ Se encontraron {count} coincidencias estructurales.")
            if count > 20:
                print("⚠️ Demasiados resultados. Listando solo los primeros 5 archivos:")
                files = list(set([r['file'] for r in results]))[:5]
                for f in files: print(f"  - {f}")
            else:
                for r in results:
                    print(f"📍 {r['file']}:{r['range']['start']['line']+1}")
                    print(f"   {r['text'].strip()[:100]}...")
        except:
            if stdout: print(stdout)
            else: print(f"❌ Error o sin resultados: {stderr}")

    else:
        # Comando para ripgrep (incluido por defecto en muchos sistemas)
        # Aquí simulamos el comportamiento de grep_search
        cmd = f"rg '{query}' {path} --count"
        stdout, stderr = run_command(cmd)
        print(f"📊 Resumen de coincidencias por archivo:\n{stdout}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python hybrid_search.py <query> [mode] [lang]")
    else:
        q = sys.argv[1]
        m = sys.argv[2] if len(sys.argv) > 2 else "text"
        l = sys.argv[3] if len(sys.argv) > 3 else None
        hybrid_search(q, m, l)
