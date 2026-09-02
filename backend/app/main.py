"""
Servidor Orquestador de AedesGuard (FastAPI)
Asignado al Rol: Software 1 (Backend & Integración)
"""

import os
import sys
import json
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Asegurar importación de módulos core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from core.bio_engine.ire_calculator import calculate_ire
from core.logistics.route_optimizer import optimize_brigade_route

app = FastAPI(
    title="AedesGuard Epidemiological API",
    version="1.0.0",
    description="Backend orquestador para vigilancia y control vectorial de arbovirosis"
)

# Habilitar CORS para desarrollo ágil con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar dataset de focos inicial (Mock Data)
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/mock_foci_guayaquil.geojson"))

def load_foci_store() -> dict:
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"type": "FeatureCollection", "features": []}

foci_store = load_foci_store()

# --- Modelos Pydantic ---
class ReportRequest(BaseModel):
    latitude: float = Field(..., example=-2.1894)
    longitude: float = Field(..., example=-79.8891)
    image_base64: Optional[str] = None
    notes: Optional[str] = None

class DispatchRequest(BaseModel):
    depot_coordinates: list[float] = Field(default=[-79.8950, -2.1800], example=[-79.8950, -2.1800])
    max_foci: int = Field(default=8, ge=1, le=25)

# --- Endpoints ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AedesGuard API", "features_loaded": len(foci_store.get("features", []))}

@app.get("/api/foci")
def get_foci():
    """Devuelve la colección completa de focos en formato GeoJSON para el dashboard."""
    return foci_store

@app.post("/api/reports", status_code=201)
def create_report(report: ReportRequest):
    """Procesa un nuevo reporte ciudadano o de brigada."""
    # Simulación de extracción de clima y visión (o llamada real)
    mock_container = "tire"
    temp_c = 29.0
    hum_pct = 84.0
    
    bio_result = calculate_ire(mock_container, temp_c, hum_pct)
    
    report_id = f"foco-{len(foci_store.get('features', [])) + 1:03d}"
    now_iso = datetime.utcnow().isoformat() + "Z"
    
    new_feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [report.longitude, report.latitude]
        },
        "properties": {
            "id": report_id,
            "sector": "Reporte en Vivo",
            "container_type": mock_container,
            "container_name": "Llanta detectada por IA",
            "water_detected": True,
            "temperature_c": temp_c,
            "humidity_pct": hum_pct,
            "ire_score": bio_result["ire_score"],
            "risk_level": bio_result["risk_level"],
            "days_to_emergence": bio_result["days_to_emergence"],
            "status": "PENDING",
            "reported_at": now_iso,
            "recommended_action": bio_result["recommended_action"]
        }
    }
    
    # Agregar a memoria y persistir
    foci_store.setdefault("features", []).insert(0, new_feature)
    
    return {
        "id": report_id,
        "timestamp": now_iso,
        "coordinates": [report.longitude, report.latitude],
        "classification": {
            "container_type": mock_container,
            "water_detected": True,
            "confidence": 0.95
        },
        "climate": {
            "temperature_c": temp_c,
            "humidity_pct": hum_pct
        },
        "risk_assessment": bio_result
    }

@app.post("/api/routes/dispatch")
def dispatch_routes(req: DispatchRequest):
    """Calcula la ruta óptima de intervención para las cuadrillas sanitarias."""
    depot_tuple = (req.depot_coordinates[0], req.depot_coordinates[1])
    return optimize_brigade_route(depot_tuple, foci_store, max_stops=req.max_foci)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
