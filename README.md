# AedesGuard 🦟⚡

> **Sistema de Inteligencia Epidemiológica y Control Vectorial Predictivo**  
> *IEEE Rising Stars 2026 Hackathon — Track 2: Public Health*

Plataforma 100% de software basada en agentes de IA y modelos deterministas bio-climáticos para la detección temprana de criaderos de *Aedes aegypti* (dengue, zika, chikungunya), cálculo del Índice de Riesgo Entomológico (IRE) y optimización de rutas de fumigación.

---

## 🚀 Inicio Rápido

### 1. Documentación Clave
* 📖 [Guía de Trabajo con Antigravity](docs/GUIA_TRABAJO_ANTIGRAVITY.md)
* 📜 [Contrato de API (Inmutable)](docs/API_CONTRACT.md)
* 🗺️ [Plan Estratégico y Arquitectura](Plan.md)

### 2. Estructura del Monorepo Modular
```text
├── core/
│   ├── bio_engine/          # Rol 1: Biotecnología (IRE y Prompts VLM)
│   └── logistics/           # Rol 2: Mecatrónica (Ruteo TSP y GeoJSON)
├── backend/                 # Rol 3: Software 1 (FastAPI / Orquestador)
├── frontend/                # Rol 4: Software 2 (PWA Móvil y Dashboard GIS)
├── data/                    # Mock Data Geoespacial (40 focos en Guayaquil)
├── docs/                    # Especificaciones y contratos
└── roles/                   # Cuestionarios técnicos por perfil
```

### 3. Levantar el Proyecto Localmente

#### Backend (FastAPI):
```bash
cd backend
pip install -r requirements.txt
python app/main.py
```
*Servidor corriendo en:* `http://localhost:8000`  
*Documentación interactiva:* `http://localhost:8000/docs`

#### Frontend:
Abrir directamente `frontend/index.html` en el navegador o servir con cualquier servidor local (ej. Live Server, Vite o `python -m http.server 3000` desde la carpeta `frontend/`).
