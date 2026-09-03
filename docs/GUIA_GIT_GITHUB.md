# Guia de Trabajo Git & GitHub — AedesGuard
**IEEE Rising Stars 2026**

> Lee esto una vez completo. Despues solo necesitas la seccion "Rutina diaria".

---

## Regla de oro

**Nadie toca `main` directamente. Jamas.**

`main` es el codigo que funciona, el que mostramos en el pitch.
Cada uno trabaja en su rama, y cuando algo esta listo y probado, se integra via Pull Request.

---

## Ramas del equipo

| Rol | Rama | Carpeta de trabajo |
|---|---|---|
| Biotecnologia | `feat/bio-engine` | `core/bio_engine/` |
| Mecatronica | `feat/gis-logistics` | `core/logistics/` |
| Software Backend | `feat/backend-api` | `backend/` |
| Software Frontend | `feat/frontend-dashboard` | `frontend/` |

---

## PASO 0 — Setup inicial (hacer UNA sola vez)

### 1. Clonar el repositorio

```bash
git clone https://github.com/Jose-beeb/Hackaton_Risings_Stars_Ec_26.git
cd Hackaton_Risings_Stars_Ec_26
```

### 2. Crear tu rama y publicarla

Ejecuta el comando que corresponde a tu rol:

```bash
# Biotecnologia
git checkout -b feat/bio-engine
git push -u origin feat/bio-engine

# Mecatronica
git checkout -b feat/gis-logistics
git push -u origin feat/gis-logistics

# Backend
git checkout -b feat/backend-api
git push -u origin feat/backend-api

# Frontend
git checkout -b feat/frontend-dashboard
git push -u origin feat/frontend-dashboard
```

### 3. Configurar el entorno Python (solo Backend y quien corra el servidor)

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Mac / Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt
```

### 4. Configurar variables de entorno (solo Backend)

Crear el archivo `.env` en la raiz del proyecto (mismo nivel que README.md):

```
GEMINI_API_KEY=AIza...tu_clave_aqui
ENVIRONMENT=development
PORT=8000
```

> IMPORTANTE: `.env` ya esta en `.gitignore`. Nunca hacer `git add .env`.
> Para obtener la clave: https://aistudio.google.com -> "Get API key"

---

## Rutina diaria (repetir cada sesion de trabajo)

### Al empezar: traer los ultimos cambios

```bash
# 1. Ir a main y actualizar
git checkout main
git pull origin main

# 2. Volver a tu rama y sincronizar
git checkout feat/tu-rama
git merge main
```

Si hay conflictos en este paso, ver la seccion "Resolver conflictos" mas abajo.

### Mientras trabajas: guardar avances

```bash
# Ver que cambiaste
git status

# Agregar solo TUS archivos (nunca usar git add . a ciegas)
git add backend/app/services/vision_service.py
git add backend/app/main.py

# Commitear con mensaje descriptivo
git commit -m "feat(backend): integrate gemini vision with json parsing"
```

### Al terminar: subir tu rama

```bash
git push origin feat/tu-rama
```

---

## Formato de commits (Conventional Commits)

```
tipo(scope): descripcion corta en minusculas
```

| Tipo | Cuando usarlo |
|---|---|
| `feat` | nueva funcionalidad |
| `fix` | correccion de bug |
| `docs` | cambios en documentacion |
| `refactor` | mejora de codigo sin cambiar funcionalidad |
| `test` | agregar o corregir tests |

**Ejemplos correctos:**
```
feat(backend): connect open-meteo climate api with coordinate cache
feat(frontend): add mobile camera capture with geolocation
fix(bio): correct IRE formula for humidity below 50%
docs(pitch): add financial ROI metrics for guayaquil pilot
```

**Ejemplos incorrectos:**
```
cambios
update
arregle el bug
WIP
```

---

## Crear un Pull Request (cuando tu modulo esta listo)

1. Ir al repo en GitHub: `https://github.com/Jose-beeb/Hackaton_Risings_Stars_Ec_26`
2. GitHub muestra un banner amarillo: **"Compare & pull request"** — click ahi
3. Titulo: mismo formato que los commits (`feat(backend): vision api integrated`)
4. Descripcion: responder en 3 lineas:
   - Que hice
   - Como probarlo
   - Que NO esta listo todavia (si aplica)
5. Avisar al equipo en el chat para que aprueben el merge

---

## Resolver conflictos (sin entrar en panico)

Un conflicto pasa cuando dos personas tocaron el mismo archivo. Git lo marca asi:

```
<<<<<<< HEAD (tu codigo)
temperatura = 29.0
=======
temperatura = climate["temperature_c"]
>>>>>>> main (codigo de otro)
```

**Pasos para resolverlo:**

```bash
# 1. Ver que archivos tienen conflicto
git status

# 2. Abrir el archivo, elegir la version correcta (o combinar ambas)
# Borrar las lineas <<<<<, =====, >>>>> y dejar el codigo que debe quedar

# 3. Marcar como resuelto
git add archivo_con_conflicto.py

# 4. Completar el merge
git commit -m "fix: resolve merge conflict in main.py"
```

**Regla practica:** si el conflicto es en tu carpeta, vos decides. Si es en un archivo compartido, habla con el equipo antes de elegir.

---

## Proteger `main` en GitHub (hacer UNA vez — quien sea admin)

1. Ir al repo en GitHub
2. **Settings** → **Branches** → **Add branch protection rule**
3. Branch name pattern: `main`
4. Activar:
   - [x] Require a pull request before merging
   - [x] Require at least 1 approval
5. Guardar

Esto hace imposible pushear directo a main por accidente.

---

## Emergencias del hackathon

### "Subi algo malo a mi rama"

```bash
# Ver el historial
git log --oneline -5

# Deshacer el ultimo commit (los archivos quedan intactos)
git reset --soft HEAD~1

# Corregir y volver a commitear
```

### "Necesito el codigo de otro integrante ya, sin esperar el PR"

```bash
# Traer su rama sin hacer merge
git fetch origin feat/backend-api

# Crear una rama local temporal basada en la de el/ella
git checkout -b temp/test-backend origin/feat/backend-api
```

### "Rompí todo en mi rama"

```bash
# Volver al ultimo commit estable
git checkout -- .

# O si es muy grave, resetear la rama al estado de main
git reset --hard origin/main
```

> ADVERTENCIA: `git reset --hard` borra cambios sin guardar. Usarlo solo si no hay otra opcion.

---

## Territorios de cada rol

Cada uno trabaja en su carpeta. No tocar la del otro sin avisar primero.

```
core/bio_engine/     ← Biotecnologia
core/logistics/      ← Mecatronica
backend/             ← Software Backend
frontend/            ← Software Frontend

# Archivos compartidos (cambiar con consenso del equipo):
docs/API_CONTRACT.md
IMPLEMENTATION_PLAN.md
PITCH.md
data/
```

Si necesitas cambiar `API_CONTRACT.md`, avisas al equipo primero.
Es el contrato — si lo cambias sin avisar, el frontend y backend se rompen.

---

## Checklist antes de cada push

- [ ] `git status` — no hay archivos de otros roles en mis cambios
- [ ] No incluyo el archivo `.env` en el commit
- [ ] El servidor corre sin errores en mi maquina
- [ ] El mensaje del commit sigue el formato `tipo(scope): descripcion`
