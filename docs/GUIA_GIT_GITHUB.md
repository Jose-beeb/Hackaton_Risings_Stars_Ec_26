# Guía de Trabajo con Git y GitHub — AedesGuard 🦟⚡

Esta guía explica paso a paso cómo cada integrante debe clonar el repositorio, trabajar en su módulo sin romper nada y subir sus cambios a GitHub de forma limpia.

---

## 1. Primer Paso: Clonar el Repositorio

Una vez que aceptes la invitación de colaboración en GitHub, abrí tu terminal y ejecutá:

```bash
git clone https://github.com/Jose-beeb/Hackaton_Risings_Stars_Ec_26.git
cd Hackaton_Risings_Stars_Ec_26
```

Abrí la carpeta del proyecto en tu IDE **Antigravity**.

---

## 2. Flujo de Ramas (Branches): Prohibido subir directo a `main`

Para evitar pisarnos el código, **cada rol trabaja en su propia rama dedicada**:

| Integrante / Rol | Nombre de Rama Asignada | Carpeta Exclusiva |
| :--- | :--- | :--- |
| **Biotecnóloga** | `feat/bio-engine` | `core/bio_engine/` |
| **Mecatrónico** | `feat/gis-logistics` | `core/logistics/` |
| **Software 1 (Backend)** | `feat/backend-api` | `backend/` |
| **Software 2 (Frontend)** | `feat/frontend-dashboard` | `frontend/` |

### Crear y pasarte a tu rama antes de picar código:
```bash
# Ejemplo si sos la Biotecnóloga:
git checkout -b feat/bio-engine

# Ejemplo si sos el Mecatrónico:
git checkout -b feat/gis-logistics

# Ejemplo si sos Software 1 (Backend):
git checkout -b feat/backend-api

# Ejemplo si sos Software 2 (Frontend):
git checkout -b feat/frontend-dashboard
```

---

## 3. Rutina Diaria de Trabajo (El Ciclo Sano)

### Paso A: Antes de empezar a trabajar (Traer lo último)
Siempre asegurate de tener los cambios más recientes del equipo:
```bash
git checkout main
git pull origin main
git checkout tu-rama
git merge main
```

### Paso B: Guardar y commitear tus cambios
Cuando termines una función o módulo en tu carpeta:
```bash
# 1. Ver qué archivos tocaste
git status

# 2. Agregar tus cambios (solo los de tu carpeta)
git add .

# 3. Crear el commit descriptivo (Conventional Commits)
git commit -m "feat(bio): implementada formula de eclosion para el IRE"
```

*Ejemplos de buenos mensajes:*
- `feat(logistics): agregado algoritmo nearest neighbor para ruteo`
- `feat(backend): conectado endpoint /api/reports con open-meteo`
- `feat(frontend): agregado mapa de calor en leaflet`

### Paso C: Subir tus cambios a GitHub (Push)
```bash
git push -u origin tu-rama
```

---

## 4. Cómo Integrar tus Cambios (Pull Request en GitHub)

Cuando tu módulo esté listo y probado localmente:

1. Entrá a [GitHub del proyecto](https://github.com/Jose-beeb/Hackaton_Risings_Stars_Ec_26).
2. Vas a ver un cartel amarillo que dice **"Compare & pull request"** para tu rama. Hacé clic ahí.
3. Poné un título claro y explicá en 2 líneas qué agregaste.
4. Avisale al equipo por el chat grupal para que revisen y aprueben el merge hacia `main`.

---

## 5. Reglas de Convivencia y Seguridad

1. **Tu carpeta es tu territorio:** No edites archivos en las carpetas de otros integrantes.
2. **El contrato manda:** Si necesitás cambiar algún campo del JSON, revisá primero [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) y comentalo con el equipo.
3. **Cero credenciales en Git:** Nunca subas archivos `.env` o API keys privadas en texto plano.
4. **Si tenés conflicto al hacer merge:** No entres en pánico, no borres nada; pedí ayuda al equipo para resolver el conflicto juntos.
