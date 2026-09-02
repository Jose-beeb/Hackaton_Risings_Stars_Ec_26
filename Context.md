**Proyecto: AedesGuard (Sistema de Vigilancia Epidemiológica y Control Vectorial Predictivo)**

**Contexto General**

* **Competencia:** IEEE Rising Stars 2026 Hackathon (Participación en el Track 2: Public Health).
* **Enfoque de la Solución:** Plataforma 100% de software (sin hardware físico para la fase MVP) orientada a la detección temprana, reporte ciudadano, análisis microclimático y priorización de zonas de riesgo para el control de arbovirosis (*Aedes aegypti* / dengue, zika y chikungunya).
* **Plataforma de Desarrollo:** Entorno de agentes de IA en **Antigravity** para desarrollo acelerado en 4 días con un equipo interdisciplinario (1 biotecnóloga, 1 mecatrónico y 2 ingenieros de software).

**Arquitectura Técnica del MVP (Puro Software)**

* **Frontend Móvil (PWA / Web App):** Interfaz ligera optimizada para teléfonos móviles que permite al usuario o brigadista tomar una foto de un recipiente con agua estancada, extraer automáticamente las coordenadas GPS y enviar el reporte en un solo clic.
* **Backend de Procesamiento (FastAPI / Node.js):**
* Orquestador central que recibe la imagen y la ubicación.
* **Módulo de Visión Artificial:** Llamada a una API multimodal (ej. Gemini Flash / OpenAI Vision) configurada con un prompt estructurado para clasificar el tipo de depósito (llanta, balde, tanque, maceta) y validar la presencia de agua.
* **Módulo Climático:** Consulta a una API abierta gratuita (Open-Meteo) para extraer la temperatura y humedad ambiental en tiempo real según las coordenadas del reporte.


* **Motor Bio-Matemático:** Algoritmo que calcula el **Índice de Riesgo Entomológico (IRE)** cruzando el tipo de criadero con la temperatura local para estimar el tiempo de eclosión de las larvas.
* **Dashboard GIS / Panel Municipal:** Mapa interactivo web (Leaflet o Mapbox) con un mapa de calor dinámico que actualiza los focos críticos en tiempo real y genera una lista priorizada para el despacho eficiente de brigadas de fumigación y abatización.

**Lógica Biológica y de Datos**

* **Cero Big Data requerido:** No se entrenan modelos de Machine Learning desde cero; se utilizan modelos de visión preentrenados y ecuaciones deterministas basadas en tasas de desarrollo metabólico del vector según rangos de temperatura ($20^\circ\text{C}$ a $32^\circ\text{C}$).
* **Datos iniciales (*Mock Data*):** Script para precargar 30-40 puntos geoespaciales ficticios en una zona piloto de la costa ecuatoriana (ej. Guayaquil o Portoviejo) con el fin de demostrar densidad en el mapa durante el pitch.

**Distribución de Tareas para los Agentes y el Equipo**

* **Biotecnóloga (Diseño Bio-Lógico):** Definición de la fórmula del Índice de Riesgo Entomológico (IRE) y calibración del prompt de la API de visión para asegurar una correcta clasificación taxonómica y sanitaria de los criaderos.
* **Mecatrónico (Logística y Modelado GIS):** Diseño de la lógica de optimización de rutas de intervención para las cuadrillas sanitarias y estructuración de la base de datos geoespacial (GeoJSON).
* **Software 1 (Backend & Integración):** Construcción del servidor, enlace con las APIs externas (Visión y Clima), ejecución del motor de cálculo y preparación de los endpoints del sistema.
* **Software 2 (Frontend & Demo UX):** Desarrollo de la interfaz web móvil de captura de reportes y despliegue del dashboard GIS interactivo con actualización en tiempo real para la presentación final.