# AedesGuard — Implementation Plan
**IEEE Rising Stars 2026 | Track 2: Public Health**

> Living document. Mark each task `[x]` when completada. El equipo debe hacer pull antes de empezar una tarea.

---

## PASO 0 — Obtener API Key de Gemini (15 min) ← HACER PRIMERO

> Quién: cualquier integrante con cuenta Google

1. [ ] Ir a **https://aistudio.google.com**
2. [ ] Iniciar sesión con cuenta Google
3. [ ] En el menú izquierdo, hacer click en **"Get API key"**
4. [ ] Click en **"Create API key"** → seleccionar o crear un proyecto
5. [ ] Copiar la clave generada (empieza con `AIza...`)
6. [ ] Crear el archivo **`.env`** en la raíz del proyecto (ver `.env.example`)
7. [ ] Pegar la clave: `GEMINI_API_KEY=AIza...`
8. [ ] Verificar que `.env` está en `.gitignore` ← NUNCA subir este archivo al repo

---

## DÍA 1 — Backend Vivo con APIs Reales

### 1.1 Setup del entorno Python
- [ ] Crear entorno virtual: `python -m venv venv`
- [ ] Activar: `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Mac/Linux)
- [ ] Instalar dependencias: `pip install -r backend/requirements.txt`
- [ ] Verificar instalación: `pip list | grep fastapi`

### 1.2 Vision Service — Gemini Flash
- [x] Archivo creado: `backend/app/services/vision_service.py`
- [x] Prompt actualizado con clasificacion cientifica de Naty (tamano, materia organica, agua, natural/artificial)
- [ ] Probar con imagen de prueba (llanta con agua)
- [ ] Verificar que el JSON de respuesta tiene todos los campos del contrato

### 1.3 Climate Service — Open-Meteo (sin API key)
- [x] Archivo creado: `backend/app/services/climate_service.py`
- [ ] Probar con coordenadas de Guayaquil: lat=-2.19, lng=-79.89
- [ ] Verificar respuesta: temperatura y humedad reales

### 1.4 IRE Calculator mejorado (aporte de Biotecnologia)
- [x] Tamano del deposito como factor (small/medium/large)
- [x] Materia organica como multiplicador de riesgo (+30%, calibrado con Tun-Lin 2000)
- [x] Distincion ACTIVE (con agua) vs POTENTIAL (sin agua, riesgo potencial)
- [x] Clasificacion natural (charco) vs artificial (llanta, balde)
- [x] Nota cientifica honesta: IRE es indice de riesgo, no certeza de eclosion
- [x] Estimacion de dias calibrada con datos empiricos de laboratorio:
  - Fuente 1: Rueda et al. (1990) — desarrollo Ae. aegypti a 6 temperaturas (15-34°C)
  - Fuente 2: Tun-Lin et al. (2000) — umbral minimo 8.3°C, supervivencia 88-93% entre 20-30°C
  - Umbral minimo de desarrollo corregido: 8.3°C (antes: 16°C)
  - Dias a emergencia calibrados: 27°C→7d, 25°C→10d, 20°C→12d, 15°C→31d
  - Factor materia organica ajustado a 1.30 (Tun-Lin: recipientes con MO producen adultos mas grandes con mayor potencial vectorial)

### 1.5 Backend integrado
- [x] `main.py` actualizado con servicios reales y campos biologicos completos
- [ ] Correr servidor: `cd backend && python app/main.py`
- [ ] Verificar `/health` → `{"status": "healthy"}`
- [ ] Probar `GET /api/foci` → devuelve 40 focos GeoJSON
- [ ] Probar `POST /api/reports` con imagen base64 real → IRE calculado con datos reales
- [ ] Probar `POST /api/routes/dispatch` → ruta optima calculada

### 1.5 Smoke test completo
- [ ] Correr script de prueba: `python backend/tests/smoke_test.py`
- [ ] Los 3 endpoints responden en < 5 segundos
- [ ] Commit: `feat(backend): integrate gemini vision and open-meteo climate apis`

---

## DÍA 2 — Frontend Móvil + Tiempo Real

### 2.1 PWA Manifest
- [ ] Crear `frontend/manifest.json`
- [ ] Agregar `<link rel="manifest">` en `index.html`
- [ ] Agregar meta `theme-color` y viewport para móvil
- [ ] Verificar que Chrome ofrece "Instalar app" en el dispositivo

### 2.2 Captura móvil (cámara + GPS)
- [ ] Agregar vista `/report` en el SPA
- [ ] Implementar `navigator.mediaDevices.getUserMedia` para cámara
- [ ] Implementar `navigator.geolocation.getCurrentPosition` para GPS
- [ ] Mostrar preview de la foto antes de enviar
- [ ] Enviar imagen en base64 a `POST /api/reports`
- [ ] Mostrar resultado (IRE score, riesgo, días de emergencia) al usuario

### 2.3 Actualización del mapa en tiempo real
- [ ] Activar polling cada 4 segundos a `GET /api/foci`
- [ ] Cuando llega un foco nuevo: agregar marcador animado al mapa
- [ ] Actualizar KPIs (total focos, críticos, protegidos) en tiempo real
- [ ] Commit: `feat(frontend): mobile capture flow and real-time map updates`

---

## DÍA 3 — Panel de Impacto + Demo Mode

### 3.1 Panel de impacto cuantificado
- [ ] Calcular y mostrar: litros de pesticida ahorrado (focos ignorados × 2.5L)
- [ ] Calcular y mostrar: km evitados vs. ruta ciega
- [ ] Calcular y mostrar: personas protegidas (densidad × área de influencia)
- [ ] Agregar animación de contadores al cargar

### 3.2 Demo Mode (botón secreto para el pitch)
- [ ] Crear función `activateDemoMode()` en frontend
- [ ] Carga escenario: 40 focos activos, 12 críticos, ruta calculada
- [ ] Trigger: doble click en el logo de AedesGuard
- [ ] Fallback backend: si el servidor no responde, usar datos locales

### 3.3 UX móvil pulida
- [ ] Animación de "Analizando con IA..." mientras Gemini procesa
- [ ] Feedback visual: badge de riesgo (CRÍTICO/MEDIO/BAJO) animado
- [ ] Vibración táctil en reporte exitoso (navigator.vibrate)
- [ ] Commit: `feat(frontend): impact dashboard and demo mode`

---

## DÍA 4 — Pitch y Ensayo

### 4.1 Métricas financieras para el pitch
- [ ] Costo por brote de dengue en Ecuador (USD)
- [ ] Costo de despliegue de AedesGuard (infraestructura cloud)
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
- [ ] README actualizado con instrucciones de instalación
- [ ] Repo limpio: no hay credenciales, no hay archivos temporales
- [ ] Tag de release: `git tag v1.0.0-mvp`

---

## Estado actual del proyecto

| Componente | Estado | Responsable |
|---|---|---|
| IRE Calculator (calibrado con literatura peer-reviewed) | ✅ Completo | Biotecnología |
| Route Optimizer | ✅ Completo | Mecatrónica |
| Mock Data (40 focos GBQ) | ✅ Generado | Mecatrónica |
| API Contract | ✅ Definido | Software |
| Backend FastAPI con servicios reales | ✅ Listo para probar | Backend |
| Vision Service — Gemini Flash | ✅ Creado | Backend |
| Climate Service — Open-Meteo | ✅ Creado | Backend |
| Smoke test de endpoints | ✅ Creado | Backend |
| Setup Python + API key | ⏳ En progreso | Backend |
| Frontend Dashboard | ✅ Funcional | Frontend |
| Captura móvil PWA | ⏳ Pendiente | Frontend |
| Panel de impacto | ⏳ Pendiente | Frontend |
| Demo Mode | ⏳ Pendiente | Frontend |
| Pitch narrative | ⏳ Pendiente | Todos |
