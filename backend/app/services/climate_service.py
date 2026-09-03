"""
Climate Service — Datos climaticos en tiempo real via Open-Meteo (sin API key).
Cache simple en memoria por coordenadas para evitar llamadas redundantes.
"""

import logging
from functools import lru_cache

import httpx

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

GUAYAQUIL_FALLBACK = {
    "temperature_c": 29.0,
    "humidity_pct": 84.0,
    "source": "fallback_guayaquil_avg",
}


@lru_cache(maxsize=128)
def _cached_climate(lat_rounded: float, lng_rounded: float) -> dict:
    """Cache por coordenadas redondeadas a 2 decimales (~1km de precision)."""
    params = {
        "latitude": lat_rounded,
        "longitude": lng_rounded,
        "current": "temperature_2m,relative_humidity_2m",
        "forecast_days": 1,
    }
    with httpx.Client(timeout=5.0) as client:
        response = client.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        data = response.json()

    current = data["current"]
    return {
        "temperature_c": round(current["temperature_2m"], 1),
        "humidity_pct": round(current["relative_humidity_2m"], 1),
        "source": "open-meteo",
    }


def get_climate(latitude: float, longitude: float) -> dict:
    """
    Obtiene temperatura y humedad actuales para las coordenadas dadas.
    Usa cache en memoria. Fallback a promedios de Guayaquil si la API falla.
    """
    try:
        lat_r = round(latitude, 2)
        lng_r = round(longitude, 2)
        return _cached_climate(lat_r, lng_r)
    except httpx.TimeoutException:
        logger.warning("Open-Meteo timeout — usando datos de respaldo")
        return GUAYAQUIL_FALLBACK
    except Exception as e:
        logger.error("Error en Climate Service: %s", e)
        return GUAYAQUIL_FALLBACK
