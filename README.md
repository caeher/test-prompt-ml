# Apps de inferencia

Repositorio autónomo: API FastAPI + interfaz web (React) para clasificar toxicidad en 4 clases con **mBERT**.

No depende del paquete `discurso_odio` del monorepo. El código ML necesario vive en `backend/ml/`.

## Estructura

```
applications/
  backend/
    main.py, services.py, schemas.py
    ml/              # inferencia, normalización, LIME
    config/          # settings.yaml
    models/mbert-sv/ # checkpoint (no en Git)
    metrics/         # JSON de referencia para /api/metrics
  frontend/
  docker-compose.yml
  scripts/sync_assets.ps1
```

## Requisitos

- Python 3.10+
- Node.js 18+ (solo desarrollo frontend)
- Checkpoint en `backend/models/mbert-sv/` con `model.safetensors`, `config.json`, `tokenizer.json`, `tokenizer_config.json`, `inference_contract.json`

### Sincronizar desde el monorepo padre

Si `applications/` aún vive dentro del repo principal:

```powershell
cd applications
.\scripts\sync_assets.ps1
```

## Backend (puerto 8000)

```powershell
cd backend
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu
uvicorn main:app --reload --port 8000
```

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del modelo y contrato de inferencia |
| POST | `/api/predict` | Clasificación rápida |
| POST | `/api/explain` | Explicación LIME (lenta) |
| GET | `/api/metrics` | Métricas globales de referencia |

### Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `MODEL_BACKEND` | `mbert` | Backend de inferencia |
| `MODEL_DIR` | `backend/models/mbert-sv` | Ruta al checkpoint |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes permitidos |

## Frontend (puerto 5173)

```powershell
cd frontend
npm install
npm run dev
```

Abrir http://localhost:5173. El proxy de Vite reenvía `/api` y `/health` al backend.

## Docker

```powershell
cd applications
# Asegúrese de tener backend/models/mbert-sv/ (sync_assets.ps1 o copia manual)
docker compose up --build
```

- **Frontend:** http://localhost:8080
- **API:** http://localhost:8000/docs

Variables en compose: `MODEL_DIR=/app/models/mbert-sv`, `CORS_ORIGINS=http://localhost:8080,http://localhost`

### Agregar XLM-R después

1. Copiar checkpoint a `backend/models/xlmr/`
2. En Docker/entorno: `MODEL_DIR=/app/models/xlmr` (o ruta local equivalente)
3. Opcional: perfil o segundo servicio en `docker-compose.yml`

## Contrato de inferencia

- Normalizador: `normalize_for_model` v1.1
- `max_length`: 128
- Clases: No Tóxico (0), Lenguaje Ofensivo (1), Discurso de Odio (2), Amenazas/Violencia (3)

## Tests

```powershell
cd backend
pytest tests/ -v
```
