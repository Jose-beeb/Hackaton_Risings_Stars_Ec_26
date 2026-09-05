# research/ — Todo lo de investigación y pitch en un solo lugar

**Antes había dos carpetas** (`research/` y `docs/research/`) separando "papers" de "narrativa". Generaba confusión, así que ahora es **una sola carpeta**.

## 📄 Empezar por acá

**`RESUMEN_INVESTIGACION.md`** — todo lo verificado (cifras, citas, benchmarking, marco legal) organizado por tema, con nivel de confianza en cada dato. Es el único archivo que hace falta leer para sacar contenido de pitch e informe; los demás son la fuente/detalle de donde sale ese resumen.

## Estructura

```
research/
├── RESUMEN_INVESTIGACION.md      # <- Leer primero. Todo consolidado.
├── GUION_PITCH_2_30_MIN.md       # Guion a cronometrar (usar este, no el de 3:30)
├── GUION_PITCH_3_30_MIN.md       # Referencia, excede el limite real de 3:00
├── ESTRATEGIA_Y_BLINDAJE_JURADO.md  # Fuente del benchmarking y Q&A del jurado
├── Jose.md                       # Fuente: bibliografia de 65 fuentes APA
└── papers/                       # PDFs y documentos de fuente cruda
    ├── rueda1990.pdf              # Citado en core/bio_engine/ire_calculator.py
    ├── 10.1046@j.1365-2915.2000.00207.x.pdf  # Tun-Lin et al. 2000, idem
    ├── s13071-025-06892-y.pdf     # Doeurk et al. 2025
    ├── pntd.0012397.pdf           # Paper de PLOS NTDs (ver Jose.md)
    ├── Nathy Research.pdf/.docx   # Investigacion de una integrante del equipo
```

**Regla para no volver a mezclar:** si es un PDF o doc de fuente (un paper, un informe externo), va en `papers/`. Si es algo que escribió el equipo (guion, estrategia, síntesis), va en la raíz de `research/`.
