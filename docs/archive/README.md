# Archivo — documentos de planificación inicial (Día 0-2)

Estos documentos cumplieron su función al arrancar el hackathon pero **ya no reflejan el estado real del proyecto**. Se guardan acá por trazabilidad histórica, no para consultarlos como referencia activa.

| Documento | Por qué está acá |
|---|---|
| `Plan.md` | Plan de arquitectura de Día 0. Propone una estructura de carpetas (`backend/app/routers/`, `frontend/js/report_capture.js`, etc.) que no es la que terminó existiendo — el backend real es un `main.py` monolítico y el frontend un solo `app.js`. |
| `IMPLEMENTATION_PLAN.md` | Checklist de tareas de Día 1-2. Quedó desactualizado (dice "PITCH.md pendiente" cuando ya está hecho, no menciona nada de la auditoría técnica posterior). Reemplazado por `README.md` → "Estado de la auditoria tecnica" y `PITCH.md` → "Estado real del MVP". |
| `GUIA_GIT_GITHUB.md` | Guía de flujo de ramas por rol. Su contenido vive duplicado (y más al día) en `README.md` → "Contribuir al proyecto". |
| `GUIA_TRABAJO_ANTIGRAVITY.md` | Guía de cómo prompear a Antigravity por rol, con nombres de archivo que no coinciden con los reales (ej. `core/bio_engine/test_bio.py`, cuando el test real es `backend/tests/test_ire_calculator.py`). |
| `roles/*.md` | Cuestionarios de requerimientos de Día 0 (una pregunta por rol). Todas las preguntas ya están respondidas en el código y en `README.md`. |

**Para el estado real y actual del proyecto, usar:** `README.md`, `PITCH.md`, `INFORME_PROPUESTA.md`, `docs/AUDITORIA_Y_MEJORAS.md`.
