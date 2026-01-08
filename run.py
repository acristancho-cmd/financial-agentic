"""
Script de inicio rápido para desarrollo
Ejecuta el servidor FastAPI con configuración de desarrollo
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )

