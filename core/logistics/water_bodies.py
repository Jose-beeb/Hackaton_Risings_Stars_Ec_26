"""
Exclusión de cuerpos de agua de Guayaquil (Río Guayas y red de canales del Estero
Salado) para evitar que la simulación genere criaderos de Aedes aegypti flotando
en agua corriente o salobre — biológicamente imposible (el mosquito se reproduce
en recipientes artificiales con agua limpia/estancada) y una pérdida inmediata de
credibilidad técnica frente al jurado en la demo.

La geometría es REAL, extraída de OpenStreetMap vía Overpass API
(data/water_bodies.geojson): el polígono exacto del Río Guayas (relation OSM
1207999) y un corredor con buffer sobre las líneas centrales reales de los brazos
y canales del Estero Salado (el estuario no tiene un único polígono de área en
OSM, se mapea como red de waterways). Un primer intento con corredores dibujados
a mano tenía ~25% de falsos negativos (puntos "tierra" que en realidad caían en
el río) — de ahí la necesidad de partir de datos geográficos reales.
"""

import json
import os
from typing import List, Tuple

Point = Tuple[float, float]  # (lng, lat)

_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/water_bodies.geojson"
)


def _load_polygons() -> List[List[Point]]:
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)
    polygons: List[List[Point]] = []
    for feature in geojson["features"]:
        ring = feature["geometry"]["coordinates"][0]
        polygons.append([(pt[0], pt[1]) for pt in ring])
    return polygons


WATER_BODY_POLYGONS: List[List[Point]] = _load_polygons()


def _point_in_polygon(lat: float, lng: float, polygon: List[Point]) -> bool:
    """Ray casting: True si (lng, lat) cae dentro del polígono."""
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = ((yi > lat) != (yj > lat)) and (
            lng < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def is_in_water_body(lat: float, lng: float) -> bool:
    """True si el punto cae dentro del Río Guayas o algún brazo del Estero Salado."""
    return any(_point_in_polygon(lat, lng, poly) for poly in WATER_BODY_POLYGONS)
