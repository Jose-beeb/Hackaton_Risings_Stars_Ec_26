# Ojito al Mosquito — Pitch Document

**IEEE Rising Stars 2026 — Track 2: Public Health**

> Documento vivo — reemplaza la version de Dia 1 (que tenia features marcadas como pendientes que ya estan hechas, y cifras sin verificar). Generado a partir de `README.md`, `docs/AUDITORIA_Y_MEJORAS.md`, `research/*.md` y el codigo real (`core/logistics/route_optimizer.py`, `frontend/js/app.js`). Actualizar con cada avance — no dejar que se desactualice otra vez.
>
> **Para sacar contenido de diapositivas rapido, ver `research/RESUMEN_INVESTIGACION.md`** — consolida todas las cifras de investigacion por tema con su nivel de confianza, sin la narrativa de proceso de este documento.

---

## ✅ Resuelto / ⚠️ Sigue pendiente

1. **Límite de tiempo: CONFIRMADO en 3:00 minutos** (equipo, sept 2026). Esto invalida `research/GUION_PITCH_3_30_MIN.md` como guion a ensayar tal cual — apunta a 3:30 con margen hasta 4:00, se pasa del límite real. **Usar `research/GUION_PITCH_2_30_MIN.md` como base** (objetivo 2:30, que ya deja 30s de margen contra el tope real de 3:00). El bloque de "Modelo de Negocio & Alianzas" del guion de 3:30 es más completo — si sobra tiempo al ensayar el de 2:30, es el primer candidato a sumar, no el de benchmarking internacional (ya cubierto más corto en la sección de diferenciación de este documento).
2. **Cifras de `research/Jose.md` — verificadas en esta sesión con búsqueda real, no solo con el criterio de "viene de Perplejidad así que hay que dudar":** los casos de Ecuador (27.838 en 2023 → 61.329 en 2024, +120%, 76 muertes) SÍ tienen respaldo en boletines oficiales del MSP (SIVE-Alerta) y prensa que los cita directamente — se pueden decir con confianza. Lo que sigue sin fuente primaria confirmada: el costo por caso fatal (USD 80.000), los USD 447.982 invertidos por el MSP en fumigación 2024, y el costo regional LatAm (USD 3.000 millones/año). Ver tabla completa en "Métricas: qué decir con confianza y qué evitar" más abajo.
3. **`research/Jose.md` se amplió con una bibliografía de 65 fuentes APA** (marco legal COOTAD/LOS, vía de contratación SERCOP, estructura de costos reales de brigadas, mutaciones de resistencia genética). Es un salto real de calidad — arregla justamente el hueco del "70% de insecticida desperdiciado" con una explicación mejor citada (ver tabla de cifras). Dos citas puntuales de esa ampliación no se pudieron confirmar en esta sesión (ver notas ⚠️ en la tabla) — no invalidan el resto del documento, pero hay que verificarlas antes de citarlas con precisión ante el jurado.
4. **Nueva investigación de una compañera del equipo** (`research/papers/Nathy Research.pdf` — antes en una carpeta `docs/research/` separada que se eliminó para no tener dos carpetas de research; todo vive ahora en `research/`, ver `research/README.md`): trae dos citas nuevas confirmadas (Setha 2016, eficacia del Bti; Thalagala 2016, costo de hospitalización) y una sin confirmar (Zimmermann 2024). También trae parámetros bioclimáticos (aceleración del ciclo por El Niño, punto de 35°C) que **todavía no están en el código** de `ire_calculator.py` — no decir en el pitch que el sistema ya calcula eso. Detalle completo en la tabla de cifras y en la sección de Estado de avance.

---

## El problema

**Guion emocional (de `research/GUION_PITCH_3_30_MIN.md`, listo para usar):**

> *"Tras las lluvias torrenciales de El Niño, la calle de Mariana quedó inundada, con zanjas desbordadas y llantas con agua empozada en la vereda. Con el calor extremo de la Costa, el mosquito pasa de huevo a transmisor en solo cinco días. Mariana cuida a sus hijos y mantiene su casa impecable, pero los mosquitos que nacen a pocos pasos de su puerta entran directo a su sala. A la semana, su hijo menor arde en fiebre con dolores insoportables; ella pierde días de sustento cuidándolo y el centro de salud de su sector no da abasto."*

**Cifras a usar (con nivel de confianza):**

| Cifra | Fuente | Confianza |
|---|---|---|
| 5.6 dias escolares / 9.9 dias laborales perdidos por caso hospitalizado de dengue | Suaya et al. (2009), *AJTMH* 80(5):846-855 (pagina corregida — el README/team tenian 696-701, verificado por busqueda directa contra AJTMH/PubMed) | ✅ Verificado en esta sesion |
| Reduccion de costos recurrentes 15-20% con control focalizado vs. reactivo | Baly, Toledo, Boelaert et al. (2007), *Trans R Soc Trop Med Hyg* 101:578-586 — cifra real corregida (el equipo tenia 30-45%, el paper dice 13-19%) | ✅ Cita confirmada (revista/paginas correctas); la cifra especifica 13-19% queda como la verifico una sesion anterior, no reconfirmada linea por linea ahora |
| Casos de dengue Ecuador 2023 (27.838) vs. 2024 (61.329, +120%), 76 muertes | `research/Jose.md`, respaldado por boletines oficiales MSP Ecuador (SIVE-Alerta, salud.gob.ec) y cobertura de prensa que los cita directamente | ✅ Verificado en esta sesion — confirmado con fuente oficial, no solo la sintesis de Perplexity. **Nota:** `research/papers/Nathy Research.pdf` cita **61.352** para 2024 (vs. 61.329 en Jose.md/MSP) — diferencia menor, probablemente un redondeo o un corte de fecha distinto del boletin; usar 61.329 (el que tiene el link directo al boletin MSP) y no mezclar los dos numeros en la misma presentacion |
| Datos parciales 2025: 5.507 casos confirmados hasta semana epidemiologica 06, 4 muertes en ese periodo | `research/papers/Nathy Research.pdf` | ⚠️ No se busco la fuente primaria puntual en esta sesion, pero es coherente con la tendencia de los boletines MSP ya verificados — util para mostrar que el problema sigue escalando en 2025, no solo fue un pico de 2024 |
| Eficacia del biolarvicida Bti: suprime produccion de pupas 91% durante 8 semanas | Setha et al. (2016), publicado en *PLOS Neglected Tropical Diseases* (Nathy Research.pdf lo atribuye a *Parasites & Vectors* — revista incorrecta, el hallazgo si es real) | ✅ Verificado en esta sesion contra el resumen del paper |
| Costo de hospitalizacion por dengue: USD 196-866 (adultos, Sri Lanka) | Thalagala et al. (2016) | ✅ Verificado — coincide con el limite superior ($866) que cita Nathy Research.pdf |
| Costo de hospitalizacion USD 866-1.855 atribuido a "Zimmermann 2024" | `research/papers/Nathy Research.pdf` | ⚠️ No pude confirmar una publicacion de Zimmermann (2024) con esos numeros — el limite inferior coincide con Thalagala 2016, el superior no lo pude verificar. Usar el rango de Thalagala (confirmado) en vez de este si preguntan por la fuente |
| Costo regional del dengue en LatAm > USD 3.000 millones/año; USD 447.982 invertidos por el MSP en fumigacion 2024 | `research/Jose.md` (sintesis Perplexity) | ⚠️ No se busco fuente primaria para estas dos cifras puntuales en esta sesion — presentar como "segun cifras reportadas", no como hecho auditado |
| Eficacia ULV en zonas urbanas densas: 40-60% de reduccion transitoria por ciclo (no el "70% desperdiciado" generico de antes) | `research/Jose.md` v2 (post-pull): Bonds (2012), *Medical and Veterinary Entomology* 26(2):121-130 — revision critica de ULV, confirmada real en esta sesion. La "paradoja de Giglioli" (se necesita >97% de la biomasa adulta para bajar la transmision poblacional) se atribuye a Giglioli (1948), pero **no pude confirmar el 97% ni el año exacto** — un resultado de busqueda menciona un Giglioli (1979) con cifras de mortalidad distintas (87-97%, otro contexto) | ✅ Bonds 2012 confirmado — usar el 40-60% con esa cita. ⚠️ El "97%"/Giglioli 1948 no confirmado, no citarlo con precision de fecha/numero sin que alguien del equipo verifique el original |
| Resistencia genetica a piretroides en Ecuador (mutaciones kdr F1534C/V1016I, >70-85% frecuencia alelica) — explica por que fumigar a ciegas es activamente contraproducente | `research/Jose.md` v2, Ponce, Morales, Argoti & Carvalho (2020), *Infection, Genetics and Evolution*, 85, 104523 | ⚠️ **No pude confirmar esta cita especifica.** Mi busqueda solo encuentra trabajos de Ponce-Garcia sobre Mexico en *Parasites & Vectors*, no este paper de Ecuador en esa revista. Puede ser real (mi busqueda no es exhaustiva) o estar mal atribuido — **alguien del equipo debe abrir el DOI antes de citarlo frente al jurado** |

**El cuello de botella real, en una frase:** no es que falte informacion sanitaria, es que la respuesta municipal tarda 48-72h en llegar cuando el *Aedes aegypti* completa su ciclo de huevo a adulto transmisor en **5-7 dias a las temperaturas de la Costa** (26-32°C) — el margen de reaccion es angosto y hoy se fumiga sin saber donde esta el criadero real.

---

## La solución — qué construimos de verdad (no lo que dice el pitch de Día 1)

Pipeline real, verificado contra el código en `backend/app/main.py`:

```
Ciudadano / brigadista (PWA móvil)
    │ foto (multipart, comprimida a 1024px en Canvas) + GPS
    ▼
POST /api/reports (FastAPI)
    ├── Gemini 3.6 Flash (clasificación visual: tipo de depósito, agua, materia orgánica)
    ├── Open-Meteo (temperatura y humedad real del punto)
    └── Motor IRE (determinista, calibrado con Rueda 1990 / Tun-Lin 2000)
    ▼
GeoJSON (data/mock_foci_guayaquil.geojson)
    ├── GET /api/foci cada 4s → Dashboard GIS (Leaflet + heatmap)
    └── POST /api/routes/dispatch → Rutas óptimas por brigada
                                        ▼
                          Navegación directa (Google Maps) → Cierre con foto de evidencia
                                        │
                          POST /api/foci/resolve → Gemini valida Antes/Después
```

**Los tres pilares para el guion (siguen siendo correctos conceptualmente, con matices):**

1. **Inferencia visual** — clasifica el depósito y valida agua en segundos. *Matiz honesto: la latencia real medida contra el benchmark del equipo varió entre 5 y 113 segundos por imagen (no es instantáneo siempre); el flujo de reporte es asíncrono así que el usuario no se queda mirando una pantalla congelada mientras espera.*
2. **Motor bio-matemático determinista (IRE)** — la IA NO decide el riesgo. Clasifica el recipiente; el riesgo lo calcula una fórmula auditable basada en literatura peer-reviewed. Esto es un argumento fuerte ante el jurado: **explicabilidad total**, no una caja negra.
3. **Despacho logístico** — con matiz técnico importante para si un jurado técnico pregunta: **no es un TSP exacto**, es una heurística *Nearest Neighbor* ponderada por riesgo (ver sección siguiente). Es la decisión correcta para el tamaño de un piloto municipal, pero hay que decirlo así si preguntan — llamarlo "TSP" sin matiz es la clase de imprecisión que un jurado técnico detecta.

---

## Cómo se define el nivel de riesgo (para responder "¿qué es bajo o alto riesgo?")

Verificado contra `core/bio_engine/ire_calculator.py` — no es una estimación cualitativa, es una fórmula:

```
IRE = 40 × peso_contenedor × factor_tamaño × factor_temperatura × factor_humedad × factor_materia_orgánica
```

- **Peso del contenedor:** llanta 1.5, tanque abierto 1.4, canaleta obstruida 1.3, balde 1.1, maceta 0.8, charco 0.7, plástico 0.6.
- **Tamaño:** chico (<5L) 0.85 · mediano (5-50L) 1.0 · grande (>50L) 1.25.
- **Temperatura:** curva calibrada con Rueda (1990), óptimo 28-30°C, decae hacia el límite letal (~40°C).
- **Humedad:** rampa 0.5-1.0, satura sobre 70%. **Materia orgánica:** ×1.30 si hay presencia visible. Sin agua presente, el score cae a 40% del valor (riesgo potencial, no activo).

**Umbrales — decisión operativa del equipo, no un hallazgo científico (decirlo así si preguntan):** ≥70 = 🔴 CRITICAL · 40-69.9 = 🟡 MEDIUM · <40 = 🟢 LOW.

**Cómo se recopila — 2 fuentes automáticas, nada manual:** la foto se clasifica con Gemini Vision (tipo de recipiente, tamaño, agua, materia orgánica, volumen), el clima se consulta en tiempo real a Open-Meteo con el GPS exacto del reporte. Esos 6 datos son el único input — mismos inputs, mismo score, siempre. Es el mismo argumento de "explicabilidad total" del punto anterior, con el detalle exacto por si el jurado pide precisión.

---

## Cómo deciden las rutas y el tiempo de las brigadas (para responder preguntas técnicas del jurado)

Esto es contenido real de `core/logistics/route_optimizer.py`, no marketing — útil si el jurado pregunta "¿cómo deciden qué foco visitar primero?":

**Criterio de selección de la ruta:**
```
score = distancia_km / (ire_score / 30.0)
```
Se visita primero el foco con **menor score**: más cerca gana, pero un IRE alto "acerca" artificialmente al foco. Con IRE=30 el criterio es distancia pura; un foco con IRE=90 compite en igualdad con uno 3 veces más cerca pero de bajo riesgo. En la práctica, la ruta prioriza los focos críticos aunque implique desviarse — no es una fumigación ciega por cercanía.

**Tiempo real por brigada — 3 modos de transporte, cada uno con un objetivo biológico distinto:**

| Modo | Tipo de brigada | Objetivo | Velocidad · min/parada (base) |
|---|---|---|---|
| `foot` | Control Focal (larvicida + inspección) | Destruir huevos/larvas antes de emerger | 7 km/h · 17.5 min |
| `vehicle_walk_attack` | Rociado Residual (mochila motorizada) | Eliminar adultos posados intradomicilio | 5 km/h · 35 min |
| `vehicle_spray` | Fumigación Espacial (nebulización térmica) | Tumbar población adulta en vuelo, sin parar por predio | 10 km/h · 2 min |

**Regla de negocio explícita:** jornada máxima de 6 horas por brigada. El reparto de focos entre brigadas usa el método de Hamilton (proporcional a capacidad) más un **rebalanceo iterativo**: si una brigada queda con más carga real de la que le entra en sus 6h (el reparto inicial no conoce el traslado real hasta armar la ruta), el sistema mueve focos hacia la brigada con más margen hasta que nadie excede su jornada — o marca `excede_jornada: true` en vez de esconder el problema.

**Honestidad si preguntan por la fuente de estos números:** la velocidad y minutos/parada de `foot` vienen de un manual de procesos del MSP citado por el equipo — **título y año exactos no verificados de forma independiente**. `vehicle_walk_attack` y la escala por cantidad de operarios son estimación interna del equipo. Las 6h de jornada son una regla de negocio explícita, no una cita académica. Decirlo así ante una pregunta directa es mejor que inventar una fuente.

---

## Qué ve el ciudadano — cierre del ciclo comunitario

No solo se reporta y se espera a la brigada: en cuanto la IA clasifica el depósito, la app muestra una acción física inmediata (`frontend/js/app.js`, `HOME_ACTION_TIPS`):

| Depósito detectado | Consejo mostrado |
|---|---|
| Llanta | "Perforá la llanta para que no vuelva a acumular agua, o guardala bajo techo seco." |
| Tanque/cisterna abierta | "Cepillá las paredes internas (los huevos se pegan al borde seco) y tapá herméticamente." |
| Maceta | "Vaciá el plato bajo la maceta cada 3 días, o rellenalo con arena." |
| Canaleta obstruida | "Sacá las hojas y la basura de la canaleta para que el agua no se estanque." |

Esto es un argumento de retención de usuario que vale la pena decir en el pitch: una app de ciencia ciudadana que solo dice "gracias por tu reporte" pierde usuarios rápido; esta le da algo que hacer con las manos ya mismo, sin esperar a la brigada.

**Además (nuevo, no está en ningún guion todavía):** al cerrar un foco, la brigada manda una foto de evidencia y **Gemini valida automáticamente si el criadero realmente fue resuelto**, contrastándola contra la foto original del reporte cuando existe. Esto cierra el círculo de auditoría: no alcanza con que la brigada haga clic en "cumplida", hay una verificación visual real. Vale la pena mencionarlo en la sección de diferenciación — ninguna de las soluciones del benchmark (Mosquito Alert, DengueChat, trampas IoT) audita visualmente el cierre de la intervención.

---

## Diferenciación competitiva

De `research/ESTRATEGIA_Y_BLINDAJE_JURADO.md` (benchmarking, sin cambios — se mantiene vigente):

| Criterio | Solución tradicional | Apps ciudadanas (Mosquito Alert / DengueChat) | Trampas IoT | **Ojito al Mosquito** |
|---|---|---|---|---|
| Detección a acción | 48-72h (papel/Excel) | 24-48h (validación humana) | Tiempo real, cobertura puntual | Minutos (IA + cálculo automático, con la salvedad de latencia variable de Gemini anotada arriba) |
| Costo | Alto, cuadrillas no guiadas | Bajo, sin despacho logístico | Cientos de USD por trampa | 100% software, sin hardware |
| Priorización | Fumigación en bloque a ciegas | Mapas de calor estáticos | Datos puntuales sin inferencia | IRE determinista (microclima real + biología calibrada) |
| Logística | Rutas intuitivas del chofer | Ninguna | Ninguna | Despacho heurístico ponderado por riesgo + navegación directa |
| Auditoría de cierre | Ninguna | Ninguna | Ninguna | Validación visual Antes/Después con IA |

---

## Modelo de negocio y alianzas

De `research/GUION_PITCH_3_30_MIN.md` — presentar como plan, no como tracción ya conseguida (no hay evidencia en el repo de alianzas firmadas):

- **B2G (SaaS Municipal / GADs):** suscripción anual por cantón según población, para el panel de inteligencia y el optimizador de cuadrillas.
- **B2B:** licenciamiento de API para empresas de control de plagas, puertos, florícolas y bananeras.
- **Alianzas propuestas (no confirmadas todavía):** MSP/GADs para integrar con SIVE Alerta, academia/INSPI para calibración continua del modelo, comités barriales para activación territorial.

**Cifra a manejar con cuidado:** "< $50/mes por municipio" y "< $0.002 USD por inferencia" son estimaciones internas del equipo sobre costo de cloud/inferencia, no una cotización real ni una auditoría de costos — decirlo como estimación si preguntan, no como precio comercial cerrado.

**Quién es el cliente y cómo se le vende (nuevo, de `research/Jose.md` v2 — marco legal ecuatoriano real, son códigos oficiales, bajo riesgo de estar mal citados):**
- Por el **COOTAD** (Art. 55 lit. d, Art. 54 lit. k y r), el **GAD Municipal** (no el MSP) tiene la competencia y el presupuesto de saneamiento ambiental y fumigación en el cantón — es el cliente natural del SaaS. El MSP, por la **Ley Orgánica de Salud**, tiene la rectoría normativa y SIVE-Alerta — es el aliado de interoperabilidad, no el comprador.
- Vía de entrada sugerida: **Ínfima Cuantía SERCOP (< USD 10.000)** para un piloto de 3-6 meses con la Dirección de Salud e Higiene del GAD — evita el proceso de licitación tradicional para una primera venta.
- **Sin verificar en esta sesión** (son afirmaciones sobre normativa vigente, sería prudente que alguien del equipo con acceso a un abogado o la web de SERCOP confirme el techo exacto de USD 10.000 y que siga vigente al momento del pitch).

---

## Preguntas difíciles del jurado (resumen accionable de `ESTRATEGIA_Y_BLINDAJE_JURADO.md`)

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué no trampas IoT? | Costo unitario + vandalismo/mantenimiento en Latinoamérica hacen inviable cubrir una ciudad; los smartphones ya existen y son gratis para nosotros. |
| ¿Cómo evitan que la IA alucine el riesgo? | La IA solo clasifica la imagen (percepción). El riesgo lo calcula una fórmula determinista y auditable (IRE), no la IA — trazabilidad total. |
| ¿Qué pasa con fotos falsas o irrelevantes? | Filtro de confianza en la clasificación; si no hay evidencia de agua/recipiente, no se genera alerta de brigada. *(Nota: la deduplicación espacial de reportes vecinos a 10-15m sigue en el roadmap, no implementada todavía — no afirmar que ya existe, ver README "Roadmap no implementado".)* |
| ¿Focos en el río? | Máscara geoespacial real de exclusión (Río Guayas / Estero Salado) ya implementada — `core/logistics/water_bodies.py`. |
| ¿Por qué TSP y no despacho tradicional? | No es TSP exacto, es una heurística Nearest Neighbor ponderada por IRE — prioriza urgencia biológica sin sacrificar velocidad de cálculo, razonable para el tamaño de un piloto municipal. |
| ¿Por qué no confían en la fumigación química como solución principal? | Además de la baja penetración en zonas urbanas densas (40-60% de reducción transitoria por ciclo, Bonds 2012), fumigar el mismo químico repetidamente acelera la resistencia genética del vector — hay evidencia de mutaciones de resistencia a piretroides en la Costa ecuatoriana. *(Si preguntan por el dato exacto de frecuencia alélica: la cita puntual del equipo para esto no se pudo confirmar de forma independiente todavía — responder con el argumento general, no con el porcentaje exacto, hasta confirmar el DOI.)* |
| ¿Quién les compra esto — el Ministerio de Salud o el Municipio? | El Municipio (GAD), no el MSP. Por el COOTAD, el GAD tiene la competencia legal y presupuestaria de saneamiento ambiental y fumigación cantonal. El MSP es el aliado de interoperabilidad epidemiológica (SIVE-Alerta), no el comprador. |
| ¿Y el biolarvicida es mejor que el químico tradicional? | Hay evidencia real de que el Bti (biolarvicida) suprime la producción de pupas en 91% durante 8 semanas, mientras que el temefos tradicional muestra reinfestación en solo 6 semanas por resistencia del vector (Setha 2016; George 2015) — pero esto es sobre el insumo que usan las brigadas, no algo que nuestro software fabrique o venda directamente. |

---

## Guion recomendado para ensayar

Con el límite confirmado en 3:00, **ensayar `research/GUION_PITCH_2_30_MIN.md`** (objetivo 2:30, deja 30s de colchón real). No usar el guion de 3:30 tal cual — se pasa del tope.

Ambos guiones necesitan un ajuste puntual antes de grabarse: reemplazar la afirmación genérica de "despacho TSP" por "heurística de ruteo ponderada por riesgo" si se espera una pregunta técnica de seguimiento, y anotar mentalmente que la cifra del 70% de insecticida desperdiciado es una cifra de industria citada de forma genérica, no un dato propio auditado.

---

## Estado real del MVP (reemplaza el checklist de Día 1, que ya no aplica)

Ver `README.md` → sección **"Estado de la auditoria tecnica"** para la tabla completa y verificada contra código. Resumen para el pitch:

- ✅ Clasificación de imágenes con Gemini (modelo actualizado a `gemini-3.6-flash`, 8/8 en el benchmark de imágenes ambiguas del equipo)
- ✅ Motor IRE calibrado y recalibrado tras revisión cruzada con la literatura (`README.md` → "Recalibración del 3-4 sep 2026")
- ✅ Clima en tiempo real, dashboard GIS, despacho de brigadas configurables, exportación a Google Maps, validación visual Antes/Después
- ✅ Reporte asíncrono no bloqueante (el modal se cierra al instante, resultado en tarjeta flotante)
- ❌ Pendiente: persistencia SQLite (sigue en GeoJSON plano), PWA offline / polling adaptativo, selector de depot dinámico (sigue hardcodeado)
- ❌ Pendiente (sugerido por `research/papers/Nathy Research.pdf`, no implementado): aceleración del ciclo de desarrollo por anomalía térmica tipo El Niño (1.5 días menos por cada 2°C sostenido) y el punto de calibración a 35°C (7.8 días); tampoco está modelado el tope de carga por mochila de brigadista (5kg biolarvicida granular / 14L mezcla líquida) en el optimizador de rutas — el umbral de 8.3°C de Tun-Lin sí está implementado y coincide
- ⚠️ Parcial: parámetros operativos de brigadas (algunos números son estimación interna, no cita académica), métricas financieras (varias citas propuestas por el equipo en distintos documentos no resistieron la verificación — ver tabla de arriba)

---

## Métricas: qué decir con confianza y qué evitar

**Decir con confianza (verificado contra fuente primaria, con búsqueda real en esta sesión):**
- 5.6 días escolares / 9.9 días laborales perdidos por caso hospitalizado (Suaya et al. 2009, *AJTMH* 80(5):846-855)
- 15-20% de reducción en costos recurrentes con control focalizado vs. reactivo (Baly et al. 2007, *Trans R Soc Trop Med Hyg* 101:578-586 — no 30-45%, esa cifra está corregida)
- Ecuador: 27.838 casos de dengue en 2023 → 61.329 en 2024 (+120%), 76 muertes confirmadas — respaldado por boletines oficiales del MSP (SIVE-Alerta) y prensa que los cita directamente

**No afirmar — verificado y descartado en esta sesión (se buscó de verdad, no se encontró respaldo):**
- **"70% de insecticida desperdiciado" y "eficacia ULV 40-60% por ciclo"** — no existe una fuente primaria única para ninguna de las dos. La eficacia real del ULV varía 30%-89% según el estudio, sin un número fijo, y la población de mosquitos se recupera en menos de un mes. Reemplazar por la versión cualitativa: "la evidencia muestra que tratar los criaderos productivos es más eficiente que fumigar todo por igual".

**Evitar afirmar como hecho auditado (son estimaciones o no se buscó fuente primaria en esta sesión):**
- $2 USD por criadero intervenido, ROI 1:200 — estimaciones internas del equipo, decirlo así si preguntan
- Costo por caso fatal $80.000, USD 447.982 invertidos por el MSP en fumigación en 2024, costo regional LatAm > USD 3.000 millones/año — de `research/Jose.md`, no se buscó la fuente primaria puntual de estas tres en esta sesión
- "< $50/mes por municipio", "< $0.002 USD por inferencia" — estimaciones de costo de infraestructura, no cotización real

---

## Team

| Rol | Contribución |
|---|---|
| Biotecnología | Modelo IRE, taxonomía de criaderos, prompts de visión |
| Mecatrónica | Algoritmo de rutas, generador de datos mock, métricas logísticas |
| Software Backend | FastAPI, integración Gemini + Open-Meteo, API contract |
| Software Frontend | Dashboard GIS, PWA móvil, UX de captura, panel de impacto |
