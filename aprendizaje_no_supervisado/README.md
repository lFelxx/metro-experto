# Aprendizaje no supervisado

En el aprendizaje no supervisado, el modelo **no recibe la respuesta (y)**: descubre por sí solo los grupos que hay en los datos.

## 1. Fuentes de datos

**Fuentes reales relacionadas con el proyecto:**

| Fuente | Qué tiene | Por qué no basta |
|---|---|---|
| [Pasajeros movilizados mensual, Metro de Medellín](https://medata.gov.co/node/16272) (MEData) | Pasajeros por mes | Datos totales, no por viaje |
| [Datos abiertos del Metro de Medellín](https://datosabiertos-metrodemedellin.opendata.arcgis.com/) | Afluencia de pasajeros | Agregados, sin rutas ni tiempos |
| [Encuesta Origen-Destino 2017, viajes](https://datosabiertos.metropol.gov.co/dataset/encuesta-origen-destino-2017-datos-por-viajes) (Área Metropolitana) | Origen, destino, modo y duración de viajes | Por zonas y todos los modos, no por estación de metro |

Ninguna fuente tiene las **paradas, minutos y transbordos de cada viaje en metro**. Por eso se usa el dataset de muestra [`datos/viajes_metro.csv`](../datos/README.md), con 3.264 viajes calculados con `ruta_metro.py`. **No se usa ninguna columna de respuesta**: solo las características de cada viaje.

## 2. Modelos

Los dos modelos usan las mismas 3 columnas, **sin columna de respuesta**:

| Datos (sin y) |
|---|
| paradas, minutos, transbordos |

Antes de entrenar, los datos se **escalan** con `StandardScaler`: paradas va de 0 a 11, minutos de 0 a 45 y transbordos de 0 a 1, así que se ponen en la misma escala para que las tres columnas pesen igual.

### Modelo 1: K-Means (`kmeans.py`)
1. **Método del codo:** se prueba K = 1 a 8 y se elige **K = 3**, donde la inercia deja de bajar mucho.
2. **K-Means:** pone 3 centros, asigna cada viaje al centro más cercano, mueve los centros al promedio de sus viajes y repite hasta que no cambian.
3. **Nombre de cada grupo:** según sus paradas y transbordos promedio.
4. **Viaje nuevo:** el usuario escribe paradas, minutos y transbordos, y el modelo dice a qué grupo pertenece.

| Grupo | Viajes | Paradas | Minutos | Con transbordo |
|---|---|---|---|---|
| Cortos y directos | 1.389 | 2.5 | 5.0 | 2 % |
| Medianos sin transbordo | 707 | 6.5 | 16.2 | 0 % (29 % caminan) |
| Con transbordo | 1.168 | 6.6 | 20.1 | 100 % |

### Modelo 2: Agrupamiento jerárquico (`jerarquico.py`)
- **No necesita saber K desde el inicio.** Empieza con cada viaje como un grupo y va **uniendo los dos grupos más parecidos**, una y otra vez.
- Ese proceso se dibuja como un árbol, el **dendrograma**. Al cortarlo a cierta altura (la línea roja) quedan **3 grupos**.

| Grupo | Viajes | Paradas | Minutos | Con transbordo | Ejemplo típico |
|---|---|---|---|---|---|
| Cortos y directos | 1.037 | 1.9 | 4.4 | 0 % | Universidad → Parque Berrío |
| Medianos sin transbordo | 1.027 | 5.8 | 13.3 | 0 % | San Antonio → Santa Lucía |
| Con transbordo | 1.200 | 6.5 | 19.7 | 100 % | Caribe → Floresta |

### Conclusión
**Los dos modelos, por caminos distintos, descubren los mismos 3 tipos de viaje.** Lo más interesante: con el mismo número de paradas (≈ 6.5), los viajes **con transbordo tardan unos 4 minutos más** que los que no transbordan. Nadie se lo dijo al modelo: lo encontró en los datos.

## Ejecución

```bash
python kmeans.py
```
```bash
python jerarquico.py
```

Gráficas que se guardan: `grafica_codo.png`, `grafica_kmeans.png` y `grafica_dendrograma.png`.
