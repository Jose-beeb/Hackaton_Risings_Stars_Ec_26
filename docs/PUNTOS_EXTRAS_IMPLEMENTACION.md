# Guía de Puntos Extras y Mejoras para Implementación Directa

> **Para el equipo de desarrollo:**  
> Este documento contiene las especificaciones listas para copiar, pegar o integrar en tu rama de trabajo tras hacer `git pull`. Cada punto indica **archivo afectado**, **código a insertar** y **resultado esperado**.

---

## 📌 Punto Extra 1: Selector Dinámico de Base de Brigadas (Depot en Leaflet y GPS)

- **Objetivo:** Permitir que la brigada no parta siempre del punto hardcodeado `[-79.8950, -2.1800]`.
- **Archivos afectados:**
  - `frontend/index.html` (o panel de despacho de brigadas).
  - `frontend/app.js` (o módulo GIS).
  - `backend/routers/dispatch.py` (o endpoint `POST /api/routes/dispatch`).

### Snippet Frontend (JavaScript / Leaflet):
```javascript
// Marcador arrastrable para la base/depot
let depotMarker = L.marker([-2.1800, -79.8950], {
  draggable: true,
  title: "Base de Operaciones / Cuadrilla"
}).addTo(map);

depotMarker.on('dragend', function (e) {
  const coord = e.target.getLatLng();
  window.currentDepot = [coord.lng, coord.lat]; // [lng, lat] GeoJSON format
});

// Botón: Usar ubicación actual del dispositivo
function setDepotFromGPS() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      depotMarker.setLatLng([lat, lng]);
      map.panTo([lat, lng]);
      window.currentDepot = [lng, lat];
    });
  }
}
```

### En el Payload de Despacho:
```javascript
// Al llamar a /api/routes/dispatch:
body: JSON.stringify({
  brigades_count: 2,
  depot_coordinates: window.currentDepot || [-79.8950, -2.1800]
})
```

---

## 📌 Punto Extra 2: Evitar Focos en Cuerpos de Agua (Río Guayas y Estero)

- **Objetivo:** Que las simulaciones de focos aleatorios no caigan en medio del río o del estero salado.
- **Archivo afectado:** `backend/services/simulation.py` (o donde se generen puntos aleatorios).

### Snippet Backend (Python):
```python
# Bounding boxes simplificados de exclusión de agua (Guayaquil)
WATER_EXCLUSION_ZONES = [
    # Río Guayas (franja este)
    {"min_lat": -2.280, "max_lat": -2.140, "min_lng": -79.882, "max_lng": -79.860},
    # Ramal Estero Salado central
    {"min_lat": -2.210, "max_lat": -2.175, "min_lng": -79.920, "max_lng": -79.905},
]

def is_point_in_water(lat: float, lng: float) -> bool:
    for zone in WATER_EXCLUSION_ZONES:
        if zone["min_lat"] <= lat <= zone["max_lat"] and zone["min_lng"] <= lng <= zone["max_lng"]:
            return True
    return False

def generate_valid_land_coordinate(generator_func, max_attempts=10):
    for _ in range(max_attempts):
        lat, lng = generator_func()
        if not is_point_in_water(lat, lng):
            return lat, lng
    return lat, lng # fallback
```

---

## 📌 Punto Extra 3: Enlace Directo para Navegación en Google Maps (A Pie vs. Vehículo)

- **Objetivo:** Permitir que el brigadista presione un botón y se abra Google Maps con la ruta paso a paso.
- **Archivo afectado:** `frontend/app.js` (en la tarjeta resumen de brigada despachada).

### Snippet Frontend:
```javascript
function generateGoogleMapsRouteUrl(depot, stops, travelMode = 'walking') {
  // depot: [lat, lng]
  // stops: [[lat1, lng1], [lat2, lng2], ...]
  // travelMode: 'walking' o 'driving'
  if (!stops || stops.length === 0) return '#';

  const origin = `${depot[0]},${depot[1]}`;
  const destination = `${stops[stops.length - 1][0]},${stops[stops.length - 1][1]}`;
  
  const waypoints = stops.slice(0, -1).map(p => `${p[0]},${p[1]}`).join('|');
  
  let url = `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}&travelmode=${travelMode}`;
  if (waypoints) {
    url += `&waypoints=${waypoints}`;
  }
  return url;
}

// Ejemplo de inserción en HTML:
// `<a href="${generateGoogleMapsRouteUrl(depot, routePoints, 'walking')}" target="_blank" class="btn-gmaps">🗺️ Navegar en Google Maps (A Pie)</a>`
```

---

## 📌 Punto Extra 4: Notificación No Bloqueante (Toast Flotante de Resultado)

- **Objetivo:** Que al enviar la foto ciudadana, el modal se cierre inmediatamente y el usuario reciba un toast flotante con el resultado del IRE y el consejo doméstico.
- **Archivo afectado:** `frontend/index.html` y `frontend/app.js`.

### Snippet CSS:
```css
.toast-floating {
  position: fixed;
  bottom: 24px;
  right: 24px;
  max-width: 360px;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  z-index: 9999;
  transition: all 0.3s ease-in-out;
}
```

### Snippet JS:
```javascript
function showReportResultToast(data) {
  const toast = document.createElement('div');
  toast.className = 'toast-floating';
  toast.innerHTML = `
    <div style="font-weight: 600; margin-bottom: 4px;">🦟 Análisis Completado</div>
    <div style="font-size: 0.9rem; color: #94a3b8;">Criadero: <strong>${data.breeding_site_type || 'Depósito detectado'}</strong></div>
    <div style="font-size: 0.85rem; margin-top: 6px; color: #38bdf8;">${data.community_action || 'Acción: Vacía o cubre el recipiente.'}</div>
  `;
  document.body.appendChild(toast);
  
  if (navigator.vibrate) {
    navigator.vibrate([80, 50, 80]);
  }
  
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 6000);
}
```
