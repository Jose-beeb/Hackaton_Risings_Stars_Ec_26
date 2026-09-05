# Investigación Estratégica: Ojito al Mosquito
**IEEE Rising Stars 2026 — Track 2: Public Health**
**Autor:** Senior Architect & Technical Advisory
**Fecha:** Septiembre 2026

---

## 1. Objetivos del Documento
1. Establecer el estado del arte y benchmarking competitivo frente a soluciones existentes (sector salud pública, apps ciudadanas y vigilancia epidemiológica).
2. Evaluar debilidades, amenazas, fortalezas y oportunidades (FODA técnico y operativo).
3. Blindar al equipo ante preguntas capciosas, técnicas y regulatorias del jurado del Hackathon.
4. Trazar un plan de ejecución de alto impacto priorizado para la demo en vivo.

---

## 2. Benchmarking Competitivo

| Criterio | Solución Tradicional (Min. Salud / Municipios) | Apps de Reporte Ciudadano (tipo DengueChat / Mosquito Alert) | Trampas IoT / Sensores de Hardware | **Ojito al Mosquito (Nuestra Solución)** |
| :--- | :--- | :--- | :--- | :--- |
| **Tiempo de Detección a Acción** | 48 - 72 horas (reporte manual en papel o Excel). | 24 - 48 horas (validación humana requerida). | Tiempo real, pero cobertura confinada al punto físico. | **< 3 minutos** (inferencia IA + cálculo microclimático en backend). |
| **Costo y Escalabilidad** | Alto costo operativo en cuadrillas no guiadas. | Bajo costo, pero baja retención de usuarios y sin despacho logístico. | Extremadamente costoso (cientos de USD por trampa, riesgo de vandalismo/batería). | **100% Software / Cloud** (< $50/mes por municipio, sin hardware físico). |
| **Priorización Sanitaria** | Fumigación en bloque por barrio (a ciegas, 70% pesticida malgastado). | Mapas de calor estáticos de conteo de quejas. | Datos puntuales sin inferencia del tipo de depósito. | **Índice de Riesgo Entomológico (IRE) Determinista:** Cruce de microclima real (Open-Meteo) y tasa de eclosión biológica (Rueda 1990/Tun-Lin 2000). |
| **Logística Operativa** | Rutas intuitivas según chofer de cuadrilla. | Ninguna (solo reporte). | Ninguna (solo monitoreo). | **Despacho Logístico Optimizado (TSP/Heurística ponderada por IRE):** Ruteo directo al foco con enlace directo a navegación. |
| **Explicabilidad ante Epidemiólogos** | Procedimiento empírico. | Sin base bio-matemática. | Caja negra de conteo acústico u óptico. | **Modelo determinista bio-matemático abierto**, auditable y justificado científicamente. |

---

## 3. Matriz FODA Técnica y de Pitch

### Fortalezas (Strengths)
- **100% Software / Despliegue Inmediato:** No depende de fabricar hardware, importar sensores ni permisos de radiofrecuencia.
- **Validación Multimodal Instantánea:** Clasificación automática de tipo de recipiente (neumático, tanque, florero, etc.) y presencia de agua con Gemini Flash.
- **Fundamento Biológico Real:** Cálculo de días para emergencia adulta según curvas térmicas reales del *Aedes aegypti*.
- **Arquitectura Resiliente (Fail-Safes para Demo):**
  - Fallback a clasificador heurístico si la API de visión no responde.
  - Fallback a serie histórica climatológica de Guayaquil si falla Open-Meteo.
  - Fallback local de datos GeoJSON en frontend ante pérdida de red.

### Debilidades (Weaknesses) & Mitigaciones
- **Dependencia de Conectividad Móvil en Campo:**
  - *Riesgo:* Brigadistas en zonas periurbanas con señal intermitente.
  - *Blindaje:* Soporte PWA offline con almacenamiento IndexedDB local y cola de sincronización en fondo (`background-sync`).
- **Falsos Positivos en Reportes Ciudadanos:**
  - *Riesgo:* Fotos irrelevantes, bromas o imágenes sin criaderos.
  - *Blindaje:* Filtro de confianza en dos etapas: validación de imagen por IA (score de confidencia de agua y recipiente) + verificación de foto antes/después al resolver el foco.
- **Persistencia en Archivo Plano en el MVP:**
  - *Riesgo:* Concurrencia limitada si crecen las peticiones.
  - *Blindaje:* Documentar la transición limpia a PostgreSQL + PostGIS mediante abstracción de repositorio (patrón Repository listo).

### Oportunidades (Opportunities)
- **Integración con Sistemas de Salud (EPI-Vigilancia):** Exportación en formatos estándar (GeoJSON, Shapefile, CSV para ArcGIS/QGIS).
- **Gamificación Ciudadana:** Incentivos municipales (reducción de tasas de aseo o insignias barriales) por criaderos eliminados comunitariamente.

### Amenazas (Threats) & Mitigaciones
- **Baja Adopción Ciudadana:**
  - *Mitigación:* La plataforma no depende exclusivamente de la ciudadanía; está pensada primariamente como herramienta de productividad para brigadistas y agentes de salud barrial.
- **Resistencia al Cambio en Cuadrillas Municipales:**
  - *Mitigación:* Botón simple de apertura en Google Maps que no obliga a aprender una app de navegación nueva.

---

## 4. Blindaje ante el Jurado (Q&A de Alta Dificultad)

### P1: "¿Por qué no usan trampas IoT o sensores de ovitrampas conectados?"
> **Respuesta del Equipo:**  
> *"Las trampas IoT tienen dos problemas mortales para la salud pública en Latinoamérica: costo unitario y mantenimiento/vandalismo. Cubrir una ciudad como Guayaquil con trampas físicas costaría cientos de miles de dólares en baterías y conectividad LoRa/4G. Nuestro enfoque 100% software aprovecha la red de sensores más densa y barata del mundo: los smartphones que ya tienen los ciudadanos y las cuadrillas municipales. Es una solución desplegable en 24 horas a costo casi marginal."*

### P2: "¿Cómo justifican que la IA no invente datos o cometa alucinaciones biológicas?"
> **Respuesta del Equipo:**  
> *"La IA (Gemini Flash) se utiliza ÚNICAMENTE como transductor perceptivo: extrae qué recipiente hay en la imagen (llanta, balde, maceta) y si hay agua estancada. La IA NO toma la decisión de riesgo. El riesgo epidemiológico lo calcula un algoritmo determinista bio-matemático basado en literatura científica validada (Rueda et al., 1990 y Tun-Lin et al., 2000), cruzado con la temperatura microclimática de la API de Open-Meteo. El epidemiólogo municipal tiene trazabilidad y reproducibilidad matemática total."*

### P3: "¿Qué pasa si un usuario sube una foto de su perro o una foto falsa?"
> **Respuesta del Equipo:**  
> *"El pipeline cuenta con un filtro de umbral de confidencia. Si la IA no detecta recipientes catalogados como potenciales criaderos o la probabilidad de agua es baja, el reporte se etiqueta como 'no concluyente / descartado' y no activa una alerta de brigada. Además, implementamos deduplicación espacial: reportes a menos de 15 metros se agrupan en un único foco para evitar spam o dobles visitas."*

### P4: "¿Cómo manejan el problema de los focos que caen en el agua (Río Guayas / Estero)?"
> **Respuesta del Equipo:**  
> *"A diferencia de simulaciones estándar, incorporamos máscaras geoespaciales de exclusión hidrológica específicas de Guayaquil (Río Guayas y ramales del Estero Salado), garantizando que las coordenadas asignadas y simuladas correspondan estrictamente a suelo firme urbano y periurbano donde residen los vectores y las personas."*

### P5: "¿Por qué TSP (Traveling Salesperson) y no un modelo de despacho tradicional?"
> **Respuesta del Equipo:**  
> *"Las cuadrillas hoy recorren manzanas al azar. Con nuestro despacho TSP ponderado por IRE, el sistema no solo minimiza los kilómetros recorridos y el combustible del vehículo municipal, sino que ordena la visita por urgencia biológica: primero se visitan los criaderos cuyo tiempo estimado de eclosión es menor a 48 horas, evitando que el vector llegue a fase adulta y transmita el virus."*

---

## 5. Plan de Ejecución Priorizado para el Demo/Pitch

1. **Fase A: Blindaje del Despacho y Demo en Vivo**
   - Selector interactivo de base de brigadas (Depot arrastrable y botón de GPS actual).
   - Generación de link directo paso a paso en Google Maps para brigadas.
   - Restricción hidrológica (filtro de cuerpos de agua para que ningún foco caiga en el río).
2. **Fase B: Validación de Métricas de Impacto para el Jurado**
   - KPI de litros de pesticida ahorrados vs. fumigación tradicional a ciegas.
   - KPI de reducción de tiempo de respuesta (72h $\rightarrow$ 3h).
   - Estimación de costo computacional por foco (< $0.002 USD por inferencia).
3. **Fase C: Ensayo del Pitch Flow**
   - Ejecución del guion de 90 segundos con demostración de captura, cálculo IRE y ruteo en el mapa Leaflet.
