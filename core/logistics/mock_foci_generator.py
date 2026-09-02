"""
Generador de Mock Data Geoespacial (GeoJSON) para AedesGuard.
Simula 40 focos epidemiológicos realistas en sectores críticos de Guayaquil y alrededores.
"""

import json
import random
from datetime import datetime, timedelta

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
    {"tipo": "tire", "nombre_es": "Llanta en desuso", "peso_riesgo": 1.4, "volumen_l": 15},
    {"tipo": "open_tank", "nombre_es": "Tanque / Cisterna sin tapa", "peso_riesgo": 1.5, "volumen_l": 200},
    {"tipo": "bucket", "nombre_es": "Balde con agua recolectada", "peso_riesgo": 1.2, "volumen_l": 20},
    {"tipo": "flowerpot", "nombre_es": "Maceta / Plato con agua", "peso_riesgo": 0.8, "volumen_l": 2},
    {"tipo": "clogged_drain", "nombre_es": "Canaleta obstruida", "peso_riesgo": 1.3, "volumen_l": 10},
    {"tipo": "litter_plastic", "nombre_es": "Basura / Botellas plásticas", "peso_riesgo": 0.7, "volumen_l": 1},
]

def calculate_mock_ire(tipo_info: dict, temp_c: float, humedad_pct: float) -> tuple[float, str, int]:
    # Factor térmico óptimo para Aedes aegypti: 26-30°C
    factor_temp = max(0.5, 1.0 - abs(28.0 - temp_c) * 0.05)
    factor_hum = humedad_pct / 100.0
    
    ire_raw = 50.0 * tipo_info["peso_riesgo"] * factor_temp * factor_hum + random.uniform(-5, 5)
    ire_score = round(max(10.0, min(99.0, ire_raw)), 1)
    
    if ire_score >= 70.0:
        nivel = "CRITICAL"
        dias_eclosion = random.randint(3, 5)
    elif ire_score >= 40.0:
        nivel = "MEDIUM"
        dias_eclosion = random.randint(6, 8)
    else:
        nivel = "LOW"
        dias_eclosion = random.randint(9, 14)
        
    return ire_score, nivel, dias_eclosion

def generate_mock_geojson(total_points: int = 40) -> dict:
    random.seed(42)  # Para reproducibilidad exacta
    features = []
    now = datetime.utcnow()

    for i in range(1, total_points + 1):
        sector = random.choice(SECTORES)
        tipo = random.choice(TIPOS_CRIADEROS)
        
        # Desplazamiento aleatorio dentro del sector (~500m - 1.5km)
        lat = sector["lat"] + random.uniform(-0.012, 0.012)
        lng = sector["lng"] + random.uniform(-0.012, 0.012)
        
        # Clima típico costero en temporada lluviosa
        temp_c = round(random.uniform(26.5, 31.5), 1)
        hum_pct = round(random.uniform(75.0, 92.0), 1)
        
        ire_score, nivel_riesgo, dias_eclosion = calculate_mock_ire(tipo, temp_c, hum_pct)
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
                "estimated_volume_l": tipo["volumen_l"],
                "water_detected": True,
                "temperature_c": temp_c,
                "humidity_pct": hum_pct,
                "ire_score": ire_score,
                "risk_level": nivel_riesgo,
                "days_to_emergence": dias_eclosion,
                "status": "PENDING",
                "reported_at": report_time,
                "recommended_action": (
                    "Drenaje y larvicida biológico prioritario" if nivel_riesgo == "CRITICAL"
                    else "Eliminación física del depósito" if nivel_riesgo == "MEDIUM"
                    else "Monitoreo preventivo y volteo de recipiente"
                )
            }
        }
        features.append(feature)

    # Ordenar por criticidad (mayor IRE primero)
    features.sort(key=lambda x: x["properties"]["ire_score"], reverse=True)

    return {
        "type": "FeatureCollection",
        "metadata": {
            "title": "AedesGuard Guayaquil Pilot Dataset",
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
