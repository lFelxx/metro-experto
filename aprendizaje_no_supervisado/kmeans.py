"""
MODELO NO SUPERVISADO 1: AGRUPAMIENTO CON K-MEANS
¿Qué tipos de viaje existen en el metro?

  Datos: paradas, minutos y transbordos de cada viaje  (SIN columna de respuesta)

Es NO SUPERVISADO porque NO le damos la respuesta: nadie le dice al modelo
qué tipo de viaje es cada uno. K-Means descubre los grupos por sí solo,
juntando los viajes que se parecen.

Ejecución:  python kmeans.py
"""
import os

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

print("=============================================")
print(" EJERCICIO: AGRUPAMIENTO CON K-MEANS ")
print("=============================================")

# 1. Preparación de los datos
carpeta = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(carpeta, "..", "datos", "viajes_metro.csv"))

# Solo usamos características: NO hay variable objetivo (y)
columnas = ["paradas", "minutos", "transbordos"]
print(f"\nViajes en el dataset: {len(df)}")
print(df[columnas].head())

# Escalamos los datos: paradas va de 0 a 11, minutos de 0 a 45 y transbordos de 0 a 1.
# StandardScaler los pone en la misma escala para que las tres columnas pesen igual.
escalador = StandardScaler()
X = escalador.fit_transform(df[columnas])

# 2. ¿Cuántos grupos (K) usar? -> Método del codo
# La "inercia" mide qué tan lejos están los viajes del centro de su grupo.
# Siempre baja al aumentar K; se elige el K donde deja de bajar mucho (el "codo").
print("\nMétodo del codo:")
inercias = []
for k in range(1, 9):
    inercias.append(KMeans(n_clusters=k, n_init=10, random_state=42).fit(X).inertia_)
    print(f"  K = {k}  ->  inercia = {inercias[-1]:,.0f}")

plt.figure()
plt.plot(range(1, 9), inercias, "o-")
plt.xlabel("Número de grupos (K)")
plt.ylabel("Inercia")
plt.title("Método del codo")
plt.savefig(os.path.join(carpeta, "grafica_codo.png"))

# 3. Creación y entrenamiento del modelo con K = 3
# K-Means: pone 3 centros, asigna cada viaje al centro más cercano,
# mueve cada centro al promedio de sus viajes y repite hasta que no cambian.
modelo = KMeans(n_clusters=3, n_init=10, random_state=42)
df["grupo"] = modelo.fit_predict(X)


# 4. Ponerle nombre a cada grupo según cómo son sus viajes en promedio
def nombrar(grupo):
    if grupo["transbordos"].mean() >= 0.5:
        return "Con transbordo"
    if grupo["paradas"].mean() < 4:
        return "Cortos y directos"
    return "Medianos sin transbordo"


nombres = {numero: nombrar(grupo) for numero, grupo in df.groupby("grupo")}
df["nombre_grupo"] = df["grupo"].map(nombres)

print("\nGrupos encontrados por K-Means:")
for nombre in ["Cortos y directos", "Medianos sin transbordo", "Con transbordo"]:
    grupo = df[df["nombre_grupo"] == nombre]
    print(f"  {nombre:24} {len(grupo):5} viajes | "
          f"{grupo['paradas'].mean():4.1f} paradas | "
          f"{grupo['minutos'].mean():5.1f} min | "
          f"{grupo['transbordos'].mean() * 100:3.0f}% con transbordo | "
          f"{grupo['camina'].mean() * 100:3.0f}% caminan")

# 5. Gráfica: cada viaje es un punto (paradas vs. minutos), coloreado según su grupo.
# Se hacen dos paneles (sin y con transbordo), porque el transbordo es la tercera
# columna que usó el modelo y no se ve en un dibujo de solo dos ejes.
colores = {"Cortos y directos": "tab:blue", "Medianos sin transbordo": "tab:green",
           "Con transbordo": "tab:orange"}
figura, paneles = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for panel, transbordos, titulo in zip(paneles, [0, 1], ["Viajes SIN transbordo", "Viajes CON transbordo"]):
    viajes = df[df["transbordos"] == transbordos]
    for nombre, color in colores.items():
        grupo = viajes[viajes["nombre_grupo"] == nombre]
        panel.scatter(grupo["paradas"], grupo["minutos"], alpha=0.4, color=color, label=nombre)
    panel.set_title(titulo)
    panel.set_xlabel("Paradas")
paneles[0].set_ylabel("Minutos")
paneles[1].legend()
figura.suptitle("K-Means: tipos de viaje")
figura.savefig(os.path.join(carpeta, "grafica_kmeans.png"))
print("\nGráficas guardadas: grafica_codo.png y grafica_kmeans.png")

# 6. Clasificar un viaje nuevo en uno de los grupos
print("\n--- ¿A qué grupo pertenece un viaje? ---")
paradas = int(input("¿Cuántas paradas tiene el viaje? "))
minutos = float(input("¿Cuántos minutos tarda? "))
transbordos = int(input("¿Cuántos transbordos? (0 o 1) "))
viaje_nuevo = pd.DataFrame([[paradas, minutos, transbordos]], columns=columnas)
grupo = modelo.predict(escalador.transform(viaje_nuevo))[0]   # se escala igual que los datos
print(f"\nEse viaje pertenece al grupo: {nombres[grupo].upper()}")
