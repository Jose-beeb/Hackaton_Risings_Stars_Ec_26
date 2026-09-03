# AedesGuard — Requisitos y Setup del Entorno

Lee esto antes de tocar cualquier archivo del proyecto.

---

## Lo que necesitas tener instalado

### 1. Python 3.11 o superior (obligatorio para Backend)

Verificar si ya lo tenes:
```bash
python --version
```

Si no esta instalado o la version es menor a 3.11:
1. Ir a **https://www.python.org/downloads**
2. Descargar la version mas reciente (boton amarillo grande)
3. Ejecutar el instalador
4. IMPORTANTE: marcar la casilla **"Add python.exe to PATH"** antes de instalar
5. Cerrar y reabrir la terminal
6. Verificar: `python --version`

### 2. Git (obligatorio para todos)

Verificar si ya lo tenes:
```bash
git --version
```

Si no esta instalado:
1. Ir a **https://git-scm.com/downloads**
2. Descargar para tu sistema operativo
3. Instalar con las opciones por defecto
4. Verificar: `git --version`

### 3. Navegador moderno (obligatorio para Frontend)

Chrome, Firefox o Edge actualizado. El dashboard usa APIs modernas del navegador (geolocalización, cámara).

### 4. Visual Studio Code (recomendado, no obligatorio)

Descarga: **https://code.visualstudio.com**

Extensiones utiles para este proyecto:
- Python (Microsoft)
- Prettier
- GitLens

---

## Setup del proyecto (orden importante)

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/Jose-beeb/Hackaton_Risings_Stars_Ec_26.git
cd Hackaton_Risings_Stars_Ec_26
```

### Paso 2 — Ir a tu rama de trabajo

```bash
git checkout feat/bio-engine        # Biotecnologia
git checkout feat/gis-logistics     # Mecatronica
git checkout feat/backend-api       # Backend
git checkout feat/frontend-dashboard # Frontend
```

### Paso 3 — Crear entorno virtual Python (Backend y quien corra el servidor)

```bash
# Crear el entorno
python -m venv venv

# Activar en Windows (PowerShell o CMD)
venv\Scripts\activate

# Activar en Mac / Linux
source venv/bin/activate

# Vas a ver (venv) al inicio de tu terminal — eso confirma que esta activo

# Instalar dependencias
pip install -r backend/requirements.txt
```

### Paso 4 — Obtener API Key de Gemini (solo Backend)

1. Ir a **https://aistudio.google.com**
2. Iniciar sesion con cuenta Google
3. Click en **"Get API key"** en el menu izquierdo
4. Click en **"Create API key in new project"**
5. Copiar la clave (empieza con `AIza...`)

### Paso 5 — Crear el archivo .env (solo Backend)

En la raiz del proyecto (donde esta el README.md), crear un archivo llamado `.env`:

```
GEMINI_API_KEY=AIza...tu_clave_aqui
ENVIRONMENT=development
PORT=8000
```

> El archivo `.env` nunca aparece en git — esta en `.gitignore` por seguridad.
> Cada integrante crea su propio `.env` localmente, no se comparte.

### Paso 6 — Verificar que todo funciona

```bash
# Terminal 1: levantar el servidor
python backend/app/main.py

# Terminal 2: correr el smoke test
python backend/tests/smoke_test.py
```

Resultado esperado: `4/4 tests pasaron`

Para el frontend, abrir `frontend/index.html` en el navegador.

---

## Dependencias Python (backend/requirements.txt)

| Paquete | Version | Para que sirve |
|---|---|---|
| fastapi | >=0.110.0 | Framework web del servidor |
| uvicorn | >=0.28.0 | Servidor ASGI para correr FastAPI |
| pydantic | >=2.6.0 | Validacion de datos de entrada/salida |
| pydantic-settings | >=2.2.0 | Carga de variables de entorno (.env) |
| httpx | >=0.27.0 | Cliente HTTP para llamar a Open-Meteo |
| google-generativeai | >=0.7.0 | SDK oficial de Gemini (Vision AI) |
| python-dotenv | >=1.0.0 | Lee el archivo .env automaticamente |
| python-multipart | >=0.0.9 | Soporte para subida de imagenes |

---

## Dependencias Frontend

El frontend no requiere instalacion. Usa librerias via CDN:

| Libreria | Version | Para que sirve |
|---|---|---|
| Leaflet | 1.9.4 | Mapas interactivos |
| leaflet-heat | 0.2.0 | Capa de mapa de calor |
| Google Fonts | — | Tipografia (Outfit, Inter) |

---

## APIs externas utilizadas

| API | Requiere key | Costo | Uso |
|---|---|---|---|
| Google Gemini Flash | SI | Gratis (tier gratuito) | Clasificacion de imagenes |
| Open-Meteo | NO | Gratis y abierta | Temperatura y humedad en tiempo real |

---

## Problemas frecuentes

**"python no se reconoce como comando"**
Reinstalar Python marcando la casilla "Add python.exe to PATH".

**"pip no se reconoce"**
Correr: `python -m pip install -r backend/requirements.txt`

**"ModuleNotFoundError: No module named 'fastapi'"**
El entorno virtual no esta activado. Correr `venv\Scripts\activate` primero.

**"El mapa no carga"**
Verificar que el backend esta corriendo en `http://localhost:8000`.
El frontend hace fallback automatico al archivo local si el backend no responde.

**"GEMINI_API_KEY not set"**
Crear el archivo `.env` en la raiz del proyecto con la clave. Ver Paso 5.
