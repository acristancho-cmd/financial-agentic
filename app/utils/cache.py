"""
Sistema de caché en memoria para reducir peticiones a Yahoo Finance
"""
import time
from typing import Optional, Dict, Any
from threading import Lock


class Cache:
    """Caché simple en memoria con TTL (Time To Live)"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutos por defecto
        """
        Args:
            default_ttl: Tiempo de vida por defecto en segundos
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché si existe y no ha expirado
        
        Args:
            key: Clave del caché
        
        Returns:
            Valor almacenado o None si no existe o expiró
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            expires_at = entry.get('expires_at', 0)
            
            # Si expiró, eliminar y retornar None
            if time.time() > expires_at:
                del self._cache[key]
                return None
            
            return entry.get('value')
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Almacena un valor en el caché
        
        Args:
            key: Clave del caché
            value: Valor a almacenar
            ttl: Tiempo de vida en segundos (usa default_ttl si es None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
    
    def delete(self, key: str) -> None:
        """Elimina una entrada del caché"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        """Limpia todo el caché"""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> None:
        """Elimina entradas expiradas del caché"""
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if current_time > entry.get('expires_at', 0)
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché"""
        with self._lock:
            return {
                'size': len(self._cache),
                'keys': list(self._cache.keys())
            }


# Instancia global del caché
# TTL por tipo de dato:
# - Info básica (fundamentals, dividends): 5 minutos (300s)
# - Datos históricos: 15 minutos (900s) - cambian menos frecuentemente
# - Noticias, recomendaciones: 10 minutos (600s)
cache = Cache(default_ttl=300)

