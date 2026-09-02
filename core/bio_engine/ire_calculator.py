"""
Motor Bio-Matemático: Cálculo del Índice de Riesgo Entomológico (IRE)
Asignado al Rol: Biotecnología
"""

from typing import Dict, Any

# Factores de ponderación de criaderos (capacidad de carga y retención de agua)
CONTAINER_WEIGHTS = {
    "tire": 1.5,            # Llantas: excelente aislante térmico y retención
    "open_tank": 1.4,       # Tanques/cisternas abiertas: gran volumen
    "clogged_drain": 1.3,   # Canaletas obstruidas: materia orgánica alta
    "bucket": 1.1,          # Baldes/recipientes domésticos
    "flowerpot": 0.8,       # Macetas y platos
    "litter_plastic": 0.6,  # Basura menor
}

def calculate_ire(container_type: str, temperature_c: float, humidity_pct: float) -> Dict[str, Any]:
    """
    Calcula el Índice de Riesgo Entomológico (0-100) y estima los días de eclosión
    del vector Aedes aegypti cruzando el tipo de depósito con variables microclimáticas.
    """
    weight = CONTAINER_WEIGHTS.get(container_type.lower(), 1.0)
    
    # Rango térmico metabólico óptimo de Aedes aegypti: 26°C a 30°C
    temp_factor = max(0.4, 1.0 - abs(28.0 - temperature_c) * 0.06)
    hum_factor = max(0.5, humidity_pct / 100.0)
    
    raw_score = 55.0 * weight * temp_factor * hum_factor
    ire_score = round(max(5.0, min(99.0, raw_score)), 1)
    
    # Estimación de días para eclosión y pase a adulto
    if ire_score >= 70.0:
        risk_level = "CRITICAL"
        days_to_emergence = 4 if temperature_c >= 28.0 else 5
        recommended_action = "Intervención prioritaria: drenaje inmediato y aplicación de larvicida biológico."
    elif ire_score >= 40.0:
        risk_level = "MEDIUM"
        days_to_emergence = 7
        recommended_action = "Eliminación física del depósito y educación comunitaria en el predio."
    else:
        risk_level = "LOW"
        days_to_emergence = 12
        recommended_action = "Monitoreo preventivo y volteo de recipientes descubiertos."
        
    return {
        "ire_score": ire_score,
        "risk_level": risk_level,
        "days_to_emergence": days_to_emergence,
        "recommended_action": recommended_action,
        "parameters_used": {
            "container_type": container_type,
            "temperature_c": temperature_c,
            "humidity_pct": humidity_pct
        }
    }
