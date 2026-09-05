"""
Motor Bio-Matematico: Calculo del Indice de Riesgo Entomologico (IRE)
Autor cientifico: Biotecnologia (Naty)

El IRE NO predice con certeza la eclosion del mosquito — es un indice de
riesgo que cruza capacidad del criadero, temperatura y tasa metabolica del
Aedes aegypti para estimar los dias en que podrian emerger adultos si hay
larvas presentes. Sin inspeccion directa no es posible conocer la etapa
biologica real (huevo, larva I-IV, pupa).
"""

from typing import Dict, Any

# --- Pesos por tipo de contenedor (capacidad de retencion y aislamiento termico) ---
CONTAINER_WEIGHTS = {
    "tire":          1.5,   # Llanta: aislante termico excelente, retiene calor
    "open_tank":     1.4,   # Tanque/cisterna abierta: gran volumen
    "clogged_drain": 1.3,   # Canaleta obstruida: materia organica alta
    "bucket":        1.1,   # Balde/recipiente domestico
    "flowerpot":     0.8,   # Maceta o plato
    "litter_plastic":0.6,   # Plastico de desecho menor
    "puddle":        0.7,   # Charco natural: efimero pero frecuente en temporada
    "other":         1.0,
}

# --- Factor de tamano del deposito ---
# Depositos pequenos se calientan mas rapido (mayor tasa metabolica),
# pero depositos grandes acumulan mas volumen de cria.
SIZE_FACTORS = {
    "small":   0.85,  # < 5 litros: calentamiento rapido, volumen bajo
    "medium":  1.00,  # 5 - 50 litros: condicion de referencia
    "large":   1.25,  # > 50 litros: alto volumen de cria potencial
    "unknown": 1.00,
}

# --- Categorias de contenedor ---
CONTAINER_CATEGORIES = {
    "tire": "artificial",
    "open_tank": "artificial",
    "clogged_drain": "artificial",
    "bucket": "artificial",
    "flowerpot": "artificial",
    "litter_plastic": "artificial",
    "puddle": "natural",
    "other": "artificial",
    "none": "none",
}


def _temperature_factor(temperature_c: float) -> float:
    """
    Factor metabolico basado en temperatura. Calibrado con datos empiricos:
    - Umbral minimo de desarrollo: 8.3°C (Tun-Lin et al., 2000)
    - Supervivencia a 15°C: solo 3% para Ae. aegypti (Rueda et al., 1990)
    - Rango optimo: 28-30°C (Rueda et al., 1990; Mordecai et al., 2017)
    - Rueda et al. (1990) reporta desarrollo pleno incluso a 34-36°C (6 dias a
      34°C, el mas rapido de su serie) — el colapso letal real esta cerca de
      40°C para hembras adultas, no a 34°C como se asumia antes aca. El
      decaimiento se modela entre 30°C y 40°C, no como corte abrupto en 34°C.
    """
    if temperature_c < 8.3:
        return 0.0
    if temperature_c > 40.0:
        return 0.05
    if temperature_c < 16.0:
        # Zona de desarrollo marginal: supervivencia ~3% a 15°C (Rueda 1990)
        return max(0.0, (temperature_c - 8.3) / (16.0 - 8.3) * 0.10)
    if temperature_c < 28.0:
        return max(0.3, 1.0 - (28.0 - temperature_c) * 0.06)
    if temperature_c <= 30.0:
        return 1.0
    # 30°C -> 40°C: decaimiento gradual hasta el limite letal real (~40°C)
    return max(0.05, 1.0 - (temperature_c - 30.0) * 0.095)


def _humidity_factor(humidity_pct: float) -> float:
    """
    La humedad relativa ambiental no impacta el metabolismo larvario de forma
    directa — el agua estancada es su propio microambiente. Su efecto principal
    es sobre la supervivencia del adulto (tiempo para completar el ciclo
    gonotrofico) y la tasa de evaporacion del deposito. Por eso se modela como
    una rampa con piso alto (0.75), no como una fraccion lineal estricta de la
    humedad: el piso anterior (0.5) castigaba a la mitad el score de un
    criadero con agua YA estancada solo porque el aire ambiental estaba seco
    (ej. Guayaquil en tarde calurosa y seca, ~40-45% HR) — inconsistente con
    que el propio deposito es su microambiente independiente. Por encima de
    70% (tipico invierno costero) el factor satura en 1.0.
    """
    if humidity_pct >= 70.0:
        return 1.0
    if humidity_pct <= 40.0:
        return 0.75
    return 0.75 + (humidity_pct - 40.0) / (70.0 - 40.0) * 0.25


def _days_to_emergence(ire_score: float, temperature_c: float) -> int:
    """
    Estimacion de dias para emergencia del adulto.
    Calibrado con datos de laboratorio de Rueda et al. (1990) Tabla 2
    y Tun-Lin et al. (2000) para Ae. aegypti:
      >=27°C → 7 dias  | 25°C → 10.5 dias | 20°C → 12 dias
      15°C  → 31 dias  | <15°C → >39 dias (Tun-Lin 2000)
    """
    if temperature_c >= 27.0:
        base_days = 7
    elif temperature_c >= 25.0:
        base_days = 10
    elif temperature_c >= 20.0:
        base_days = 12
    elif temperature_c >= 15.0:
        base_days = 31
    else:
        base_days = 45

    return base_days


def calculate_ire(
    container_type: str,
    temperature_c: float,
    humidity_pct: float,
    container_size: str = "medium",
    organic_matter: bool = False,
    water_present: bool = True,
    estimated_volume_liters: float = 10.0,
) -> Dict[str, Any]:
    """
    Calcula el Indice de Riesgo Entomologico (0-100).

    Parametros:
        container_type: tipo de recipiente (ver CONTAINER_WEIGHTS)
        temperature_c: temperatura ambiente en grados Celsius
        humidity_pct: humedad relativa en porcentaje (0-100)
        container_size: 'small' | 'medium' | 'large' | 'unknown'
        organic_matter: True si hay materia organica visible (acelera desarrollo)
        water_present: True si hay agua. False = riesgo potencial, no activo
        estimated_volume_liters: volumen estimado de agua acumulada

    Retorna:
        dict con ire_score, risk_level, risk_type, dias estimados y recomendacion
    """
    container_type = container_type.lower()
    container_size = container_size.lower()

    # Factores del modelo
    container_weight = CONTAINER_WEIGHTS.get(container_type, 1.0)
    size_factor = SIZE_FACTORS.get(container_size, 1.0)
    temp_factor = _temperature_factor(temperature_c)
    hum_factor = _humidity_factor(humidity_pct)
    # Tun-Lin et al. (2000): materia organica acelera desarrollo y aumenta tamano del adulto
    organic_factor = 1.30 if organic_matter else 1.0

    # Puntuacion base. Constante 40.0 (antes 55.0): con 55.0 el peor escenario
    # (llanta+large+organico+temp/hum optimas) da 134, muy por encima del techo
    # de 99 — el clamp lo aplanaba junto con otros escenarios distintos,
    # perdiendo resolucion en el extremo alto. Con 40.0 el peor caso da 97.5,
    # dentro de rango sin necesidad de aplastar la escala.
    raw_score = 40.0 * container_weight * size_factor * temp_factor * hum_factor * organic_factor
    ire_score = round(max(5.0, min(99.0, raw_score)), 1)

    # Sin agua: riesgo potencial (score reducido — el recipiente puede acumular agua)
    risk_type = "ACTIVE" if water_present else "POTENTIAL"
    if not water_present:
        ire_score = round(ire_score * 0.40, 1)

    # Nivel de riesgo
    if ire_score >= 70.0:
        risk_level = "CRITICAL"
        recommended_action = (
            "Intervencion prioritaria: drenaje inmediato, aplicacion de larvicida "
            "biologico (Bacillus thuringiensis israelensis) y reporte a autoridad sanitaria."
        )
    elif ire_score >= 40.0:
        risk_level = "MEDIUM"
        recommended_action = (
            "Eliminacion fisica del deposito o vaciado completo. "
            "Educacion comunitaria sobre manejo de recipientes en el predio."
        )
    else:
        risk_level = "LOW"
        recommended_action = (
            "Monitoreo preventivo. Voltear o cubrir recipientes descubiertos. "
            "Revisitar en 7 dias si hay lluvia prevista."
        )

    days_est = _days_to_emergence(ire_score, temperature_c)
    container_category = CONTAINER_CATEGORIES.get(container_type, "artificial")

    return {
        "ire_score": ire_score,
        "risk_level": risk_level,
        "risk_type": risk_type,
        "days_to_emergence_estimate": days_est,
        "container_category": container_category,
        "recommended_action": recommended_action,
        "scientific_note": (
            "El IRE es un indice de riesgo basado en condiciones ambientales. "
            "No confirma la presencia de larvas ni la etapa biologica del vector. "
            "Se requiere inspeccion directa para confirmacion entomologica."
        ),
        "parameters_used": {
            "container_type": container_type,
            "container_size": container_size,
            "container_category": container_category,
            "temperature_c": temperature_c,
            "humidity_pct": humidity_pct,
            "organic_matter": organic_matter,
            "water_present": water_present,
            "estimated_volume_liters": estimated_volume_liters,
        },
    }
