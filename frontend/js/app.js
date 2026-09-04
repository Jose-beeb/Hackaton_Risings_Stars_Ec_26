// Ojito al Mosquito — Frontend Application
let map;
let heatLayer;
let markersLayer;
let routeLayer;
let fociData = [];
let demoFoci = [];        // focos agregados en demo mode — sobreviven el polling
let previousFociHash = '';
let cameraStream = null;
let lastRouteData = null;
let brigadePolylines = {};   // brigade_id -> capa Leaflet, para poder sacar una sola al marcarla cumplida

const MOBILE_BREAKPOINT = 860;

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  loadEpidemiologicalData();
  setupEventListeners();

  // Vista Ciudadana por defecto al iniciar — se puede seguir alternando
  // con el mismo boton de siempre. toggleView() ya deja todo consistente
  // (paneles, labels de KPI, texto del boton), asi que se reusa en vez de
  // duplicar esa logica.
  toggleView();

  // En mobile arranca oculto para que el mapa sea lo primero que se ve —
  // en desktop arranca visible, igual que siempre.
  if (window.innerWidth <= MOBILE_BREAKPOINT) {
    document.getElementById('sidebar').classList.add('hidden');
    // Al ocultar el sidebar el mapa crece (flex:1 reclama el alto liberado),
    // pero Leaflet ya midio el contenedor en initMap() con el tamaño viejo —
    // sin avisarle, deja una franja gris sin tiles en el espacio nuevo.
    requestAnimationFrame(() => map.invalidateSize());
  }

  updateHeaderHeightVar();
  window.addEventListener('resize', updateHeaderHeightVar);

  // Google Fonts carga async: si el texto del header cambia de fuente
  // despues de initMap() y eso lo hace envolver a 2 filas, el alto
  // disponible para el mapa cambia y Leaflet queda con tiles de mas o
  // de menos otra vez — mismo problema que el hide del sidebar de arriba.
  window.addEventListener('load', () => map.invalidateSize());

  // Polling en tiempo real cada 4 segundos
  setInterval(() => loadEpidemiologicalData(), 4000);
});

// El header tiene alto variable (los botones se acomodan en 1 o 2 filas
// segun el ancho), asi que el drawer no puede asumir un top fijo o termina
// tapando el logo y los botones de vista/reportar/simular — se mide la
// altura real y se la pasa al CSS como variable.
function updateHeaderHeightVar() {
  const header = document.querySelector('.app-header');
  document.documentElement.style.setProperty('--header-height', `${header.offsetHeight}px`);
}

// Aplica igual en Vista Ciudadana y Vista Brigada — opera sobre el
// contenedor #sidebar, no sobre los paneles de adentro (esos los maneja
// toggleView() por separado).
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  const isHidden = sidebar.classList.toggle('hidden');
  backdrop.classList.toggle('hidden', isHidden);

  // El mapa cambia de ancho al mostrar/ocultar el sidebar en desktop —
  // Leaflet necesita que se lo avisen o deja tiles a medio cargar.
  requestAnimationFrame(() => map.invalidateSize());
}

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
    const hash = newFeatures.length + '_' + (newFeatures[0]?.properties?.id ?? '');

    // Solo redibujar si los datos cambiaron — evita el flicker del polling
    if (hash === previousFociHash) return;
    const isNewData = newFeatures.length > (fociData.length - demoFoci.length);
    previousFociHash = hash;

    fociData = [...demoFoci, ...newFeatures];
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

  // Antes esto solo se sincronizaba al tocar "Vista Ciudadana" — si esa
  // vista arranca por defecto, quedaba en "--" hasta el primer toggle.
  document.getElementById('citizen-critical').textContent =
    document.getElementById('kpi-critical-count').textContent;
  document.getElementById('citizen-protected').textContent =
    document.getElementById('kpi-protected').textContent;
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
  const btnUpload = document.getElementById('btn-upload');
  const btnRetake = document.getElementById('btn-retake');
  const btnSend = document.getElementById('btn-send-report');
  const reportResult = document.getElementById('report-result');

  // Reset estado del modal
  photoPreview.classList.add('hidden');
  videoEl.classList.remove('hidden');
  btnCapture.classList.remove('hidden');
  btnUpload.classList.remove('hidden');
  btnRetake.classList.add('hidden');
  btnSend.classList.add('hidden');
  reportResult.classList.add('hidden');
  reportResult.className = 'report-result hidden';

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    statusEl.textContent = 'Cámara no disponible — podés subir una foto.';
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
    statusEl.textContent = 'No se pudo acceder a la cámara. Verificá los permisos o subí una foto.';
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
  const btnUpload = document.getElementById('btn-upload');
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
  btnUpload.classList.add('hidden');
  btnRetake.classList.remove('hidden');
  btnSend.classList.remove('hidden');
  statusEl.textContent = 'Foto capturada. Revisá y enviá el reporte.';
}

// Vuelca un archivo de imagen elegido por el usuario al mismo canvas que usa
// la cámara, para que sendReport() no tenga que distinguir el origen de la foto.
function handleFileUpload(file) {
  if (!file || !file.type.startsWith('image/')) return;

  const statusEl = document.getElementById('modal-status');
  const videoEl = document.getElementById('camera-preview');
  const canvas = document.getElementById('photo-canvas');
  const photoPreview = document.getElementById('photo-preview');
  const btnCapture = document.getElementById('btn-capture');
  const btnUpload = document.getElementById('btn-upload');
  const btnRetake = document.getElementById('btn-retake');
  const btnSend = document.getElementById('btn-send-report');

  const objectUrl = URL.createObjectURL(file);
  const img = new Image();

  img.onload = () => {
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    canvas.getContext('2d').drawImage(img, 0, 0);
    URL.revokeObjectURL(objectUrl);

    photoPreview.src = canvas.toDataURL('image/jpeg', 0.8);
    photoPreview.classList.remove('hidden');
    videoEl.classList.add('hidden');

    btnCapture.classList.add('hidden');
    btnUpload.classList.add('hidden');
    btnRetake.classList.remove('hidden');
    btnSend.classList.remove('hidden');
    statusEl.textContent = 'Foto cargada. Revisá y enviá el reporte.';
  };
  img.onerror = () => {
    URL.revokeObjectURL(objectUrl);
    statusEl.textContent = 'No se pudo cargar la imagen seleccionada.';
  };
  img.src = objectUrl;
}

function retakePhoto() {
  const videoEl = document.getElementById('camera-preview');
  const photoPreview = document.getElementById('photo-preview');
  const btnCapture = document.getElementById('btn-capture');
  const btnUpload = document.getElementById('btn-upload');
  const btnRetake = document.getElementById('btn-retake');
  const btnSend = document.getElementById('btn-send-report');
  const statusEl = document.getElementById('modal-status');
  const reportResult = document.getElementById('report-result');

  photoPreview.classList.add('hidden');
  videoEl.classList.remove('hidden');
  btnCapture.classList.remove('hidden');
  btnUpload.classList.remove('hidden');
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

// Consejo de accion fisica inmediata segun el tipo de deposito detectado —
// cierra el bucle comunitario: la persona recibe algo que puede hacer YA,
// sin esperar a que llegue la brigada. Validado con criterio entomologico
// basico (huevos de Aedes se pegan a la pared seca del recipiente, por eso
// "cepillar" y no solo "vaciar").
const HOME_ACTION_TIPS = {
  tire: 'Perforá la llanta para que no vuelva a acumular agua, o guardala bajo techo seco.',
  open_tank: 'Cepillá las paredes internas (los huevos se pegan al borde seco) y tapá herméticamente con malla o lona.',
  bucket: 'Volteá el balde o vacialo por completo. Si no lo usás, guardalo bajo techo.',
  flowerpot: 'Vaciá el plato bajo la maceta cada 3 días, o rellenalo con arena para que no junte agua.',
  clogged_drain: 'Sacá las hojas y la basura de la canaleta para que el agua no se estanque.',
  litter_plastic: 'Juntá y desechá botellas, vasos o bolsas que puedan acumular agua de lluvia.',
  puddle: 'Rellená el hueco con tierra o mejorá el drenaje de esa zona del patio.',
  other: 'Eliminá o cubrí el recipiente para que no vuelva a acumular agua.',
  none: 'No se detectó un criadero en esta foto. Igual, revisá el patio cada semana buscando agua estancada.'
};

function showReportResult(container, data) {
  // El backend anida el resultado bajo risk_assessment (ver POST /api/reports
  // en main.py) — no viene en la raiz del payload.
  const riskAssessment = data.risk_assessment || {};
  const riskLevel = (riskAssessment.risk_level || 'medium').toLowerCase();
  const ire = riskAssessment.ire_score ?? '--';
  const citizenMessages = {
    critical: '¡Zona de riesgo alto! Las brigadas sanitarias serán notificadas.',
    medium: 'Riesgo moderado detectado. Gracias por reportar.',
    low: 'Riesgo bajo. Te avisamos si la situación cambia.'
  };
  const containerType = data.classification?.container_type;
  const actionTip = HOME_ACTION_TIPS[containerType];
  const actionCard = actionTip
    ? `<div class="action-card"><strong>🛠️ Qué podés hacer ahora mismo:</strong><p>${actionTip}</p></div>`
    : '';

  container.className = `report-result ${riskLevel}`;
  container.innerHTML = (isCitizenMode
    ? `<strong>✅ Reporte recibido</strong><br><span>${citizenMessages[riskLevel] || 'Gracias por tu reporte.'}</span>`
    : `<strong>IRE Score: ${ire}</strong><br><span>Nivel de Riesgo: ${riskAssessment.risk_level || riskLevel.toUpperCase()}</span>`
  ) + actionCard;
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
  updateHeaderHeightVar();  // el texto del boton cambia de largo y puede alterar el wrap del header
}

function setupEventListeners() {
  // Toggle vista ciudadana / brigada
  document.getElementById('btn-view-toggle').addEventListener('click', toggleView);

  // Mostrar/ocultar panel informativo (hamburguesa) — misma funcion en las
  // dos vistas, y cerrar tocando el fondo oscuro en mobile.
  document.getElementById('btn-toggle-sidebar').addEventListener('click', toggleSidebar);
  document.getElementById('sidebar-backdrop').addEventListener('click', toggleSidebar);

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

  // Subir foto desde galería/archivos
  document.getElementById('btn-upload').addEventListener('click', () => {
    document.getElementById('photo-file-input').click();
  });
  document.getElementById('photo-file-input').addEventListener('change', (e) => {
    const file = e.target.files && e.target.files[0];
    handleFileUpload(file);
    e.target.value = ''; // permite volver a elegir el mismo archivo
  });

  // Modal "Confirmar Cuadrilla Cumplida"
  document.getElementById('btn-close-complete-modal').addEventListener('click', closeCompleteBrigadeModal);
  document.getElementById('complete-brigade-modal').addEventListener('click', (e) => {
    if (e.target === document.getElementById('complete-brigade-modal')) {
      closeCompleteBrigadeModal();
    }
  });
  document.getElementById('input-after-photo').addEventListener('change', (e) => {
    const file = e.target.files && e.target.files[0];
    const preview = document.getElementById('after-photo-preview');
    if (!file) {
      afterPhotoBase64 = null;
      preview.classList.add('hidden');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      afterPhotoBase64 = reader.result;  // data:image/...;base64,... — se guarda tal cual, no se decodifica
      preview.src = reader.result;
      preview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  });
  document.getElementById('btn-confirm-complete-brigade').addEventListener('click', confirmCompleteBrigade);

  // Retomar foto
  document.getElementById('btn-retake').addEventListener('click', () => {
    retakePhoto();
  });

  // Enviar reporte
  document.getElementById('btn-send-report').addEventListener('click', () => {
    sendReport();
  });

  // Botón Simular Reporte en Vivo (Pitch Fail-safe — siempre CRITICAL para la demo)
  document.getElementById("btn-simulate-report").addEventListener("click", async () => {
    const randomLat = -2.185 + (Math.random() - 0.5) * 0.04;
    const randomLng = -79.89 + (Math.random() - 0.5) * 0.04;

    const newFeature = {
      type: "Feature",
      geometry: { type: "Point", coordinates: [randomLng, randomLat] },
      properties: {
        id: `foco-live-${Date.now()}`,
        sector: "Reporte Ciudadano en Vivo",
        container_name: "Llanta con agua",
        container_category: "artificial",
        ire_score: 91.4,
        risk_level: "CRITICAL",
        risk_type: "ACTIVE",
        days_to_emergence_estimate: 7,
        recommended_action: "Intervención prioritaria: drenaje inmediato y aplicación de larvicida.",
        status: "PENDING",
        reported_at: new Date().toISOString(),
      }
    };

    demoFoci.unshift(newFeature);
    fociData = [...demoFoci, ...fociData.filter(f => !demoFoci.includes(f))];
    renderDashboard(fociData, true);
    map.setView([randomLat, randomLng], 14, { animate: false });
    showToast('Nuevo reporte crítico recibido', 'success');
  });

  // Config de brigadas: filas dinamicas segun el tope maximo ingresado
  const inputMaxBrigades = document.getElementById("input-max-brigades");
  renderBrigadeConfigRows(parseInt(inputMaxBrigades.value, 10) || 1);
  inputMaxBrigades.addEventListener("input", () => {
    const n = Math.max(1, Math.min(10, parseInt(inputMaxBrigades.value, 10) || 1));
    renderBrigadeConfigRows(n);
  });

  // Botón Trazar Ruta de Brigada
  document.getElementById("btn-calc-route").addEventListener("click", async () => {
    routeLayer.clearLayers();

    try {
      const res = await fetch("http://localhost:8000/api/routes/dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          depot_coordinates: [-79.895, -2.18],
          max_foci: 16,
          max_brigades: parseInt(inputMaxBrigades.value, 10) || 1,
          brigade_configs: collectBrigadeConfigs()
        })
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

const BRIGADE_COLORS = ['#38bdf8', '#a855f7', '#f97316', '#84cc16', '#ec4899'];

// Debe coincidir con TRANSPORT_MODES en core/logistics/route_optimizer.py.
// Cada modo corresponde a un tipo de brigada de campo distinto — ver el
// comentario en ese archivo para la procedencia de cada numero (no todas
// las cifras tienen el mismo nivel de respaldo cientifico todavia).
const TRANSPORT_MODE_LABELS = {
  foot: 'A pie — Control Focal',
  vehicle_walk_attack: 'Vehículo + ataque a pie — Rociado Residual',
  vehicle_spray: 'Vehículo fumigador — Fumigación Espacial'
};

// Crea/actualiza las filas de configuracion (fumigadores + transporte) para
// el numero de brigadas indicado, preservando los valores ya ingresados.
function renderBrigadeConfigRows(count) {
  const container = document.getElementById('brigade-config-rows');
  const previous = collectBrigadeConfigs();
  container.innerHTML = '';

  for (let i = 0; i < count; i++) {
    const prev = previous[i] || { fumigadores: 2, transport_mode: 'vehicle_spray' };
    const row = document.createElement('div');
    row.className = 'brigade-config-row';
    row.innerHTML = `
      <span class="brigade-row-label">Brigada ${i + 1}</span>
      <input type="number" min="1" max="10" value="${prev.fumigadores}"
             class="brigade-cfg-fumigadores" title="Fumigadores/operarios">
      <select class="brigade-cfg-transport" title="Tipo de transporte">
        ${Object.entries(TRANSPORT_MODE_LABELS).map(([value, label]) =>
          `<option value="${value}" ${value === prev.transport_mode ? 'selected' : ''}>${label}</option>`
        ).join('')}
      </select>
    `;
    container.appendChild(row);
  }
}

// Lee la config actual de todas las filas de brigada renderizadas.
function collectBrigadeConfigs() {
  const rows = document.querySelectorAll('#brigade-config-rows .brigade-config-row');
  return Array.from(rows).map(row => ({
    fumigadores: parseInt(row.querySelector('.brigade-cfg-fumigadores').value, 10) || 2,
    transport_mode: row.querySelector('.brigade-cfg-transport').value
  }));
}

function drawRoute(routeData) {
  lastRouteData = routeData;
  routeLayer.clearLayers();
  brigadePolylines = {};

  const brigades = routeData.brigades;
  let firstPolyline = null;

  const legendContainer = document.getElementById('brigade-legend-items');
  legendContainer.innerHTML = '';

  if (brigades && brigades.length > 0) {
    brigades.forEach((brigade, idx) => {
      const color = BRIGADE_COLORS[idx % BRIGADE_COLORS.length];

      const legendItem = document.createElement('div');
      legendItem.className = 'legend-item';
      legendItem.innerHTML = `<span class="line-indicator" style="background:${color}"></span> ${brigade.brigade_id}`;
      legendContainer.appendChild(legendItem);

      const lineCoords = brigade.route_geometry.coordinates.map(c => [c[1], c[0]]);
      const polyline = L.polyline(lineCoords, {
        color,
        weight: 4,
        dashArray: "8, 8",
        opacity: 0.9
      }).addTo(routeLayer);
      brigadePolylines[brigade.brigade_id] = polyline;

      const transportLabel = TRANSPORT_MODE_LABELS[brigade.transport_mode] || brigade.transport_mode || '';
      const crewLabel = brigade.fumigadores ? ` · ${brigade.fumigadores} fumigadores` : '';
      polyline.bindTooltip(
        `${brigade.brigade_id} · ${brigade.stops_count} focos · ${brigade.distance_km} km` +
        (transportLabel ? ` · ${transportLabel}` : '') + crewLabel,
        { sticky: true }
      );

      if (idx === 0) firstPolyline = polyline;
    });
  } else {
    // Fallback: ruta única sin datos de brigadas
    const lineCoords = routeData.route_geometry.coordinates.map(c => [c[1], c[0]]);
    firstPolyline = L.polyline(lineCoords, {
      color: BRIGADE_COLORS[0],
      weight: 4,
      dashArray: "8, 8",
      opacity: 0.9
    }).addTo(routeLayer);
  }

  if (firstPolyline) {
    map.fitBounds(firstPolyline.getBounds(), { padding: [40, 40] });
  }

  // Resumen de ruta
  const summaryBox = document.getElementById("route-summary");
  summaryBox.classList.remove("hidden");
  document.getElementById("route-dist").textContent = routeData.total_distance_km;

  // estimated_duration_min es un campo agregado que NO depende de la config
  // por brigada (fumigadores/transporte) — por eso cambiar esos valores no
  // se notaba en el resumen. Como las brigadas trabajan en paralelo, el
  // tiempo real de la operacion lo marca la mas lenta.
  const brigadeDurations = (brigades || []).map(b => b.duration_min).filter(n => typeof n === 'number');
  const displayDuration = brigadeDurations.length > 0
    ? Math.max(...brigadeDurations)
    : routeData.estimated_duration_min;
  document.getElementById("route-time").textContent = displayDuration;

  const brigadeCount = routeData.savings?.brigades_required ?? 1;
  document.getElementById("route-stops").textContent =
    routeData.priority_foci_count + (brigadeCount > 1 ? ` (${brigadeCount} cuadrillas)` : '');

  updateImpactMetrics(fociData, lastRouteData);
  renderBrigadeStatusList(brigades);

  if (routeData.savings) {
    const msg = brigadeCount > 1
      ? `${brigadeCount} cuadrillas · ${routeData.savings.efficiency_pct}% más eficiente que ruta ciega`
      : `Ruta optimizada: ${routeData.savings.efficiency_pct}% más eficiente que ruta ciega`;
    showToast(msg, 'success');
  }
}

// Lista con el tiempo real de cada brigada y un boton para marcarla
// cumplida (soluciona: el tooltip del mapa requiere hover, esto queda
// visible siempre; y agrega la accion de cerrar la ruta de una brigada).
function renderBrigadeStatusList(brigades) {
  const container = document.getElementById('brigade-status-list');
  container.innerHTML = '';
  if (!brigades || brigades.length === 0) return;

  brigades.forEach((brigade, idx) => {
    const color = BRIGADE_COLORS[idx % BRIGADE_COLORS.length];
    const transportLabel = TRANSPORT_MODE_LABELS[brigade.transport_mode] || brigade.transport_mode || '';
    const timeMin = Math.round(brigade.tiempo_total_minutos ?? brigade.duration_min ?? 0);
    const warning = brigade.excede_jornada
      ? ' · <span class="brigade-warning">⚠ excede jornada de 6h</span>'
      : '';

    const row = document.createElement('div');
    row.className = 'brigade-status-row';
    row.dataset.brigadeId = brigade.brigade_id;
    row.innerHTML = `
      <span class="brigade-dot" style="background:${color}"></span>
      <div class="brigade-info">
        <strong>${brigade.brigade_id}</strong>
        <span class="brigade-meta">${brigade.stops_count} focos · ${timeMin} min · ${transportLabel}${warning}</span>
      </div>
      <button class="btn-complete-brigade" data-brigade-id="${brigade.brigade_id}">✓ Cumplida</button>
    `;
    container.appendChild(row);
  });

  container.querySelectorAll('.btn-complete-brigade').forEach(btn => {
    btn.addEventListener('click', () => completeBrigade(btn.dataset.brigadeId));
  });
}

// --- Modulo Antes/Despues: cerrar la ruta de una brigada exige nombre de
// operador + foto de confirmacion (evidencia de que la intervencion se hizo
// de verdad, no solo un click). Abre el modal en vez de resolver directo.
let pendingCompleteBrigadeId = null;
let afterPhotoBase64 = null;

function completeBrigade(brigadeId) {
  if (!lastRouteData || !lastRouteData.brigades) return;
  const brigade = lastRouteData.brigades.find(b => b.brigade_id === brigadeId);
  if (!brigade) return;

  pendingCompleteBrigadeId = brigadeId;
  afterPhotoBase64 = null;
  document.getElementById('input-operator-name').value = '';
  document.getElementById('input-after-photo').value = '';
  document.getElementById('after-photo-preview').classList.add('hidden');
  document.getElementById('complete-brigade-modal').classList.remove('hidden');
}

function closeCompleteBrigadeModal() {
  pendingCompleteBrigadeId = null;
  document.getElementById('complete-brigade-modal').classList.add('hidden');
}

// Marca los focos de la brigada pendiente como resueltos en el backend, saca
// su linea del mapa y refresca el resto del dashboard (que ya no los trae).
async function confirmCompleteBrigade() {
  const brigadeId = pendingCompleteBrigadeId;
  if (!brigadeId || !lastRouteData || !lastRouteData.brigades) return;
  const brigade = lastRouteData.brigades.find(b => b.brigade_id === brigadeId);
  if (!brigade) return;

  const operatorName = document.getElementById('input-operator-name').value.trim();
  const btnConfirm = document.getElementById('btn-confirm-complete-brigade');
  btnConfirm.disabled = true;
  btnConfirm.textContent = 'Confirmando...';

  const row = document.querySelector(`.brigade-status-row[data-brigade-id="${brigadeId}"]`);
  const rowBtn = row ? row.querySelector('.btn-complete-brigade') : null;

  try {
    const res = await fetch('http://localhost:8000/api/foci/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        foco_ids: brigade.secuencia_paradas || [],
        brigade_id: brigadeId,
        // "Firma digital" en el alcance de este demo es nombre + timestamp
        // del operador — no una firma criptografica real. Aclarar en el
        // pitch si el jurado pregunta.
        operator_name: operatorName || null,
        after_photo_base64: afterPhotoBase64
      })
    });
    if (!res.ok) throw new Error('resolve fallo');
    const data = await res.json();

    if (brigadePolylines[brigadeId]) {
      routeLayer.removeLayer(brigadePolylines[brigadeId]);
      delete brigadePolylines[brigadeId];
    }
    if (row) row.classList.add('completed');
    if (rowBtn) rowBtn.textContent = '✓ Hecho';

    closeCompleteBrigadeModal();
    await loadEpidemiologicalData();  // /api/foci ya no devuelve los resueltos
    showToast(`${brigadeId} completada — ${data.resolved_count} focos resueltos`, 'success');
  } catch (err) {
    console.error('Error al marcar brigada como cumplida:', err);
    showToast('No se pudo marcar la brigada como cumplida', 'error');
  } finally {
    btnConfirm.disabled = false;
    btnConfirm.textContent = '✓ Confirmar';
  }
}
