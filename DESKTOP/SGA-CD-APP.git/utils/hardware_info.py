import re
import platform
import ctypes
import flet as ft

def get_device_ram_gb(page: ft.Page = None) -> float | None:
    """
    Detecta la memoria RAM fisica real del dispositivo en Gigabytes.
    - Android: Lee /proc/meminfo del kernel Linux.
    - iOS / macOS: Invoca sysctlbyname('hw.memsize') del subsistema Darwin.
    - Windows: Invoca GlobalMemoryStatusEx via kernel32.
    - Fallback: Utiliza psutil si esta disponible, o devuelve None de forma segura.
    """
    system_name = platform.system().lower()

    # 1. Caso Android (Linux /proc/meminfo)
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        match = re.search(r'MemTotal:\s+(\d+)\s+kB', meminfo)
        if match:
            total_gb = int(match.group(1)) / (1024 * 1024)
            print(f"[Profiler Android] RAM fisica detectada: {total_gb:.2f} GB")
            return round(total_gb, 2)
    except Exception:
        pass

    # 2. Caso iOS / macOS (Darwin kernel via ctypes)
    if "darwin" in system_name or (page and getattr(page, "platform", None) == "ios"):
        try:
            libc = ctypes.CDLL(None)
            mem_size = ctypes.c_uint64()
            size = ctypes.c_size_t(ctypes.sizeof(mem_size))
            if libc.sysctlbyname(b"hw.memsize", ctypes.byref(mem_size), ctypes.byref(size), None, 0) == 0:
                total_gb = mem_size.value / (1024 ** 3)
                print(f"[Profiler Apple/iOS] RAM fisica detectada: {total_gb:.2f} GB")
                return round(total_gb, 2)
        except Exception as e:
            print(f"[Profiler Apple] Error en sysctl: {e}")

    # 3. Caso Windows (via ctypes kernel32)
    if "windows" in system_name:
        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                total_gb = stat.ullTotalPhys / (1024 ** 3)
                print(f"[Profiler Windows] RAM fisica detectada: {total_gb:.2f} GB")
                return round(total_gb, 2)
        except Exception as e:
            print(f"[Profiler Windows] Error en GlobalMemoryStatusEx: {e}")

    # 4. Fallback general con psutil
    try:
        import psutil
        total_gb = psutil.virtual_memory().total / (1024 ** 3)
        print(f"[Profiler psutil] RAM fisica detectada: {total_gb:.2f} GB")
        return round(total_gb, 2)
    except Exception:
        pass

    print("[Profiler] No se pudo determinar la RAM de forma segura. Fallback seguro activado.")
    return None
