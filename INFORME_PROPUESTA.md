# Informe de Propuesta

> Generado a partir de `README.md`, `docs/AUDITORIA_Y_MEJORAS.md`, `research/*.md`, el código real del proyecto y verificación directa de fuentes (búsqueda web en esta sesión). Cada afirmación de impacto lleva su nivel de confianza — ver la nota al pie de cada sección. Documento vivo: actualizar si cambia el estado del MVP.

---

## 1. Título de la propuesta

**Ojito al Mosquito: Sistema de Vigilancia Epidemiológica y Control Vectorial Predictivo ante El Niño**

**Competencia:** IEEE Rising Stars 2026 — Track 2: Public Health

---

## 2. El problema abordado

Ecuador atraviesa un crecimiento crítico de casos de dengue, agravado por los patrones de lluvia intensa asociados a El Niño en la Costa: agua estancada en llantas, tanques y zanjas desbordadas crea criaderos masivos de *Aedes aegypti* justo cuando las temperaturas de la Costa (26-32°C) permiten que el mosquito complete su ciclo de huevo a adulto transmisor en apenas **5-7 días**.

**Cifras verificadas contra fuente oficial (búsqueda directa en esta sesión, no solo la síntesis previa del equipo):**
- Ecuador registró **27.838 casos** de dengue en 2023 y **61.329 en 2024** — un incremento del **+120%** interanual — con **76 muertes confirmadas** (48 adultos, 28 niños). Fuente: boletines epidemiológicos del MSP Ecuador (sistema SIVE-Alerta, [salud.gob.ec](https://www.salud.gob.ec/wp-content/uploads/2025/02/ENFERMEDADES-TRANSMITIDAS-POR-VECTORES-SE-06.pdf)) y cobertura de prensa que los cita directamente ([Primicias](https://www.primicias.ec/sociedad/dengue-casos-ecuador-duplicaron-muertes-covid-88226/)). *(Nota: `docs/research/Nathy Research.pdf` cita 61.352 para el mismo año — diferencia menor entre documentos del equipo, usar 61.329 que tiene el boletín MSP linkeado.)* Hasta la semana epidemiológica 06 de 2025 ya había 5.507 casos y 4 muertes — el problema sigue escalando, no fue solo un pico de 2024.
- Un caso hospitalizado de dengue implica en promedio **5.6 días escolares y 9.9 días laborales perdidos** (Suaya et al. 2009, *AJTMH* 80(5):846-855 — verificado contra AJTMH/PubMed).
- El control focalizado y proactivo puede reducir **15-20%** los costos operativos recurrentes frente a un modelo reactivo (Baly, Toledo & Boelaert 2007, *Trans R Soc Trop Med Hyg* 101:578-586 — verificado).
- La fumigación ULV en zonas urbanas densas logra solo un **40-60% de reducción transitoria por ciclo** de la población adulta (Bonds 2012, *Medical and Veterinary Entomology* 26(2):121-130 — revisión crítica, confirmada real en esta sesión), y la población se recupera en semanas. `research/Jose.md` atribuye a Giglioli (1948) el umbral de que se necesitaría cubrir >97% de la biomasa adulta para bajar la transmisión a nivel poblacional ("paradoja de Giglioli") — **ese 97%/1948 puntual no lo pude confirmar independientemente**; usar el 40-60% de Bonds (2012) como cifra principal, y el concepto de la paradoja de forma cualitativa si no se puede verificar el original antes del pitch.
- *Aedes aegypti* en la Costa ecuatoriana presenta mutaciones de resistencia genética a piretroides (kdr F1534C/V1016I) en frecuencias superiores al 70-85%, según `research/Jose.md` (cita: Ponce et al. 2020, *Infection, Genetics and Evolution*). **Esta cita puntual no la pude confirmar** en esta sesión — mi búsqueda solo encuentra trabajos similares de Ponce-García sobre México en otra revista. Si es correcta, es un argumento fuerte (fumigar a ciegas con el mismo químico acelera la resistencia); si el equipo no puede confirmar el DOI antes del pitch, mejor no citarla con esa precisión.

**El cuello de botella operativo:** el modelo actual de respuesta municipal (fumigación en bloque por barrio, sin saber dónde están los criaderos reales) tarda días en reaccionar, cuando la ventana biológica real es de una semana, logra una reducción parcial y transitoria de la población adulta, y no ataca los criaderos que siguen produciendo nuevos mosquitos. La cifra de "70% del insecticida desperdiciado" que circulaba en material anterior del equipo **no tiene fuente primaria confirmada y se descarta** — usar en su lugar la cifra de Bonds (2012) de arriba.

---

## 3. Solución desarrollada

**Ojito al Mosquito** es una plataforma 100% software (sin hardware físico) que cierra el ciclo completo entre la detección de un criadero y la intervención sanitaria en el terreno. Pipeline real, verificado contra el código (`backend/app/main.py`):

```
Ciudadano / brigadista (PWA móvil)
    │ foto (comprimida en Canvas, multipart/form-data) + GPS
    ▼
POST /api/reports
    ├── Gemini 3.6 Flash → clasifica tipo de depósito, agua, materia orgánica
    ├── Open-Meteo → temperatura y humedad real del punto
    └── Motor IRE (determinista) → Índice de Riesgo Entomológico, calibrado con
        Rueda et al. (1990) y Tun-Lin et al. (2000)
    ▼
Dashboard GIS (Leaflet + heatmap, actualización cada 4s)
    ▼
POST /api/routes/dispatch → heurística de ruteo (Nearest Neighbor ponderada por
                             riesgo, no un TSP exacto) + configuración de brigadas
                             por modo de transporte (a pie / mochila / vehicular)
    ▼
Navegación directa a Google Maps → intervención en campo → cierre con foto
    ▼
POST /api/foci/resolve → Gemini valida visualmente que la intervención fue real
                          (contraste Antes/Después cuando hay foto original)
```

**Decisión de diseño clave para la credibilidad ante evaluadores técnicos:** la IA (Gemini) actúa únicamente como *transductor perceptivo* — clasifica qué hay en la foto. El riesgo epidemiológico (IRE) lo calcula una fórmula matemática determinista y auditable, no la IA. Esto da trazabilidad científica total: cualquier resultado se puede explicar y reproducir con la fórmula, no depende de una caja negra.

**Stack:** FastAPI (Python) · Vanilla JS + Leaflet.js · Google Gemini 3.6 Flash · Open-Meteo · PWA.

---

## 4. Beneficios e impacto esperado

- **Reducción del tiempo de reacción:** de un ciclo de reporte-a-intervención de días (proceso manual/reactivo típico) a minutos de procesamiento automático + despacho inmediato de brigada, dentro de la ventana biológica de 5-7 días antes de que el mosquito complete su ciclo.
- **Uso más eficiente de recursos de fumigación:** al dirigir la intervención a criaderos confirmados (con tipo de depósito, volumen y presencia de agua clasificados por IA) en vez de fumigar barrios completos a ciegas — consistente con la evidencia de que el tratamiento dirigido a contenedores productivos es más eficiente que el tratamiento indiscriminado.
- **Retención ciudadana:** cada reporte recibe una acción doméstica inmediata y concreta (ej. *"Perforá la llanta para que no vuelva a acumular agua"*), no solo un "gracias por reportar" — evita el abandono típico de herramientas de ciencia ciudadana que no dan una respuesta útil de inmediato.
- **Auditoría real del cierre de intervenciones:** validación visual Antes/Después con IA, algo que ninguna de las soluciones comparables (Mosquito Alert, DengueChat, trampas IoT) ofrece hoy.
- **Costo de despliegue bajo:** 100% software, sin inversión en hardware físico (trampas, sensores), lo que lo hace desplegable rápidamente a diferencia de soluciones IoT que requieren meses de fabricación/instalación.
- **Escalabilidad:** cualquier ciudad con GPS y smartphones puede adoptarlo; no depende de infraestructura física instalada previamente.

*Nota de honestidad: las cifras de porcentaje de ahorro de pesticida/combustible que circulan en materiales previos del equipo no tienen todavía una medición propia auditada — el beneficio real se puede argumentar cualitativamente (evidencia científica de que el tratamiento dirigido es más eficiente) y se debe medir con datos reales durante un piloto, no proyectar como número cerrado.*

**Contraste de costos verificado en esta sesión** (`docs/research/Nathy Research.pdf`, dos de tres citas confirmadas): un caso hospitalizado de dengue cuesta entre **USD 196 y 866** al sistema de salud (Thalagala et al. 2016, confirmado), mientras que el biolarvicida Bti suprime la producción de pupas en **91% durante 8 semanas** — más efectivo que el temefos químico tradicional, que muestra reinfestación en solo 6 semanas por resistencia del vector (Setha 2016 y George 2015, ambos confirmados). Esto sostiene el argumento de prevención-vs-tratamiento con evidencia real, independientemente de las cifras de ahorro operativo (35-40%) que siguen sin medición propia.

---

## 5. Estado de avance de la solución

Verificado contra el código, no contra lo que dice cada commit — ver `README.md` → "Estado de la auditoria tecnica" para el detalle completo.

**Implementado y funcionando:**
- Clasificación de imágenes con IA (Gemini 3.6 Flash), validada con un benchmark de 8 imágenes de prueba diseñado por el equipo (8/8 correctas)
- Motor IRE calibrado y recalibrado tras revisión cruzada con la literatura científica
- Clima en tiempo real (Open-Meteo) con fallback a datos históricos
- Dashboard GIS con mapa de calor en tiempo real
- Optimización y despacho de rutas de brigadas, configurable por modo de transporte y número de operarios, con jornada máxima de 6h y rebalanceo automático de carga
- Exportación de rutas a navegación de Google Maps
- Exclusión de cuerpos de agua reales (Río Guayas / Estero Salado) en las simulaciones
- Validación visual Antes/Después con IA al cerrar un foco
- Reporte ciudadano asíncrono (no bloquea la interfaz mientras la IA analiza)
- Subida de fotos optimizada (compresión + multipart, no Base64)

**Pendiente:**
- Migración de persistencia a una base de datos real (SQLite/PostGIS) — hoy usa un archivo GeoJSON plano, funcional para un piloto pero no para producción con múltiples procesos concurrentes
- Soporte offline (PWA con cola local) y polling adaptativo para ahorrar batería/datos móviles
- Selector dinámico de base de operaciones de brigadas (hoy sigue fijo en una coordenada)
- Refinamientos bio-climáticos sugeridos por `docs/research/Nathy Research.pdf` (aceleración del ciclo por anomalía tipo El Niño, punto de calibración a 35°C) y tope de carga por mochila de brigadista (5kg/14L) — ninguno está en el código todavía; el umbral de 8.3°C sí está implementado

**Parcial / con matices a declarar:**
- Algunos parámetros operativos de brigadas (velocidad, minutos por parada) son estimaciones internas del equipo, no todos tienen cita académica primaria confirmada de forma independiente
- Algunas métricas financieras de materiales previos no resistieron la verificación cruzada (ver `PITCH.md` → "Métricas: qué decir con confianza y qué evitar")

---

## 6. Recursos necesarios

**Para continuar el desarrollo (corto plazo):**
- Tiempo de equipo para cerrar los pendientes técnicos (persistencia, offline, depot dinámico) — mismo equipo interdisciplinario actual (biotecnología, mecatrónica, 2x software)
- Costo de API de Gemini (nivel gratuito usado durante el MVP; a escala real habría que presupuestar el costo por inferencia — no auditado todavía, ver nota de honestidad en Beneficios)
- Hosting cloud básico para el backend (FastAPI) y una base de datos administrada si se migra de GeoJSON plano

**Para un piloto institucional (mediano plazo, si aplica):**
- Convenio con un GAD municipal o el MSP para acceso a brigadas reales y datos de contraste (validar el modelo IRE contra reportes epidemiológicos reales, no solo datos simulados)
- Acompañamiento de un entomólogo o epidemiólogo para calibrar/validar el modelo con datos de campo del cantón piloto
- Presupuesto de comunicación/difusión ciudadana para lograr adopción del reporte comunitario

*Nota: no hay alianzas institucionales confirmadas todavía (MSP, INSPI, GADs) — son parte del plan propuesto, no tracción ya conseguida. Presentarlas como tal ante evaluadores.*

**Marco legal e institucional del cliente objetivo** (`research/Jose.md` v2 — códigos oficiales ecuatorianos, bajo riesgo de estar mal citados, pero no reverificados en esta sesión):
- El **GAD Municipal** (no el MSP) tiene la competencia legal y presupuestaria del saneamiento ambiental y la fumigación cantonal, según el **COOTAD** (Art. 55 lit. d; Art. 54 lit. k y r) — es el cliente institucional natural. El **MSP**, por la Ley Orgánica de Salud, es el aliado de interoperabilidad (SIVE-Alerta), no el comprador del software.
- Vía de entrada al mercado público sugerida: **Ínfima Cuantía SERCOP (techo reportado de USD 10.000)** para un piloto ágil de 3-6 meses, evitando el proceso de licitación tradicional.
- **Referencia de costo operativo real de una brigada en Guayaquil** (según SERCOP y el Salario Básico Unificado 2026 de USD 482): entre **USD 145 y USD 245 por brigada/día**, considerando insumo químico, combustible y mano de obra. Esta cifra da una base real para argumentar el ahorro potencial del software — pero **el porcentaje de ahorro (35% en km, 40% en químicos) sigue siendo una proyección del equipo, no una medición propia**; hay que decirlo así si preguntan.

---

## 7. Plan de implementación — principales hitos

| Fase | Horizonte | Hitos principales |
|---|---|---|
| **Fase 0 — MVP Hackathon** (completada) | Sept 2026 | Pipeline completo funcionando: reporte → clasificación IA → IRE → despacho de brigadas → cierre validado. Ver sección 5 para el detalle exacto de qué está hecho. |
| **Fase 1 — Endurecimiento técnico** | 0-3 meses | Migrar persistencia a base de datos real, implementar soporte offline (PWA), selector dinámico de base de brigadas, medir latencia/costo real de la IA en producción |
| **Fase 2 — Piloto controlado** | 3-6 meses | Piloto en un sector acotado de Guayaquil con brigadas reales; validar el modelo IRE contra reportes epidemiológicos reales; ajustar parámetros operativos con datos de campo (reemplazar estimaciones internas por mediciones propias) |
| **Fase 3 — Integración institucional** | 6-12 meses | Explorar integración con SIVE-Alerta (MSP), formalizar modelo de sostenibilidad (B2G/B2B), evaluar expansión a otro cantón de la Costa |

---

## 8. Material de apoyo

- **Código fuente y documentación técnica completa:** `README.md` (arquitectura, endpoints, modelo IRE, criterio de rutas, brigadas configurables)
- **Auditoría técnica y UX con propuestas de mejora:** `docs/AUDITORIA_Y_MEJORAS.md`
- **Snippets de implementación de mejoras:** `docs/PUNTOS_EXTRAS_IMPLEMENTACION.md`
- **Guion de pitch y preparación ante jurado:** `PITCH.md` (incluye benchmarking competitivo, Q&A de jurado, y la misma tabla de verificación de cifras que este informe)
- **Guiones de pitch cronometrados:** `research/GUION_PITCH_2_30_MIN.md` (usar este — límite de tiempo confirmado en 3:00 min), `research/GUION_PITCH_3_30_MIN.md` (referencia, excede el límite real)
- **Bibliografía de 65 fuentes APA (epidemiología, resistencia genética, modelos bio-matemáticos, marco legal y SERCOP):** `research/Jose.md` — dos citas puntuales (Ponce et al. 2020 sobre kdr en Ecuador, y el "97%"/Giglioli 1948) no se pudieron confirmar de forma independiente en esta sesión, ver `PITCH.md` para el detalle
- **Base científica del modelo IRE y papers de respaldo:** `docs/research/` (ver `docs/research/README.md` — incluye Rueda 1990, Tun-Lin 2000, Doeurk 2025, y la investigación de contexto técnico de una compañera del equipo)
- **Benchmark de clasificación de imágenes:** `test-images/` (8 imágenes diseñadas para casos límite — control negativo, falso positivo, ambigüedad taxonómica, arquetipos positivos)
- **Dataset de demostración:** `data/mock_foci_guayaquil.geojson`
