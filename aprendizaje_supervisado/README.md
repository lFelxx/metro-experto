# Aprendizaje supervisado

En el aprendizaje supervisado, el modelo aprende de ejemplos que **traen la respuesta correcta (y)**.

## 1. Fuentes de datos

**Fuentes reales relacionadas con el proyecto:**

| Fuente | Qué tiene | Por qué no basta |
|---|---|---|
| [Pasajeros movilizados mensual, Metro de Medellín](https://medata.gov.co/node/16272) (MEData) | Pasajeros por mes | Datos totales, no por viaje |
| [Datos abiertos del Metro de Medellín](https://datosabiertos-metrodemedellin.opendata.arcgis.com/) | Afluencia de pasajeros | Agregados, sin rutas ni tiempos |
| [Encuesta Origen-Destino 2017, viajes](https://datosabiertos.metropol.gov.co/dataset/encuesta-origen-destino-2017-datos-por-viajes) (Área Metropolitana) | Origen, destino, modo y duración de viajes | Por zonas y todos los modos, no por estación de metro |
| [Precipitación, IDEAM](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Precipitaci-n/s54a-sgyg) | Lluvia por estación meteorológica | Solo clima, sin viajes |

Ninguna fuente tiene, para cada viaje en metro, **la ruta, las paradas, los transbordos y el tiempo según la lluvia o la hora pico**. Por eso se **desarrolló un dataset de muestra**, [`datos/viajes_metro.csv`](../datos/README.md), con 3.264 viajes calculados con `ruta_metro.py`.

## 2. Modelos

### Modelo 1: Regresión lineal (`regresion_lineal.py`)
**¿Cuántos minutos tarda un viaje?** Predice un número.

| X (entradas) | y (respuesta) |
|---|---|
| paradas, transbordos, camina, lluvia, hora_pico | minutos |

Lo que aprendió: cada parada suma **≈ 2 min**, cada transbordo **≈ 7 min**, caminar **≈ 13.6 min**, la hora pico **≈ 2.6 min** y la lluvia **≈ 0.9 min**.

**Resultado:** error promedio de **2.85 minutos**, R² = **0.85**.

### Modelo 2: Árbol de decisión (`arbol_decision.py`)
**¿Llegaré a tiempo?** Predice una categoría: sí o no.

| X (entradas) | y (respuesta) |
|---|---|
| paradas, transbordos, camina, lluvia, hora_pico, minutos_disponibles | llega_a_tiempo (1 = sí, 0 = no) |

El modelo **no ve cuánto duró el viaje**: aprende, a partir de la ruta y las condiciones, si al viajero le alcanza el tiempo. El árbol hace preguntas del tipo SI … ENTONCES, igual que las reglas de `ruta_metro.py`. Por ejemplo: *"SI tiene más de 18.5 minutos Y el viaje tiene pocas paradas → llega"*.

Al predecir un viaje nuevo, el usuario elige las estaciones y el tiempo que tiene. El programa muestra la ruta, la respuesta (✅ / ❌) y la **confianza** del modelo.

**Resultado:** **92.8 %** de aciertos.

## Ejecución

```bash
python regresion_lineal.py
```
```bash
python arbol_decision.py
```

Cada script muestra los datos, entrena el modelo, lo evalúa, guarda una gráfica (`grafica_regresion.png`, `grafica_arbol.png`) y al final permite **predecir un viaje nuevo**.
