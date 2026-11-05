import re
import flet as ft

def get_device_ram_gb(page: ft.Page) -> float | None:
    """
    Detects the total RAM of the device in Gigabytes.
    On Android, it reads /proc/meminfo.
    For other platforms, it returns a mock value for testing.
    """
    # Flet's page.platform returns 'android' on Android devices.
    if page.platform != "android":
        print("--- ⚠️ Plataforma no es Android, devolviendo RAM simulada (8 GB) ---")
        return 8.0  # Mock value for testing on desktop

    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()

        # Find the MemTotal line, e.g., "MemTotal:        8065344 kB"
        match = re.search(r'MemTotal:\s+(\d+)\s+kB', meminfo)

        if match:
            total_kb = int(match.group(1))
            total_gb = total_kb / (1024 * 1024)
            print(f"--- ℹ️ RAM detectada: {total_gb:.2f} GB ---")
            return total_gb
        else:
            print("--- ❌ No se pudo encontrar MemTotal en /proc/meminfo ---")
            return None
    except FileNotFoundError:
        print("--- ❌ No se encontró el archivo /proc/meminfo ---")
        return None
    except Exception as e:
        print(f"--- ❌ Error al leer la información de RAM: {e} ---")
        return None
