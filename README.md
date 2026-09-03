# MosquitoAlert
**_Ojo al mosquito_**

Sistema de deteccion de criaderos de mosquitos y optimizacion de brigadas sanitarias.
IEEE Rising Stars 2026 — Track 2: Public Health

---

## Que es este proyecto

Plataforma web y movil para deteccion temprana de criaderos de *Aedes aegypti*.
El ciudadano toma una foto, la IA la clasifica con Gemini Vision, calcula el Indice de Riesgo Entomologico (IRE) calibrado con literatura cientifica peer-reviewed, y optimiza la ruta de brigadas sanitarias.

**Stack:** FastAPI + Vanilla JS + Leaflet + Google Gemini Flash + Open-Meteo

---

## Empezar rapido

> Nuevo en el proyecto? Lee **[SETUP.md](SETUP.md)** — tiene todo lo que necesitas.

```powershell
# 1. Clonar
git clone https://github.com/Jose-beeb/Hackaton_Risings_Stars_Ec_26.git
cd Hackaton_Risings_Stars_Ec_26

# 2. Entorno virtual
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt

# 3. Configurar API key (copiar y editar)
copy .env.example .env

# 4. Levantar backend
py -m uvicorn backend.app.main:app --reload --port 8000

# 5. Levantar frontend (otra terminal)
cd frontend
py -m http.server 3000
```

Abrir en el navegador: **http://localhost:3000**

---

## Verificar que todo funciona

```powershell
# Tests unitarios del motor IRE (no requiere servidor)
pytest backend/tests/test_ire_calculator.py -v

# Smoke test de endpoints (requiere backend corriendo)
py backend/tests/smoke_test.py
```

Resultados esperados: `20 passed` y `4/4 tests pasaron`

---

## Estructura del proyecto

```
MosquitoAlert/
├── core/
│   ├── bio_engine/
│   │   ├── ire_calculator.py        # Motor IRE calibrado (Rueda 1990, Tun-Lin 2000)
│   │   └── vision_prompts.py        # Prompts entomologicos para Gemini
│   └── logistics/
│       ├── route_optimizer.py       # Optimizador TSP de rutas de brigada
│       └── mock_foci_generator.py   # Generador de datos mock con IRE real
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI: endpoints + persistencia GeoJSON
│   │   ├── config.py                # Variables de entorno (.env)
│   │   └── services/
│   │       ├── vision_service.py    # Gemini Flash: clasificacion de imagenes
│   │       └── climate_service.py  # Open-Meteo: clima en tiempo real
│   ├── tests/
│   │   ├── test_ire_calculator.py   # 20 unit tests del motor IRE
│   │   └── smoke_test.py            # Prueba los 4 endpoints
│   └── requirements.txt
├── frontend/
│   ├── index.html                   # Dashboard + PWA movil
│   ├── manifest.json                # PWA manifest
│   ├── css/style.css
│   └── js/app.js                    # Mapa, polling, camara, demo mode
├── data/
│   └── mock_foci_guayaquil.geojson  # 40 focos (10 criticos, 15 medios, 15 bajos)
├── docs/
│   └── research/                    # Papers cientificos del modelo IRE
│       ├── rueda1990.pdf            # Rueda et al. (1990) — desarrollo Ae. aegypti
│       └── 10.1046@j.1365-2915.2000.00207.x.pdf  # Tun-Lin et al. (2000)
├── SETUP.md                         # Guia de instalacion paso a paso
├── IMPLEMENTATION_PLAN.md           # Checklist de tareas con estado
└── .env.example                     # Plantilla de variables de entorno
```

---

## Funcionalidades

| Feature | Estado |
|---|---|
| Clasificacion de imagenes con Gemini Flash | ✅ |
| Motor IRE calibrado con literatura peer-reviewed | ✅ |
| Clima en tiempo real (Open-Meteo) | ✅ |
| Mapa de focos con heatmap (Leaflet) | ✅ |
| Optimizacion de ruta de brigadas (TSP) | ✅ |
| Vista Ciudadana / Vista Brigada | ✅ |
| Captura movil con camara y GPS | ✅ |
| Polling en tiempo real (cada 4s) | ✅ |
| Panel de impacto cuantificado | ✅ |
| Demo Mode (doble click en logo) | ✅ |
| Persistencia de reportes en GeoJSON | ✅ |
| PWA instalable en movil | ✅ |

---

## Endpoints

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/health` | Estado del servidor |
| GET | `/api/foci` | Todos los focos en GeoJSON |
| POST | `/api/reports` | Nuevo reporte con foto + GPS |
| POST | `/api/routes/dispatch` | Ruta optima de brigadas |

---

## Base cientifica del modelo IRE

El Indice de Riesgo Entomologico esta calibrado con datos empiricos de laboratorio:

- **Rueda et al. (1990)** — Desarrollo de *Ae. aegypti* a 6 temperaturas (15-34°C). Dias a emergencia: 27°C→7d, 25°C→10d, 20°C→12d, 15°C→31d.
- **Tun-Lin et al. (2000)** — Umbral minimo de desarrollo: 8.3°C. Materia organica aumenta el potencial vectorial del adulto emergente.

Papers disponibles en `docs/research/`.
