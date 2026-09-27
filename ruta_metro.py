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

     # =============================================================================
# 3. MOTOR DE INFERENCIA (encadenamiento hacia adelante)
# Revisa las reglas una y otra vez: si TODAS las condiciones de una regla
# están en los hechos, agrega su conclusión como un hecho nuevo.
# Se detiene cuando ya no se puede deducir nada nuevo.
# =============================================================================
def inferir(hechos):
    hechos = set(hechos)
    aplicadas = []
    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False
        for nombre, condiciones, conclusion, explicacion in REGLAS:
            se_cumple = all(c in hechos for c in condiciones)
            if se_cumple and conclusion not in hechos:
                hechos.add(conclusion)                     # hecho nuevo deducido
                aplicadas.append((nombre, explicacion))
                hubo_cambios = True
    return hechos, aplicadas


# =============================================================================
# 4. BÚSQUEDA A*
# Siempre revisa primero la opción con menor  f = g + h
#   g = minutos que ya lleva el viaje desde el origen (tiempo acumulado)
#   h = HEURÍSTICA: estimación optimista de los minutos que faltan
#       h = paradas que faltan como mínimo × 0.6 min  (0.6 = el tramo más rápido de la red)
#         + 4 min si la estación NO está en la línea del destino (falta un transbordo)
#   h nunca exagera lo que falta, por eso A* garantiza encontrar la MEJOR ruta.
# =============================================================================
MINUTOS_TRAMO_MAS_RAPIDO = 0.6
TRANSBORDO_MINIMO = 4


def paradas_minimas(estacion, destino):
    """Cuenta cuántas paradas hay como mínimo entre dos estaciones."""
    for orden in ORDEN.values():
        if estacion in orden and destino in orden:              # misma línea: se cuentan directo
            return abs(orden.index(estacion) - orden.index(destino))
    # Líneas distintas: paradas hasta San Antonio + paradas desde San Antonio al destino
    return paradas_a_san_antonio(estacion) + paradas_a_san_antonio(destino)


def paradas_a_san_antonio(estacion):
    """Paradas entre una estación y San Antonio (la estación de transbordo) en su línea."""
    orden = ORDEN[min(LINEAS_DE[estacion])]
    return abs(orden.index(estacion) - orden.index("San Antonio"))


def a_estrella(origen, destino, hechos):
    # 4.1 Usar las conclusiones del motor de inferencia
    factor_metro = 1.3 if "metro_lento" in hechos else 1.0
    factor_caminata = 1.5 if "caminata_lenta" in hechos else 1.0
    costo_transbordo = 12 if "transbordo_costoso" in hechos else 4

    # 4.2 Armar el mapa de vecinos (cada tramo en los dos sentidos)
    vecinos = {}
    for est1, est2, linea, minutos in TRAMOS:
        if linea == "C" and "evitar_caminata" in hechos:
            continue                                        # la regla R3 prohíbe caminar
        vecinos.setdefault(est1, []).append((est2, linea, minutos))
        vecinos.setdefault(est2, []).append((est1, linea, minutos))

    def h(estacion):
        estimado = paradas_minimas(estacion, destino) * MINUTOS_TRAMO_MAS_RAPIDO
        comparten_linea = LINEAS_DE[estacion] & LINEAS_DE[destino]   # ¿tienen alguna línea en común?
        if not comparten_linea:
            estimado += TRANSBORDO_MINIMO                               # falta cambiar de línea
        return estimado

    # 4.3 Búsqueda. Cada opción guardada: (f, g, estación, línea en la que voy, camino)
    abiertos = [(h(origen), 0, origen, None, [(origen, None)])]
    revisados = set()
    while abiertos:
        f, g, estacion, linea, camino = heapq.heappop(abiertos)   # la de menor f
        if estacion == destino:
            return camino, g                                      # ¡llegamos!
        if (estacion, linea) in revisados:
            continue
        revisados.add((estacion, linea))

        for siguiente, nueva_linea, minutos in vecinos[estacion]:
            costo = minutos * (factor_caminata if nueva_linea == "C" else factor_metro)
            if linea in ("A", "B") and nueva_linea in ("A", "B") and nueva_linea != linea:
                costo += costo_transbordo                         # cambió de tren
            nuevo_g = g + costo
            heapq.heappush(abiertos, (nuevo_g + h(siguiente), nuevo_g, siguiente,
                                      nueva_linea, camino + [(siguiente, nueva_linea)]))
    return None, 0
]


