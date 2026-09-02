# Preguntas Clave para el Rol: Biotecnología y Diseño Bio-Lógico

Este documento reúne las definiciones técnicas y biológicas necesarias para que el equipo de desarrollo implemente el motor de cálculo y la visión artificial sin ambigüedades.

---

### 1. Modelo Matemático del Índice de Riesgo Entomológico (IRE)
* **Fórmula Concreta:** ¿Cuál es la ecuación matemática determinista para calcular el IRE? (Ejemplo: $IRE = f(\text{TipoCriadero}, \text{VolumenAproximado}, T^\circ, \text{Humedad})$).
* **Escala y Normalización:** ¿En qué rango se medirá el IRE? (¿0 a 100? ¿Bajo [0-30], Medio [31-70], Crítico [71-100]?).
* **Tiempo de Eclosión / Ciclo de Desarrollo:** ¿Qué función o tabla de referencia relaciona la temperatura ambiente ($20^\circ\text{C} - 32^\circ\text{C}$) con los días de transición de huevo $\rightarrow$ larva $\rightarrow$ pupa $\rightarrow$ mosquito adulto de *Aedes aegypti*?

---

### 2. Taxonomía de Criaderos y Calibración de Visión Artificial
* **Categorías de Depósitos:** ¿Cuáles son las categorías esenciales de recipientes que el modelo debe clasificar?
  * *Ejemplo:* Llanta usada, balde/tanque abierto, maceta/florero, canaleta obstruida, cisterna sin tapa, basura menor (botellas, latas).
* **Ponderación Biológica por Tipo de Depósito:** ¿Qué peso de riesgo o capacidad de carga larvaria tiene cada tipo de recipiente?
* **Criterios de Descarte:** ¿Qué elementos visuales descartan un criadero como foco activo? (Ej. agua clorada visible, recipiente totalmente seco, depósito herméticamente cerrado).

---

### 3. Prompt Engineering y Validación Multimodal
* **Estructura del System Prompt:** ¿Qué instrucciones y terminología biológica precisa debe contener el prompt para que el LLM/VLM devuelva un JSON estructurado confiable?
* **Manejo de Falsos Positivos:** ¿Cómo debe responder el modelo si la foto no corresponde a un potencial criadero (ej. una selfie o foto de paisaje)?

---

### 4. Directrices Sanitarias y Recomendaciones al Usuario
* **Acciones Inmediatas Ciudadanas:** ¿Qué recomendación de 1 o 2 líneas debe recibir el ciudadano según el tipo de criadero detectado? (Ej. voltear recipiente, tapar herméticamente, aplicar abate).
* **Protocolo de Intervención de Cuadrillas:** ¿Qué tipo de tratamiento se sugiere para el reporte municipal? (Fumigación espacial, abatización focalizada o eliminación física del residuo).
