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

DEFAULT_TRANSPORT_MODE = "vehicle_spray"
DEFAULT_FUMIGADORES = 2

# Jornada operativa maxima fija por brigada (regla de negocio explicita del
# equipo — reemplaza el rango 5.5-6h usado antes solo como estimacion).
MAX_HOURS_PER_BRIGADE = 6.0

# --- Escalado del tiempo de atencion por parada segun cantidad de operarios ---
# BASE_MINUTES_PER_STOP: tiempo de atencion con la pareja estandar (2
# operarios) para el modo de referencia. Los 3 modos de TRANSPORT_MODES
# tienen cada uno su propio "base" (17.5/35/2 minutos, calibrados asumiendo
# 2 operarios) — este es el factor de referencia usado para escalar esos
# valores segun cuantos operarios tenga la brigada.
BASE_MINUTES_PER_STOP = 20.0
MIN_STOP_TIME = 8.0   # piso minimo de atencion, incluso con muchos operarios
STOP_TIME_ALPHA = 0.75  # exponente de rendimientos decrecientes

# Tabla explicita para 1-4 operarios (el caso mas comun); fuera de ese rango
# se usa la funcion de rendimientos decrecientes con el mismo piso.
STOP_TIME_TABLE_MINUTES = {1: 30.0, 2: 20.0, 3: 13.0, 4: 10.0}

# --- Modos de transporte por brigada ---
# Corresponden a 3 tipos de brigada de campo con objetivo biologico y
# operativa distintos. Procedencia de cada numero (honesta, no todo tiene el
# mismo nivel de respaldo — ver README "Base cientifica" / tabla de
# investigacion):
#   - minutes_per_stop de "foot": rango 15-20 min/predio citado por el equipo
#     a un manual de procesos del MSP Ecuador — titulo/anio exacto NO
#     verificado de forma independiente todavia, se usa el punto medio.
#   - speed_kmh de "foot": 6-8 km/h, tomado explicitamente como *parametro de
#     calibracion de ingenieria* (desplazamiento urbano/peatonal mixto), NO
#     como cita academica forzada.
#   - "vehicle_walk_attack" (brigada de rociado residual con mochila
#     motorizada 14-15L): mas lenta que "foot" por el peso del equipo y el
#     tiempo de aplicacion por vivienda (8-10 viviendas/dia reportadas vs.
#     12-16 de "foot") — speed_kmh y minutes_per_stop son ESTIMACION INTERNA
#     derivada de ese rango diario, no una cita directa.
#   - "vehicle_spray" (brigada de fumigacion espacial/nebulizacion termica):
#     vehicular continuo, sin paradas domiciliarias — minutes_per_stop queda
#     casi nulo (solo reposicionamiento), speed_kmh en el rango 8-12 km/h
#     reportado para este tipo de barrido.
TRANSPORT_MODES = {
    "foot": {
        "label": "A pie — Control Focal (larvicida/inspección)",
        "speed_kmh": 7.0,
        "minutes_per_stop": 17.5,
    },
    "vehicle_walk_attack": {
        "label": "Vehículo + ataque a pie — Rociado Residual (mochila)",
        "speed_kmh": 5.0,
        "minutes_per_stop": 35.0,
    },
    "vehicle_spray": {
        "label": "Vehículo fumigador — Fumigación Espacial (sin paradas)",
        "speed_kmh": 10.0,
        "minutes_per_stop": 2.0,
    },
}


def _stop_time_minutes_for_operarios(operarios: int) -> float:
    """
    Minutos de atencion por parada PARA EL MODO DE REFERENCIA (base 20 min
    con 2 operarios), segun cantidad de operarios en la brigada. Usa la
    tabla explicita para 1-4 operarios; fuera de ese rango, una funcion de
    rendimientos decrecientes: BASE * (2/operarios)^alpha, con piso
    MIN_STOP_TIME (evita tiempos irreales como 0 min con muchos operarios).

    Heuristica interna del equipo, NO respaldada por una fuente primaria
    verificada todavia — ver README, tabla de investigacion.
    """
    operarios = max(1, int(operarios))
    if operarios in STOP_TIME_TABLE_MINUTES:
        return STOP_TIME_TABLE_MINUTES[operarios]
    raw = BASE_MINUTES_PER_STOP * (2.0 / operarios) ** STOP_TIME_ALPHA
    return max(MIN_STOP_TIME, raw)


def _effective_minutes_per_stop(mode: Dict[str, Any], operarios: int) -> float:
    """
    Combina el tiempo base de CADA modo de transporte (mode["minutes_per_stop"],
    calibrado para 2 operarios — ver TRANSPORT_MODES) con el escalado por
    cantidad de operarios, manteniendo la proporcion relativa entre modos.

    El piso MIN_STOP_TIME se aplica ANTES de escalar por modo (protege el
    numero de referencia), no despues: "vehicle_spray" esta diseñado para
    tener casi cero minutos de atencion (no hace paradas domiciliarias) y
    un piso absoluto ahi anularia esa diferencia adrede.
    """
    reference_minutes = _stop_time_minutes_for_operarios(operarios)  # ya con piso aplicado
    mode_scale = mode["minutes_per_stop"] / BASE_MINUTES_PER_STOP
    return reference_minutes * mode_scale


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
    max_brigades: int = 999,
    brigade_configs: List[Dict[str, Any]] | None = None,
) -> list:
    """
    Divide la ruta optimizada en brigadas.

    Si brigade_configs trae MAS DE UNA entrada, se interpreta como brigadas
    configuradas explicitamente por el usuario (una fila por brigada en el
    panel de despacho) — se reparte ordered_route en partes iguales entre
    min(max_brigades, len(brigade_configs)) brigadas, sin esperar a que la
    capacidad nominal (horas/litros) se agote. Antes, con la capacidad por
    defecto (8h/20L) muy holgada, casi nunca se llegaba a usar mas de una
    brigada aunque el usuario hubiera configurado varias — quedaban
    "colocadas" en el panel pero nunca se dibujaban en el mapa.

    Si brigade_configs tiene 0 o 1 entradas, se usa el comportamiento
    original: split dirigido por capacidad (horas/litros), topado en
    max_brigades — las paradas que sobran tras el tope se acumulan en la
    ultima brigada en vez de descartarse en silencio.
    """
    def _config_for(idx: int) -> Dict[str, Any]:
        if not brigade_configs:
            return {"fumigadores": DEFAULT_FUMIGADORES, "transport_mode": DEFAULT_TRANSPORT_MODE}
        return brigade_configs[min(idx, len(brigade_configs) - 1)]

    def _mode_and_stop_minutes(cfg: Dict[str, Any]):
        mode = TRANSPORT_MODES.get(cfg.get("transport_mode", DEFAULT_TRANSPORT_MODE), TRANSPORT_MODES[DEFAULT_TRANSPORT_MODE])
        stop_minutes = _effective_minutes_per_stop(mode, cfg.get("fumigadores", DEFAULT_FUMIGADORES))
        return mode, stop_minutes

    def _capacity_weight(cfg: Dict[str, Any]) -> float:
        """
        Focos/dia que una brigada puede cubrir en su jornada, segun su modo
        de transporte y su cantidad de operarios. Ignora el tiempo de
        traslado entre paradas (no se conoce hasta armar el chunk) — es una
        aproximacion basada solo en el tiempo de atencion por parada, igual
        que las cifras de "predios/dia" citadas en el README.
        """
        _, stop_minutes = _mode_and_stop_minutes(cfg)
        return (MAX_HOURS_PER_BRIGADE * 60) / max(0.1, stop_minutes)

    def _build_brigade(stops: list, num: int, cfg: Dict[str, Any]) -> Dict[str, Any]:
        mode, stop_minutes = _mode_and_stop_minutes(cfg)
        pos = depot_coords
        dist = 0.0
        tiempo_traslado = 0.0
        tiempo_atencion = 0.0
        for s in stops:
            coords = tuple(s["geometry"]["coordinates"])
            leg_km = haversine_distance(pos, coords)
            dist += leg_km
            tiempo_traslado += (leg_km / mode["speed_kmh"]) * 60
            tiempo_atencion += stop_minutes
            pos = coords
        tiempo_total = tiempo_traslado + tiempo_atencion
        max_minutes = MAX_HOURS_PER_BRIGADE * 60
        return {
            "brigade_id": f"{brigade_base_id}-{num}",
            "stops_count": len(stops),
            "focos_atendidos_count": len(stops),
            "distance_km": round(dist, 2),
            "duration_min": round(tiempo_total),
            "tiempo_total_minutos": round(tiempo_total, 1),
            "tiempo_atencion_minutos": round(tiempo_atencion, 1),
            "tiempo_traslado_minutos": round(tiempo_traslado, 1),
            "excede_jornada": tiempo_total > max_minutes,
            "pesticide_liters": round(len(stops) * PESTICIDE_LITERS_PER_STOP, 1),
            "fumigadores": cfg.get("fumigadores", DEFAULT_FUMIGADORES),
            "operarios_asignados": cfg.get("fumigadores", DEFAULT_FUMIGADORES),
            "transport_mode": cfg.get("transport_mode", DEFAULT_TRANSPORT_MODE),
            "secuencia_paradas": [s.get("properties", {}).get("id") for s in stops],
            "route_geometry": {
                "type": "LineString",
                "coordinates": [list(depot_coords)] + [s["geometry"]["coordinates"] for s in stops],
            },
        }

    if not ordered_route:
        return []

    # --- Reparto explicito: el usuario configuro N brigadas, usarlas todas ---
    if brigade_configs and len(brigade_configs) > 1:
        target_count = max(1, min(max_brigades, len(brigade_configs), len(ordered_route)))
        configs = [_config_for(i) for i in range(target_count)]

        # Reparto proporcional a la capacidad de cada brigada (metodo de
        # Hamilton): una brigada con menos fumigadores o transporte mas lento
        # debe cubrir menos focos, no una parte igual. Cada brigada arranca
        # con 1 foco garantizado (para que ninguna quede vacia) y el resto se
        # reparte segun el peso de capacidad (_capacity_weight), redondeando
        # hacia abajo y asignando las unidades sobrantes a las brigadas con
        # mayor resto fraccionario — así la suma da exacto sin sesgar por
        # orden de configuracion.
        weights = [_capacity_weight(cfg) for cfg in configs]
        total_weight = sum(weights) or 1.0
        total_stops = len(ordered_route)
        remaining = max(0, total_stops - target_count)

        ideal_extra = [remaining * w / total_weight for w in weights]
        sizes = [1 + int(x) for x in ideal_extra]
        leftover = total_stops - sum(sizes)
        # Asignar el resto a quien tiene mayor parte fraccionaria pendiente
        fractional_order = sorted(
            range(target_count), key=lambda i: ideal_extra[i] - int(ideal_extra[i]), reverse=True
        )
        for i in fractional_order[:leftover]:
            sizes[i] += 1

        chunks: List[list] = []
        offset = 0
        for i in range(target_count):
            chunks.append(ordered_route[offset: offset + sizes[i]])
            offset += sizes[i]

        # --- Rebalanceo iterativo ---
        # El reparto de arriba estima capacidad solo por tiempo de atencion
        # (no conoce el traslado real hasta armar el chunk), asi que puede
        # dejar una brigada con mas trabajo real del que le entra en su
        # jornada. Este paso prueba mover CUALQUIERA de los focos de una
        # brigada que excede (no solo el ultimo — un intento anterior que
        # solo probaba el ultimo fallaba cuando justo ese no entraba en
        # ninguna otra brigada aunque otro si hubiera entrado) hacia la
        # brigada donde mas reduzca el exceso de la de origen sin hacer que
        # la de destino tambien se pase. Repite hasta que nadie exceda o ya
        # no haya un movimiento valido. No vuelve a correr TSP dentro del
        # chunk (el foco se agrega al final de la lista destino) — es una
        # heuristica local, no una solucion exacta de bin-packing.
        max_minutes = MAX_HOURS_PER_BRIGADE * 60

        def _chunk_total_minutes(stops: list, cfg: Dict[str, Any]) -> float:
            return _build_brigade(stops, 0, cfg)["tiempo_total_minutos"] if stops else 0.0

        max_iterations = max(1, len(ordered_route) * target_count)
        for _ in range(max_iterations):
            totals = [_chunk_total_minutes(chunks[i], configs[i]) for i in range(target_count)]
            over_idx = next(
                (i for i in range(target_count) if totals[i] > max_minutes and len(chunks[i]) > 1),
                None,
            )
            if over_idx is None:
                break

            source_total = totals[over_idx]
            best_move = None  # (stop_idx, target_idx, reduccion_en_origen)
            for stop_idx, stop in enumerate(chunks[over_idx]):
                remaining_source = chunks[over_idx][:stop_idx] + chunks[over_idx][stop_idx + 1:]
                reduction = source_total - _chunk_total_minutes(remaining_source, configs[over_idx])
                for j in range(target_count):
                    if j == over_idx:
                        continue
                    candidate_total = _chunk_total_minutes(chunks[j] + [stop], configs[j])
                    if candidate_total <= max_minutes and (best_move is None or reduction > best_move[2]):
                        best_move = (stop_idx, j, reduction)

            if best_move is None:
                break  # ningun foco de la brigada sobrecargada entra en otra sin pasarla

            stop_idx, target_idx, _ = best_move
            moving_stop = chunks[over_idx].pop(stop_idx)
            chunks[target_idx] = chunks[target_idx] + [moving_stop]

        brigades = []
        for i in range(target_count):
            if chunks[i]:
                brigades.append(_build_brigade(chunks[i], i + 1, configs[i]))
        return brigades

    # --- Split dirigido por capacidad (comportamiento original) ---
    brigades = []
    current_stops = []
    current_minutes = 0.0
    current_liters = 0.0
    current_pos = depot_coords
    max_minutes = max_hours * 60
    brigade_num = 1
    cfg = _config_for(0)
    mode, stop_minutes = _mode_and_stop_minutes(cfg)

    for stop in ordered_route:
        coords = tuple(stop["geometry"]["coordinates"])
        leg_km = haversine_distance(current_pos, coords)
        leg_minutes = (leg_km / mode["speed_kmh"]) * 60 + stop_minutes
        leg_liters = PESTICIDE_LITERS_PER_STOP

        at_last_allowed_brigade = brigade_num >= max_brigades

        # Si esta parada supera la capacidad de la brigada actual, cerrar y
        # abrir nueva — salvo que ya estemos en el tope maximo de brigadas.
        if current_stops and not at_last_allowed_brigade and (
            current_minutes + leg_minutes > max_minutes
            or current_liters + leg_liters > max_liters
        ):
            brigades.append(_build_brigade(current_stops, brigade_num, cfg))
            brigade_num += 1
            current_stops = []
            current_minutes = 0.0
            current_liters = 0.0
            current_pos = depot_coords
            cfg = _config_for(brigade_num - 1)
            mode, stop_minutes = _mode_and_stop_minutes(cfg)
            # La pierna se recalcula con la config de la nueva brigada
            leg_minutes = (leg_km / mode["speed_kmh"]) * 60 + stop_minutes

        current_stops.append(stop)
        current_minutes += leg_minutes
        current_liters += leg_liters
        current_pos = coords

    if current_stops:
        brigades.append(_build_brigade(current_stops, brigade_num, cfg))

    return brigades


def optimize_brigade_route(
    depot_coords: tuple[float, float],
    foci_geojson: Dict[str, Any],
    max_stops: int = 8,
    brigade_id: str = "brigada-norte",
    max_hours_per_brigade: float = MAX_HOURS_PER_BRIGADE,
    max_liters_per_brigade: float = 20.0,
    max_brigades: int = 999,
    brigade_configs: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    Selecciona y ordena los focos más críticos usando heurística Nearest Neighbor
    ponderada por IRE. Divide automáticamente en múltiples brigadas si la capacidad
    operativa (horas, pesticida) es superada, sin superar max_brigades. Calcula
    el ahorro real vs. ruta ciega.

    brigade_configs: config por brigada (fumigadores, transport_mode), en el
    orden en que se van a usar. Ver TRANSPORT_MODES y _effective_minutes_per_stop.
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
        ordered_route, depot_coords, brigade_base, max_hours_per_brigade, max_liters_per_brigade,
        max_brigades=max_brigades, brigade_configs=brigade_configs,
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
