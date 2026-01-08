# Super Agente Financiero API

Backend especializado en consultas financieras usando la librería `yfinance`. Proporciona endpoints para consultar información financiera de acciones.

## 🏗️ Arquitectura

El proyecto está estructurado de manera modular y escalable:

```
super_agente_financiero/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── config.py               # Configuración centralizada
│   ├── api/                    # Endpoints de la API
│   │   ├── v1/
│   │   │   ├── router.py      # Router principal v1
│   │   │   └── endpoints/
│   │   │       └── dividends.py  # Endpoint de dividendos
│   ├── services/               # Lógica de negocio
│   │   └── yfinance_service.py
│   ├── models/                 # Schemas y modelos Pydantic
│   │   └── dividend.py
│   └── utils/                  # Utilidades
│       └── ticker_formatter.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Principios de diseño

- **Separación de responsabilidades**: Cada capa tiene una responsabilidad específica
- **Modularidad**: Cada funcionalidad está aislada en su propio módulo
- **Escalabilidad**: Fácil agregar nuevas funcionalidades sin afectar las existentes
- **Versionado de API**: Estructura preparada para múltiples versiones de API

## 🚀 Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

Para ejecutar el servidor en modo desarrollo:

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

Para producción:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentación

Una vez que el servidor esté corriendo, puedes acceder a:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🔌 Endpoints

### GET `/api/v1/dividends`

Consulta información de dividendos para uno o múltiples tickers.

#### Parámetros de consulta:

- `ticker` (opcional): Un solo ticker a consultar
- `tickers` (opcional): Múltiples tickers separados por comas

**Nota**: Debes proporcionar al menos uno de los dos parámetros.

#### Ejemplos:

**Consulta de un solo ticker:**
```
GET /api/v1/dividends?ticker=AAPL
```

**Consulta de múltiples tickers:**
```
GET /api/v1/dividends?tickers=AAPL,TSLA,ECOPETROL
```

**También puedes combinar ambos parámetros:**
```
GET /api/v1/dividends?ticker=AAPL&tickers=TSLA,ECOPETROL
```

#### Respuesta:

```json
[
  {
    "ticker": "AAPL",
    "dividend_yield": 0.5,
    "payout_ratio": 15.2,
    "dividend_rate": 0.96,
    "last_dividend_value": 0.24,
    "currency": "USD",
    "status": "success"
  },
  {
    "ticker": "TSLA",
    "dividend_yield": 0.0,
    "payout_ratio": 0.0,
    "dividend_rate": 0.0,
    "last_dividend_value": 0.0,
    "currency": "USD",
    "status": "success"
  }
]
```

### GET `/health`

Endpoint de salud para verificar que la API está funcionando.

### GET `/`

Endpoint raíz con información de la API y lista de endpoints disponibles.

## 🔧 Configuración

La configuración se encuentra en `app/config.py` y puede ser sobrescrita usando variables de entorno en un archivo `.env`:

```env
APP_NAME=Super Agente Financiero API
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
DEBUG=False
DEFAULT_CURRENCY=COP
DEFAULT_COUNTRY_SUFFIX=.CL
MAX_TICKER_LENGTH_WITHOUT_SUFFIX=5
```

## 📝 Formateo de Tickers

El sistema automáticamente formatea los tickers colombianos agregando el sufijo `.CL` cuando:
- El ticker no tiene un sufijo existente (como `.CL`, `.US`, etc.)
- El ticker tiene 5 caracteres o menos

Ejemplos:
- `ECOPETROL` → `ECOPETROL.CL`
- `BANCOLOMBIA` → `BANCOLOMBIA.CL`
- `AAPL` → `AAPL` (no se modifica, es una acción global)
- `TSLA.US` → `TSLA.US` (ya tiene sufijo, no se modifica)

## ➕ Agregar Nuevas Funcionalidades

Para agregar una nueva funcionalidad:

1. **Crear el modelo** en `app/models/`:
   ```python
   # app/models/nueva_funcionalidad.py
   from pydantic import BaseModel
   ```

2. **Crear el servicio** en `app/services/`:
   ```python
   # app/services/nueva_funcionalidad_service.py
   class NuevaFuncionalidadService:
       @staticmethod
       def metodo():
           pass
   ```

3. **Crear el endpoint** en `app/api/v1/endpoints/`:
   ```python
   # app/api/v1/endpoints/nueva_funcionalidad.py
   from fastapi import APIRouter
   router = APIRouter(prefix="/nueva-funcionalidad", tags=["nueva-funcionalidad"])
   
   @router.get("")
   async def endpoint():
       pass
   ```

4. **Registrar el router** en `app/api/v1/router.py`:
   ```python
   from app.api.v1.endpoints import nueva_funcionalidad
   api_router.include_router(nueva_funcionalidad.router)
   ```

## 🛡️ Manejo de Errores

Si un ticker no puede ser consultado, la respuesta incluirá un objeto con `status: "error"` y un campo `error` con el mensaje de error. Los demás tickers se procesarán normalmente.

## 🧪 Testing

Para ejecutar tests (cuando se implementen):
```bash
pytest
```

## 📦 Tecnologías

- **FastAPI**: Framework web moderno y rápido para construir APIs
- **yfinance**: Librería para descargar datos financieros de Yahoo Finance
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Pydantic**: Validación de datos y configuración

## 📄 Licencia

Este proyecto es privado.
