import os
import sys

def normalize_path(path):
    """Convierte cualquier ruta en una ruta absoluta de Windows limpia."""
    try:
        abs_path = os.path.abspath(path)
        print(abs_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        normalize_path(sys.argv[1])
    else:
        print(os.getcwd())
