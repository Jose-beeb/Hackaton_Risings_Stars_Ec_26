# AedesGuard — Guia de Setup

Lee esto antes de tocar cualquier archivo. Tiempo estimado: 10 minutos.

---

## Requisitos previos

| Herramienta | Version minima | Como verificar |
|---|---|---|
| Python | 3.11+ | `py --version` |
| Git | cualquiera | `git --version` |
| Chrome / Edge | actualizado | — |

### Instalar Python (si no lo tenes)

1. Ir a **https://www.python.org/downloads**
2. Descargar la version mas reciente
3. Ejecutar el instalador — marcar **"Add python.exe to PATH"** antes de instalar
4. Abrir una terminal **nueva** y verificar: `py --version`

> En Windows el comando es `py`, no `python`. Usa `py` en todos los pasos.

---

## Setup del proyecto

### Paso 1 — Clonar el repositorio

```powershell
git clone https://github.com/Jose-beeb/Hackaton_Risings_Stars_Ec_26.git
cd Hackaton_Risings_Stars_Ec_26
```

### Paso 2 — Crear entorno virtual e instalar dependencias

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Vas a ver `(.venv)` al inicio de tu terminal — eso confirma que esta activo.

### Paso 3 — Configurar la API Key de Gemini

1. Ir a **https://aistudio.google.com**
2. Iniciar sesion con cuenta Google
3. Click en **"Get API key"** → **"Create API key"**
4. Copiar la clave (empieza con `AIza...`)
5. En la raiz del proyecto ya existe un archivo `.env.example` — copiarlo como `.env`:

```powershell
copy .env.example .env
```

6. Abrir `.env` con cualquier editor y pegar tu clave:

```
GEMINI_API_KEY=AIza...tu_clave_aqui
```

> El archivo `.env` nunca sube al repo (esta en `.gitignore`). Cada integrante crea el suyo.

### Paso 4 — Verificar que el backend funciona

Necesitas **dos terminales** abiertas al mismo tiempo.

**Terminal 1 — Levantar el servidor:**
```powershell
.venv\Scripts\Activate.ps1
py -m uvicorn backend.app.main:app --reload --port 8000
```
Debes ver: `Application startup complete.`

**Terminal 2 — Correr el smoke test:**
```powershell
.venv\Scripts\Activate.ps1
py backend/tests/smoke_test.py
```
Resultado esperado: `4/4 tests pasaron`

### Paso 5 — Levantar el frontend

Con el backend corriendo, abri una **tercera terminal**:

```powershell
cd frontend
py -m http.server 3000
```

Luego abri Chrome en: **http://localhost:3000**

---

## Correr los tests unitarios

```powershell
.venv\Scripts\Activate.ps1
pytest backend/tests/test_ire_calculator.py -v
```

Resultado esperado: `20 passed`

---

## Dependencias Python

| Paquete | Para que sirve |
|---|---|
| fastapi | Framework web del servidor |
| uvicorn | Servidor ASGI para correr FastAPI |
| pydantic + pydantic-settings | Validacion de datos y variables de entorno |
| httpx | Cliente HTTP para Open-Meteo |
| google-generativeai | SDK de Gemini Vision AI |
| python-dotenv | Lee el archivo .env |
| python-multipart | Soporte para subida de imagenes |
| pytest | Tests unitarios del motor IRE |

## APIs externas

| API | Key requerida | Costo | Uso |
|---|---|---|---|
| Google Gemini Flash | SI | Gratis (tier gratuito) | Clasificacion de imagenes con IA |
| Open-Meteo | NO | Gratis | Temperatura y humedad en tiempo real |
| OpenStreetMap | NO | Gratis | Tiles del mapa |

---

## Problemas frecuentes

**`py` no se reconoce**
Reinstalar Python marcando "Add python.exe to PATH". Abrir terminal nueva despues.

**`Activate.ps1` no se puede ejecutar (error de politica)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**`ModuleNotFoundError: No module named 'fastapi'`**
El entorno virtual no esta activo. Correr `.venv\Scripts\Activate.ps1` primero.

**`ModuleNotFoundError: No module named 'app'`**
Asegurate de correr uvicorn desde la raiz del proyecto, no desde dentro de `backend/`.

**El mapa carga pero sale "API KEY REQUIRED"**
Ya esta corregido en la version actual. Hacer `git pull` para obtener el fix.

**El frontend muestra el listado del directorio en vez del mapa**
Correr `py -m http.server 3000` desde dentro de la carpeta `frontend/`, no desde la raiz.

**Vision Service usa "fallback" en vez de Gemini**
La API key no esta configurada. Verificar el archivo `.env` en la raiz del proyecto.
