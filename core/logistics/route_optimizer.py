"""
Optimizador Heurístico de Rutas de Despacho para Cuadrillas Sanitarias
Asignado al Rol: Mecatrónica y Logística
"""

import math
from typing import Dict, Any, List

def haversine_distance(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    """Calcula la distancia aproximada en kilómetros entre dos coordenadas (lng, lat)."""
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    
    r = 6371.0  # Radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c

def optimize_brigade_route(
    depot_coords: tuple[float, float],
    foci_geojson: Dict[str, Any],
    max_stops: int = 8,
    brigade_id: str = "brigada-norte-1"
) -> Dict[str, Any]:
    """
    Selecciona y ordena los focos más críticos y cercanos usando una heurística
    Nearest Neighbor ponderada por el Índice de Riesgo Entomológico (IRE).
    """
    features = foci_geojson.get("features", [])
    
    # Filtrar focos activos / pendientes y ordenar por criticidad inicial
    candidates = [f for f in features if f.get("properties", {}).get("status") != "RESOLVED"]
    if not candidates:
        candidates = features[:max_stops]
    
    # Heurística de selección: mayor IRE y menor distancia
    current_pos = depot_coords
    unvisited = list(candidates)
    ordered_route = []
    total_dist_km = 0.0
    
    stops_to_make = min(max_stops, len(unvisited))
    
    for _ in range(stops_to_make):
        # Puntuación combinada: minimizar distancia, maximizar IRE
        best_candidate = None
        best_score = float('inf')
        
        for cand in unvisited:
            coords = tuple(cand["geometry"]["coordinates"])
            dist = haversine_distance(current_pos, coords)
            ire = cand.get("properties", {}).get("ire_score", 50.0)
            
            # Penaliza distancia alta y premia IRE alto
            score = dist / (ire / 30.0)
            if score < best_score:
                best_score = score
                best_candidate = cand
                
        if best_candidate:
            coords = tuple(best_candidate["geometry"]["coordinates"])
            total_dist_km += haversine_distance(current_pos, coords)
            ordered_route.append(best_candidate)
            current_pos = coords
            unvisited.remove(best_candidate)
            
    # Construir geometría LineString y el itinerario
    route_coords = [list(depot_coords)] + [f["geometry"]["coordinates"] for f in ordered_route]
    
    itinerary = []
    for idx, f in enumerate(ordered_route, start=1):
        props = f.get("properties", {})
        itinerary.append({
            "order": idx,
            "foco_id": props.get("id"),
            "sector": props.get("sector"),
            "container_name": props.get("container_name"),
            "ire_score": props.get("ire_score"),
            "action": props.get("recommended_action", "Abatización y eliminación física")
        })
        
    return {
        "brigade_id": brigade_id,
        "depot_start": list(depot_coords),
        "total_distance_km": round(total_dist_km, 2),
        "estimated_duration_min": round(total_dist_km * 4 + len(ordered_route) * 15),
        "priority_foci_count": len(ordered_route),
        "route_geometry": {
            "type": "LineString",
            "coordinates": route_coords
        },
        "itinerary": itinerary
    }
