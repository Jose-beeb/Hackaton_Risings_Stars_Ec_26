# Preguntas Clave para el Rol: Software 1 (Backend & Integración)

Este documento reúne las decisiones de arquitectura, stack, contratos de API y resiliencia para el desarrollo del orquestador del sistema.

---

### 1. Definición del Stack y Dependencias
* **Framework Principal:** ¿Se utilizará **Python (FastAPI)** para facilitar la integración nativa con librerías matemáticas/científicas y algoritmos bio, o **Node.js (Express/Fastify)**? (Recomendación técnica: FastAPI por tipado Pydantic y velocidad de prototyping).
* **Persistencia / Base de Datos:** ¿Se usará SQLite con extensión SpatiaLite, PostgreSQL/Supabase con PostGIS, o almacenamiento en memoria / archivo GeoJSON persistido en disco para simplificar el despliegue del MVP?

---

### 2. Integración y Resiliencia de APIs Externas
* **Proveedor de Visión Multimodal:** ¿Qué API se usará como principal (Gemini 1.5/2.0 Flash / OpenAI GPT-4o-mini) y cuál será el mecanismo de *fallback* o *mock response* si falla la conexión a internet en la demo en vivo?
* **Consulta Climática (Open-Meteo):** ¿Cómo se estructurará la llamada a la API abierta de Open-Meteo? ¿Se implementará un caché en memoria por coordenadas aproximadas para no saturar peticiones?
* **Pipeline Asíncrono de Procesamiento:** ¿El cálculo de visión, clima e IRE se procesará de forma síncrona en el endpoint de reporte (`POST /api/reports`) o se implementará una respuesta inmediata con actualización en background?

---

### 3. Contratos de Datos (API Contract) y Endpoints
* **Contrato de Reporte (`POST /api/reports`):** ¿Aceptará `multipart/form-data` con archivo de imagen binaria + campos `lat`/`lng`, o payload JSON con imagen en base64?
* **Contrato de Puntos GIS (`GET /api/foci`):** ¿El endpoint devolverá una estructura estándar `FeatureCollection` GeoJSON compatible con Leaflet/Mapbox?
* **Contrato de Rutas de Brigadas (`POST /api/routes/dispatch`):** ¿Qué parámetros recibirá (número de cuadrillas, punto de partida) y qué formato de coordenadas entregará al frontend?
* **Script de Inicialización / Seed Data:** ¿Cómo se ejecutará el script para precargar los 30-40 puntos iniciales al arrancar el servidor?
