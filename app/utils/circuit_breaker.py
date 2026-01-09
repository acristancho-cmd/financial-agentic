"""
Circuit breaker para evitar peticiones cuando Yahoo Finance está bloqueando
"""
import time
from threading import Lock
from typing import Optional


class CircuitBreaker:
    """Circuit breaker simple para detectar bloqueos de Yahoo Finance"""
    
    def __init__(self, failure_threshold: int = 2, recovery_timeout: int = 300):
        """
        Args:
            failure_threshold: Número de fallos consecutivos antes de abrir el circuito
            recovery_timeout: Tiempo en segundos antes de intentar de nuevo
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open
        self._lock = Lock()
    
    def record_success(self):
        """Registra un éxito y cierra el circuito"""
        with self._lock:
            self.failure_count = 0
            self.state = "closed"
            self.last_failure_time = None
    
    def record_failure(self):
        """Registra un fallo"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
    
    def can_proceed(self) -> bool:
        """Verifica si se puede hacer una petición"""
        with self._lock:
            if self.state == "closed":
                return True
            
            if self.state == "open":
                # Verificar si ha pasado suficiente tiempo para intentar de nuevo
                if self.last_failure_time and (time.time() - self.last_failure_time) >= self.recovery_timeout:
                    self.state = "half_open"
                    self.failure_count = 0  # Resetear contador en half_open
                    return True
                return False
            
            # half_open: permitir un intento
            return True
    
    def get_wait_time(self) -> float:
        """Obtiene el tiempo de espera recomendado si el circuito está abierto"""
        with self._lock:
            if self.state == "open" and self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                remaining = self.recovery_timeout - elapsed
                return max(0, remaining)
            return 0.0
    
    def get_state(self) -> str:
        """Obtiene el estado actual del circuito"""
        with self._lock:
            return self.state


# Instancia global del circuit breaker
circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=300)  # 5 minutos

