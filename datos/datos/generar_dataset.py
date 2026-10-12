"""
=============================================================
 GENERAR EL DATASET DE VIAJES  ->  viajes_metro.csv
=============================================================
Usa el sistema de la actividad anterior (ruta_metro.py) para calcular
MUCHOS viajes y guardarlos en una tabla.

¿Cómo? Se prueban TODAS las combinaciones:
    cada estación de origen  x  cada estación de destino
    x  con lluvia y sin lluvia
    x  en hora pico y fuera de hora pico
    x  cada perfil de viajero

Para cada combinación, ruta_metro.py dice qué ruta tomar, cuántas paradas
hace, si transborda o camina y cuántos minutos tarda.

Ejecución:  python generar_dataset.py
"""
import os
import random
import sys

import pandas as pd

pd.set_option("display.width", 160)              # mostrar la tabla completa en la consola
pd.set_option("display.max_columns", 20)

# Para poder usar ruta_metro.py, que está en la carpeta de arriba
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from ruta_metro import LINEAS_DE, inferir, a_estrella

ESTACIONES = list(LINEAS_DE)                                    # las 17 estaciones
PERFILES = ["normal", "pocos_transbordos", "movilidad_reducida"]
random.seed(42)                                                 # siempre los mismos datos

filas = []
for origen in ESTACIONES:
    for destino in ESTACIONES:
        if origen == destino:
            continue
        for lluvia in [0, 1]:
            for hora_pico in [0, 1]:
                for perfil in PERFILES:

                    # 1) Las condiciones del viaje se convierten en HECHOS (igual que en ruta_metro.py)
                    hechos = [perfil]
                    if lluvia:
                        hechos.append("lluvia")
                    if hora_pico:
                        hechos.append("hora_pico")
                    hechos, _ = inferir(hechos)

                    # 2) A* calcula la mejor ruta: lista de (estación, línea)
                    camino, minutos = a_estrella(origen, destino, hechos)

                    # 3) Contar paradas, transbordos y si hay caminata
                    lineas = [linea for _, linea in camino[1:]]          # línea de cada tramo
                    paradas = sum(1 for linea in lineas if linea in ("A", "B"))
                    camina = 1 if "C" in lineas else 0
                    transbordos = sum(1 for a, b in zip(lineas, lineas[1:])
                                      if a in ("A", "B") and b in ("A", "B") and a != b)

                    # 4) Tipo de ruta (lo usa el árbol de decisión)
                    if camina:
                        tipo_ruta = "caminata"
                    elif transbordos:
                        tipo_ruta = "transbordo"
                    else:
                        tipo_ruta = "directa"

                    # 5) En la vida real ningún viaje dura exactamente igual:
                    #    se aplica una pequeña variación de ±10% al tiempo
                    minutos_reales = round(minutos * random.uniform(0.9, 1.1), 1)

                    # 6) Cada viajero tiene entre 5 y 45 minutos para llegar a su destino.
                    #    Si el viaje dura menos que eso, llegó a tiempo (1); si no, no (0).
                    minutos_disponibles = random.randint(5, 45)
                    llega_a_tiempo = 1 if minutos_reales <= minutos_disponibles else 0

                    filas.append({
                        "origen": origen,
                        "destino": destino,
                        "lluvia": lluvia,
                        "hora_pico": hora_pico,
                        "perfil": perfil,
                        "ruta": " > ".join(estacion for estacion, _ in camino),
                        "paradas": paradas,
                        "transbordos": transbordos,
                        "camina": camina,
                        "minutos": minutos_reales,
                        "tipo_ruta": tipo_ruta,
                        "minutos_disponibles": minutos_disponibles,
                        "llega_a_tiempo": llega_a_tiempo,
                    })

# Convertir la lista de viajes en una tabla (DataFrame) y guardarla en CSV
df = pd.DataFrame(filas)
archivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viajes_metro.csv")
df.to_csv(archivo, index=False, encoding="utf-8")

print(f"Dataset creado: {archivo}")
print(f"Total de viajes: {len(df)}")
print(df.head())
