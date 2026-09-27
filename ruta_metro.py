"""
METRO EXPERTO - Mejor ruta en el Metro de Medellín
Sistema inteligente basado en conocimiento: REGLAS LÓGICAS + BÚSQUEDA A*

¿Cómo funciona?
  1. El usuario elige origen, destino y las condiciones del viaje.
  2. El MOTOR DE INFERENCIA aplica las REGLAS y deduce qué cambia en el viaje.
  3. La BÚSQUEDA A* usa esas conclusiones para encontrar la ruta más rápida.

Secciones: 1. Base de conocimiento · 2. Base de reglas · 3. Motor de inferencia
           4. Búsqueda A* · 5. Programa principal · 6. Presentación en consola
"""
import heapq

# =============================================================================
# 1. BASE DE CONOCIMIENTO: la red del metro
# =============================================================================
# tramo(Estación1, Estación2, Línea, Minutos): conexión directa entre dos estaciones.
# Cada tramo sirve en los dos sentidos (ida y regreso).
TRAMOS = [
    # Línea A (de norte a sur)
    ("Caribe", "Universidad", "A", 1.8),
    ("Universidad", "Hospital", "A", 1.1),
    ("Hospital", "Prado", "A", 1.4),
    ("Prado", "Parque Berrío", "A", 1.3),
    ("Parque Berrío", "San Antonio", "A", 0.6),
    ("San Antonio", "Alpujarra", "A", 0.8),
    ("Alpujarra", "Exposiciones", "A", 0.9),
    ("Exposiciones", "Industriales", "A", 1.6),
    ("Industriales", "Poblado", "A", 3.3),
    ("Poblado", "Aguacatala", "A", 3.4),
    # Línea B (del centro al occidente)
    ("San Antonio", "Cisneros", "B", 1.9),
    ("Cisneros", "Suramericana", "B", 2.9),
    ("Suramericana", "Estadio", "B", 1.7),
    ("Estadio", "Floresta", "B", 3.6),
    ("Floresta", "Santa Lucía", "B", 2.0),
    ("Santa Lucía", "San Javier", "B", 3.3),
    # Caminata "C": de Alpujarra (Línea A) a Cisneros (Línea B), 0.8 km a pie
    ("Alpujarra", "Cisneros", "C", 12),
]

# Líneas de metro a las que pertenece cada estación (se arma a partir de los tramos).
# Ejemplo: LINEAS_DE["Poblado"] = {"A"}   y   LINEAS_DE["San Antonio"] = {"A", "B"}
LINEAS_DE = {}
for est1, est2, linea, _ in TRAMOS:
    if linea != "C":                                   # la caminata no es una línea de metro
        LINEAS_DE.setdefault(est1, set()).add(linea)
        LINEAS_DE.setdefault(est2, set()).add(linea)

# Orden de las estaciones en cada línea (se arma con los tramos, que están escritos en orden).
# Ejemplo: ORDEN["B"] = ["San Antonio", "Cisneros", "Suramericana", "Estadio", ...]
ORDEN = {}
for est1, est2, linea, _ in TRAMOS:
    if linea != "C":
        if linea not in ORDEN:
            ORDEN[linea] = [est1]
        ORDEN[linea].append(est2)

# Sitios de interés cerca de algunas estaciones
ATRACTIVOS = {
    "Parque Berrío": "Plaza Botero",
    "Universidad": "Jardín Botánico y Parque Explora",
    "Alpujarra": "Parque de los Pies Descalzos",
    "Estadio": "Estadio Atanasio Girardot",
    "San Javier": "Comuna 13 y su recorrido de grafitis",
}

# =============================================================================
# 2. BASE DE REGLAS:  SI condiciones ENTONCES conclusión
# Formato: (nombre, [condiciones], conclusión, explicación)
# =============================================================================
REGLAS = [
    # R1: hora_pico → metro_lento
    ("R1", ["hora_pico"], "metro_lento",
     "Es hora pico: el metro va lleno y tarda 30% más"),

    # R2: lluvia → caminata_lenta
    ("R2", ["lluvia"], "caminata_lenta",
     "Está lloviendo: caminar entre estaciones tarda 50% más"),

    # R3: movilidad_reducida → evitar_caminata
    ("R3", ["movilidad_reducida"], "evitar_caminata",
     "Movilidad reducida: no se hacen caminatas entre estaciones"),

    # R4: pocos_transbordos → transbordo_costoso
    ("R4", ["pocos_transbordos"], "transbordo_costoso",
     "No quiere transbordar: cada transbordo cuenta como 12 minutos"),

    # R5: turista → recomendar_sitios
    ("R5", ["turista"], "recomendar_sitios",
     "Es turista: se le recomiendan los sitios de interés de su ruta"),

    # R6: metro_lento ∧ caminata_lenta → salir_temprano
    # (usa conclusiones de R1 y R2: así se ve el ENCADENAMIENTO de reglas)
    ("R6", ["metro_lento", "caminata_lenta"], "salir_temprano",
     "Hora pico + lluvia: se recomienda salir 15 minutos antes"),
]


