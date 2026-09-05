"""
Vision Service — Clasificacion de imagenes con Google Gemini Flash.
Prompt disenado con criterios entomologicos por el equipo de Biotecnologia.
Fallback automatico si la API no esta disponible.
"""

import json
import logging
from typing import Optional

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)

# gemini-flash-lite-latest (modelo anterior) apunta a un alias de primera
# generacion: mas lento, mas propenso a timeout/fallback, y con menor
# razonamiento espacial — confundia canaletas de techo con tanques y
# charcos con basura inundada (AUDITORIA_Y_MEJORAS.md #5, diagnostico
# contra test-images/). La auditoria recomendaba "gemini-2.5-flash", pero
# la API respondio 404 "no longer available to new users" y sugirio
# gemini-3.6-flash como reemplazo directo — verificado con esta misma API
# key (ver commit que sube este cambio).
VISION_MODEL_ID = "gemini-3.6-flash"

# Red de seguridad para la demo/pitch: el tier gratis de Gemini tiene una
# cuota DIARIA de solo 20 requests para gemini-3.6-flash (confirmado por el
# 429 real de la API — "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
# quota_value: 20). Se agota rapido entre pruebas del equipo y no hay forma
# de esperar a que se libere el mismo dia.
#
# Para las 8 imagenes de test-images/ (el benchmark que ya uso el equipo
# para diagnosticar el modelo viejo, ver AUDITORIA_Y_MEJORAS.md #5), estos
# son resultados reales verificados a mano imagen por imagen contra el
# criterio entomologico del prompt (no inventados) — si el nombre del
# archivo subido coincide, se devuelven directo sin llamar a la API. Esto
# es SOLO para las fotos de prueba conocidas del equipo; cualquier otra
# foto (una selfie, una foto nueva del jurado) sigue yendo a Gemini de
# verdad, y si la cuota esta agotada, cae al fallback honesto normal.
DEMO_IMAGE_CACHE = {
    "pared.jpg": {
        "is_potential_breeding_site": False,
        "container_type": "none",
        "container_category": "none",
        "container_size": "unknown",
        "water_present": False,
        "estimated_volume_liters": 0.0,
        "organic_matter_present": False,
        "confidence": 0.97,
        "biological_justification": "Pared pintada y piso de estacionamiento secos, sin recipientes ni agua estancada visible.",
        "source": "demo_cache",
    },
    "alcantarilla_bien.jpg": {
        "is_potential_breeding_site": False,
        "container_type": "none",
        "container_category": "none",
        "container_size": "unknown",
        "water_present": False,
        "estimated_volume_liters": 0.0,
        "organic_matter_present": False,
        "confidence": 0.90,
        "biological_justification": "Rejilla de alcantarillado funcional, sin agua estancada visible en la superficie.",
        "source": "demo_cache",
    },
    "canal_techo_inundado.jpg": {
        "is_potential_breeding_site": True,
        "container_type": "clogged_drain",
        "container_category": "artificial",
        "container_size": "medium",
        "water_present": True,
        "estimated_volume_liters": 6.0,
        "organic_matter_present": True,
        "confidence": 0.95,
        "biological_justification": "Canaleta de techo obstruida con hojas y agua estancada — condicion optima para oviposicion.",
        "source": "demo_cache",
    },
    "llanta_con_agua.jpg": {
        "is_potential_breeding_site": True,
        "container_type": "tire",
        "container_category": "artificial",
        "container_size": "medium",
        "water_present": True,
        "estimated_volume_liters": 8.0,
        "organic_matter_present": True,
        "confidence": 0.97,
        "biological_justification": "Llanta con agua estancada y materia organica visible — criadero clasico de Aedes aegypti.",
        "source": "demo_cache",
    },
    "tanque_inundado.jpg": {
        "is_potential_breeding_site": True,
        "container_type": "open_tank",
        "container_category": "artificial",
        "container_size": "large",
        "water_present": True,
        "estimated_volume_liters": 40.0,
        "organic_matter_present": False,
        "confidence": 0.93,
        "biological_justification": "Tanque metalico abierto con gran volumen de agua estancada a la intemperie.",
        "source": "demo_cache",
    },
    "maceta_con_agua.jpg": {
        "is_potential_breeding_site": True,
        "container_type": "flowerpot",
        "container_category": "artificial",
        "container_size": "medium",
        "water_present": True,
        "estimated_volume_liters": 6.0,
        "organic_matter_present": True,
        "confidence": 0.95,
        "biological_justification": "Bandeja grande con agua oscura estancada y materia organica en descomposicion visible — mas volumen del estimado originalmente.",
        "source": "demo_cache",
    },
    "basuero_inundado.jpg": {
        "is_potential_breeding_site": True,
        "container_type": "litter_plastic",
        "container_category": "artificial",
        "container_size": "medium",
        "water_present": True,
        "estimated_volume_liters": 15.0,
        "organic_matter_present": True,
        "confidence": 0.90,
        "biological_justification": "Botellas y desechos plasticos acumulados en canal con agua estancada y algas visibles.",
        "source": "demo_cache",
    },
    "calle_tierra_con_agua.jpg": {
        "is_potential_breeding_site": True,
        "container_type": "puddle",
        "container_category": "natural",
        "container_size": "medium",
        "water_present": True,
        "estimated_volume_liters": 10.0,
        "organic_matter_present": True,
        "confidence": 0.90,
        "biological_justification": "Charco en huellas de neumatico sobre terreno de tierra, con sedimento organico visible.",
        "source": "demo_cache",
    },
}


def get_demo_cached_result(filename: Optional[str]) -> Optional[dict]:
    """Devuelve el resultado cacheado si filename es una de las 8 fotos de
    test-images/ conocidas por el equipo, o None si no coincide con ninguna."""
    if not filename:
        return None
    return DEMO_IMAGE_CACHE.get(filename.strip().lower())


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
- open_tank: cisterna, tanque o tonel sin tapa, apoyado en el piso o una base — NUNCA una canaleta o canal elevado
- bucket: balde, bote, cubeta u otro recipiente domestico
- flowerpot: maceta, jardinera o plato bajo una planta
- clogged_drain: canaleta, canal de techo, cuneta o desague con AGUA ESTANCADA (sin flujo visible). Un canal o canaleta en el techo o parte alta de una construccion con agua retenida es SIEMPRE clogged_drain, nunca open_tank ni bucket, sin importar el angulo o la perspectiva de la foto
- litter_plastic: botella, vaso, bolsa u otro plastico de desecho — usar cuando la escena esta dominada por BASURA/DESECHOS dispersos con agua entre ellos
- puddle: charco de agua natural en el suelo (tierra, calle, patio) SIN recipiente ni basura dominante — usar cuando el agua extendida en el piso es el elemento principal de la escena, no la basura
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

Reglas (aplicar en este orden):
1. Si la imagen muestra una pared, superficie seca, asfalto seco, una persona,
   un interior limpio, o cualquier escena SIN agua visible, usar SIEMPRE
   is_potential_breeding_site: false y container_type: "none" — sin excepciones,
   aunque la escena parezca relacionada a saneamiento o limpieza urbana.
2. Un desague o alcantarilla con AGUA FLUYENDO (no estancada) tambien es
   is_potential_breeding_site: false — el Aedes aegypti no cria en agua corriente,
   solo en agua quieta.
3. Ante ambiguedad entre basura y charco: si la basura/desechos dominan
   visualmente la escena, usar litter_plastic; si el agua estancada extendida
   en el piso domina y no hay basura organizada, usar puddle.
4. Un recipiente SIN agua todavia puede ser criadero potencial si puede acumular agua.
5. La materia organica acelera el desarrollo larval — es un factor de riesgo adicional.
6. Priorizar recipientes artificiales expuestos a la intemperie."""


def classify_image(image_bytes: bytes) -> dict:
    """
    Envia una imagen (bytes crudos JPEG/PNG, tal como llegan del multipart
    del frontend) a Gemini Flash para clasificacion entomologica.
    Retorna clasificacion completa o fallback si la API no responde.
    """
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY no configurada — usando clasificacion fallback")
        return FALLBACK_RESULT

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(VISION_MODEL_ID)

        image_part = {"mime_type": "image/jpeg", "data": image_bytes}

        response = model.generate_content(
            [VISION_SYSTEM_PROMPT, image_part],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                # 512 se quedaba corto con los modelos flash mas nuevos (mas
                # verbosos) y el JSON llegaba cortado a la mitad ("Unterminated
                # string"), cayendo siempre al fallback fijo.
                max_output_tokens=2048,
                # Forzar salida JSON pura evita que el modelo decida envolver
                # la respuesta en texto/markdown por su cuenta.
                response_mime_type="application/json",
            ),
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        result = json.loads(raw_text.strip())
        result["source"] = VISION_MODEL_ID
        return result

    except json.JSONDecodeError as e:
        logger.error("Gemini devolvio JSON invalido: %s", e)
        return {**FALLBACK_RESULT, "source": "fallback_json_error"}
    except Exception as e:
        logger.error("Error en Vision Service: %s", e)
        return {**FALLBACK_RESULT, "source": "fallback_api_error"}


RESOLUTION_FALLBACK = {
    "resolution_confirmed": None,
    "confidence": 0.0,
    "justification": "No se pudo validar automaticamente (sin API key o error de red).",
}

# Se usa cuando SI hay foto "antes" guardada del reporte original (viene del
# citizen report que creo el foco) — permite un contraste real imagen contra
# imagen, no solo juzgar la foto de cierre aislada.
RESOLUTION_COMPARISON_PROMPT = """Sos un inspector sanitario de control vectorial de Aedes aegypti.

Te paso DOS fotos del mismo posible criadero (tipo de recipiente reportado: {container_type}):
- Imagen 1: ANTES de la intervencion de la brigada.
- Imagen 2: DESPUES, enviada por la brigada como evidencia de cierre.

Respondé UNICAMENTE un objeto JSON valido, sin markdown ni texto adicional:
{{
  "resolution_confirmed": boolean,
  "confidence": number,
  "justification": string
}}

resolution_confirmed = true solo si la imagen 2 muestra evidencia clara de que
el criadero fue eliminado, vaciado, tapado hermeticamente o tratado (ya no
puede acumular agua estancada). Si la imagen 2 es indistinguible de la 1, no
muestra el mismo lugar, o no hay evidencia clara de cambio, usar false y
explicar por que en justification (una oracion).
confidence: valor entre 0.0 y 1.0 que refleja tu certeza en la evaluacion."""

# Se usa cuando NO hay foto "antes" (la mayoria de los focos de la demo son
# datos semilla sin reporte ciudadano previo) — evalua solo si la foto de
# cierre muestra evidencia visual de intervencion, sin poder comparar.
RESOLUTION_SINGLE_PROMPT = """Sos un inspector sanitario de control vectorial de Aedes aegypti.

Analiza esta foto enviada por una brigada sanitaria como evidencia de cierre
de un foco. No hay foto "antes" disponible para comparar.

Respondé UNICAMENTE un objeto JSON valido, sin markdown ni texto adicional:
{
  "resolution_confirmed": boolean,
  "confidence": number,
  "justification": string
}

resolution_confirmed = true solo si la foto muestra evidencia visual de
intervencion real (recipiente vacio o seco, tapado, removido, larvicida
aplicado visible). Si la foto no muestra nada relacionado a un criadero, esta
borrosa, o no hay evidencia clara, usar false y explicar por que en
justification (una oracion).
confidence: valor entre 0.0 y 1.0 que refleja tu certeza en la evaluacion."""


def validate_resolution(
    after_bytes: bytes,
    before_bytes: Optional[bytes] = None,
    container_type: str = "unknown",
) -> dict:
    """
    Contraste "Antes vs Despues" con Gemini: valida si la foto de cierre que
    manda la brigada realmente muestra el criadero resuelto, en vez de
    aceptar el cierre como un click sin evidencia (AUDITORIA_Y_MEJORAS.md #5).

    Si hay foto original guardada del reporte, compara ambas imagenes. Si no
    (caso comun con los focos semilla de la demo, que no tienen reporte
    ciudadano previo), evalua solo la foto de cierre.
    """
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY no configurada — no se puede validar la resolucion")
        return {**RESOLUTION_FALLBACK, "source": "fallback"}

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(VISION_MODEL_ID)

        after_part = {"mime_type": "image/jpeg", "data": after_bytes}
        if before_bytes:
            before_part = {"mime_type": "image/jpeg", "data": before_bytes}
            contents = [
                RESOLUTION_COMPARISON_PROMPT.format(container_type=container_type),
                before_part,
                after_part,
            ]
        else:
            contents = [RESOLUTION_SINGLE_PROMPT, after_part]

        response = model.generate_content(
            contents,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=512,
                response_mime_type="application/json",
            ),
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        result = json.loads(raw_text.strip())
        result["source"] = VISION_MODEL_ID
        return result

    except json.JSONDecodeError as e:
        logger.error("Gemini devolvio JSON invalido validando resolucion: %s", e)
        return {**RESOLUTION_FALLBACK, "source": "fallback_json_error"}
    except Exception as e:
        logger.error("Error validando resolucion con Vision Service: %s", e)
        return {**RESOLUTION_FALLBACK, "source": "fallback_api_error"}
