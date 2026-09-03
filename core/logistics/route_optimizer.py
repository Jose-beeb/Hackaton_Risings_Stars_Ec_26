"""
Optimizador Heurístico de Rutas de Despacho para Cuadrillas Sanitarias
Asignado al Rol: Mecatrónica y Logística
"""

import math
from typing import Dict, Any, List

MINUTES_PER_STOP = 15          # minutos de trabajo en campo por foco (fumigación + inspección)
SPEED_KMH = 15.0               # velocidad promedio de desplazamiento (moto/vehículo urbano)
FUEL_LITERS_PER_KM = 0.08      # consumo de combustible: moto promedio ~12.5 km/L
PESTICIDE_LITERS_PER_STOP = 2.5  # litros de pesticida por foco tratado


def haversine_distance(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    """Calcula la distancia aproximada en kilómetros entre dos coordenadas (lng, lat)."""
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _blind_route_distance(depot: tuple, stops: list) -> float:
    """
    Ruta ciega: mismos focos visitados en orden de reporte (sin optimización).
    Sirve de baseline para calcular el ahorro real de la optimización.
    """
    if not stops:
        return 0.0
    coords = [depot] + [tuple(f["geometry"]["coordinates"]) for f in stops]
    return sum(haversine_distance(coords[i], coords[i + 1]) for i in range(len(coords) - 1))


def _split_into_brigades(
    ordered_route: list,
    depot_coords: tuple,
    brigade_base_id: str,
    max_hours: float,
    max_liters: float,
) -> list:
    """
    Divide la ruta optimizada en brigadas según capacidad operativa.
    Cada brigada tiene límite de horas y litros de pesticida.
    """
    brigades = []
    current_stops = []
    current_dist = 0.0
    current_minutes = 0.0
    current_liters = 0.0
    current_pos = depot_coords
    max_minutes = max_hours * 60
    brigade_num = 1

    for stop in ordered_route:
        coords = tuple(stop["geometry"]["coordinates"])
        leg_km = haversine_distance(current_pos, coords)
        leg_minutes = (leg_km / SPEED_KMH) * 60 + MINUTES_PER_STOP
        leg_liters = PESTICIDE_LITERS_PER_STOP

        # Si esta parada supera la capacidad de la brigada actual, cerrar y abrir nueva
        if current_stops and (
            current_minutes + leg_minutes > max_minutes
            or current_liters + leg_liters > max_liters
        ):
            brigades.append({
                "brigade_id": f"{brigade_base_id}-{brigade_num}",
                "stops_count": len(current_stops),
                "distance_km": round(current_dist, 2),
                "duration_min": round(current_minutes),
                "pesticide_liters": round(current_liters, 1),
                "route_geometry": {
                    "type": "LineString",
                    "coordinates": [list(depot_coords)] + [s["geometry"]["coordinates"] for s in current_stops],
                },
            })
            brigade_num += 1
            current_stops = []
            current_dist = 0.0
            current_minutes = 0.0
            current_liters = 0.0
            current_pos = depot_coords

        current_stops.append(stop)
        current_dist += leg_km
        current_minutes += leg_minutes
        current_liters += leg_liters
        current_pos = coords

    if current_stops:
        brigades.append({
            "brigade_id": f"{brigade_base_id}-{brigade_num}",
            "stops_count": len(current_stops),
            "distance_km": round(current_dist, 2),
            "duration_min": round(current_minutes),
            "pesticide_liters": round(current_liters, 1),
            "route_geometry": {
                "type": "LineString",
                "coordinates": [list(depot_coords)] + [s["geometry"]["coordinates"] for s in current_stops],
            },
        })

    return brigades


def optimize_brigade_route(
    depot_coords: tuple[float, float],
    foci_geojson: Dict[str, Any],
    max_stops: int = 8,
    brigade_id: str = "brigada-norte",
    max_hours_per_brigade: float = 8.0,
    max_liters_per_brigade: float = 20.0,
) -> Dict[str, Any]:
    """
    Selecciona y ordena los focos más críticos usando heurística Nearest Neighbor
    ponderada por IRE. Divide automáticamente en múltiples brigadas si la capacidad
    operativa (horas, pesticida) es superada. Calcula el ahorro real vs. ruta ciega.
    """
    features = foci_geojson.get("features", [])
    candidates = [f for f in features if f.get("properties", {}).get("status") != "RESOLVED"]
    if not candidates:
        candidates = list(features)

    # --- Heurística Nearest Neighbor ponderada por IRE ---
    current_pos = depot_coords
    unvisited = list(candidates)
    ordered_route: List[dict] = []
    total_dist_km = 0.0
    stops_to_make = min(max_stops, len(unvisited))

    for _ in range(stops_to_make):
        best_candidate = None
        best_score = float("inf")
        for cand in unvisited:
            coords = tuple(cand["geometry"]["coordinates"])
            dist = haversine_distance(current_pos, coords)
            ire = cand.get("properties", {}).get("ire_score", 50.0)
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

    # --- Ruta ciega (mismos focos, orden de reporte) para comparación ---
    blind_stops = sorted(ordered_route, key=lambda f: candidates.index(f))
    blind_dist_km = _blind_route_distance(depot_coords, blind_stops)
    km_saved = round(max(0.0, blind_dist_km - total_dist_km), 2)
    fuel_liters_saved = round(km_saved * FUEL_LITERS_PER_KM, 1)
    efficiency_pct = round((km_saved / blind_dist_km * 100) if blind_dist_km > 0 else 0.0, 1)

    # --- División en brigadas según capacidad operativa ---
    brigade_base = brigade_id.rsplit("-", 1)[0] if brigade_id[-1].isdigit() else brigade_id
    brigades = _split_into_brigades(
        ordered_route, depot_coords, brigade_base, max_hours_per_brigade, max_liters_per_brigade
    )

    # --- Itinerario y geometría (brigade 1, compatibilidad con frontend) ---
    route_coords = [list(depot_coords)] + [f["geometry"]["coordinates"] for f in ordered_route]
    itinerary = [
        {
            "order": idx,
            "foco_id": f.get("properties", {}).get("id"),
            "sector": f.get("properties", {}).get("sector"),
            "container_name": f.get("properties", {}).get("container_name"),
            "ire_score": f.get("properties", {}).get("ire_score"),
            "action": f.get("properties", {}).get("recommended_action", "Abatización y eliminación física"),
        }
        for idx, f in enumerate(ordered_route, start=1)
    ]

    return {
        "brigade_id": brigade_id,
        "depot_start": list(depot_coords),
        "total_distance_km": round(total_dist_km, 2),
        "estimated_duration_min": round(total_dist_km * 4 + len(ordered_route) * MINUTES_PER_STOP),
        "priority_foci_count": len(ordered_route),
        "route_geometry": {"type": "LineString", "coordinates": route_coords},
        "itinerary": itinerary,
        "brigades": brigades,
        "savings": {
            "blind_route_km": round(blind_dist_km, 2),
            "optimized_route_km": round(total_dist_km, 2),
            "km_saved": km_saved,
            "fuel_liters_saved": fuel_liters_saved,
            "pesticide_liters_used": round(len(ordered_route) * PESTICIDE_LITERS_PER_STOP, 1),
            "efficiency_pct": efficiency_pct,
            "brigades_required": len(brigades),
        },
    }
