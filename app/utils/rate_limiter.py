"""
Rate limiter para controlar peticiones a Yahoo Finance
"""
import time
from threading import Lock
from typing import Optional
from collections import deque


class RateLimiter:
    """Rate limiter usando algoritmo de ventana deslizante"""
    
    def __init__(self, max_requests: int = 2, time_window: float = 5.0):
        """
        Args:
            max_requests: Número máximo de peticiones permitidas
            time_window: Ventana de tiempo en segundos
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self._lock = Lock()
    
    def acquire(self, wait: bool = True) -> bool:
        """
        Intenta adquirir un permiso para hacer una petición
        
        Args:
            wait: Si es True, espera hasta que haya disponibilidad
        
        Returns:
            True si se adquirió el permiso, False si no
        """
        with self._lock:
            current_time = time.time()
            
            # Eliminar peticiones fuera de la ventana de tiempo
            while self.requests and self.requests[0] < current_time - self.time_window:
                self.requests.popleft()
            
            # Si hay espacio disponible, permitir la petición
            if len(self.requests) < self.max_requests:
                self.requests.append(current_time)
                return True
            
            # Si no hay espacio y wait=False, retornar False
            if not wait:
                return False
            
            # Calcular cuánto tiempo esperar
            oldest_request = self.requests[0]
            wait_time = self.time_window - (current_time - oldest_request) + 0.1
            
            if wait_time > 0:
                time.sleep(wait_time)
                # Después de esperar, intentar de nuevo
                return self.acquire(wait=False)
            
            return False
    
    def wait_if_needed(self) -> None:
        """Espera si es necesario antes de hacer una petición"""
        self.acquire(wait=True)
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del rate limiter"""
        with self._lock:
            current_time = time.time()
            # Limpiar peticiones antiguas
            while self.requests and self.requests[0] < current_time - self.time_window:
                self.requests.popleft()
            
            return {
                'current_requests': len(self.requests),
                'max_requests': self.max_requests,
                'time_window': self.time_window,
                'available_slots': max(0, self.max_requests - len(self.requests))
            }


# Instancia global del rate limiter
# Máximo 1 petición cada 15 segundos a Yahoo Finance (muy conservador para producción)
rate_limiter = RateLimiter(max_requests=1, time_window=15.0)

