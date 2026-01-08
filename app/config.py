"""
Configuración centralizada de la aplicación
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Información de la API
    APP_NAME: str = "Super Agente Financiero API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API especializada en consultas financieras usando yfinance"
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Configuración de yfinance
    DEFAULT_CURRENCY: str = "COP"
    DEFAULT_COUNTRY_SUFFIX: str = ".CL"
    MAX_TICKER_LENGTH_WITHOUT_SUFFIX: int = 5
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


# Instancia global de configuración
settings = Settings()

