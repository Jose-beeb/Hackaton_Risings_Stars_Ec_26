# AedesGuard
**Sistema de Inteligencia Epidemiologica y Control Vectorial Predictivo**
IEEE Rising Stars 2026 — Track 2: Public Health

---

## Que es este proyecto

Plataforma de software para deteccion temprana de criaderos de *Aedes aegypti* (dengue, zika, chikungunya).
El ciudadano toma una foto, la IA la clasifica, calcula el riesgo entomologico y optimiza la ruta de brigadas sanitarias.

---

## Configuracion inicial (hacer una vez por integrante)

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/Jose-beeb/Hackaton_Risings_Stars_Ec_26.git
cd Hackaton_Risings_Stars_Ec_26
```

### Paso 2 — Obtener la API Key de Gemini (Vision AI)

> Solo el integrante de Backend necesita la clave para correr el servidor.
> Los demas pueden trabajar sin ella — el sistema tiene fallback automatico.

1. Abrir **https://aistudio.google.com** en el navegador
2. Iniciar sesion con una cuenta Google
3. En el menu izquierdo, hacer click en **"Get API key"**
4. Click en **"Create API key in new project"**
5. Copiar la clave generada (empieza con `AIza...`)

### Paso 3 — Crear el archivo .env

En la raiz del proyecto (mismo nivel que este README), crear un archivo llamado exactamente `.env`:

```
GEMINI_API_KEY=AIza...pegar_tu_clave_aqui
ENVIRONMENT=development
PORT=8000
```

> IMPORTANTE: El archivo `.env` esta en `.gitignore`. Nunca aparecera en git.
> Nunca compartas esta clave por chat, correo o GitHub.

### Paso 4 — Instalar dependencias Python

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Mac / Linux
source venv/bin/activate

# Instalar paquetes
pip install -r backend/requirements.txt
```

### Paso 5 — Ir a tu rama de trabajo

```bash
# Biotecnologia
git checkout feat/bio-engine

# Mecatronica
git checkout feat/gis-logistics

# Backend
git checkout feat/backend-api

# Frontend
git checkout feat/frontend-dashboard
```

---

## Levantar el proyecto

### Backend

```bash
# Con el entorno virtual activado
python backend/app/main.py
```

Servidor disponible en: `http://localhost:8000`
Documentacion interactiva: `http://localhost:8000/docs`

### Frontend

```bash
# Opcion A: abrir directo en el navegador
frontend/index.html

# Opcion B: servidor local simple
python -m http.server 3000 --directory frontend
```

Abrir en el navegador: `http://localhost:3000`

### Verificar que todo funciona

```bash
# Con el backend corriendo en otra terminal
python backend/tests/smoke_test.py
```

Resultado esperado: `4/4 tests pasaron`

---

## Estructura del proyecto

```
AedesGuard/
├── core/
│   ├── bio_engine/          # Biotecnologia: formula IRE y prompts de vision
│   └── logistics/           # Mecatronica: optimizador de rutas y mock data
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI: 3 endpoints principales
│   │   ├── config.py        # Carga variables de entorno (.env)
│   │   └── services/
│   │       ├── vision_service.py    # Gemini Flash: clasificacion de imagenes
│   │       └── climate_service.py  # Open-Meteo: clima en tiempo real
│   ├── tests/
│   │   └── smoke_test.py    # Prueba los 3 endpoints
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Dashboard GIS + PWA movil
│   ├── css/style.css
│   └── js/app.js
├── data/
│   └── mock_foci_guayaquil.geojson  # 40 focos pre-generados
├── docs/
│   ├── API_CONTRACT.md      # Contrato de API (no modificar sin consenso)
│   └── GUIA_GIT_GITHUB.md   # Flujo de trabajo con git
├── IMPLEMENTATION_PLAN.md   # Checklist de tareas con estado
├── PITCH.md                 # Documento del pitch (actualizar con avances)
└── .env                     # Variables privadas (NO subir a git)
```

---

## Documentacion del equipo

| Documento | Descripcion |
|---|---|
| `IMPLEMENTATION_PLAN.md` | Checklist de tareas — marcar al completar |
| `PITCH.md` | Narrativa del pitch — actualizar con metricas reales |
| `docs/API_CONTRACT.md` | Contratos JSON de los endpoints — no modificar sin avisar |
| `docs/GUIA_GIT_GITHUB.md` | Flujo de trabajo con git para todo el equipo |

---

## Endpoints disponibles

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/health` | Estado del servidor |
| GET | `/api/foci` | Todos los focos en GeoJSON |
| POST | `/api/reports` | Nuevo reporte con foto + GPS |
| POST | `/api/routes/dispatch` | Ruta optima de brigadas |
