"""
Vision Service — Clasificacion de imagenes con Google Gemini Flash.
Fallback automatico a clasificacion mock si la API no esta disponible.
"""

import json
import base64
import logging
from typing import Optional

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)

FALLBACK_RESULT = {
    "is_potential_breeding_site": True,
    "container_type": "bucket",
    "water_detected": True,
    "estimated_volume_liters": 5.0,
    "organic_matter_present": False,
    "confidence": 0.60,
    "biological_justification": "Clasificacion de respaldo: API no disponible.",
    "source": "fallback",
}

VISION_SYSTEM_PROMPT = """Eres un experto entomologo y epidemiologo especializado en control vectorial de arbovirosis (Aedes aegypti).

Analiza la imagen y responde UNICAMENTE con un objeto JSON valido (sin markdown ni texto adicional):

{
  "is_potential_breeding_site": boolean,
  "container_type": "tire" | "open_tank" | "bucket" | "flowerpot" | "clogged_drain" | "litter_plastic" | "other" | "none",
  "water_detected": boolean,
  "estimated_volume_liters": number,
  "organic_matter_present": boolean,
  "confidence": number,
  "biological_justification": string
}

Reglas:
1. Si la imagen NO muestra un criadero potencial, usa "is_potential_breeding_site": false y "container_type": "none".
2. Prioriza recipientes artificiales expuestos a la intemperie (llantas, baldes, cisternas).
3. confidence entre 0.0 y 1.0."""


def classify_image(image_base64: str) -> dict:
    """
    Envia una imagen en base64 a Gemini Flash para clasificacion entomologica.
    Retorna el resultado de la API o el fallback si algo falla.
    """
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY no configurada — usando clasificacion fallback")
        return FALLBACK_RESULT

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        image_data = base64.b64decode(image_base64)
        image_part = {"mime_type": "image/jpeg", "data": image_data}

        response = model.generate_content(
            [VISION_SYSTEM_PROMPT, image_part],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=512,
            ),
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        result = json.loads(raw_text)
        result["source"] = "gemini-1.5-flash"
        return result

    except json.JSONDecodeError as e:
        logger.error("Gemini devolvio JSON invalido: %s", e)
        return {**FALLBACK_RESULT, "source": "fallback_json_error"}
    except Exception as e:
        logger.error("Error en Vision Service: %s", e)
        return {**FALLBACK_RESULT, "source": "fallback_api_error"}
