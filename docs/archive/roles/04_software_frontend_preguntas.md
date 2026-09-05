# Preguntas Clave para el Rol: Software 2 (Frontend & Demo UX)

Este documento reúne las decisiones de diseño de interfaz, experiencia de usuario móvil, integración de mapas y dinamismo para el pitch.

---

### 1. Arquitectura de Interfaces (App Móvil vs. Dashboard)
* **Estructura de la Aplicación:** ¿Será una única Single Page Application (SPA) con selector de vistas / rutas (ej. `/report` para la vista ciudadana móvil y `/dashboard` para la sala de control), o dos proyectos desacoplados?
* **Stack y Bundler:** ¿Se utilizará Vite + Vanilla JS / React / Svelte? ¿Qué sistema de diseño y paleta de colores asegurará una estética visual moderna y de alto impacto?

---

### 2. Captura Móvil y Geolocalización (Vista Ciudadana / Brigadista)
* **Acceso a Cámara y Geolocalización:** ¿Cómo se gestionará la obtención de coordenadas GPS (`navigator.geolocation`) y la captura de cámara web/móvil con permisos directos en navegador?
* **Feedback Inmediato de Usuario:** ¿Qué animación o tarjeta de estado mostrará el resultado del análisis (ej. nivel de riesgo, días estimados de eclosión, badge de color e icono de advertencia)?
* **Modo Offline / Fallback de Demo:** ¿Tiene la interfaz un modo de prueba predefinido con coordenadas fijas y fotos de muestra precargadas en caso de fallas de señal móvil durante el pitch?

---

### 3. Dashboard GIS y Visualización en Tiempo Real
* **Librería de Mapas:** ¿Se utilizará **Leaflet con plugin de Heatmap (`leaflet-heat`)** o **MapLibre GL**? (Recomendación: Leaflet por ligereza y cero necesidad de tokens de pago).
* **Actualización en Tiempo Real:** ¿Cómo se reflejará un nuevo reporte en el mapa cuando el usuario envíe una foto desde el celular? (¿Polling cada 3-5 segundos, WebSocket, o evento reactivo?).
* **Capas del Mapa:** ¿Cómo se representará la diferencia visual entre:
  1. Mapa de calor general de densidad de riesgo.
  2. Marcadores individuales con popups interactivos detallando el criadero y la fecha de eclosión.
  3. Trazo poligonal de la ruta óptima de fumigación para la brigada?
* **Panel Lateral de Despacho y Métricas:** ¿Qué KPIs se visualizarán en tiempo real (ej. Total de focos críticos, Cuadrillas activas, Población protegida estimada)?
