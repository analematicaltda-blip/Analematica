import os
import subprocess
import glob

def validate():
    files = sorted(glob.glob('sarita_db/**/*.sql', recursive=True))
    log_path = 'sarita_db/80_testing/sql_syntax_validation.log'
    with open(log_path, 'w') as log:
        for f in files:
            print(f"Validating: {f}")
            # Use sqlfluff to validate syntax
            res = subprocess.run(['sqlfluff', 'parse', f, '--dialect', 'postgres'], capture_output=True, text=True)
            if res.returncode != 0:
                log.write(f"FAIL: {f}\n{res.stdout}\n{res.stderr}\n")
            else:
                log.write(f"PASS: {f}\n")
    print(f"Validation complete. See {log_path}")

if __name__ == "__main__":
    validate()
