# Preguntas Clave para el Rol: Mecatrónica, Logística y Modelado GIS

Este documento reúne las definiciones técnicas, algorítmicas y de negocio necesarias para estructurar el motor de despacho de cuadrillas y el esquema geoespacial.

---

### 1. Algoritmo de Optimización de Rutas y Despacho
* **Estrategia Algorítmica:** ¿Qué enfoque algorítmico se utilizará para ordenar los puntos de intervención? (Ej. Nearest Neighbor, Traveling Salesperson Problem - TSP con heurística 2-opt, o Clustering K-Means por sector + ruteo interno).
* **Función Objetivo:** ¿Qué variables pondera el algoritmo para decidir el orden de visita? (¿Distancia euclidiana / geodésica, nivel de criticidad del IRE, días restantes para eclosión?).
* **Capacidad Operativa de Cuadrillas:** ¿Cuántos focos puede atender una cuadrilla por jornada de trabajo y cuánto tiempo promedio de intervención se asigna por punto?

---

### 2. Estructura y Capas de Datos Geoespaciales (GeoJSON)
* **Esquema de Datos de Foco:** ¿Cuáles son las propiedades exactas que debe contener cada `Feature` en el GeoJSON? (Coordenadas `[long, lat]`, ID de foco, nivel de riesgo, tipo de depósito, tiempo estimado de atención, estado de intervención).
* **Generación de Mock Data:** ¿Cuáles son los límites geográficos (bounding box) de la zona piloto (ej. sector específico de Guayaquil o Portoviejo) para precargar los 30-40 puntos realistas?
* **Capa de Rutas:** ¿Cómo se serializará la ruta calculada para que el frontend la dibuje en el mapa? (¿`LineString` en GeoJSON o secuencia de waypoints ordenados?).

---

### 3. Modelo de Negocio y Unit Economics (Pitch B2B / B2G)
* **Métricas de Ahorro para Municipios:** ¿Cómo se cuantifica el ahorro del 40% en combustible e insecticida frente a la fumigación tradicional "a ciegas"?
* **Cálculo de Pérdida Evitada para Empresas Privadas:** ¿Cuál es el costo estimado por día de incapacidad laboral de un operario agrícola/industrial frente al costo de la suscripción mensual de monitoreo?
* **KPIs Clave del Dashboard:** ¿Qué indicadores ejecutivos deben resaltarse en la vista gerencial? (Focos detectados, focos neutralizados, porcentaje de reducción de riesgo, costo estimado ahorrado).
