"""
Generador de Mock Data Geoespacial (GeoJSON) para Ojito al Mosquito.
Simula 40 focos epidemiológicos realistas en sectores críticos de Guayaquil y alrededores.
"""

import json
import random
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from core.bio_engine.ire_calculator import calculate_ire
from core.logistics.water_bodies import is_in_water_body

# Sectores y coordenadas centrales de Guayaquil para clustering realista
SECTORES = [
    {"nombre": "Guasmo Sur", "lat": -2.2550, "lng": -79.8950, "riesgo_base": "CRITICAL"},
    {"nombre": "Suburbio Oeste", "lat": -2.2050, "lng": -79.9200, "riesgo_base": "CRITICAL"},
    {"nombre": "Mapasingue", "lat": -2.1550, "lng": -79.9300, "riesgo_base": "MEDIUM"},
    {"nombre": "Bastión Popular / Pascuales", "lat": -2.1050, "lng": -79.9350, "riesgo_base": "CRITICAL"},
    {"nombre": "Samanes / Sauces", "lat": -2.1350, "lng": -79.8950, "riesgo_base": "MEDIUM"},
    {"nombre": "Durán (Zona Centro)", "lat": -2.1700, "lng": -79.8450, "riesgo_base": "CRITICAL"},
]

TIPOS_CRIADEROS = [
    {"tipo": "tire",          "nombre_es": "Llanta en desuso",           "volumen_l": 15,  "size": "medium"},
    {"tipo": "open_tank",     "nombre_es": "Tanque / Cisterna sin tapa", "volumen_l": 200, "size": "large"},
    {"tipo": "bucket",        "nombre_es": "Balde con agua recolectada", "volumen_l": 20,  "size": "medium"},
    {"tipo": "flowerpot",     "nombre_es": "Maceta / Plato con agua",    "volumen_l": 2,   "size": "small"},
    {"tipo": "clogged_drain", "nombre_es": "Canaleta obstruida",         "volumen_l": 10,  "size": "medium"},
    {"tipo": "litter_plastic","nombre_es": "Basura / Botellas plasticas","volumen_l": 1,   "size": "small"},
]

def generate_mock_geojson(total_points: int = 40) -> dict:
    random.seed(42)  # Para reproducibilidad exacta
    features = []
    now = datetime.utcnow()

    for i in range(1, total_points + 1):
        sector = random.choice(SECTORES)
        tipo = random.choice(TIPOS_CRIADEROS)
        
        # Desplazamiento aleatorio dentro del sector (~500m - 1.5km), evitando que el
        # punto caiga en el cauce del Río Guayas o el Estero Salado (biológicamente
        # imposible para un criadero de Aedes aegypti). Reintenta unas pocas veces y,
        # si no logra un punto en tierra firme, usa el centro del sector como respaldo.
        lat, lng = sector["lat"], sector["lng"]
        for _ in range(20):
            candidate_lat = sector["lat"] + random.uniform(-0.012, 0.012)
            candidate_lng = sector["lng"] + random.uniform(-0.012, 0.012)
            if not is_in_water_body(candidate_lat, candidate_lng):
                lat, lng = candidate_lat, candidate_lng
                break
        
        # Clima típico costero en temporada lluviosa
        temp_c = round(random.uniform(26.5, 31.5), 1)
        hum_pct = round(random.uniform(75.0, 92.0), 1)
        
        organic = random.random() < 0.35
        bio = calculate_ire(
            container_type=tipo["tipo"],
            temperature_c=temp_c,
            humidity_pct=hum_pct,
            container_size=tipo["size"],
            organic_matter=organic,
            water_present=True,
            estimated_volume_liters=float(tipo["volumen_l"]),
        )
        report_time = (now - timedelta(hours=random.randint(1, 48))).isoformat() + "Z"

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(lng, 6), round(lat, 6)]
            },
            "properties": {
                "id": f"foco-{i:03d}",
                "sector": sector["nombre"],
                "container_type": tipo["tipo"],
                "container_name": tipo["nombre_es"],
                "container_category": bio["container_category"],
                "container_size": tipo["size"],
                "estimated_volume_liters": float(tipo["volumen_l"]),
                "water_present": True,
                "organic_matter_present": organic,
                "temperature_c": temp_c,
                "humidity_pct": hum_pct,
                "ire_score": bio["ire_score"],
                "risk_level": bio["risk_level"],
                "risk_type": bio["risk_type"],
                "days_to_emergence_estimate": bio["days_to_emergence_estimate"],
                "status": "PENDING",
                "reported_at": report_time,
                "recommended_action": bio["recommended_action"],
                "scientific_note": bio["scientific_note"],
            }
        }
        features.append(feature)

    # Ordenar por criticidad (mayor IRE primero)
    features.sort(key=lambda x: x["properties"]["ire_score"], reverse=True)

    return {
        "type": "FeatureCollection",
        "metadata": {
            "title": "Ojito al Mosquito — Guayaquil Pilot Dataset",
            "total_foci": len(features),
            "generated_at": now.isoformat() + "Z",
            "bounding_box": {
                "min_lat": -2.28, "max_lat": -2.09,
                "min_lng": -79.95, "max_lng": -79.83
            }
        },
        "features": features
    }

if __name__ == "__main__":
    import os
    data = generate_mock_geojson(40)
    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "mock_foci_guayaquil.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Mock data generado con exito: {len(data['features'])} focos en '{out_path}'")
