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

## 3. Matriz de Mejoras Justificadas

| # | Propuesta de Mejora | Área | Justificación Técnica & Sanitaria | Prioridad |
|---|---------------------|------|-----------------------------------|-----------|
| **1** | **Subida multipart (`multipart/form-data`) y compresión previa en Canvas** | Backend / UX Móvil | Reduce el tamaño de carga en redes 3G/4G precarias de zonas vulnerables y evita bloquear el event loop decodificando Base64 pesados. | **Alta** |
| **2** | **Migración de persistencia a SQLite con SpatiaLite o TinyDB/PostGIS** | Arquitectura / Datos | Evita corrupción del GeoJSON ante caídas abruptas de energía o escrituras concurrentes. Permite auditoría de intervenciones sin reescribir todo el archivo. | **Alta** |
| **3** | **Selector de Centro Operativo / Base de Brigadas en el Mapa** | Logística / UX | Las cuadrillas sanitarias no siempre salen del centro de la ciudad; permitir seleccionar el depósito o usar el GPS del móvil calcula rutas realistas de despacho. | **Media** |
| **4** | **Polling Adaptativo y Soporte para PWA Offline (IndexedDB / Service Worker)** | Frontend / UX | En zonas suburbanas sin señal celular, el brigadista debe poder registrar fotos y coordenadas para que sincronicen automáticamente al recuperar conectividad. | **Alta** |
| **5** | **Validación Visual de Evidencia Post-Intervención (Antes vs. Después)** | IA / Control Sanitario | El endpoint `/api/foci/resolve` recibe una foto pero no la evalúa. Un contraste con Gemini de "Antes vs. Después" validaría si el neumático fue removido o el tanque fue abatizado/tapado. | **Media** |

---

## 4. Consistencia y Sentido de los Flujos de Usuario

### Flujo 1: Reporte Ciudadano
- **Secuencia:** Abrir cámara -> Captura / Subida -> Detección automática de GPS -> Clasificación IA -> Retorno con sugerencia doméstica ("Da vuelta el recipiente", "Tapa el tanque").
- **Evaluación:** **Excelente consistencia.** El feedback no alarma innecesariamente al vecino y le da un rol activo de prevención.

### Flujo 2: Despacho y Logística de Brigadas
- **Secuencia:** Vista Brigada -> Configuración de cuadrillas (operarios y transporte) -> Trazado heurístico TSP -> Inspección en terreno -> Cierre de foco con foto y nombre de operador.
- **Evaluación:** **Muy buen flujo.** Cubre la brecha habitual donde las aplicaciones de salud se quedan en el reporte y no resuelven la logística de atención.
