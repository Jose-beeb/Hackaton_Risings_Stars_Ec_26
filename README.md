# Ojito al Mosquito

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

Resultados esperados: `22 passed` y `4/4 tests pasaron`

---

## Estructura del proyecto

```
OjitoAlMosquito/
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
│   │   ├── test_ire_calculator.py   # 22 unit tests del motor IRE
│   │   └── smoke_test.py            # Prueba los 4 endpoints
│   └── requirements.txt
├── frontend/
│   ├── index.html                   # Dashboard + PWA movil
│   ├── manifest.json                # PWA manifest
│   ├── css/style.css
│   └── js/app.js                    # Mapa, polling, camara, demo mode
├── data/
│   └── mock_foci_guayaquil.geojson  # ~70 focos base de Guayaquil, IRE real (LOW/MEDIUM/CRITICAL)
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
| Optimizacion de ruta de brigadas (TSP ponderado por IRE) | ✅ |
| Division automatica en multiples cuadrillas por capacidad operativa | ✅ |
| Calculo real de ahorro vs ruta ciega (km + combustible) | ✅ |
| Vista Ciudadana (lenguaje simple, arranca por defecto) / Vista Brigada (tecnico) — alternables | ✅ |
| Captura movil con camara y GPS | ✅ |
| Reportar criadero: subir foto desde galeria/archivos (ademas de camara en vivo) | ✅ |
| Polling en tiempo real (sin flicker, solo redibuja si hay cambios) | ✅ |
| Panel de impacto con datos reales de la ruta | ✅ |
| Demo Mode (doble click en logo — ruta automatica + KPIs animados) | ✅ |
| Simular Reporte en Vivo (marcador CRITICAL instantaneo para el pitch) | ✅ |
| Persistencia de reportes en GeoJSON | ✅ |
| PWA instalable en movil | ✅ |
| Layout responsive con panel informativo colapsable (boton hamburguesa, drawer en mobile) | ✅ |
| Configuracion de brigadas: tope maximo, fumigadores y tipo de transporte por brigada | ✅ |
| Jornada maxima fija (6h) por brigada con rebalanceo iterativo si el reparto inicial excede | ✅ |
| Tiempo real por brigada visible en lista (no solo tooltip del mapa) | ✅ |
| Marcar brigada como cumplida: resuelve sus focos y los saca del mapa (`POST /api/foci/resolve`) | ✅ |
| Modulo Antes/Despues: nombre de operador + foto de confirmacion al cerrar una brigada | ✅ (firma es texto simple, no criptografica) |
| Tarjeta de accion domestica instantanea segun tipo de criadero detectado | ✅ |
| Parametros operativos reales de brigadas (stops, horas, litros, velocidad) | 🔶 Parcial — ver tabla de investigacion abajo |
| Metricas financieras: costo brote dengue Ecuador, ROI a 12 meses | 🔶 Parcial — 2 de 3 citas verificadas, 2 cifras de ROI sin fuente |
| Offline-first (cola local IndexedDB + sincronizacion diferida) | 🔍 Investigado, no implementado — ver nota abajo |
| Deduplicacion espacio-temporal de reportes vecinos (10-15m / 72h) | 🔍 Investigado, no implementado — ver nota abajo |
| PITCH.md — narrativa, problema, impacto, ROI | ⚠️ Existe pero esta desactualizado (checklist y conteo de endpoints de Dia 1) — revisar antes de usarlo, no reemplaza este README |

---

## Endpoints

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/health` | Estado del servidor |
| GET | `/api/foci` | Focos activos (no resueltos) en GeoJSON |
| POST | `/api/reports` | Nuevo reporte con foto + GPS |
| POST | `/api/routes/dispatch` | Ruta optima de brigadas |
| POST | `/api/foci/resolve` | Marca focos como resueltos (operador + foto opcional) |

---

## Roadmap no implementado (investigado, con plan)

- **Offline-first**: el GPS ya funciona sin internet hoy (usa el chip del telefono, no requiere red). Lo que falta es la cola local — IndexedDB para encolar reportes cuando falla el fetch, mas un listener de reconexion (`window.addEventListener('online', ...)`) o un Service Worker con Background Sync para disparar el envio diferido. Es la feature de mayor esfuerzo del roadmap.
- **Deduplicacion espacio-temporal**: antes de crear un foco nuevo en `POST /api/reports`, buscar focos existentes a 10-15m (ya existe `haversine_distance` para esto) reportados en las ultimas 72h, y si hay uno, subirle un contador de validacion en vez de duplicar el punto. Pendiente: no hay almacenamiento de fotos secundarias hoy (la imagen se clasifica y se descarta) — adjuntar "fotos secundarias" real requeriria agregar eso primero.

---

## Base cientifica del modelo IRE

El Indice de Riesgo Entomologico esta calibrado con datos empiricos de laboratorio:

- **Rueda et al. (1990)** — Desarrollo de *Ae. aegypti* a distintas temperaturas. Dias a emergencia: 27°C→7d, 25°C→10d, 20°C→12d, 15°C→31d. A 34°C el desarrollo fue el **mas rapido** de toda su serie (6 dias) — el limite termico letal real esta cerca de **40°C** para hembras adultas, no a 34°C.
- **Tun-Lin et al. (2000)** — Umbral minimo de desarrollo: 8.3°C. Materia organica aumenta el potencial vectorial del adulto emergente.
- **Mordecai et al. (2017)** — Modelos mecanisticos de transmision: ventana optima 26-29°C, transmision posible entre 18-34°C. Corrobora que el pico de riesgo del modelo (28-30°C) es consistente con la curva de transmision, no solo con desarrollo larvario.
- **Focks & Alexander (2006, OMS/TDR)** — Encuestas de productividad pupal: tanques/cisternas grandes pueden aportar la mayor carga de produccion de adultos en una comunidad urbana. Validado contra el modelo: el `size_factor` (independiente del tipo de recipiente) ya hace que un tanque *large* supere a una llanta *small* o *medium* en el IRE.
- **Arrivillaga & Barrera (2004)** — La disponibilidad de alimento (materia organica) es un factor limitante/acelerador del desarrollo larvario, respaldando el `organic_factor` (×1.30) del modelo.

Los dos primeros papers estan disponibles en `docs/research/`. Mordecai, Focks & Alexander y Arrivillaga & Barrera se citan en `core/bio_engine/ire_calculator.py` pero sus PDFs todavia no se agregaron a la carpeta.

### Recalibracion del 3-4 sep 2026 (revision por jurado tecnico)

Una revision cruzada contra la literatura detecto que el codigo original citaba mal su propia fuente (Rueda 1990) para el limite termico superior, y que la constante base del score saturaba el rango 0-99 perdiendo resolucion en escenarios de alto riesgo. Cambios aplicados en `ire_calculator.py`:

| Parametro | Antes | Ahora | Motivo |
|---|---|---|---|
| Constante base del score | 55.0 | 40.0 | Con 55.0 el peor escenario (llanta+grande+organico) daba 134 — muy por encima del techo de 99, aplanando casos distintos al mismo valor clampeado. Con 40.0 el peor caso da 97.5, sin necesidad de saturar. |
| Colapso termico superior | Corte abrupto en 34°C → factor 0.05 | Decaimiento gradual de 30°C a 40°C | A 34°C Rueda (1990) reporto el desarrollo mas rapido de su serie; el codigo anterior interpretaba mal esa fuente. |
| Factor de humedad | Lineal estricto (`humedad% / 100`) | Rampa con piso 0.5, satura en 1.0 sobre 70% | La humedad ambiental no afecta directamente el metabolismo larvario (el agua estancada es su propio microambiente) — su efecto principal es sobre supervivencia del adulto y evaporacion del deposito. |

Una llanta con agua limpia y sin materia organica ya no satura automaticamente en CRITICAL (ahora da MEDIUM) — hace falta tamaño grande y/o materia organica visible para llegar a CRITICAL, lo cual da mas margen de diferenciacion entre reportes reales. Tests actualizados y pasando: `pytest backend/tests/test_ire_calculator.py -v` → **22 passed**.

---

## Brigadas configurables (despacho)

Desde la vista Brigada, "Despacho de Cuadrillas" permite configurar:

- **Tope maximo de brigadas** disponibles.
- **Operarios (fumigadores) por brigada**, que reduce el tiempo de atencion por parada.
- **Tipo de transporte por brigada**, mapeado a 3 tipos de brigada de campo reales:

| Modo (`transport_mode`) | Tipo de brigada | Objetivo biologico | Velocidad / min por parada (base, 2 operarios) |
|---|---|---|---|
| `foot` | Control Focal (larvicida + inspeccion) | Destruir huevos/larvas antes de emerger | 7 km/h · 17.5 min |
| `vehicle_walk_attack` | Rociado Residual (mochila motorizada 14-15L) | Eliminar adultos posados intradomicilio | 5 km/h · 35 min |
| `vehicle_spray` | Fumigacion Espacial (nebulizacion termica vehicular) | Tumbar poblacion adulta en vuelo, sin paradas por predio | 10 km/h · 2 min |

**Regla de negocio: jornada maxima fija de `MAX_HOURS_PER_BRIGADE = 6.0h`** por brigada (`tiempo_traslado + tiempo_atencion <= 360 min`).

**Escalado del tiempo de atencion por cantidad de operarios** (cada modo mantiene su propia base de la tabla de arriba, escalada por la misma tabla relativa):

| Operarios | Minutos/parada (base 20, modo de referencia) |
|---|---|
| 1 | 30 |
| 2 | 20 (base) |
| 3 | 13 |
| 4 | 10 |
| 5+ | `20 * (2/operarios)^0.75`, piso de 8 min |

Formula completa en `_effective_minutes_per_stop()`: el piso de 8 min se aplica ANTES de escalar por modo (protege el numero de referencia), no despues — si no, "vehicle_spray" (diseñado para casi no tener tiempo de parada) perderia su sentido.

**Reparto de focos proporcional a la capacidad** de cada brigada (metodo de Hamilton: minimo 1 foco garantizado, el resto segun cuantos focos/dia rendiria cada una) + **rebalanceo iterativo**: si una brigada queda con mas trabajo real del que le entra en sus 6h (el reparto inicial no conoce el traslado real hasta armar la ruta), se prueba mover cualquiera de sus focos hacia la brigada donde mas alivie el exceso sin hacer que la otra tambien se pase — se repite hasta que nadie exceda o ya no haya un movimiento valido. Cuando esto ultimo pasa (ej. muy pocas brigadas para focos muy dispersos), la brigada queda marcada con `excede_jornada: true` en vez de ocultar el problema. No es una solucion exacta de bin-packing (no vuelve a correr TSP dentro del chunk movido) — para eso haria falta OR-Tools u otro solver de VRP, fuera de alcance para el hackathon.

Salida por brigada (`POST /api/routes/dispatch` → `brigades[]`): `brigade_id`, `operarios_asignados`, `focos_atendidos_count`, `tiempo_total_minutos`, `tiempo_atencion_minutos`, `tiempo_traslado_minutos`, `excede_jornada`, `secuencia_paradas` (orden de visita), ademas de los campos ya existentes (`distance_km`, `pesticide_liters`, `route_geometry`).

Implementado en `core/logistics/route_optimizer.py` (`TRANSPORT_MODES`, `_effective_minutes_per_stop`, `_split_into_brigades`).

**Procedencia de estos numeros (no todos tienen el mismo respaldo):**
- `foot`: 15-20 min/predio citado por el equipo a un manual de procesos del MSP Ecuador — **titulo y año exactos no verificados de forma independiente** (se encontraron manuales reales de vigilancia epidemiologica del MSP, pero de 2013 y con otro nombre). La velocidad 6-8 km/h se usa explicitamente como *parametro de ingenieria* (desplazamiento urbano/peatonal mixto), no como cita academica.
- `vehicle_walk_attack` y la tabla de escalado por operarios: **estimacion interna del equipo**, derivada del rango informado de 8-10 viviendas/dia, sin cita primaria.
- `vehicle_spray`: rango 8-12 km/h reportado para brigadas de fumigacion espacial continua.
- `MAX_HOURS_PER_BRIGADE=6.0`: regla de negocio explicita del equipo, misma fuente MSP no verificada de forma independiente.

---

## Metricas financieras para el pitch

Verificacion contra fuente primaria (no cite nada de esta lista sin leer esta tabla primero):

| Metrica | Cita propuesta | Estado |
|---|---|---|
| Dias de perdida laboral/escolar por dengue (5.5 - 9.9 dias) | Suaya et al. (2009), *AJTMH* 80(5):696-701 | ✅ **Confirmado** — 5.6 dias escolares / 9.9 dias laborales para casos hospitalizados |
| Costo por paciente hospitalizado ($400-1000) vs ambulatorio ($50-90) | "Shepard, Undurraga & Halasa (2013), *AJTMH* 88(4):679-684" | ❌ **Esa cita no existe** (verificado dos veces). El Shepard 2013 real es de Sudeste Asiatico. El paper real de Americas es **Shepard, Coudeville, Halasa, Zambrano & Dayan (2011), *AJTMH* 84:200-207** (~$2.1B/año regional) — falta confirmar las cifras de $/paciente ahi antes de citarlas |
| Ahorro en costos operativos por control focalizado vs reactivo (30-45% / 35-40%, segun el mensaje) | Baly, Toledo, Boelaert et al. (2007), *Trans R Soc Trop Med Hyg* 101(6):578-586 | ⚠️ **Paper real, cifra incorrecta.** Lo que reporta de verdad: **13%** de reduccion en costos recurrentes (2001-02) y **~19%** en el seguimiento a 5 años (2004: $29.8 vs $36.7 USD/hab/año). Usar ~15-20%, no 30-45% |
| $2 USD por criadero intervenido (abatizacion) | — | 🏷️ **Estimacion interna del equipo, sin fuente** — declarar asi explicitamente en el pitch, no presentar como dato de un paper |
| ROI 1:200 (cada $1 invertido evita $200 en costos futuros) | — | 🏷️ **Estimacion interna del equipo, sin fuente** — mismo tratamiento que la anterior |

---

## Contribuir al proyecto

**Regla de equipo: cada cambio que hagas, actualiza el README.**

Esto nos ahorra tiempo al preparar el pitch — si el README está al día, el resumen ejecutivo ya está listo.

### Qué actualizar según lo que hiciste

| Tipo de cambio | Qué tocar en el README |
|---|---|
| Nueva feature | Agregar fila en tabla **Funcionalidades** con ✅ |
| Nuevo endpoint | Agregar fila en tabla **Endpoints** |
| Cambio en el modelo IRE | Actualizar sección **Base científica** |
| Bug fix importante | No es necesario (va en el commit message) |

### Flujo de trabajo con ramas

```powershell
# Siempre partir de main actualizado
git checkout main
git pull origin main
git checkout -b feat/tu-area   # ej: feat/bio-engine, feat/gis-logistics

# Trabajar, commitear con conventional commits
git commit -m "feat(bio): descripcion del cambio"

# Subir y abrir Pull Request a main
git push -u origin feat/tu-area
```

**Ramas sugeridas por rol:**
- `feat/bio-engine` — Biotecnología (modelo IRE, papers)
- `feat/gis-logistics` — Mecatrónica (rutas, optimización)
- `feat/backend-api` — Software Backend
- `feat/frontend-dashboard` — Software Frontend
