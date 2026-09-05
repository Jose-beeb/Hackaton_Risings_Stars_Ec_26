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
| Validacion visual Antes/Despues con Gemini al resolver un foco (contrasta la foto original del reporte contra la foto de cierre; si no hay foto original — caso comun en los focos semilla — evalua solo la de cierre) | ✅ |
| Subida de fotos por `multipart/form-data` (no Base64 en JSON) + compresion en Canvas a maximo 1280px de lado antes de enviar | ✅ |
| Reporte ciudadano asincrono: el modal se cierra al instante al enviar (no bloquea 2-4s esperando a Gemini), tarjeta flotante con badge de riesgo, IRE, consejo de accion y atajo para centrar el mapa | ✅ |
| Tarjeta de accion domestica instantanea segun tipo de criadero detectado | ✅ |
| Parametros operativos reales de brigadas (stops, horas, litros, velocidad) | 🔶 Parcial — ver tabla de investigacion abajo |
| Metricas financieras: costo brote dengue Ecuador, ROI a 12 meses | 🔶 Parcial — 2 de 3 citas verificadas, 2 cifras de ROI sin fuente |
| Offline-first (cola local IndexedDB + sincronizacion diferida) | 🔍 Investigado, no implementado — ver nota abajo |
| Deduplicacion espacio-temporal de reportes vecinos (10-15m / 72h) | 🔍 Investigado, no implementado — ver nota abajo |
| PITCH.md — narrativa, problema, impacto, ROI, guion recomendado, Q&A de jurado | ✅ Actualizado (sept 2026) contra el estado real del codigo y los docs de `research/`. Limite de tiempo confirmado en 3:00 min — usar `research/GUION_PITCH_2_30_MIN.md`, no el de 3:30 |

---

## Endpoints

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/health` | Estado del servidor |
| GET | `/api/foci` | Focos activos (no resueltos) en GeoJSON |
| POST | `/api/reports` | Nuevo reporte: `multipart/form-data` (`latitude`, `longitude`, `notes`, `photo` opcional) — no JSON con Base64 |
| POST | `/api/routes/dispatch` | Ruta optima de brigadas |
| POST | `/api/foci/resolve` | Marca focos como resueltos (operador + foto opcional); responde `resolution_validations[]` con el veredicto de Gemini por foco |

---

## Estado de la auditoria tecnica (docs/AUDITORIA_Y_MEJORAS.md, sept 2026)

La auditoria del equipo lista 8 mejoras priorizadas. Estado real verificado contra el codigo (no contra lo que dice cada commit):

| # | Mejora | Prioridad | Estado |
|---|---|---|---|
| 1 | Multipart + compresion en Canvas | Alta | ✅ Hecho |
| 2 | Migrar persistencia a SQLite/TinyDB/PostGIS | Alta | ❌ Pendiente — sigue en `.geojson` plano con `threading.Lock` |
| 3 | Selector de Centro Operativo / Depot dinamico en el mapa | Alta | ❌ Pendiente — `depot_coordinates` sigue hardcodeado en `frontend/js/app.js:777` (`[-79.895, -2.18]`), no hay marcador arrastrable ni boton de GPS |
| 4 | Polling adaptativo + PWA offline (IndexedDB/Service Worker) | Alta | ❌ Pendiente |
| 5 | Optimizacion del modelo de vision (prompt mas estricto + resize 1024px) | **Critica** | ✅ Hecho — ver nota abajo sobre el modelo real usado |
| 6 | Flujo asincrono no bloqueante (cerrar modal al instante + toast flotante con el resultado) | Alta | ✅ Hecho — `sendReport()` cierra el modal al instante, `showFloatingReportCard()` en `app.js` |
| 7 | Evitar focos simulados en cuerpos de agua (Rio Guayas / Estero) | Alta | ✅ Hecho (`core/logistics/water_bodies.py`) |
| 8 | Exportar rutas a Google Maps (a pie / vehiculo) | Alta | ✅ Hecho (`buildGoogleMapsUrl()` en `app.js`) |

**Correccion sobre una afirmacion previa de esta sesion:** en un chequeo anterior se dijo que el punto 3 (depot dinamico) ya estaba resuelto por una coincidencia de `grep` sobre la palabra "geolocation" — esa coincidencia era del GPS del reporte ciudadano, no del depot de despacho. Verificado de nuevo leyendo el codigo: **sigue pendiente**.

Extra ya implementado que la revision de auditoria actual no lista (viene de una version anterior del documento): **validacion visual Antes/Despues con Gemini** en `POST /api/foci/resolve` (ver tabla de Funcionalidades y seccion "Cumplimiento de rutas").

**Nota sobre el modelo de vision real (punto 5):** la auditoria recomendaba migrar a `gemini-2.5-flash`, pero al probarlo la API respondio `404 — no longer available to new users` y sugirio `gemini-3.6-flash` como reemplazo directo. Se uso ese (verificado con la API key del proyecto). Benchmark contra las 8 imagenes de `test-images/` (el mismo set que uso el equipo para diagnosticar el modelo viejo): **8/8 clasificadas correctamente**, incluyendo los dos casos que antes fallaban (`canal_techo_inundado.jpg` ya no se confunde con tanque, `alcantarilla_bien.jpg` ya no genera falsa alarma). Advertencia honesta: la latencia por imagen vario mucho en la prueba (5s a 113s) — no correlaciona con el tamaño del archivo, parece variabilidad propia del modelo. El flujo asincrono del punto 6 amortigua esto (el usuario no se queda mirando una pantalla congelada), pero vale la pena remedirlo antes del pitch en vivo.

Snippets de referencia listos para copiar/pegar para los puntos 3, 6, 7 y 8: `docs/PUNTOS_EXTRAS_IMPLEMENTACION.md`.

---

## Preparacion del pitch

Documentos con contenido para el pitch, mas nuevos y especificos que `PITCH.md` (que el equipo ya marco como desactualizado):

| Documento | Contenido |
|---|---|
| `research/GUION_PITCH_3_30_MIN.md` | Guion completo minuto a minuto para el formato largo (3:30 min) |
| `research/GUION_PITCH_2_30_MIN.md` | Guion recortado para el limite duro del concurso (2:30 min objetivo, 3:00 min tope) |
| `research/ESTRATEGIA_Y_BLINDAJE_JURADO.md` | Benchmarking vs. soluciones existentes (apps ciudadanas, IoT, control tradicional), FODA tecnico, y respuestas preparadas para preguntas dificiles del jurado |
| `research/Jose.md` | Investigacion ampliada con bibliografia de 65 fuentes APA: epidemiologia Ecuador 2019-2026, resistencia genetica del vector, modelos bio-matematicos, marco legal COOTAD/LOS y via de contratacion SERCOP, costos reales de brigadas. Dos citas puntuales sin confirmar de forma independiente — ver `PITCH.md` |
| `INFORME_PROPUESTA.md` | Informe formal de la propuesta (problema, solucion, impacto, estado de avance, recursos, plan de implementacion) — mismo nivel de verificacion de cifras que `PITCH.md` |

Antes de citar cualquier cifra financiera en el pitch, revisar la tabla **Metricas financieras para el pitch** de este README — dos de las citas propuestas por el equipo no resistieron la verificacion (una cita no existe, otra cambia el numero real en 2-3x).

---

## Roadmap no implementado (investigado, con plan)

- **Offline-first**: el GPS ya funciona sin internet hoy (usa el chip del telefono, no requiere red). Lo que falta es la cola local — IndexedDB para encolar reportes cuando falla el fetch, mas un listener de reconexion (`window.addEventListener('online', ...)`) o un Service Worker con Background Sync para disparar el envio diferido. Es la feature de mayor esfuerzo del roadmap.
- **Deduplicacion espacio-temporal**: antes de crear un foco nuevo en `POST /api/reports`, buscar focos existentes a 10-15m (ya existe `haversine_distance` para esto) reportados en las ultimas 72h, y si hay uno, subirle un contador de validacion en vez de duplicar el punto. Pendiente: la imagen de un reporte ciudadano se clasifica y se descarta, no se guarda — adjuntar "fotos secundarias" real requeriria agregar eso primero. (Distinto del `after_photo_base64` de "Cumplimiento de rutas" — ese sí persiste, pero solo para la foto de confirmacion de la brigada, no para reportes ciudadanos).

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

## Criterio de seleccion de rutas

`optimize_brigade_route()` decide **que focos visitar y en que orden** con una heuristica Nearest Neighbor ponderada por riesgo, no solo por cercania:

```
score = distancia_km / (ire_score / 30.0)
```

Se elige en cada paso el foco con **menor score** (mas cerca gana, pero un IRE mas alto "acerca" al foco artificialmente). Con `ire_score = 30` el divisor da 1 y el criterio es distancia pura; un foco con `ire_score = 90` (3x) compite en igualdad de condiciones con uno 3 veces mas cerca pero de bajo riesgo — en la practica, la ruta prioriza los focos criticos aunque implique desviarse un poco, en vez de barrer ciegamente por cercania.

Reglas adicionales:
- Los focos con `status: RESOLVED` (ya atendidos, ver "Cumplimiento de rutas" abajo) quedan excluidos de los candidatos — nunca se les vuelve a asignar una brigada.
- `max_foci` (parametro del request) tope la cantidad de paradas de la ruta completa; despues de eso, el reparto entre brigadas es el que se explica abajo.
- Es una heuristica greedy de vecino mas cercano, no un TSP exacto — prioriza velocidad de calculo y explicabilidad (cada decision se puede justificar con un numero) sobre encontrar la ruta matematicamente optima, razonable para el tamaño de datos de un piloto municipal.

Implementado en `core/logistics/route_optimizer.py`, dentro de `optimize_brigade_route()`.

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

## Cumplimiento de rutas (modulo Antes/Despues)

Cierra el ciclo operativo: no alcanza con *ver* el problema, hay que poder auditar que la brigada fue de verdad al lugar. Desde la lista de brigadas del panel de despacho, cada una tiene un boton **"✓ Cumplida"** que abre un modal pidiendo:

- **Nombre del operador** (texto libre — ver aclaracion abajo).
- **Foto de confirmacion** (opcional, `capture="environment"` abre la camara del celular directo si el navegador lo soporta, o el selector de archivos).

Al confirmar, se llama a `POST /api/foci/resolve` con los `foco_ids` de esa brigada especifica (los que trajo en `secuencia_paradas`, ver seccion de arriba). El backend:

1. Marca cada foco con `status: "RESOLVED"`, `resolved_at` (timestamp UTC), `resolved_by_brigade`, y si vinieron, `resolved_by_operator` y `after_photo_base64`. **No borra el registro** — queda como historial auditable.
2. `GET /api/foci` deja de devolver esos focos — desaparecen del mapa y de la lista de focos criticos.
3. Ese foco queda excluido de cualquier despacho futuro (ver "Criterio de seleccion de rutas" arriba).

En el frontend, confirmar tambien saca la linea de esa brigada especifica del mapa (no las otras) y refresca los KPIs.

**Aclaracion importante para el pitch**: "operator_name" es un campo de texto simple con timestamp del servidor — **no es una firma digital criptografica**. Si el jurado pregunta por trazabilidad legal/no-repudio, hay que ser honestos con esa distincion; la foto + nombre + timestamp sirven como evidencia operativa razonable para un MVP, no como firma electronica certificada.

Implementado en `backend/app/main.py` (`ResolveFociRequest`, `resolve_foci()`) y `frontend/js/app.js` (`completeBrigade()`, `confirmCompleteBrigade()`).

---

## Sugerencias instantaneas al ciudadano

Cierra el bucle comunitario: la persona que reporta recibe algo que puede hacer YA con sus manos, sin esperar a que llegue la brigada — reduce la tasa de abandono de herramientas de ciencia ciudadana (si reportás y no sentís una respuesta util, no volves a usar la app). En cuanto la IA clasifica el tipo de deposito, se muestra una tarjeta de accion fisica:

| `container_type` detectado | Consejo mostrado |
|---|---|
| `tire` (llanta) | Perforá la llanta para que no vuelva a acumular agua, o guardala bajo techo seco. |
| `open_tank` (tanque/cisterna) | Cepillá las paredes internas (los huevos se pegan al borde seco) y tapá herméticamente con malla o lona. |
| `bucket` (balde) | Volteá el balde o vacialo por completo. Si no lo usás, guardalo bajo techo. |
| `flowerpot` (maceta) | Vaciá el plato bajo la maceta cada 3 días, o rellenalo con arena para que no junte agua. |
| `clogged_drain` (canaleta) | Sacá las hojas y la basura de la canaleta para que el agua no se estanque. |
| `litter_plastic` (plastico suelto) | Juntá y desechá botellas, vasos o bolsas que puedan acumular agua de lluvia. |
| `puddle` (charco natural) | Rellená el hueco con tierra o mejorá el drenaje de esa zona del patio. |
| `other` | Eliminá o cubrí el recipiente para que no vuelva a acumular agua. |
| `none` (sin criadero detectado) | No se detectó un criadero en esta foto. Igual, revisá el patio cada semana buscando agua estancada. |

Se muestra en ambas vistas (Ciudadana y Brigada), inmediatamente despues del resultado del reporte — sin esperar el veredicto de la brigada. Consejos validados con criterio entomologico basico (los huevos de *Aedes* se adhieren a la pared seca del recipiente, por eso "cepillar" y no solo "vaciar").

Implementado en `frontend/js/app.js` (`HOME_ACTION_TIPS`, dentro de `showReportResult()`).

---

## Metricas financieras para el pitch

Verificacion contra fuente primaria (no cite nada de esta lista sin leer esta tabla primero):

| Metrica | Cita propuesta | Estado |
|---|---|---|
| Dias de perdida laboral/escolar por dengue (5.5 - 9.9 dias) | Suaya et al. (2009), *AJTMH* 80(5):846-855 | ✅ **Confirmado** — 5.6 dias escolares / 9.9 dias laborales para casos hospitalizados |
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
