# Guía de Trabajo en Equipo con Antigravity — AedesGuard

Esta guía explica a cada integrante del equipo cómo utilizar **Antigravity** de forma coordinada, maximizando la velocidad de desarrollo con agentes de IA y evitando colisiones de código.

---

## 1. La Regla de Oro: "Tu Carpeta es tu Dominio"

Cada integrante tiene asignado un directorio exclusivo. **No modifiques archivos en las carpetas de otros integrantes sin previo acuerdo.** La comunicación entre módulos se realiza **únicamente** a través de los contratos definidos en [`docs/API_CONTRACT.md`](file:///c:/Users/jaacu/OneDrive/Documents/Jos/Dev/Hackaton_ElNino/docs/API_CONTRACT.md).

```text
┌───────────────────────────────┐
│     docs/API_CONTRACT.md      │  <-- CONTRATO INMUTABLE
└───────────────┬───────────────┘
                │
 ┌──────────────┼──────────────┬──────────────┐
 │              │              │              │
 ▼              ▼              ▼              ▼
core/bio_engine core/logistics  backend/       frontend/
(Biotecnología) (Mecatrónica)  (Software 1)   (Software 2)
```

---

## 2. Instrucciones Específicas por Rol para Antigravity

### 🔬 Rol 1: Biotecnología (`core/bio_engine/`)
* **Tu Objetivo:** Crear las funciones puras en Python para el cálculo del Índice de Riesgo Entomológico (IRE) y calibrar los prompts de visión artificial.
* **Cómo usar tu agente en Antigravity:**
  * Pídele al agente: *"Genera la función `calculate_ire` en `core/bio_engine/ire_calculator.py` que reciba tipo de depósito, temperatura y humedad, devolviendo el puntaje 0-100 y días de eclosión según la literatura de Aedes aegypti."*
  * Pídele: *"Crea pruebas unitarias con `pytest` en `core/bio_engine/test_bio.py` para validar diferentes escenarios climáticos (22°C vs 30°C)."*
  * Pídele: *"Escribe el system prompt estructurado en `core/bio_engine/vision_prompts.py` para que Gemini Flash identifique recipientes con agua estancada y devuelva un JSON estricto."*

---

### ⚙️ Rol 2: Mecatrónica y Logística (`core/logistics/`)
* **Tu Objetivo:** Desarrollar el algoritmo de optimización de rutas para las brigadas de fumigación y estructurar la capa geoespacial (GeoJSON).
* **Cómo usar tu agente en Antigravity:**
  * Pídele al agente: *"Implementa en `core/logistics/route_optimizer.py` un algoritmo heurístico (Nearest Neighbor + 2-opt) que ordene los focos prioritarios minimizando la distancia desde una base de operaciones."*
  * Pídele: *"Genera un script `core/logistics/mock_foci_generator.py` que cree 40 puntos GeoJSON realistas en el área urbana de Guayaquil con diferentes niveles de riesgo."*
  * Pídele: *"Documenta en `docs/UNIT_ECONOMICS.md` la fórmula de ahorro de combustible y químicos para el pitch comercial."*

---

### 💻 Rol 3: Software 1 — Backend (`backend/`)
* **Tu Objetivo:** Levantar el servidor FastAPI, conectar las APIs de Visión y Clima (Open-Meteo), y exponer los endpoints definidos en el contrato.
* **Cómo usar tu agente en Antigravity:**
  * Pídele al agente: *"Crea la aplicación FastAPI en `backend/app/main.py` implementando los endpoints `POST /api/reports`, `GET /api/foci` y `POST /api/routes/dispatch` respetando `docs/API_CONTRACT.md`."*
  * Pídele: *"Integra el cliente de Open-Meteo con manejo de errores y caché local en memoria."*
  * Pídele: *"Importa e integra las funciones de `core.bio_engine.ire_calculator` y `core.logistics.route_optimizer` dentro del pipeline del backend."*
  * Pídele: *"Implementa un modo fallback que devuelva datos locales simulados si falla la conexión a internet durante el pitch."*

---

### 🎨 Rol 4: Software 2 — Frontend & UX (`frontend/`)
* **Tu Objetivo:** Construir la interfaz PWA móvil para reporte ciudadano y el Dashboard GIS interactivo con mapa de calor y panel de despacho.
* **Cómo usar tu agente en Antigravity:**
  * Pídele al agente: *"Diseña una interfaz moderna y responsiva en `frontend/` con Leaflet.js para mostrar el mapa de calor epidemiológico y los marcadores de focos activos."*
  * Pídele: *"Crea la vista de captura móvil con acceso a cámara y geolocalización en 1 clic, con un diseño visualmente impactante y modo oscuro."*
  * Pídele: *"Agrega un botón 'Simular Reporte' que inyecte una foto y coordenadas de prueba al instante para no depender del GPS en la presentación en vivo."*
  * Pídele: *"Conecta el frontend al backend mediante `fetch` consumiendo los endpoints de `docs/API_CONTRACT.md`."*

---

## 3. Protocolo de Sincronización Diaria (15 Minutos)

1. **Mañana (09:00):** Revisión de 5 min: ¿Qué módulo avanzó cada uno? ¿Hay algún cambio necesario en `docs/API_CONTRACT.md`?
2. **Tarde (18:00):** Prueba de integración: ejecutar el backend y verificar que el frontend lea los datos reales producidos por los módulos de bio y logística.
3. **Control de Cambios:** Si un cambio en el contrato de API es indispensable, ambos lados (backend y frontend) deben aprobarlo antes de modificar `docs/API_CONTRACT.md`.
