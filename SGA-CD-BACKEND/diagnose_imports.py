import os
import importlib
import traceback
from dotenv import load_dotenv

# Load environment variables first
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print("--- .env file loaded for diagnosis ---")

def find_python_files(start_path):
    """Find all .py files recursively."""
    for root, _, files in os.walk(start_path):
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)

def get_module_name(file_path, base_path):
    """Convert a file path to a Python module path."""
    relative_path = os.path.relpath(file_path, base_path)
    module_path = os.path.splitext(relative_path)[0]
    return module_path.replace(os.sep, '.')

def diagnose_all_imports():
    """Attempt to import all modules in the 'app' directory and report errors."""
    print("--- Starting Import Diagnosis ---")
    base_dir = os.path.dirname(__file__)
    app_dir = os.path.join(base_dir, "app")
    errors = []

    py_files = sorted(list(find_python_files(app_dir)))
    print(f"Found {len(py_files)} Python files to check.")

    for file_path in py_files:
        module_name = get_module_name(file_path, base_dir)
        if "__init__" in module_name and module_name.endswith(".__init__"):
            module_name = module_name.replace(".__init__", "")

        print(f"Testing import for: {module_name} (from {file_path})")
        try:
            importlib.import_module(module_name)
            print(f"  -> SUCCESS")
        except Exception as e:
            error_info = {
                "module": module_name,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            errors.append(error_info)
            print(f"  -> FAILED: {type(e).__name__}: {e}")

    print("\n--- Diagnosis Complete ---")
    if not errors:
        print("✅ No import errors found!")
    else:
        print(f"🔥 Found {len(errors)} module(s) with import errors:")
        for i, error in enumerate(errors, 1):
            print(f"\n--- Error #{i} in module: {error['module']} ---")
            print(f"  Type: {error['error_type']}")
            print(f"  Message: {error['error_message']}")
            # print(f"  Traceback:\n{error['traceback']}") # Optional: for more detail

    return not errors

if __name__ == "__main__":
    # We need to run this with the correct PYTHONPATH
    # Example: cd SGA-CD-FASTAPI-BACKEND && PYTHONPATH=. python diagnose_imports.py
    is_successful = diagnose_all_imports()
    if is_successful:
        print("\nSuggestion: The application seems to be importable. Try starting the server now.")
    else:
        print("\nSuggestion: Please fix the import errors listed above.")
