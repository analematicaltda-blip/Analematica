import time
import logging
from functools import wraps
from django.db import connection, OperationalError

logger = logging.getLogger(__name__)

def db_retry(max_retries=3, delay=1):
    """
    Fase 8: Resiliencia Operativa.
    Decorador para reintentar operaciones de base de datos en caso de fallos transitorios
    (ej: deadlock, pérdida de conexión momentánea).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"DB Retry: Fallo definitivo tras {max_retries} intentos. Error: {str(e)}")
                        raise

                    wait = delay * (2 ** (retries - 1)) # Backoff exponencial
                    logger.warning(f"DB Retry: Fallo transitorio detectado ({str(e)}). Reintentando {retries}/{max_retries} en {wait}s...")
                    time.sleep(wait)

                    # Intentar resetear la conexión si es un error de conexión
                    if "closed" in str(e).lower() or "connection" in str(e).lower():
                        connection.close()
            return func(*args, **kwargs)
        return wrapper
    return decorator
