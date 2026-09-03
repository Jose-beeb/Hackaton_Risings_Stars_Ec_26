# Alerta Mosquitos — Implementation Plan
**IEEE Rising Stars 2026 | Track 2: Public Health**

> Living document. El equipo debe hacer pull antes de empezar una tarea.

---

## Estado actual del proyecto

| Componente | Estado |
|---|---|
| IRE Calculator (calibrado con Rueda 1990 + Tun-Lin 2000) | ✅ Completo |
| 20 unit tests del motor IRE | ✅ Completo |
| Route Optimizer (TSP heurístico) | ✅ Completo |
| Mock Data (40 focos Guayaquil: 10 críticos, 15 medios, 15 bajos) | ✅ Completo |
| Backend FastAPI + persistencia GeoJSON + thread-safe | ✅ Completo |
| Vision Service — Gemini Flash (prompt entomológico) | ✅ Completo |
| Climate Service — Open-Meteo (sin API key) | ✅ Completo |
| Smoke test de 4 endpoints | ✅ Completo |
| PWA manifest + meta tags móvil | ✅ Completo |
| Captura con cámara + GPS (modal) | ✅ Completo |
| Polling en tiempo real (cada 4s) | ✅ Completo |
| Panel de impacto cuantificado | ✅ Completo |
| Demo Mode (doble click en logo) | ✅ Completo |
| Vista Ciudadana / Vista Brigada | ✅ Completo |
| Lenguaje diferenciado ciudadano vs brigada | ✅ Completo |
| Rebrand: AedesGuard → Alerta Mosquitos | ✅ Completo |
| README con guía de contribución y ramas | ✅ Completo |
| PITCH.md — narrativa, problema, impacto, ROI | ⏳ Pendiente |

---

## TAREA PENDIENTE — Parámetros operativos reales de brigadas (Mecatrónica)

> Estos valores están hardcodeados con estimaciones arbitrarias. Deben validarse con datos reales
> antes del pitch para que las métricas de impacto sean defendibles ante el jurado.

- [ ] ¿Cuántos focos puede tratar una cuadrilla sanitaria en un turno? → ajustar `max_stops`
- [ ] ¿Cuántas horas dura un turno de brigada en Ecuador? → ajustar `max_hours_per_brigade`
- [ ] ¿Cuántos litros carga una mochila fumigadora real? → ajustar `max_liters_per_brigade`
- [ ] ¿Cuántos minutos toma tratar un criadero en campo? → ajustar `MINUTES_PER_STOP`
- [ ] ¿Se desplazan en moto, vehículo o a pie? → ajustar `SPEED_KMH`

**Dónde cambiar los valores:** `core/logistics/route_optimizer.py` líneas 10-14

---

## DÍA 4 — Pitch y Ensayo (PENDIENTE)

### 4.1 Métricas financieras para el pitch
- [ ] Costo por brote de dengue en Ecuador (USD)
- [ ] Costo de despliegue de Alerta Mosquitos (infraestructura cloud)
- [ ] ROI proyectado a 12 meses para un municipio de 500k habitantes
- [ ] Añadir a `PITCH.md`

### 4.2 Preparar la demo en vivo
- [ ] Backend corriendo en dispositivo principal (o servidor cloud)
- [ ] Frontend abierto en móvil Y en pantalla para proyectar
- [ ] Escenario demo pre-cargado y funcionando
- [ ] Imagen de prueba (llanta con agua) lista para la demostración
- [ ] Probar en red del venue (o usar hotspot personal)

### 4.3 Ensayos
- [ ] Ensayo 1: pitch completo en 3 minutos (grabado)
- [ ] Ensayo 2: con preguntas simuladas del jurado
- [ ] Ensayo 3: la demo en vivo tiene que ser perfecta

### 4.4 Entregables finales
- [ ] `PITCH.md` completo y revisado
- [ ] Repo limpio: no hay credenciales, no hay archivos temporales
- [ ] Tag de release: `git tag v1.0.0-mvp`

---

## Base científica del modelo IRE

- **Rueda et al. (1990)** — Desarrollo de *Ae. aegypti* a 6 temperaturas (15–34°C).
  Días a emergencia: 27°C→7d, 25°C→10d, 20°C→12d, 15°C→31d.
- **Tun-Lin et al. (2000)** — Umbral mínimo de desarrollo: 8.3°C.
  Materia orgánica aumenta el potencial vectorial del adulto emergente (+30% IRE).

Papers disponibles en `docs/research/`.

---

## Flujo de trabajo del equipo

```powershell
# Siempre partir de main actualizado
git checkout main
git pull origin main
git checkout -b feat/tu-area

# Commitear con conventional commits
git commit -m "feat(bio): descripcion del cambio"

# Subir y abrir PR a main
git push -u origin feat/tu-area
```

**Regla:** Cada cambio que hagas → actualizar la tabla de estado de este archivo.
