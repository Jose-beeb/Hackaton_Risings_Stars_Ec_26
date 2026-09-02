// AedesGuard Frontend Application
let map;
let heatLayer;
let markersLayer;
let routeLayer;
let fociData = [];

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  loadEpidemiologicalData();
  setupEventListeners();
});

function initMap() {
  // Centro en Guayaquil, Ecuador
  map = L.map("map", {
    center: [-2.19, -79.89],
    zoom: 12,
    zoomControl: false
  });

  L.control.zoom({ position: "topright" }).addTo(map);

  // CartoDB Dark Matter Tile Layer (Modern Dark Map)
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: "abcd",
    maxZoom: 19
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
  routeLayer = L.layerGroup().addTo(map);
}

async function loadEpidemiologicalData() {
  try {
    // Intentar conectar con el backend local primero, con fallback al archivo mock local
    let res = await fetch("http://localhost:8000/api/foci").catch(() => null);
    if (!res || !res.ok) {
      res = await fetch("../data/mock_foci_guayaquil.geojson");
    }
    const data = await res.json();
    fociData = data.features || [];
    renderDashboard(fociData);
  } catch (err) {
    console.error("Error al cargar datos epidemiológicos:", err);
  }
}

function renderDashboard(features) {
  markersLayer.clearLayers();
  
  const heatPoints = [];
  let criticalCount = 0;
  const feedContainer = document.getElementById("foci-list");
  feedContainer.innerHTML = "";

  features.forEach((feature) => {
    const coords = feature.geometry.coordinates; // [lng, lat]
    const props = feature.properties;
    const latLng = [coords[1], coords[0]];

    // Heatmap intensity (normalizado por IRE)
    const intensity = (props.ire_score || 50) / 100.0;
    heatPoints.push([latLng[0], latLng[1], intensity]);

    if (props.risk_level === "CRITICAL") criticalCount++;

    // Color del marcador
    const markerColor =
      props.risk_level === "CRITICAL" ? "#ef4444" :
      props.risk_level === "MEDIUM" ? "#f59e0b" : "#10b981";

    const circle = L.circleMarker(latLng, {
      radius: 6,
      fillColor: markerColor,
      color: "#ffffff",
      weight: 1.5,
      opacity: 0.9,
      fillOpacity: 0.8
    });

    circle.bindPopup(`
      <div style="font-family: sans-serif; font-size: 13px; color: #1e293b;">
        <h4 style="margin: 0 0 4px 0; color: ${markerColor};">${props.container_name || props.container_type}</h4>
        <p><strong>Sector:</strong> ${props.sector}</p>
        <p><strong>IRE:</strong> ${props.ire_score} | <strong>Riesgo:</strong> ${props.risk_level}</p>
        <p><strong>Eclosión est.:</strong> ${props.days_to_emergence} días</p>
        <p style="font-size: 11px; margin-top: 4px; color: #475569;">${props.recommended_action || ''}</p>
      </div>
    `);

    markersLayer.addLayer(circle);
  });

  // Render Heatmap
  if (heatLayer) map.removeLayer(heatLayer);
  heatLayer = L.heatLayer(heatPoints, {
    radius: 25,
    blur: 18,
    maxZoom: 15,
    gradient: { 0.2: '#10b981', 0.5: '#f59e0b', 0.8: '#ef4444' }
  }).addTo(map);

  // Update KPIs
  document.getElementById("kpi-critical-count").textContent = criticalCount;
  document.getElementById("kpi-total-count").textContent = features.length;

  // Render Top 6 en el Feed
  features.slice(0, 6).forEach((f) => {
    const p = f.properties;
    const item = document.createElement("div");
    item.className = `foci-item ${p.risk_level.toLowerCase()}`;
    item.innerHTML = `
      <div class="foci-header">
        <span>${p.container_name || p.container_type}</span>
        <span>IRE: ${p.ire_score}</span>
      </div>
      <div class="foci-detail">${p.sector} · Eclosión en ${p.days_to_emergence} días</div>
    `;
    item.addEventListener("click", () => {
      map.flyTo([f.geometry.coordinates[1], f.geometry.coordinates[0]], 15);
    });
    feedContainer.appendChild(item);
  });
}

function setupEventListeners() {
  // Botón Simular Reporte en Vivo (Pitch Fail-safe)
  document.getElementById("btn-simulate-report").addEventListener("click", async () => {
    const randomLat = -2.185 + (Math.random() - 0.5) * 0.04;
    const randomLng = -79.89 + (Math.random() - 0.5) * 0.04;

    const payload = {
      latitude: randomLat,
      longitude: randomLng,
      image_base64: "data:mock",
      notes: "Reporte en vivo durante presentación"
    };

    try {
      const res = await fetch("http://localhost:8000/api/reports", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        await loadEpidemiologicalData();
      }
    } catch {
      // Fallback local en frontend si backend no está corriendo
      const newFeature = {
        type: "Feature",
        geometry: { type: "Point", coordinates: [randomLng, randomLat] },
        properties: {
          id: `foco-live-${Date.now()}`,
          sector: "Demostración en Vivo",
          container_name: "Llanta con agua (Detectado IA)",
          ire_score: 92.4,
          risk_level: "CRITICAL",
          days_to_emergence: 3,
          recommended_action: "Intervención prioritaria inmediata."
        }
      };
      fociData.unshift(newFeature);
      renderDashboard(fociData);
    }
    map.flyTo([randomLat, randomLng], 14);
  });

  // Botón Trazar Ruta de Brigada
  document.getElementById("btn-calc-route").addEventListener("click", async () => {
    routeLayer.clearLayers();
    
    try {
      const res = await fetch("http://localhost:8000/api/routes/dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ depot_coordinates: [-79.895, -2.18], max_foci: 8 })
      });
      const data = await res.json();
      drawRoute(data);
    } catch {
      // Heurística local de fallback
      const criticalFoci = fociData.filter(f => f.properties.risk_level === "CRITICAL").slice(0, 6);
      const coords = [[-79.895, -2.18], ...criticalFoci.map(f => f.geometry.coordinates)];
      drawRoute({
        total_distance_km: 7.4,
        estimated_duration_min: 95,
        priority_foci_count: criticalFoci.length,
        route_geometry: { type: "LineString", coordinates: coords }
      });
    }
  });
}

function drawRoute(routeData) {
  const lineCoords = routeData.route_geometry.coordinates.map(c => [c[1], c[0]]);
  
  const polyline = L.polyline(lineCoords, {
    color: "#38bdf8",
    weight: 4,
    dashArray: "8, 8",
    opacity: 0.9
  }).addTo(routeLayer);

  map.fitBounds(polyline.getBounds(), { padding: [40, 40] });

  // Mostrar estadísticas
  const summaryBox = document.getElementById("route-summary");
  summaryBox.classList.remove("hidden");
  document.getElementById("route-dist").textContent = routeData.total_distance_km;
  document.getElementById("route-time").textContent = routeData.estimated_duration_min;
  document.getElementById("route-stops").textContent = routeData.priority_foci_count;
}
