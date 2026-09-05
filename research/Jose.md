# Investigación Perplexity: Blindaje Epidemiológico y Técnico
**Documento de Entrada:** Jose  
**Proyecto:** Ojito al Mosquito — IEEE Rising Stars 2026 (Track 2: Public Health)  
**Fecha:** Septiembre 2026

---

## 1. Cifras Oficiales y Evidencia Económica y Sanitaria

- **Crecimiento Crítico en Ecuador (2023 vs 2024):**
  - Casos en Ecuador 2023: **27.838 casos**.
  - Casos en Ecuador 2024: **61.329 casos** (un incremento brutal del **+120%** interanual) con **76 muertes confirmadas**.
  - Cifras récord continentales (OPS/OMS): **12.6 millones de casos** reportados en las Américas en 2024.
- **Eficacia Real de la Fumigación Espacial (ULV):**
  - La nebulización espacial (ULV) solo alcanza una **reducción del 40% al 60% por ciclo**.
  - No elimina huevos ni larvas en recipientes protegidos o dentro de los domicilios.
- **Resistencia Vectorial Comprobada:**
  - Resistencia confirmada de *Aedes aegypti* a insecticidas piretroides en **Guayas, Manabí y la zona costera sur del Ecuador**. Fumigar a ciegas agrava la presión de selección genética.
- **Impacto Económico:**
  - Costo regional del dengue en América Latina: **> USD 3.000 millones anuales**.
  - Costo por caso fatal: hasta **USD 80.000** considerando atención médica intensiva, hospitalización y años de vida productiva perdidos.
- **Brecha Presupuestaria del Estado:**
  - El Ministerio de Salud Pública (MSP) de Ecuador invirtió únicamente **USD 447.982 en fumigación durante 2024**, sin presupuesto específico destinado a investigación o modernización tecnológica del control vectorial.

---

## 2. Modelos Bio-Matemáticos y Ventana Crítica de Intervención

- **Modelos de referencia validados:**
  - *Rueda et al. (1990)*: Efecto de la temperatura en el desarrollo preimaginal de *Aedes aegypti*.
  - *Tun-Lin et al. (2000)*: Calibración de tasas de eclosión y desarrollo según el tipo de contenedor.
  - *Mordecai et al. (2019)*: Límites térmicos y transmisión óptima de arbovirosis.
- **Ventana Crítica de Intervención Sanitaria:**
  - En temperaturas de la Costa ecuatoriana (**26°C a 32°C**), el mosquito completa su ciclo de huevo a adulto transmisor en **solo 5 a 7 días** (e incluso menos en agua tibia estancada con materia orgánica).
  - Toda respuesta municipal que tarde más de 5 días llega cuando el vector ya está volando y transmitiendo.

---

## 3. Benchmarking de Soluciones Existentes

- **Mosquito Alert (España / Unión Europea):**
  - Gran alcance ciudadano, pero cuello de botella severo: requiere validación de entomólogos humanos que tarda días o semanas. Carece de despacho municipal táctico automatizado.
- **DengueChat (Nicaragua / UC Berkeley):**
  - Plataforma comunitaria valiosa pero con registro manual de formularios; sin inferencia climática micro-local ni optimización logística de rutas.
- **Ovitrampas y Trampas IoT:**
  - Requieren inversión en hardware físico por punto; barreras insalvables en barrios periurbanos por vandalismo, hurto, reposición de baterías y costo unitario.

---

## 4. Contramedidas y Blindaje para el Jurado

1. **Separación IA de Percepción vs. Modelo Determinista:**
   - La IA (Gemini Flash) actúa exclusivamente como transductor perceptivo (clasifica recipiente y agua); la estimación del riesgo (IRE) y los días de eclosión provienen de ecuaciones matemáticas deterministas y reproducibles.
2. **Triaje y Mitigación de Falsos Positivos:**
   - Filtro de confidencia en la inferencia visual + deduplicación geoespacial (< 15 metros) para no saturar a los operadores municipales.
3. **Sostenibilidad B2G y B2B:**
   - Solución orientada a la evidente brecha presupuestaria del sector público: reemplaza gastos inútiles de combustible y pesticida por una suscripción SaaS de bajo costo (< $50/mes por municipio).

---

## 5. Vacíos de Evidencia Reconocidos

- Cifras exactas y desglosadas del desperdicio de insecticida en Guayaquil específico (la literatura cita ineficiencias de ULV del 40-60%, pero no hay una auditoría pública cantonal de litros perdidos).
- Costos consolidados de robo y pérdida por vandalismo de trampas IoT en Ecuador (no se han desplegado masivamente por inviabilidad previa).
