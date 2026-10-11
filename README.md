# Metro Experto: mejor ruta en el Metro de Medellín

Sistema inteligente en Python que usa **reglas lógicas** y **búsqueda A\*** para encontrar la mejor ruta entre dos estaciones del Metro de Medellín (líneas A y B).

## Ejecución

Requiere Python 3.8 o superior. No usa librerías externas.

```bash
python ruta_metro.py
```

El programa pregunta el origen, el destino, el perfil del viajero, si es hora pico y si llueve. Luego muestra las reglas que se cumplieron, la mejor ruta y el tiempo estimado. Si aplica, también muestra los sitios recomendados y el aviso de salir temprano.

## Estructura del código (`ruta_metro.py`)

| Sección | Contenido |
|---|---|
| 1. Base de conocimiento | `TRAMOS`, `LINEAS_DE`, `ORDEN`, `ATRACTIVOS` |
| 2. Base de reglas | `REGLAS` (R1 a R6) |
| 3. Motor de inferencia | `inferir()` |
| 4. Búsqueda A\* | `paradas_minimas()`, `paradas_a_san_antonio()`, `a_estrella()` |
| 5. Programa principal | `main()` |
| 6. Presentación | Colores y organización de la consola (no hace parte del sistema inteligente) |

## Cómo funciona

1. **Base de conocimiento:** 17 estaciones de las líneas A y B conectadas por tramos, por ejemplo `("Poblado", "Aguacatala", "A", 3.4)`. Incluye una caminata de 0.8 km entre Alpujarra y Cisneros (línea "C"). A partir de los tramos se arman `LINEAS_DE` (a qué línea pertenece cada estación) y `ORDEN` (el orden de las estaciones en cada línea).
2. **Reglas lógicas:** son 6 reglas del tipo SI … ENTONCES …

| Regla | Lógica | Significado |
|---|---|---|
| R1 | hora_pico → metro_lento | El metro tarda 30 % más |
| R2 | lluvia → caminata_lenta | Caminar tarda 50 % más |
| R3 | movilidad_reducida → evitar_caminata | No se hacen caminatas |
| R4 | pocos_transbordos → transbordo_costoso | El transbordo cuenta como 12 min |
| R5 | turista → recomendar_sitios | Muestra sitios de interés en la ruta |
| R6 | metro_lento ∧ caminata_lenta → salir_temprano | Encadenamiento: usa las conclusiones de R1 y R2 |

3. **Motor de inferencia:** aplica las reglas hasta que no se puede deducir nada nuevo (encadenamiento hacia adelante).
4. **Búsqueda A\*:** usa los hechos deducidos por las reglas:
   - `metro_lento`: los minutos del metro se multiplican por 1.3.
   - `caminata_lenta`: los minutos de la caminata se multiplican por 1.5.
   - `transbordo_costoso`: el transbordo pasa de 4 a 12 min.
   - `evitar_caminata`: la caminata no se incluye en el mapa.

   A\* revisa primero la opción con menor `f = g + h`.
   - `g` son los minutos que lleva el viaje.
   - `h` es la heurística: paradas que faltan como mínimo × 0.6 min (el tramo más rápido), más 4 min si la estación no está en la línea del destino (falta un transbordo).

## Pruebas

| Viaje | Condición | Resultado |
|---|---|---|
| Poblado → Estadio | Normal | Transbordo en San Antonio, 17.1 min |
| Poblado → Estadio | Pocos transbordos (R4) | Camina de Alpujarra a Cisneros, 22.4 min |
| Poblado → Estadio | Pocos transbordos + lluvia (R2, R4) | Vuelve al transbordo, 25.1 min |
| Universidad → San Javier | Turista, hora pico y lluvia (R1, R2, R5, R6) | 29.7 min, 4 sitios recomendados y aviso de salir temprano |

## Datos

- Minutos por tramo estimados a partir del tiempo total de recorrido de cada línea (A: 40 min, B: 15.5 min).
- El transbordo de 4 min y los porcentajes de hora pico y lluvia son supuestos del modelo.

---

# Actividad: aprendizaje automático

Con el sistema de `ruta_metro.py` se creó un **dataset de viajes** (qué ruta tomar, cuántas paradas, transbordos y minutos, según la lluvia, la hora pico y el perfil). Con ese dataset se entrenaron 4 modelos:

| Carpeta | Tipo | Modelo | Pregunta que responde |
|---|---|---|---|
| [`datos/`](datos/README.md) | Dataset | — | 3.264 viajes generados con `ruta_metro.py` |
| [`aprendizaje_supervisado/`](aprendizaje_supervisado/README.md) | Supervisado (regresión) | Regresión lineal | ¿Cuántos minutos tarda el viaje? |
| | Supervisado (clasificación) | Árbol de decisión | ¿Llegaré a tiempo? |
| [`aprendizaje_no_supervisado/`](aprendizaje_no_supervisado/README.md) | No supervisado (agrupamiento) | K-Means | ¿Qué tipos de viaje existen? |
| | No supervisado (agrupamiento) | Agrupamiento jerárquico | ¿Qué tipos de viaje existen? (dendrograma) |

Las fuentes de datos están descritas en el README de cada carpeta.

## Instalación de librerías

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
cd datos
python generar_dataset.py
```

```bash
cd aprendizaje_supervisado
python regresion_lineal.py
python arbol_decision.py
```

```bash
cd aprendizaje_no_supervisado
python kmeans.py
python jerarquico.py
```
