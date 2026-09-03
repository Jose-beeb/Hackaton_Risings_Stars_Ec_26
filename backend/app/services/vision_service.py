"""
Vision Service — Clasificacion de imagenes con Google Gemini Flash.
Prompt disenado con criterios entomologicos por el equipo de Biotecnologia.
Fallback automatico si la API no esta disponible.
"""

import json
import base64
import logging

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)

FALLBACK_RESULT = {
    "is_potential_breeding_site": True,
    "container_type": "bucket",
    "container_category": "artificial",
    "container_size": "medium",
    "water_present": True,
    "estimated_volume_liters": 5.0,
    "organic_matter_present": False,
    "confidence": 0.60,
    "biological_justification": "Clasificacion de respaldo: API no disponible.",
    "source": "fallback",
}

VISION_SYSTEM_PROMPT = """Eres un entomologo y epidemiologo experto en control vectorial de Aedes aegypti.

Analiza la imagen y responde UNICAMENTE con un objeto JSON valido, sin markdown ni texto adicional:

{
  "is_potential_breeding_site": boolean,
  "container_type": "tire" | "open_tank" | "bucket" | "flowerpot" | "clogged_drain" | "litter_plastic" | "puddle" | "other" | "none",
  "container_category": "artificial" | "natural" | "none",
  "container_size": "small" | "medium" | "large" | "unknown",
  "water_present": boolean,
  "estimated_volume_liters": number,
  "organic_matter_present": boolean,
  "confidence": number,
  "biological_justification": string
}

Definiciones de clasificacion:

container_type:
- tire: llanta o neumatico (nuevo o usado)
- open_tank: cisterna, tanque o tonel sin tapa
- bucket: balde, bote, cubeta u otro recipiente domestico
- flowerpot: maceta, jardinera o plato bajo una planta
- clogged_drain: canaleta, cuneta o desague con agua retenida
- litter_plastic: botella, vaso, bolsa u otro plastico de desecho
- puddle: charco de agua natural en suelo, sin recipiente
- other: recipiente artificial que no encaja en categorias anteriores
- none: la imagen no muestra ningun posible criadero

container_category:
- artificial: objeto fabricado por el humano
- natural: formacion de agua en terreno natural (charco, hueco en arbol)
- none: no aplica

container_size (volumen de agua que puede acumular):
- small: menos de 5 litros
- medium: entre 5 y 50 litros
- large: mas de 50 litros
- unknown: no se puede estimar

water_present:
- true: hay agua acumulada visible en este momento
- false: el recipiente esta seco pero podria acumular agua (riesgo potencial)

organic_matter_present:
- true: hay hojas, tierra, musgo u otro material organico en el agua o recipiente
- false: el recipiente esta limpio o con agua clara

confidence: valor entre 0.0 y 1.0 que refleja tu certeza en la clasificacion

biological_justification: una oracion explicando por que es un criadero potencial
  y que caracteristicas lo hacen riesgoso para el Aedes aegypti

Reglas:
1. Si la imagen no muestra ningun criadero potencial (selfie, pared, paisaje sin agua),
   usar is_potential_breeding_site: false y container_type: "none".
2. Un recipiente SIN agua todavia puede ser criadero potencial si puede acumular agua.
3. La materia organica acelera el desarrollo larval — es un factor de riesgo adicional.
4. Priorizar recipientes artificiales expuestos a la intemperie."""


def classify_image(image_base64: str) -> dict:
    """
    Envia una imagen en base64 a Gemini Flash para clasificacion entomologica.
    Retorna clasificacion completa o fallback si la API no responde.
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

        result = json.loads(raw_text.strip())
        result["source"] = "gemini-1.5-flash"
        return result

    except json.JSONDecodeError as e:
        logger.error("Gemini devolvio JSON invalido: %s", e)
        return {**FALLBACK_RESULT, "source": "fallback_json_error"}
    except Exception as e:
        logger.error("Error en Vision Service: %s", e)
        return {**FALLBACK_RESULT, "source": "fallback_api_error"}
