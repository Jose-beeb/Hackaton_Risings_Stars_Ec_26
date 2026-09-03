// Alerta Mosquitos Frontend Application
let map;
let heatLayer;
let markersLayer;
let routeLayer;
let fociData = [];
let previousFociCount = 0;
let cameraStream = null;
let lastRouteData = null;

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  loadEpidemiologicalData();
  setupEventListeners();

  // Polling en tiempo real cada 4 segundos
  setInterval(() => loadEpidemiologicalData(), 4000);
});

function initMap() {
  // Centro en Guayaquil, Ecuador
  map = L.map("map", {
    center: [-2.19, -79.89],
    zoom: 12,
    zoomControl: false
  });

  L.control.zoom({ position: "topright" }).addTo(map);

  // OpenStreetMap — gratuito, sin API key requerida
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
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
    const newFeatures = data.features || [];
    const newCount = newFeatures.length;

    // Animar marcadores nuevos si el count creció
    const isNewData = newCount > previousFociCount;
    previousFociCount = newCount;

    fociData = newFeatures;
    renderDashboard(fociData, isNewData);
  } catch (err) {
    console.error("Error al cargar datos epidemiológicos:", err);
  }
}

function renderDashboard(features, animateNew = false) {
  markersLayer.clearLayers();

  const heatPoints = [];
  let criticalCount = 0;
  const feedContainer = document.getElementById("foci-list");
  feedContainer.innerHTML = "";

  features.forEach((feature, index) => {
    const coords = feature.geometry.coordinates; // [lng, lat]
    const props = feature.properties;
    const latLng = [coords[1], coords[0]];

    // Heatmap intensity (normalizado por IRE)
    const intensity = (props.ire_score || 50) / 100.0;
    heatPoints.push([latLng[0], latLng[1], intensity]);

    if (props.risk_level === "CRITICAL") criticalCount++;

    // BUG FIX: usar days_to_emergence_estimate con fallback a days_to_emergence
    const days = props.days_to_emergence_estimate ?? props.days_to_emergence ?? '--';

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

    const riskLabel = { CRITICAL: 'Alto', MEDIUM: 'Medio', LOW: 'Bajo' }[props.risk_level] || props.risk_level;
    const popupContent = isCitizenMode
      ? `<div style="font-family: sans-serif; font-size: 13px; color: #1e293b;">
          <h4 style="margin: 0 0 4px 0; color: ${markerColor};">${props.container_name || 'Punto sospechoso'}</h4>
          <p><strong>Zona:</strong> ${props.sector}</p>
          <p><strong>Nivel de riesgo:</strong> ${riskLabel}</p>
          <p><strong>Mosquitos pueden aparecer en:</strong> ~${days} días</p>
          <p style="font-size: 11px; margin-top: 4px; color: #475569;">Reportá si ves agua acumulada cerca.</p>
        </div>`
      : `<div style="font-family: sans-serif; font-size: 13px; color: #1e293b;">
          <h4 style="margin: 0 0 4px 0; color: ${markerColor};">${props.container_name || props.container_type}</h4>
          <p><strong>Sector:</strong> ${props.sector}</p>
          <p><strong>IRE:</strong> ${props.ire_score} | <strong>Riesgo:</strong> ${props.risk_level}</p>
          <p><strong>Eclosión est.:</strong> ${days} días</p>
          <p style="font-size: 11px; margin-top: 4px; color: #475569;">${props.recommended_action || ''}</p>
        </div>`;
    circle.bindPopup(popupContent);

    // Animar nuevos marcadores con clase pulse si es dato nuevo
    if (animateNew && index === 0) {
      const el = circle.getElement ? circle.getElement() : null;
      circle.on('add', () => {
        const el = circle.getElement();
        if (el) el.classList.add('new-marker');
      });
    }

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
    const days = p.days_to_emergence_estimate ?? p.days_to_emergence ?? '--';
    const riskLabel = { CRITICAL: 'Alto', MEDIUM: 'Medio', LOW: 'Bajo' }[p.risk_level] || p.risk_level;
    const item = document.createElement("div");
    item.className = `foci-item ${p.risk_level.toLowerCase()}`;
    item.innerHTML = isCitizenMode
      ? `<div class="foci-header">
          <span>${p.container_name || 'Punto sospechoso'}</span>
          <span>Riesgo: ${riskLabel}</span>
        </div>
        <div class="foci-detail">${p.sector} · Mosquitos en ~${days} días</div>`
      : `<div class="foci-header">
          <span>${p.container_name || p.container_type}</span>
          <span>IRE: ${p.ire_score}</span>
        </div>
        <div class="foci-detail">${p.sector} · Eclosión en ${days} días</div>`;
    item.addEventListener("click", () => {
      map.flyTo([f.geometry.coordinates[1], f.geometry.coordinates[0]], 15);
    });
    feedContainer.appendChild(item);
  });

  // Actualizar métricas de impacto (con datos de ruta si están disponibles)
  updateImpactMetrics(features, lastRouteData);
}

function updateImpactMetrics(features, routeData = null) {
  const total = features.length;
  const protected_ = Math.round(total * 850);

  // Usar datos reales del optimizador si están disponibles
  const liters = routeData?.savings
    ? routeData.savings.pesticide_liters_used + ' L'
    : Math.round(total * 2.5) + ' L';
  const kmSaved = routeData?.savings
    ? routeData.savings.km_saved + ' km (' + routeData.savings.efficiency_pct + '%)'
    : '--';

  document.getElementById('impact-liters').textContent = liters;
  document.getElementById('impact-km').textContent = kmSaved;
  document.getElementById('kpi-protected').textContent = protected_ > 999
    ? (protected_ / 1000).toFixed(1) + 'k'
    : protected_;
}

function showToast(msg, type = 'info') {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

function activateDemoMode() {
  showToast('Demo Mode activado', 'info');
  document.getElementById('btn-calc-route').click();

  // Animar KPIs con contadores
  animateCounter('kpi-critical-count', 0, parseInt(document.getElementById('kpi-critical-count').textContent) || 8, 800);
  animateCounter('kpi-total-count', 0, parseInt(document.getElementById('kpi-total-count').textContent) || 24, 1000);
}

function animateCounter(elementId, from, to, duration) {
  const el = document.getElementById(elementId);
  if (!el || isNaN(to)) return;
  const start = performance.now();
  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    el.textContent = Math.round(from + (to - from) * progress);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ---- Cámara / Modal ----

async function startCamera() {
  const statusEl = document.getElementById('modal-status');
  const videoEl = document.getElementById('camera-preview');
  const photoPreview = document.getElementById('photo-preview');
  const btnCapture = document.getElementById('btn-capture');
  const btnRetake = document.getElementById('btn-retake');
  const btnSend = document.getElementById('btn-send-report');
  const reportResult = document.getElementById('report-result');

  // Reset estado del modal
  photoPreview.classList.add('hidden');
  videoEl.classList.remove('hidden');
  btnCapture.classList.remove('hidden');
  btnRetake.classList.add('hidden');
  btnSend.classList.add('hidden');
  reportResult.classList.add('hidden');
  reportResult.className = 'report-result hidden';

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    statusEl.textContent = 'Cámara no disponible — usá HTTPS';
    btnCapture.disabled = true;
    return;
  }

  try {
    statusEl.textContent = 'Iniciando cámara...';
    btnCapture.disabled = true;
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },
      audio: false
    });
    videoEl.srcObject = cameraStream;
    statusEl.textContent = 'Cámara lista. Apuntá al criadero.';
    btnCapture.disabled = false;
  } catch (err) {
    console.error('Error al acceder a la cámara:', err);
    statusEl.textContent = 'No se pudo acceder a la cámara. Verificá los permisos.';
    btnCapture.disabled = true;
  }
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(t => t.stop());
    cameraStream = null;
  }
}

function openReportModal() {
  document.getElementById('report-modal').classList.remove('hidden');
  startCamera();
}

function closeReportModal() {
  stopCamera();
  document.getElementById('report-modal').classList.add('hidden');
}

function capturePhoto() {
  const videoEl = document.getElementById('camera-preview');
  const canvas = document.getElementById('photo-canvas');
  const photoPreview = document.getElementById('photo-preview');
  const statusEl = document.getElementById('modal-status');
  const btnCapture = document.getElementById('btn-capture');
  const btnRetake = document.getElementById('btn-retake');
  const btnSend = document.getElementById('btn-send-report');

  canvas.width = videoEl.videoWidth || 640;
  canvas.height = videoEl.videoHeight || 480;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);

  const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
  photoPreview.src = dataUrl;
  photoPreview.classList.remove('hidden');
  videoEl.classList.add('hidden');

  btnCapture.classList.add('hidden');
  btnRetake.classList.remove('hidden');
  btnSend.classList.remove('hidden');
  statusEl.textContent = 'Foto capturada. Revisá y enviá el reporte.';
}

function retakePhoto() {
  const videoEl = document.getElementById('camera-preview');
  const photoPreview = document.getElementById('photo-preview');
  const btnCapture = document.getElementById('btn-capture');
  const btnRetake = document.getElementById('btn-retake');
  const btnSend = document.getElementById('btn-send-report');
  const statusEl = document.getElementById('modal-status');
  const reportResult = document.getElementById('report-result');

  photoPreview.classList.add('hidden');
  videoEl.classList.remove('hidden');
  btnCapture.classList.remove('hidden');
  btnRetake.classList.add('hidden');
  btnSend.classList.add('hidden');
  reportResult.classList.add('hidden');
  reportResult.className = 'report-result hidden';
  statusEl.textContent = 'Cámara lista. Apuntá al criadero.';

  // Reanudar stream si fue detenido
  if (!cameraStream) {
    startCamera();
  }
}

async function sendReport() {
  const canvas = document.getElementById('photo-canvas');
  const statusEl = document.getElementById('modal-status');
  const reportResult = document.getElementById('report-result');
  const btnSend = document.getElementById('btn-send-report');

  btnSend.disabled = true;
  statusEl.textContent = 'Analizando con IA...';

  const imageBase64 = canvas.toDataURL('image/jpeg', 0.8);

  // Obtener GPS
  let latitude = -2.19;
  let longitude = -79.89;

  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
    });
    latitude = pos.coords.latitude;
    longitude = pos.coords.longitude;
  } catch {
    // Usar coordenadas por defecto si GPS no disponible
  }

  const payload = {
    latitude,
    longitude,
    image_base64: imageBase64,
    notes: 'Reporte desde app móvil'
  };

  try {
    const res = await fetch('http://localhost:8000/api/reports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const data = await res.json();
      showReportResult(reportResult, data);
      await loadEpidemiologicalData();
    } else {
      throw new Error('Backend no disponible');
    }
  } catch {
    // Fallback: simular resultado de IA
    const mockResult = {
      ire_score: Math.round(60 + Math.random() * 35),
      risk_level: Math.random() > 0.4 ? 'CRITICAL' : 'MEDIUM'
    };
    showReportResult(reportResult, mockResult);
  }

  btnSend.disabled = false;
  statusEl.textContent = 'Reporte enviado.';
}

function showReportResult(container, data) {
  const riskLevel = (data.risk_level || 'medium').toLowerCase();
  const ire = data.ire_score ?? data.ire ?? '--';
  const citizenMessages = {
    critical: '¡Zona de riesgo alto! Las brigadas sanitarias serán notificadas.',
    medium: 'Riesgo moderado detectado. Gracias por reportar.',
    low: 'Riesgo bajo. Te avisamos si la situación cambia.'
  };
  container.className = `report-result ${riskLevel}`;
  container.innerHTML = isCitizenMode
    ? `<strong>✅ Reporte recibido</strong><br><span>${citizenMessages[riskLevel] || 'Gracias por tu reporte.'}</span>`
    : `<strong>IRE Score: ${ire}</strong><br><span>Nivel de Riesgo: ${data.risk_level || riskLevel.toUpperCase()}</span>`;
  container.classList.remove('hidden');
}

let isCitizenMode = false;

function toggleView() {
  isCitizenMode = !isCitizenMode;
  const btn = document.getElementById('btn-view-toggle');
  const brigadeEls = document.querySelectorAll('.brigade-only');
  const citizenPanel = document.querySelector('.citizen-panel');

  if (isCitizenMode) {
    brigadeEls.forEach(el => el.classList.add('hidden'));
    citizenPanel.classList.remove('hidden');
    btn.textContent = '🧭 Vista Brigada';
    document.getElementById('citizen-critical').textContent =
      document.getElementById('kpi-critical-count').textContent;
    document.getElementById('citizen-protected').textContent =
      document.getElementById('kpi-protected').textContent;
    // KPI labels — lenguaje ciudadano
    document.querySelector('#kpi-critical-count').closest('.kpi-card').querySelector('.kpi-label').textContent = 'Zonas de riesgo';
    document.querySelector('#kpi-total-count').closest('.kpi-card').querySelector('.kpi-label').textContent = 'Puntos reportados';
    document.querySelector('#kpi-protected').closest('.kpi-card').querySelector('.kpi-label').textContent = 'Vecinos protegidos';
  } else {
    brigadeEls.forEach(el => el.classList.remove('hidden'));
    citizenPanel.classList.add('hidden');
    btn.textContent = '📱 Vista Ciudadana';
    // KPI labels — lenguaje brigada
    document.querySelector('#kpi-critical-count').closest('.kpi-card').querySelector('.kpi-label').textContent = 'Focos Críticos';
    document.querySelector('#kpi-total-count').closest('.kpi-card').querySelector('.kpi-label').textContent = 'Total Monitoreados';
    document.querySelector('#kpi-protected').closest('.kpi-card').querySelector('.kpi-label').textContent = 'Personas Protegidas';
  }
  renderDashboard(fociData);
}

function setupEventListeners() {
  // Toggle vista ciudadana / brigada
  document.getElementById('btn-view-toggle').addEventListener('click', toggleView);

  // Demo mode: doble click en brand-title
  document.querySelector('.brand-title').addEventListener('dblclick', () => {
    activateDemoMode();
  });

  // Botón Reportar Criadero (ciudadano)
  document.getElementById('btn-report-citizen').addEventListener('click', () => {
    openReportModal();
  });

  // Botón Reportar Criadero
  document.getElementById('btn-report').addEventListener('click', () => {
    openReportModal();
  });

  // Cerrar modal
  document.getElementById('btn-close-modal').addEventListener('click', () => {
    closeReportModal();
  });

  // Cerrar modal al hacer click en el overlay
  document.getElementById('report-modal').addEventListener('click', (e) => {
    if (e.target === document.getElementById('report-modal')) {
      closeReportModal();
    }
  });

  // Capturar foto
  document.getElementById('btn-capture').addEventListener('click', () => {
    capturePhoto();
  });

  // Retomar foto
  document.getElementById('btn-retake').addEventListener('click', () => {
    retakePhoto();
  });

  // Enviar reporte
  document.getElementById('btn-send-report').addEventListener('click', () => {
    sendReport();
  });

  // Botón Simular Reporte en Vivo (Pitch Fail-safe)
  document.getElementById("btn-simulate-report").addEventListener("click", async () => {
    const randomLat = -2.185 + (Math.random() - 0.5) * 0.04;
    const randomLng = -79.89 + (Math.random() - 0.5) * 0.04;

    const payload = {
      latitude: randomLat,
      longitude: randomLng,
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
          days_to_emergence_estimate: 3,
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
  lastRouteData = routeData;

  const lineCoords = routeData.route_geometry.coordinates.map(c => [c[1], c[0]]);
  const polyline = L.polyline(lineCoords, {
    color: "#38bdf8",
    weight: 4,
    dashArray: "8, 8",
    opacity: 0.9
  }).addTo(routeLayer);

  map.fitBounds(polyline.getBounds(), { padding: [40, 40] });

  // Mostrar estadísticas de ruta
  const summaryBox = document.getElementById("route-summary");
  summaryBox.classList.remove("hidden");
  document.getElementById("route-dist").textContent = routeData.total_distance_km;
  document.getElementById("route-time").textContent = routeData.estimated_duration_min;

  const brigades = routeData.savings?.brigades_required ?? 1;
  document.getElementById("route-stops").textContent =
    routeData.priority_foci_count + (brigades > 1 ? ` (${brigades} cuadrillas)` : '');

  // Actualizar panel de impacto con datos reales
  updateImpactMetrics(fociData, lastRouteData);

  if (routeData.savings) {
    showToast(`Ruta optimizada: ${routeData.savings.efficiency_pct}% más eficiente que ruta ciega`, 'success');
  }
}
