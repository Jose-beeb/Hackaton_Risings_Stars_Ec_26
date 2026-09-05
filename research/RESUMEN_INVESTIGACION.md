# Resumen de Investigación — Todo lo verificado en un solo lugar

> Consolida `Jose.md`, `papers/Nathy Research.pdf` y `ESTRATEGIA_Y_BLINDAJE_JURADO.md`. Cada dato lleva su nivel de confianza. **Leer esto es suficiente para armar el pitch y el informe** — no hace falta abrir los documentos fuente salvo que quieras el detalle completo.

**Leyenda:** ✅ Verificado con fuente primaria real (búsqueda directa) · ⚠️ Sin verificar de forma independiente, presentar con cuidado · ❌ Buscado y descartado, no usar

---

## 1. Magnitud del problema (Ecuador)

| Dato | Confianza | Fuente |
|---|---|---|
| Ecuador: 27.838 casos de dengue en 2023 → **61.329 en 2024** (+120% interanual), **76 muertes** confirmadas (48 adultos, 28 niños) | ✅ | Boletines MSP Ecuador (SIVE-Alerta) + prensa que los cita directamente |
| Hasta semana epidemiológica 06 de 2025: 5.507 casos, 4 muertes — el problema sigue escalando en 2025 | ⚠️ | `papers/Nathy Research.pdf`, coherente con la tendencia ya verificada |
| Récord continental OPS/OMS 2024: >12.6 millones de casos en las Américas | ⚠️ | `Jose.md`, no se buscó la fuente OPS puntual |
| Serie histórica 2019-2026 (8.416 casos en 2019 hasta 61.329 en 2024) | ⚠️ | `Jose.md`, no se verificó cada año individualmente, solo 2023/2024 |
| **Nota:** `papers/Nathy Research.pdf` cita 61.352 para 2024 (no 61.329) — diferencia menor entre documentos del equipo | — | Usar **61.329**, el que tiene el boletín MSP linkeado |

---

## 2. Ventana biológica y modelo bio-matemático

| Dato | Confianza | Fuente |
|---|---|---|
| Umbral mínimo de desarrollo larvario: **8.3°C** | ✅ | Tun-Lin et al. (2000) — **implementado en `ire_calculator.py`** |
| A 26-32°C (Costa ecuatoriana), el mosquito completa huevo→adulto en **5-7 días** | ✅ | Consistente con Rueda (1990) y Tun-Lin (2000), ya en el modelo implementado |
| Aceleración del ciclo por anomalía tipo El Niño: 1.5 días menos por cada 2°C sostenido | ❌ **No implementado** | `papers/Nathy Research.pdf` lo sugiere, el código no lo tiene todavía |
| A 35°C el ciclo se comprime a 7.8 días | ❌ **No implementado** | Idem — sugerido, no codificado |

**Para el pitch:** decir que el modelo usa Rueda (1990) y Tun-Lin (2000) — eso es cierto y está implementado. No decir que ya modela la aceleración por El Niño ni el punto de 35°C — son mejoras sugeridas, todavía no están en el código.

---

## 3. Metodología: cómo se define el nivel de riesgo y cómo se recopila la información

Esto es 100% verificable contra el código (`core/bio_engine/ire_calculator.py`), no una estimación — útil para responder "¿cómo deciden qué es alto o bajo riesgo?" con precisión ante el jurado o en el informe.

**Cómo se calcula el score (0-99):**

```
IRE = 40 × peso_contenedor × factor_tamaño × factor_temperatura × factor_humedad × factor_materia_orgánica
```

| Factor | Valores |
|---|---|
| Peso del contenedor | Llanta 1.5, tanque abierto 1.4, canaleta obstruida 1.3, balde 1.1, maceta 0.8, charco 0.7, plástico 0.6 |
| Tamaño | Chico (<5L) 0.85, mediano (5-50L) 1.0, grande (>50L) 1.25 |
| Temperatura | Curva calibrada con Rueda (1990): sube hasta 28-30°C (óptimo), decae gradual hacia 40°C (límite letal), cae a casi 0 bajo 8.3°C (Tun-Lin 2000) |
| Humedad | Rampa 0.5-1.0, satura sobre 70% |
| Materia orgánica | ×1.30 si hay presencia visible |

Si no hay agua presente, el score se multiplica además por 0.40 (`risk_type: POTENTIAL` en vez de `ACTIVE`) — es riesgo latente, no un criadero activo ahora mismo.

**Los 3 umbrales de clasificación (decisión operativa del equipo, no un hallazgo de un paper — decirlo así si preguntan):**

| Score | Nivel |
|---|---|
| ≥ 70 | 🔴 CRITICAL |
| 40 – 69.9 | 🟡 MEDIUM |
| < 40 | 🟢 LOW |

**Cómo se recopila la información — 2 fuentes automáticas, nada manual:**
1. **Foto → Gemini Vision** clasifica: tipo de recipiente, tamaño, si hay agua, si hay materia orgánica, volumen estimado. Es percepción pura — la IA no decide el riesgo.
2. **GPS del reporte → Open-Meteo** trae temperatura y humedad reales del punto exacto, en tiempo real (no un promedio genérico de la ciudad).

Esos 6 datos son el único input de la fórmula — nada se tipea a mano, por eso el resultado es reproducible: mismos inputs, mismo score, siempre.

*(✅ Toda esta sección está verificada directamente contra el código fuente, no es una síntesis de investigación externa.)*

---

## 4. Por qué la fumigación tradicional no alcanza

| Dato | Confianza | Fuente |
|---|---|---|
| ULV en zonas urbanas densas: **40-60% de reducción transitoria por ciclo** de la población adulta, con recuperación en semanas | ✅ | Bonds (2012), *Medical and Veterinary Entomology* 26(2):121-130 |
| "Paradoja de Giglioli": se necesitaría cubrir >97% de la biomasa adulta para bajar la transmisión a nivel poblacional | ⚠️ | Atribuido a Giglioli (1948) en `Jose.md` — **el 97%/1948 puntual no se pudo confirmar**, usar el concepto de forma cualitativa |
| Resistencia genética a piretroides en la Costa ecuatoriana (mutaciones kdr F1534C/V1016I, >70-85% frecuencia alélica) | ⚠️ | `Jose.md` cita Ponce et al. (2020) — **cita no confirmada de forma independiente**, verificar el DOI antes de usar el número exacto |
| **"70% del insecticida se desperdicia fumigando a ciegas"** | ❌ **Descartado** | Sin fuente primaria en ninguna búsqueda — no usar este número |

**Para el pitch:** el argumento sólido es "la fumigación ULV logra 40-60% de reducción transitoria, no resuelve el criadero, y fumigar el mismo químico repetidamente puede acelerar la resistencia del vector" — con Bonds (2012) como respaldo. Evitar cifras exactas de resistencia genética o el "70%" hasta confirmar esas citas puntuales.

---

## 5. Economía sanitaria — costos y ROI

| Dato | Confianza | Fuente |
|---|---|---|
| Un caso hospitalizado de dengue implica **5.6 días escolares / 9.9 días laborales perdidos** | ✅ | Suaya et al. (2009), *AJTMH* 80(5):846-855 (página corregida — varios documentos del equipo tenían 696-701, que es incorrecto) |
| Costo de hospitalización: **USD 196-866** (adultos, Sri Lanka) | ✅ | Thalagala et al. (2016) |
| Control focalizado reduce **15-20%** los costos operativos recurrentes vs. modelo reactivo | ✅ | Baly, Toledo & Boelaert (2007), *Trans R Soc Trop Med Hyg* 101:578-586 — la cifra real es 15-20%, no el 30-45% que circulaba antes |
| Biolarvicida Bti suprime producción de pupas **91% durante 8 semanas** — más efectivo que el temefos tradicional (reinfestación en 6 semanas) | ✅ | Setha (2016, publicado en *PLOS NTDs*, no en *Parasites & Vectors* como dice el documento del equipo) y George (2015) |
| Costo por caso fatal: USD 50.000-80.000 | ⚠️ | `Jose.md`, sin fuente primaria puntual buscada |
| USD 447.982 invertidos por el MSP en fumigación 2024 | ⚠️ | `Jose.md`, sin fuente primaria puntual buscada |
| Costo regional LatAm: >USD 3.000 millones/año | ⚠️ | `Jose.md`, sin fuente primaria puntual buscada |
| Hospitalización USD 866-1.855 atribuido a "Zimmermann (2024)" | ⚠️ | `papers/Nathy Research.pdf` — no se pudo confirmar esa publicación; el límite inferior coincide con Thalagala (2016, sí confirmado) |
| Ahorro operativo de 35-40% en km y químicos por el despacho dirigido | ⚠️ **Proyección del equipo** | No es una medición propia — decirlo como estimación, no como resultado medido |
| $2 USD por criadero intervenido, ROI 1:200, <$50/mes por municipio, <$0.002 USD/inferencia | ⚠️ **Estimaciones internas** | Sin cotización real ni auditoría de costos |

---

## 6. Benchmarking competitivo

| Criterio | Mosquito Alert (España) | DengueChat (Nicaragua) | Trampas IoT | **Ojito al Mosquito** |
|---|---|---|---|---|
| Detección a acción | Días-semanas (75% requiere validación entomólogo humano) | Semanas-meses (auditoría periódica) | Tiempo real, cobertura puntual | Minutos (con latencia variable de la IA, ver README) |
| Costo por punto | Cero hardware | Cero hardware | USD 150-450/trampa | Cero hardware nuevo |
| Resiliencia en LatAm | Alta en Europa, baja en emergencias tropicales | Vulnerable a fatiga del voluntariado | Muy baja (hurto, vandalismo) | Alta — 100% software con fallbacks |
| Motor de riesgo | Presencia/ausencia de especie | Conteo de viviendas libres de larvas | Conteo de adultos capturados | IRE determinista (microclima real + biología calibrada) |
| Despacho de brigadas | No tiene | Manual, sin optimización | No tiene | Heurística ponderada por riesgo + navegación directa |
| Auditoría de cierre | No tiene | No tiene | No tiene | Validación visual Antes/Después con IA |

*(Tabla de `ESTRATEGIA_Y_BLINDAJE_JURADO.md` y `Jose.md` — descripciones de competidores no re-verificadas de forma independiente esta sesión, pero internamente consistentes entre ambos documentos.)*

---

## 7. Marco legal y modelo de negocio

| Dato | Confianza | Fuente |
|---|---|---|
| El **GAD Municipal** (no el MSP) tiene la competencia legal y presupuestaria de saneamiento ambiental y fumigación cantonal | ⚠️ | COOTAD Art. 55 lit. d, Art. 54 lit. k y r — código oficial, no reverificado en esta sesión |
| El MSP tiene la rectoría normativa y SIVE-Alerta (Ley Orgánica de Salud) — es aliado de interoperabilidad, no comprador | ⚠️ | LOS Art. 4, 6 núm. 5, Art. 122 — ídem |
| Vía de entrada al mercado público: Ínfima Cuantía SERCOP, techo reportado de USD 10.000, para un piloto de 3-6 meses | ⚠️ | `Jose.md` — confirmar el techo vigente en la web de SERCOP antes de citarlo con precisión |
| Costo real de una brigada en Guayaquil: **USD 145-245/día** (insumo químico + combustible + mano de obra, SBU 2026 = USD 482) | ⚠️ | `Jose.md`, cifras de SERCOP y Ministerio del Trabajo — no reverificadas en esta sesión, pero son datos públicos plausibles |

**Modelo de negocio propuesto (no tracción confirmada):** B2G (SaaS municipal por suscripción anual según población) + B2B (API para empresas de control de plagas, puertos, agroindustria).

---

## 8. Preguntas de jurado ya preparadas (ver también `PITCH.md`)

- ¿Por qué no trampas IoT? → Costo + vandalismo hacen inviable cubrir una ciudad; los smartphones ya existen.
- ¿Cómo evitan que la IA alucine el riesgo? → La IA solo clasifica la foto; el riesgo lo calcula una fórmula determinista (IRE), no la IA.
- ¿Fotos falsas o irrelevantes? → Filtro de confianza en la clasificación. *(La deduplicación espacial de reportes vecinos sigue en el roadmap, no implementada.)*
- ¿Focos en el río? → Máscara geoespacial real de exclusión, ya implementada.
- ¿Por qué esa heurística de rutas y no un TSP exacto? → Prioriza urgencia biológica, razonable para un piloto municipal.
- ¿Por qué no confían solo en la fumigación química? → 40-60% de reducción transitoria (Bonds 2012) + riesgo de acelerar resistencia genética.
- ¿Quién les compra esto? → El GAD Municipal, por el COOTAD — no el MSP.
- ¿El biolarvicida es mejor que el químico? → Sí hay evidencia (Setha 2016, George 2015) — pero es sobre el insumo de la brigada, no algo que el software venda directamente.

---

## 9. Regla de uso para el equipo

Antes de poner un número en una diapositiva o en el informe:
1. Buscalo en la tabla correspondiente de arriba.
2. Si dice ✅ — citalo con la fuente completa, tal como está.
3. Si dice ⚠️ — decilo como "según fuentes reportadas" o como estimación propia, nunca como hecho auditado.
4. Si dice ❌ — no lo uses, ya se buscó y no tiene respaldo.

Detalle completo y proceso de verificación en `PITCH.md` (raíz del repo) e `INFORME_PROPUESTA.md`.
