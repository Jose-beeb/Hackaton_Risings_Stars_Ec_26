# Auditoría Técnica, de UX y Propuestas de Mejora: Ojito al Mosquito

**Proyecto:** Ojito al Mosquito (Vigilancia Epidemiológica y Control Vectorial Predictivo)  
**Track:** IEEE Rising Stars 2026 — Track 2: Public Health  
**Evaluador:** Senior Architect & Technical Advisor  
**Fecha:** Septiembre 2026  

---

## 1. Funcionamiento End-to-End del Sistema

El sistema implementa una tubería de inteligencia epidemiológica orientada a reducir el ciclo de reacción contra vectores de dengue, zika y chikungunya (*Aedes aegypti*):

```
[Captura / Simulación] 
       │ (Foto Base64 + Coordenadas GPS)
       ▼
[Backend FastAPI (/api/reports)]
       ├── 1. Inferencia Visual (Gemini Flash Vision)
       │       └── Detecta tipo de depósito, agua, volumen y materia orgánica
       ├── 2. Clima Micro-local (Open-Meteo API)
       │       └── Consulta temperatura y humedad relativa actuales
       └── 3. Motor Bio-Matemático IRE (Calibrado con Rueda 1990 y Tun-Lin 2000)
               └── Calcula Índice de Riesgo Entomológico y días para emergencia adulta
       │
       ▼
[Almacenamiento GeoJSON] ─── (data/mock_foci_guayaquil.geojson)
       ▲
       ├── Polling cada 4s (/api/foci) ──► [Dashboard GIS / Leaflet & Heatmap]
       └── Heurística TSP (/api/routes/dispatch) ──► [Rutas Óptimas por Brigada]
                                                         │
                                                         ▼
                                             [Resolución de Foco con Evidencia]
```

---

## 2. Evaluación de Desempeño y Usabilidad (UX)

### Aspectos Positivos
1. **Doble perfil de usuario:** La separación entre *Vista Ciudadana* (lenguaje empático, consejos de acción inmediata en el hogar) y *Vista Brigada* (parámetros operativos, cálculo de combustible, pesticida y días de eclosión) es conceptualmente sólida.
2. **Resiliencia operativa (Fail-safes para Pitch/Demo):**
   - Si no hay API key o falla Gemini, se activa un clasificador de fallback entomológico.
   - Si no hay conexión al backend, el frontend consume el GeoJSON local o permite simulación en cliente.
   - Si Open-Meteo tiene timeout, se usa la serie histórica promedio de Guayaquil.
3. **Mecanismo anti-parpadeo:** El frontend calcula un hash ligero en polling para no re-renderizar Leaflet si no hay novedades.

### Puntos Críticos y Fricciones Detectadas
1. **Sobrecarga de red en la carga de imágenes:** Enviar fotos como cadenas base64 directamente dentro del JSON satura el ancho de banda móvil (un 33% más pesado que binario puro) y degrada la memoria en FastAPI.
2. **Persistencia concurrente frágil en archivo plano (`.geojson`):**
   - El backend lee y reescribe un archivo JSON completo en disco bajo un `threading.Lock`.
   - Si bien previene condiciones de carrera en un único proceso, colapsa ante múltiples workers (`uvicorn --workers 4`), ya que los locks en memoria no se comparten entre procesos del SO.
3. **Ubicación fija de partida (Depot Hardcodeado):** Las brigadas parten siempre de `[-79.8950, -2.1800]` a menos que se altere vía API externa. Falta permitir al operador elegir su base o usar su GPS en vivo.
4. **Frecuencia de Polling Ciego (cada 4s):** El frontend interroga continuamente al servidor sin importar si la pestaña está oculta o inactiva, drenando batería en dispositivos móviles.

---

## 3. Matriz General de Mejoras Justificadas

| # | Propuesta de Mejora | Área | Justificación Técnica & Sanitaria | Prioridad |
|---|---------------------|------|-----------------------------------|-----------|
| **1** | **Subida multipart (`multipart/form-data`) y compresión previa en Canvas** | Backend / UX Móvil | Reduce el tamaño de carga en redes 3G/4G precarias de zonas vulnerables y evita bloquear el event loop decodificando Base64 pesados. | **Alta** |
| **2** | **Migración de persistencia a SQLite con SpatiaLite o TinyDB/PostGIS** | Arquitectura / Datos | Evita corrupción del GeoJSON ante caídas abruptas de energía o escrituras concurrentes. Permite auditoría de intervenciones sin reescribir todo el archivo. | **Alta** |
| **3** | **Selector de Centro Operativo / Base de Brigadas en el Mapa** | Logística / UX | Las cuadrillas sanitarias no siempre salen del centro de la ciudad; permitir seleccionar el depósito o usar el GPS del móvil calcula rutas realistas de despacho. | **Alta** |
| **4** | **Polling Adaptativo y Soporte para PWA Offline (IndexedDB / Service Worker)** | Frontend / UX | En zonas suburbanas sin señal celular, el brigadista debe poder registrar fotos y coordenadas para que sincronicen automáticamente al recuperar conectividad. | **Alta** |
| **5** | **Validación Visual de Evidencia Post-Intervención (Antes vs. Después)** | IA / Control Sanitario | El endpoint `/api/foci/resolve` recibe una foto pero no la evalúa. Un contraste con Gemini de "Antes vs. Después" validaría si el neumático fue removido o el tanque fue abatizado/tapado. | **Media** |

---

## 4. Análisis y Plan de Ejecución para las Nuevas Propuestas del Equipo

Evaluación técnica de las 4 ideas bajo consideración y la mejor estrategia de implementación para el MVP del Hackathon:

### A. Punto de Partida Dinámico de Brigadas (Zona de Abastecimiento / Depot)
- **¿Es una buena idea?:** **EXCELENTE y CRÍTICA.** En una emergencia sanitaria o jornada de fumigación, las cuadrillas salen desde centros de salud específicos, bodegas de químicos o su propia posición en campo. Si el punto de partida es fijo en el centro de Guayaquil, los cálculos de distancia, consumo de combustible y tiempos de viaje carecen de realismo operativo.
- **Mejor manera de ejecutarlo en el MVP:**
  1. Agregar en Leaflet un marcador interactivo arrastrable (`draggable: true`) con ícono de base/almacén (ej. 🏥 o 🚛).
  2. Ofrecer un botón *"Usar mi ubicación actual"* (`navigator.geolocation`) o hacer click en el mapa para posicionar el depot.
  3. Enviar estas coordenadas en el payload de `POST /api/routes/dispatch` (`depot_coordinates: [lng, lat]`), el cual el backend ya soporta de forma nativa.

### B. Evitar Simulaciones de Focos en Cuerpos de Agua (Ríos Guayas / Estero Salado)
- **¿Es una buena idea?:** **MUY BUENA.** En demos o evaluaciones ante el jurado, ver un foco de *Aedes aegypti* flotando en medio del Río Guayas o en el estero genera pérdida inmediata de credibilidad técnica. Biológicamente, el *Aedes aegypti* se reproduce en recipientes artificiales urbanos con agua limpia/estancada, jamás en corrientes fluviales abiertas o aguas salobres.
- **Mejor manera de ejecutarlo en el MVP:**
  1. **Enfoque MVP rápido y robusto (Sin dependencias GIS pesadas):** Definir una máscara de polígonos simples (Bounding Boxes o polígonos GeoJSON livianos) que delimiten el lecho del Río Guayas y el Estero Salado.
  2. En el generador de simulación (`btn-simulate-report` y `mock_foci_generator.py`), antes de instanciar las coordenadas aleatorias, pasar la tupla `(lat, lng)` por una función `is_in_water_body(lat, lng)`. Si cae dentro del polígono de agua, regenerar el punto en tierra firme.

### C. Exportar Rutas de Intervención a Google Maps (A Pie vs. Vehículo)
- **¿Es una buena idea?:** **EXCELENTE.** Cierra la brecha entre la planificación en el dashboard y la ejecución de la cuadrilla en el mundo real. Ningún brigadista conduce mirando un mapa web estático; necesitan abrir la navegación en su app nativa de celular.
- **Mejor manera de ejecutarlo en el MVP:**
  1. Google Maps permite abrir rutas secuenciales mediante URLs universales sin pagar API de Directions:
     ```
     https://www.google.com/maps/dir/?api=1&origin=LAT_DEPOT,LNG_DEPOT&destination=LAT_FIN,LNG_FIN&waypoints=LAT1,LNG1|LAT2,LNG2...&travelmode=walking (o driving)
     ```
  2. Generar un botón en cada tarjeta de brigada: *"📲 Abrir ruta en Google Maps"*.
  3. Según el `transport_mode` configurado en la brigada (`foot` -> `travelmode=walking`; `vehicle_spray` o `vehicle_walk_attack` -> `travelmode=driving`), armar el enlace con origen (depot) y los waypoints ordenados por el TSP.
  4. (Opcional MVP): Ofrecer también un botón para descargar el archivo `.kml` o `.gpx` estándar.

### D. Flujo Asíncrono de Análisis con Notificación (Feedback Ciudadano / Toast)
- **¿Es una buena idea?:** **FUNDAMENTAL PARA UX.** El análisis visual con Gemini y la consulta climática pueden demorar entre 1.5 y 4 segundos dependiendo de la red. Si la interfaz se queda congelada sin estado de carga, el usuario presiona varias veces o cree que la app falló.
- **Mejor manera de ejecutarlo en el MVP:**
  1. **Micro-interacción de carga inmediata:** Al tocar "Enviar Reporte", deshabilitar el botón, mostrar un spinner elegante o barra de escaneo animada sobre la foto con texto *"🧠 Entomólogo IA analizando criadero y microclima..."*.
  2. **Notificación Toast / Modal:** Ni bien responde la API, emitir una notificación sonora/háptica suave (Web Vibration API en móviles), mostrar un Toast de confirmación (*"¡Reporte clasificado con éxito!"*) y desplegar la tarjeta de acción domiciliaria recomendada con transición suave.

---

## 5. Consistencia y Sentido de los Flujos de Usuario

### Flujo 1: Reporte Ciudadano
- **Secuencia:** Abrir cámara -> Captura / Subida -> Feedback visual de escaneo IA -> Clasificación y cálculo de riesgo -> Notificación y sugerencia preventiva de acción en el hogar.
- **Evaluación:** **Excelente consistencia.** El ciudadano recibe retroalimentación inmediata sobre qué hacer con el criadero sin generar alarma.

### Flujo 2: Despacho y Logística de Brigadas
- **Secuencia:** Vista Brigada -> Selección del punto de partida (depot) -> Configuración de cuadrillas y transporte -> Cálculo de ruta TSP -> Exportación a Google Maps para navegación -> Ejecución en terreno -> Cierre de foco con foto de evidencia.
- **Evaluación:** **Flujo completo y de alto impacto.** Resuelve la operatividad en campo de principio a fin.
