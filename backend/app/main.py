"""
Ojito al Mosquito — API Orquestadora (FastAPI)
Integra Vision AI, datos climaticos en tiempo real y el motor bio-matematico IRE.
"""

import os
import sys
import json
import logging
import threading
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))   # backend/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.bio_engine.ire_calculator import calculate_ire
from core.logistics.route_optimizer import optimize_brigade_route
from app.services.vision_service import classify_image
from app.services.climate_service import get_climate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ojito al Mosquito Epidemiological API",
    version="1.0.0",
    description="Plataforma de inteligencia vectorial para prevencion de arbovirosis",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/mock_foci_guayaquil.geojson")
)


def load_foci_store() -> dict:
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"type": "FeatureCollection", "features": []}


foci_store = load_foci_store()
_store_lock = threading.Lock()


def save_foci_store() -> None:
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(foci_store, f, ensure_ascii=False, indent=2)


class ReportRequest(BaseModel):
    latitude: float = Field(..., example=-2.1894)
    longitude: float = Field(..., example=-79.8891)
    image_base64: Optional[str] = Field(None, description="Imagen en base64 (JPEG/PNG)")
    notes: Optional[str] = None


class BrigadeConfig(BaseModel):
    fumigadores: int = Field(default=2, ge=1, le=10, description="Operarios/fumigadores en la brigada")
    transport_mode: str = Field(
        default="vehicle_spray",
        description="'foot' | 'vehicle_spray' | 'vehicle_walk_attack'",
    )


class DispatchRequest(BaseModel):
    depot_coordinates: list[float] = Field(default=[-79.8950, -2.1800])
    max_foci: int = Field(default=8, ge=1, le=25)
    max_brigades: int = Field(default=1, ge=1, le=10, description="Tope maximo de brigadas a usar")
    brigade_configs: list[BrigadeConfig] = Field(
        default_factory=list,
        description="Config por brigada en orden de uso; se repite la ultima si faltan",
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Ojito al Mosquito API",
        "version": "1.0.0",
        "features_loaded": len(foci_store.get("features", [])),
    }


@app.get("/api/foci")
def get_foci():
    """Devuelve los focos activos (no resueltos) en formato GeoJSON."""
    active_features = [
        f for f in foci_store.get("features", [])
        if f.get("properties", {}).get("status") != "RESOLVED"
    ]
    return {**foci_store, "features": active_features}


class ResolveFociRequest(BaseModel):
    foco_ids: list[str] = Field(..., description="IDs de los focos que la brigada ya atendio")
    brigade_id: Optional[str] = None
    operator_name: Optional[str] = Field(
        None, description="Nombre del operador que confirma. NO es una firma criptografica real."
    )
    after_photo_base64: Optional[str] = Field(
        None, description="Foto de confirmacion (antes/despues), se guarda tal cual sin decodificar"
    )


@app.post("/api/foci/resolve")
def resolve_foci(req: ResolveFociRequest):
    """
    Marca los focos indicados como RESOLVED (no se borran del archivo, solo
    dejan de aparecer en /api/foci y de ser candidatos para futuros despachos
    — ver el filtro de status en route_optimizer.optimize_brigade_route).

    Canal de validacion de intervencion: guarda quien confirmo y, si la
    mandaron, una foto de "despues" — evidencia de que la brigada fue al
    lugar, no solo un click. "operator_name" es un campo de texto simple,
    NO una firma digital criptografica; aclarar esa distincion si preguntan
    en el pitch.
    """
    ids = set(req.foco_ids)
    resolved = []
    resolved_at = datetime.utcnow().isoformat() + "Z"
    with _store_lock:
        for feature in foci_store.get("features", []):
            props = feature.get("properties", {})
            if props.get("id") in ids and props.get("status") != "RESOLVED":
                props["status"] = "RESOLVED"
                props["resolved_at"] = resolved_at
                if req.brigade_id:
                    props["resolved_by_brigade"] = req.brigade_id
                if req.operator_name:
                    props["resolved_by_operator"] = req.operator_name
                if req.after_photo_base64:
                    props["after_photo_base64"] = req.after_photo_base64
                resolved.append(props["id"])
        save_foci_store()

    logger.info(
        "Focos resueltos: %s (brigada %s, operador %s, con foto: %s)",
        resolved, req.brigade_id or "?", req.operator_name or "?", bool(req.after_photo_base64),
    )
    return {"resolved_count": len(resolved), "resolved_ids": resolved}


@app.post("/api/reports", status_code=201)
def create_report(report: ReportRequest):
    """
    Procesa un reporte ciudadano o de brigada.
    Ejecuta clasificacion de imagen con Gemini, obtiene clima real y calcula IRE.
    """
    # 1. Clasificacion visual (Gemini Flash o fallback)
    if report.image_base64:
        vision_result = classify_image(report.image_base64)
    else:
        vision_result = {
            "is_potential_breeding_site": True,
            "container_type": "tire",
            "container_category": "artificial",
            "container_size": "medium",
            "water_present": True,
            "estimated_volume_liters": 15.0,
            "organic_matter_present": True,
            "confidence": 0.70,
            "biological_justification": "Reporte sin imagen — criadero típico de alto riesgo.",
            "source": "no_image",
        }

    # 2. Clima en tiempo real (Open-Meteo o fallback)
    climate = get_climate(report.latitude, report.longitude)

    # 3. Calculo del Indice de Riesgo Entomologico con todos los factores biologicos
    container_type = vision_result.get("container_type", "bucket")
    bio_result = calculate_ire(
        container_type=container_type,
        temperature_c=climate["temperature_c"],
        humidity_pct=climate["humidity_pct"],
        container_size=vision_result.get("container_size", "medium"),
        organic_matter=vision_result.get("organic_matter_present", False),
        water_present=vision_result.get("water_present", True),
        estimated_volume_liters=vision_result.get("estimated_volume_liters", 10.0),
    )

    report_id = f"foco-{len(foci_store.get('features', [])) + 1:03d}"
    now_iso = datetime.utcnow().isoformat() + "Z"

    container_names = {
        "tire": "Llanta",
        "open_tank": "Tanque abierto",
        "bucket": "Balde / recipiente",
        "flowerpot": "Maceta",
        "clogged_drain": "Canaleta obstruida",
        "litter_plastic": "Plastico en desecho",
        "other": "Otro recipiente",
        "none": "Sin criadero detectado",
    }

    new_feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [report.longitude, report.latitude],
        },
        "properties": {
            "id": report_id,
            "sector": "Reporte en Vivo",
            "container_type": container_type,
            "container_name": container_names.get(container_type, "Recipiente"),
            "container_category": bio_result["container_category"],
            "container_size": vision_result.get("container_size", "medium"),
            "water_present": vision_result.get("water_present", True),
            "organic_matter_present": vision_result.get("organic_matter_present", False),
            "estimated_volume_liters": vision_result.get("estimated_volume_liters", 10.0),
            "temperature_c": climate["temperature_c"],
            "humidity_pct": climate["humidity_pct"],
            "ire_score": bio_result["ire_score"],
            "risk_level": bio_result["risk_level"],
            "risk_type": bio_result["risk_type"],
            "days_to_emergence_estimate": bio_result["days_to_emergence_estimate"],
            "status": "PENDING",
            "reported_at": now_iso,
            "recommended_action": bio_result["recommended_action"],
            "scientific_note": bio_result["scientific_note"],
            "notes": report.notes,
        },
    }

    with _store_lock:
        foci_store.setdefault("features", []).insert(0, new_feature)
        save_foci_store()

    logger.info(
        "Nuevo reporte: %s | IRE %.1f (%s) | Fuente vision: %s",
        report_id,
        bio_result["ire_score"],
        bio_result["risk_level"],
        vision_result.get("source", "unknown"),
    )

    return {
        "id": report_id,
        "timestamp": now_iso,
        "coordinates": [report.longitude, report.latitude],
        "classification": {
            "container_type": container_type,
            "container_name": container_names.get(container_type, "Recipiente"),
            "water_detected": vision_result.get("water_detected", True),
            "confidence": vision_result.get("confidence", 0.0),
            "source": vision_result.get("source", "unknown"),
        },
        "climate": {
            "temperature_c": climate["temperature_c"],
            "humidity_pct": climate["humidity_pct"],
            "source": climate.get("source", "unknown"),
        },
        "risk_assessment": bio_result,
    }


@app.post("/api/routes/dispatch")
def dispatch_routes(req: DispatchRequest):
    """Calcula la ruta optima de intervencion para las cuadrillas sanitarias."""
    depot_tuple = (req.depot_coordinates[0], req.depot_coordinates[1])
    configs = [c.model_dump() for c in req.brigade_configs] or None
    return optimize_brigade_route(
        depot_tuple,
        foci_store,
        max_stops=req.max_foci,
        max_brigades=req.max_brigades,
        brigade_configs=configs,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
