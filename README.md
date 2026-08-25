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
- Node.js 20.9+ (solo desarrollo frontend; requerido por Next.js 16)
- Para uso local, conexión a Hugging Face en el primer arranque; el checkpoint se descarga automáticamente desde `caeher/mbert-sv` a `backend/models/mbert-sv/`. También se puede colocar manualmente en esa ruta.

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
| `HF_MODEL_REPO` | `caeher/mbert-sv` | Repositorio de Hugging Face para descarga inicial |
| `HF_MODEL_REVISION` | — | Rama, tag o commit del checkpoint remoto |
| `HF_TOKEN` | — | Token de Hugging Face para repositorios privados |
| `CORS_ORIGINS` | `http://localhost:3000` | Orígenes permitidos |

## Frontend (Next.js, puerto 8080 con Docker / 3000 en desarrollo)

```powershell
cd frontend
npm install
npm run dev -- --hostname 0.0.0.0
```

Abrir http://localhost:3000 en desarrollo. En Docker, abrir
http://localhost:8080; Next.js reenvía `/api` y `/health` al backend interno.

## Docker

```powershell
cd applications
docker compose up --build
```

En el primer arranque, el backend descarga los pesos de
[`caeher/mbert-sv`](https://huggingface.co/caeher/mbert-sv). Docker los conserva
en el volumen nombrado `mbert_model`, por lo que los siguientes arranques no los
vuelven a descargar. Para usar otro checkpoint, defina `HF_MODEL_REPO` (y
`HF_TOKEN` si es privado).

- **Frontend Next.js:** http://localhost:8080
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
