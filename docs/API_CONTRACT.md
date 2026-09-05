# Especificación de Contrato de API (Contract-First)

Este documento define la interfaz pública e inmutable entre el Frontend, el Backend, el Motor Biológico y el Optimizador Logístico de **Ojito al Mosquito**.

---

## 1. Endpoints del Backend

### `POST /api/reports`
Recibe un reporte de criadero potencial desde la PWA móvil.

* **Headers:** `Content-Type: multipart/form-data` (lo arma el browser solo al usar `FormData`; no fijarlo a mano o se pierde el boundary)
* **Request Body (campos de formulario):**

| Campo | Tipo | Requerido | Notas |
|---|---|---|---|
| `latitude` | float | Sí | |
| `longitude` | float | Sí | |
| `photo` | file (JPEG/PNG) | No | Comprimida en Canvas a máx. 1280px de lado antes de enviarse |
| `notes` | string | No | |

Reemplaza el body JSON con `image_base64` que se usaba antes — mandar la foto como binario en vez de texto Base64 reduce ~33% el tamaño del payload y evita decodificar Base64 en el event loop del backend (ver `AUDITORIA_Y_MEJORAS.md` #1).

* **Response (201 Created):**
```json
{
  "id": "foco-042",
  "timestamp": "2026-09-02T13:45:00Z",
  "coordinates": [-79.889123, -2.189412],
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

---

### `GET /api/foci`
Devuelve la colección completa de focos activos en formato GeoJSON para alimentar el mapa de calor y los marcadores del Dashboard GIS.

* **Response (200 OK):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-79.889123, -2.189412]
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

---

### `POST /api/routes/dispatch`
Calcula la ruta óptima de intervención para las cuadrillas de fumigación/abatización según la criticidad del IRE.

* **Request Body:**
```json
{
  "depot_coordinates": [-79.8970, -2.1800],
  "max_foci": 10
}
```

* **Response (200 OK):**
```json
{
  "brigade_id": "cuadrilla-norte-1",
  "total_distance_km": 6.8,
  "estimated_duration_min": 110,
  "priority_foci_count": 5,
  "route_geometry": {
    "type": "LineString",
    "coordinates": [
      [-79.8970, -2.1800],
      [-79.8891, -2.1894],
      [-79.8920, -2.1850]
    ]
  },
  "itinerary": [
    { "order": 1, "foco_id": "foco-042", "action": "Abatización focalizada" },
    { "order": 2, "foco_id": "foco-019", "action": "Eliminación física de depósito" }
  ]
}
```

---

## 2. Firma de Funciones para Módulos Core (Python / JS)

### Motor Biológico (`core/bio_engine/ire_calculator.py`)
```python
def calculate_ire(container_type: str, temperature_c: float, humidity_pct: float) -> dict:
    """
    Calcula el Índice de Riesgo Entomológico y días estimados de eclosión.
    
    Retorna:
    {
        "ire_score": float (0-100),
        "risk_level": "LOW" | "MEDIUM" | "CRITICAL",
        "days_to_emergence": int,
        "recommended_action": str
    }
    """
    pass
```

### Motor de Ruteo (`core/logistics/route_optimizer.py`)
```python
def optimize_brigade_route(depot: tuple, foci_geojson: dict, max_stops: int = 10) -> dict:
    """
    Ordena los focos críticos minimizando la distancia y priorizando el mayor IRE.
    
    Retorna payload con LineString GeoJSON y la lista ordenada de paradas.
    """
    pass
```
