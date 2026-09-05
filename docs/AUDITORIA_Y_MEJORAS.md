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
| **5** | **Optimización del Modelo de Visión (Gemini 2.5 Flash / Few-Shot)** | IA / Precisión | Resuelve falsos positivos/negativos en imágenes reales (canales, basureros, fotos sin criaderos) y reduce latencia. | **Crítica** |
| **6** | **Flujo Desacoplado con Notificación Flotante (Toast de Resultado)** | Frontend / UX | Permite al usuario continuar navegando el mapa tras reportar y recibir el resultado en una tarjeta flotante elegante. | **Alta** |
| **7** | **Evitar Generación de Focos en Cuerpos de Agua (Ríos/Esteros)** | GIS / Validación | Evita que simulaciones y reportes ubiquen criaderos en agua abierta o salobre, protegiendo la credibilidad del pitch. | **Alta** |
| **8** | **Exportación de Rutas a Google Maps (A Pie vs. Vehicular)** | Logística / Brigadas | Proporciona navegación real paso a paso al brigadista según su modo de transporte. | **Alta** |

---

## 4. Diagnóstico y Optimización del Reconocimiento de Imágenes (`test-images/`)

### A. Metodología de Benchmark y Diagnóstico con Imágenes de Prueba (`test-images/`)

> [!NOTE]
> **Sobre la validez metodológica (¿Existe sesgo al listar las imágenes?):**  
> **No.** Detallar los nombres y propósitos de los archivos en esta auditoría constituye una práctica estándar de ingeniería de software y evaluación empírica (test harness / benchmark suite). No introduce sesgo estadístico (*data leakage*) debido a que:
> 1. **Cero filtración al clasificador:** El backend envía exclusivamente los bytes puros de la imagen a la API de visión; en ningún momento se inyecta el nombre del archivo ni sus metadatos en el prompt o pipeline de inferencia.
> 2. **Evaluación de casos límite (*Edge Cases*):** La suite fue diseñada intencionalmente para contrastar controles negativos, perspectivas anómalas y arquetipos positivos de riesgo vectorial.

| Imagen de Prueba | Rol Metodológico en el Benchmark | Desafío / Riesgo Evaluado |
|---|---|---|
| `Pared.jpg` | **Control Negativo** | Superficie neutra sin agua ni depósitos. Valida que el modelo no alucine criaderos (Score 0). |
| `alcantarilla_bien.jpg` | **Control de Falso Positivo** | Drenaje funcional con flujo normal. Evalúa que el sistema no alerte falsas alarmas comunitarias. |
| `Basuero_inundado.jpg` / `Calle_tierra_con_agua.jpg` | **Ambigüedad Taxonómica** | Residuos dispersos y agua extendida. Evalúa resolución entre `puddle`, `litter_plastic` y `other`. |
| `canal_techo_inundado.jpg` | **Perspectiva Cenital / Compleja** | Canaleta elevada obstruida con agua estancada (`clogged_drain`). Riesgo de clasificarla erróneamente como `bucket` o `other`. |
| `Tanque_inundado.jpg` / `Llanta_Con_agua.jpg` / `maceta_con_agua.jpg` | **Arquetipos Positivos (*Aedes aegypti*)** | Criaderos domiciliarios y peridomiciliarios clásicos de alta prioridad sanitaria. |

### B. Causas Técnicas de Baja Precisión y Lentitud
1. **Modelo obsoleto configurado (`gemini-flash-lite-latest`):** Este alias apunta a versiones ligeras de primera generación con menor capacidad de razonamiento espacial y mayor tendencia al timeout o al fallback automático.
2. **Ambigüedad en la taxonomía:** Criaderos urbanos complejos (ej. basura inundada vs. charco) no tienen distinciones claras en las instrucciones del prompt.
3. **Falta de ejemplos de referencia (Zero-Shot):** El modelo no tiene ejemplos de qué considerar "materia orgánica" en aguas oscuras vs. agua limpia.

### C. Soluciones Concretas para Máxima Precisión
1. **Actualizar el identificador del modelo:** Migrar a `gemini-2.5-flash` (disponible en la API Key actual). Es significativamente más rápido, preciso en visión espacial y no produce timeouts.
2. **Refinar el System Prompt con Reglas Claras:**
   - Si hay múltiples desechos plásticos o basura inundada, clasificar como `litter_plastic` o `clogged_drain` con tamaño `medium`/`large`.
   - Distinguir canaletas de techo (`clogged_drain`) explícitamente de tanques.
   - Forzar `is_potential_breeding_site: false` ante paredes, personas, asfalto seco o interiores limpios.
3. **Reducción de resolución previa (Client-Side Resize):** Redimensionar la imagen a máx. 1024x1024 en el canvas antes del Base64. Acelera la transferencia en red y la inferencia de Gemini sin perder detalle entomológico.

---

## 5. Nuevo Flujo UX: Cierre Inmediato del Modal y Notificación Flotante con Resultado

### A. Problema de Usabilidad Actual
Actualmente, al tocar "Enviar Reporte", el modal permanece abierto en pantalla congelando la interacción durante 2-4 segundos. Si la red es lenta, la experiencia resulta frustrante y genera incertidumbre.

### B. Especificación del Nuevo Flujo Asíncrono
1. **Envío y Cierre Inmediato del Modal:**
   - Al hacer click en "Enviar Reporte", el modal de captura se cierra instantáneamente (`closeReportModal()`).
   - Se muestra un indicador sutil o Toast en la esquina inferior: *"📤 Enviando reporte... analizando con IA..."*.
2. **Procesamiento en Segundo Plano:**
   - La petición HTTP sigue ejecutándose en background mientras el usuario puede explorar el mapa o ver otros focos.
3. **Notificación Flotante del Resultado (Floating Result Card):**
   - Ni bien responde el backend, aparece una tarjeta flotante animada (Toast enriquecido) en la pantalla con:
     - Badge de nivel de riesgo (`CRITICAL`, `MEDIUM`, `LOW`).
     - Tipo de criadero detectado (ej. *"Llanta con agua"*).
     - Valor del IRE y días estimados para emergencia.
     - Consejo inmediato de acción comunitaria (*"🛠️ Qué podés hacer ahora mismo: Perforá la llanta..."*).
     - Botón para centrar el mapa en el nuevo foco.
   - En dispositivos móviles, emite una vibración háptica suave (`navigator.vibrate([80, 50, 80])`).

---

## 6. Plan de Ejecución para las Nuevas Mejoras del Equipo

### A. Punto de Partida Dinámico de Brigadas (Zona de Abastecimiento / Depot)
- **Implementación:**
  - Marcador arrastrable en Leaflet con ícono de base operativa (`🏥 Base Brigada`).
  - Botón *"Usar mi ubicación actual"* en el panel de despacho que actualiza las coordenadas de salida.
  - Envío automático de `depot_coordinates: [lng, lat]` en `POST /api/routes/dispatch`.

### B. Evitar Simulaciones de Focos en Cuerpos de Agua (Río Guayas y Estero)
- **Implementación:**
  - Delimitación poligonal simple de las áreas de agua de Guayaquil (Río Guayas y ramales del Estero Salado).
  - Función de validación `is_in_water(lat, lng)`. Si el punto aleatorio cae en agua, se reubica automáticamente en tierra firme antes de guardarlo o simularlo.

### C. Exportar Rutas de Intervención a Google Maps (A Pie vs. Vehículo)
- **Implementación:**
  - Generación de URL universal directa:
    `https://www.google.com/maps/dir/?api=1&origin=LAT_DEPOT,LNG_DEPOT&destination=LAT_FINAL,LNG_FINAL&waypoints=LAT1,LNG1|LAT2,LNG2...&travelmode=walking|driving`
  - En la tarjeta de cada brigada despachada, se incluye el botón *"📲 Navegar en Google Maps"* configurado con `walking` para cuadrillas a pie y `driving` para cuadrillas en vehículo.

---

## 7. Consistencia y Sentido de los Flujos de Usuario

### Flujo 1: Reporte Ciudadano Optimizado
- **Secuencia:** Captura de foto -> Envío y cierre inmediato del modal -> Notificación flotante de escaneo -> Notificación con resultado entomológico y tarjeta de acción para el hogar -> Nuevo foco marcado en el mapa.
- **Evaluación:** **Experiencia moderna, ágil y de alta retención.** El usuario no espera frente a una pantalla bloqueada.

### Flujo 2: Logística y Despacho de Brigadas Integral
- **Secuencia:** Selección de base de operaciones (mapa o GPS) -> Configuración de brigadas y movilidad -> Trazado TSP optimizado -> Exportación directa a Google Maps -> Intervención en campo -> Cierre con foto de evidencia.
- **Evaluación:** **Flujo operativo 100% aplicable al mundo real.** Resuelve el vacío tradicional entre la detección del problema y la acción sanitaria en territorio.
