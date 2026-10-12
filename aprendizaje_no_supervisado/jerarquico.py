"""
MODELO NO SUPERVISADO 2: AGRUPAMIENTO JERÁRQUICO
¿Qué tipos de viaje existen en el metro? (otra forma de encontrarlos)

  Datos: paradas, minutos y transbordos de cada viaje  (SIN columna de respuesta)

¿En qué se diferencia de K-Means?
  - K-Means necesita que le digamos cuántos grupos (K) buscar desde el inicio.
  - El jerárquico empieza con cada viaje como un grupo y va UNIENDO los dos
    grupos más parecidos, una y otra vez, hasta que todo queda en un solo grupo.
    Ese proceso se dibuja como un árbol llamado DENDROGRAMA, y se "corta" a la
    altura que dé el número de grupos deseado.

Ejecución:  python jerarquico.py
"""
import os

import matplotlib.pyplot as plt
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler

print("=============================================")
print(" EJERCICIO: AGRUPAMIENTO JERÁRQUICO ")
print("=============================================")

# 1. Preparación de los datos (igual que en K-Means)
carpeta = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(carpeta, "..", "datos", "viajes_metro.csv"))

columnas = ["paradas", "minutos", "transbordos"]
print(f"\nViajes en el dataset: {len(df)}")
X = StandardScaler().fit_transform(df[columnas])   # misma escala para las tres columnas

# 2. Dendrograma: muestra cómo se van uniendo los grupos
# "ward" une en cada paso los dos grupos que menos aumentan la diferencia interna.
uniones = linkage(X, method="ward")

plt.figure(figsize=(12, 6))
# Se muestran solo las últimas 20 uniones para que el dibujo se pueda leer
dendrogram(uniones, truncate_mode="lastp", p=20)
altura_corte = (uniones[-3, 2] + uniones[-2, 2]) / 2      # altura donde quedan 3 grupos
plt.axhline(altura_corte, color="red", linestyle="--", label="Corte: 3 grupos")
plt.xlabel("Grupos de viajes (entre paréntesis: cuántos viajes tiene)")
plt.ylabel("Distancia entre grupos")
plt.title("Dendrograma de los viajes")
plt.legend()
plt.savefig(os.path.join(carpeta, "grafica_dendrograma.png"))
print("\nDendrograma guardado: grafica_dendrograma.png")
print("  Las líneas verticales largas indican grupos muy distintos entre sí.")
print("  Al cortar en la línea roja quedan 3 grupos.")

# 3. Creación y entrenamiento del modelo con 3 grupos
modelo = AgglomerativeClustering(n_clusters=3, linkage="ward")
df["grupo"] = modelo.fit_predict(X)


# 4. Ponerle nombre a cada grupo (mismo criterio que en K-Means)
def nombrar(grupo):
    if grupo["transbordos"].mean() >= 0.5:
        return "Con transbordo"
    if grupo["paradas"].mean() < 4:
        return "Cortos y directos"
    return "Medianos sin transbordo"


nombres = {numero: nombrar(grupo) for numero, grupo in df.groupby("grupo")}
df["nombre_grupo"] = df["grupo"].map(nombres)

print("\nGrupos encontrados por el agrupamiento jerárquico:")
for nombre in ["Cortos y directos", "Medianos sin transbordo", "Con transbordo"]:
    grupo = df[df["nombre_grupo"] == nombre]
    print(f"  {nombre:24} {len(grupo):5} viajes | "
          f"{grupo['paradas'].mean():4.1f} paradas | "
          f"{grupo['minutos'].mean():5.1f} min | "
          f"{grupo['transbordos'].mean() * 100:3.0f}% con transbordo | "
          f"{grupo['camina'].mean() * 100:3.0f}% caminan")

# 5. Un ejemplo típico de cada grupo (el viaje con la duración más cercana a la mediana)
print("\nEjemplo típico de cada grupo:")
for nombre in ["Cortos y directos", "Medianos sin transbordo", "Con transbordo"]:
    grupo = df[df["nombre_grupo"] == nombre]
    ejemplo = grupo.loc[(grupo["minutos"] - grupo["minutos"].median()).abs().idxmin()]
    print(f"  {nombre:24} -> {ejemplo['origen']} a {ejemplo['destino']} "
          f"({ejemplo['paradas']} paradas, {ejemplo['minutos']} min)")
