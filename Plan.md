# AedesGuard — Plan Estratégico y Arquitectura Técnica MVP

**Competencia:** IEEE Rising Stars 2026 Hackathon (Track 2: Public Health)  
**Proyecto:** AedesGuard (Sistema de Inteligencia Epidemiológica y Control Vectorial Predictivo)  
**Modalidad:** Plataforma 100% de Software (PWA Móvil + Backend Orquestador + Dashboard GIS Predictivo)

---

## 1. Estrategia de Trabajo: ¿Monolito Compartido o Módulos Desacoplados?

### Veredicto de Arquitectura: **Monorepo Modular con Enfoque "Contract-First" (Diseño por Contrato)**

> [!CAUTION]
> **El peligro del "Big Bang Integration":** En una hackathon de 4 días, dejar que cada persona trabaje aislada en su carpeta y pretender que "alguien integre todo al final" es la causa #1 de fracaso. Termina en merge conflicts destructivos, formatos de datos incompatibles y horas perdidas a las 3 AM antes de la entrega.
> 
> Tampoco se debe trabajar todo en un solo archivo a la vez porque se bloquean mutuamente.

### La Solución Ganadora:
1. **Estructura Modular por Carpetas:** Cada rol trabaja en su propio directorio con límites de responsabilidad bien definidos.
2. **Contrato de API Inmutable desde la Hora 1:** Todo el equipo acuerda los esquemas de datos (JSON / GeoJSON) antes de escribir código funcional.
3. **Desarrollo en Paralelo con Mock Data:**
   * El Frontend no espera al Backend; consume un servidor mock o datos locales con el contrato acordado.
   * El Backend no espera la fórmula final de biotecnología; consume una función con interfaz estándar que devuelve un valor dummy.
   * La Biotecnóloga y el Mecatrónico desarrollan la lógica pura (fórmulas y optimizador de rutas) en scripts independientes que luego se importan sin fricción.
4. **Integración Continua (Shift-Left):** La integración ocurre desde el **Día 2**, no al final del Día 4.

---

## 2. Estructura de Carpetas del Proyecto

```text
Hackaton_ElNino/
├── docs/                             # Especificaciones de API, diseño y pitch
│   ├── API_CONTRACT.md               # Esquemas canónicos de datos (JSON/GeoJSON)
│   └── PITCH_SCRIPT.md               # Minuto a minuto de la presentación
├── roles/                            # Preguntas y especificaciones por perfil
│   ├── 01_biotecnologia_preguntas.md
│   ├── 02_mecatronica_preguntas.md
│   ├── 03_software_backend_preguntas.md
│   └── 04_software_frontend_preguntas.md
├── core/                             # Lógica pura de dominio (sin acoplamiento web)
│   ├── bio_engine/                   # Rol: Biotecnología
│   │   ├── ire_calculator.py         # Fórmula matemática del IRE y eclosión
│   │   └── vision_prompts.py         # System prompts y esquemas para VLM
│   └── logistics/                    # Rol: Mecatrónica
│       ├── route_optimizer.py        # Algoritmo de optimización de rutas (TSP/Greedy)
│       └── mock_foci_generator.py    # Generador de 40 puntos GeoJSON de prueba
├── backend/                          # Rol: Software 1
│   ├── app/
│   │   ├── main.py                   # Servidor FastAPI
│   │   ├── routers/                  # Endpoints (/reports, /foci, /routes)
│   │   ├── services/                 # Clientes Open-Meteo, Gemini Vision
│   │   └── db.py                     # Almacén de GeoJSON / persistencia
│   └── requirements.txt
└── frontend/                         # Rol: Software 2
    ├── index.html                    # Single Page App (PWA + Dashboard)
    ├── css/                          # Vanilla CSS con diseño moderno y tema oscuro
    ├── js/
    │   ├── app.js                    # Router y estado de la aplicación
    │   ├── report_capture.js         # Vista móvil: Cámara, GPS y feedback
    │   └── gis_dashboard.js          # Vista municipal: Leaflet + Heatmap + Despacho
    └── assets/                       # Iconos, badges e imágenes de muestra
```

---

## 3. Contratos Canónicos de Datos (API Contract)

### A. Reporte de Criadero (`POST /api/reports`)
* **Request (Multipart o JSON):**
```json
{
  "latitude": -2.1894,
  "longitude": -79.8891,
  "image_base64": "data:image/jpeg;base64,...",
  "notes": "Llantas acumuladas en patio trasero"
}
```
* **Response:**
```json
{
  "id": "foco-042",
  "timestamp": "2026-09-02T13:45:00Z",
  "coordinates": [-79.8891, -2.1894],
  "classification": {
    "container_type": "tire",
    "water_detected": true,
    "confidence": 0.94
  },
  "climate": {
    "temperature_c": 28.5,
    "humidity_pct": 82
  },
  "risk_assessment": {
    "ire_score": 88.5,
    "risk_level": "CRITICAL",
    "days_to_emergence": 4,
    "recommended_action": "Drenaje inmediato y aplicación de larvicida biológico."
  }
}
```

### B. Capa Geoespacial para Dashboard (`GET /api/foci`)
* **Response (GeoJSON FeatureCollection estándar):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-79.8891, -2.1894]
      },
      "properties": {
        "id": "foco-042",
        "container_type": "tire",
        "ire_score": 88.5,
        "risk_level": "CRITICAL",
        "days_to_emergence": 4,
        "status": "PENDING"
      }
    }
  ]
}
```

### C. Despacho y Rutas de Cuadrillas (`POST /api/routes/dispatch`)
* **Response:**
```json
{
  "brigade_id": "cuadrilla-norte-1",
  "total_distance_km": 6.8,
  "estimated_duration_min": 110,
  "priority_foci_count": 5,
  "route_geometry": {
    "type": "LineString",
    "coordinates": [
      [-79.8891, -2.1894],
      [-79.8920, -2.1850],
      [-79.8965, -2.1812]
    ]
  },
  "itinerary": [
    { "order": 1, "foco_id": "foco-042", "action": "Abatización focalizada" },
    { "order": 2, "foco_id": "foco-019", "action": "Eliminación física" }
  ]
}
```

---

## 4. Cronograma de Ejecución de 4 Días

| Fase / Día | Objetivo Principal | Entregables Clave |
| :--- | :--- | :--- |
| **Día 1: Contratos y Setup** | Alinear arquitectura, fijar contratos JSON y mock data. | • Responder cuestionarios de roles.<br>• Generar mock data de 40 puntos en Guayaquil.<br>• Skeleton de FastAPI y UI con mapas Leaflet. |
| **Día 2: Desarrollo Desacoplado** | Construcción de módulos independientes. | • **Bio:** Función matemática del IRE + prompt VLM.<br>• **Meca:** Algoritmo de ruteo TSP + unit economics.<br>• **Soft 1:** Pipeline visión + Open-Meteo integrado.<br>• **Soft 2:** PWA de captura GPS y heatmap funcional. |
| **Día 3: Integración y Tiempo Real** | Conexión de frontend con backend orquestador. | • End-to-end funcional (foto en PWA $\rightarrow$ actualización en vivo en mapa).<br>• Capa de ruteo de cuadrillas visible en mapa. |
| **Día 4: Resiliencia, Pulido y Pitch** | Cero riesgos en vivo, narrativa B2B/B2G y ensayo. | • Sistema de Fallbacks / Modo Offline para demo.<br>• Métricas de impacto financiero en dashboard.<br>• Ensayo del pitch de 3 minutos. |

---

## 5. Estrategia Anticaídas para el Pitch en Vivo

Para garantizar que la demo sea 100% infalible ante jueces:
1. **Modo Demo con 1 Clic:** Un botón de acceso rápido en la UI que inyecta una foto y coordenadas de prueba sin depender de la señal GPS ni de la cámara física del jurado.
2. **Fallback Local de APIs:** Si la API externa de visión o clima tiene latencia excesiva (>3s), el backend conmuta de forma transparente a una respuesta heurística estructurada local.
3. **Precarga de Datos Históricos:** El mapa siempre inicia con los 40 puntos precargados para mostrar calor epidemiológico instantáneo desde el segundo 0.