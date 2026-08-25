# Frontend Next.js

Aplicación Next.js 16.3 con App Router. El frontend usa `/api` y `/health` como
rutas relativas; `next.config.mjs` las reenvía al servicio FastAPI `backend`.

```bash
npm install
npm run dev
```

Abrir http://localhost:3000 en desarrollo. En Docker Compose se publica en
http://localhost:8080.
