import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """
    Implementación básica de Circuit Breaker para servicios externos (Fase 6.5.3).
    """
    def __init__(self, name, failure_threshold=5, recovery_timeout=30):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = 'CLOSED' # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                    logger.info(f"Circuit Breaker {self.name} is HALF_OPEN")
                else:
                    logger.warning(f"Circuit Breaker {self.name} is OPEN. Skipping call.")
                    raise Exception(f"Service {self.name} is temporarily unavailable (Circuit Open)")

            try:
                result = func(*args, **kwargs)
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failures = 0
                    logger.info(f"Circuit Breaker {self.name} is CLOSED again")
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                if self.failures >= self.failure_threshold:
                    self.state = 'OPEN'
                    logger.error(f"Circuit Breaker {self.name} is now OPEN due to {self.failures} failures")
                raise e
        return wrapper

# Instancias compartidas para servicios críticos
taxation_cb = CircuitBreaker("TaxationService")
payment_gateway_cb = CircuitBreaker("PaymentGateway")
