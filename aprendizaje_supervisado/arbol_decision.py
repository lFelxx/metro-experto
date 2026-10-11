"""
MODELO SUPERVISADO 2: CLASIFICACIÓN CON ÁRBOL DE DECISIÓN
¿Llegaré a tiempo?

  X (entradas): paradas, transbordos, camina, lluvia, hora_pico, minutos_disponibles
  y (salida):   llega_a_tiempo  ->  1 = sí, 0 = no

Es SUPERVISADO porque cada viaje del dataset trae la respuesta correcta
(si ese viajero llegó a tiempo o no), y el modelo aprende de esos ejemplos.
Es CLASIFICACIÓN porque lo que predice es una CATEGORÍA (sí / no).

Ojo: el modelo NO ve cuántos minutos duró el viaje. Debe aprender, a partir
de las paradas, transbordos, lluvia y hora pico, si le alcanza el tiempo.

Ejecución:  python arbol_decision.py
"""
import os

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

print("===================================================")
print(" EJERCICIO: ÁRBOL DE DECISIÓN - ¿LLEGARÉ A TIEMPO? ")
print("===================================================")

# 1. Preparación de los datos
carpeta = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(carpeta, "..", "datos", "viajes_metro.csv"))

print(f"\nViajes en el dataset: {len(df)}")
print(df[["origen", "destino", "paradas", "transbordos", "lluvia", "hora_pico",
          "minutos_disponibles", "llega_a_tiempo"]].head())
print("\nViajes que llegaron a tiempo (1) y que no (0):")
print(df["llega_a_tiempo"].value_counts())

# Definimos las características (X) y la variable objetivo (y)
X = df[["paradas", "transbordos", "camina", "lluvia", "hora_pico", "minutos_disponibles"]]
y = df["llega_a_tiempo"]

# 80% para entrenar y 20% para probar
X_entreno, X_prueba, y_entreno, y_prueba = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Creación y entrenamiento del modelo
# max_depth=8: el árbol hace como máximo 8 preguntas seguidas antes de decidir
modelo = DecisionTreeClassifier(max_depth=8, random_state=42)
modelo.fit(X_entreno, y_entreno)

# 3. Evaluación con los datos de prueba
y_predicho = modelo.predict(X_prueba)
print(f"\nPrecisión del modelo (accuracy): {accuracy_score(y_prueba, y_predicho) * 100:.1f}%")

# Matriz de confusión: filas = lo que pasó, columnas = lo que predijo el modelo.
# La diagonal son los aciertos.
matriz = pd.DataFrame(confusion_matrix(y_prueba, y_predicho, labels=[1, 0]),
                      index=["real: llegó", "real: no llegó"],
                      columns=["pred.: llega", "pred.: no llega"])
print("\nMatriz de confusión:")
print(matriz)

# 4. Gráfica del árbol (se dibujan las 3 primeras preguntas para que se pueda leer)
plt.figure(figsize=(20, 9))
plot_tree(modelo, max_depth=3, feature_names=X.columns, class_names=["No llega", "Llega"],
          filled=True, fontsize=9)
plt.title("Árbol de decisión: ¿llegaré a tiempo? (primeros niveles)")
plt.savefig(os.path.join(carpeta, "grafica_arbol.png"))
print("\nGráfica guardada: grafica_arbol.png")

# 5. Predecir un viaje nuevo
# El usuario elige estaciones; la ruta (paradas, transbordos...) se toma del dataset
print("\n--- ¿Llegaré a tiempo? ---")
estaciones = list(df["origen"].unique())
for i, nombre in enumerate(estaciones, 1):
    print(f"  {i:2}. {nombre}")
origen = estaciones[int(input("Número de la estación de ORIGEN: ")) - 1]
destino = estaciones[int(input("Número de la estación de DESTINO: ")) - 1]
lluvia = 1 if input("¿Está lloviendo? (s/n) ").lower() == "s" else 0
hora_pico = 1 if input("¿Es hora pico? (s/n) ").lower() == "s" else 0
perfiles = ["normal", "pocos_transbordos", "movilidad_reducida"]
perfil = perfiles[int(input("Perfil (1 = normal, 2 = pocos transbordos, 3 = movilidad reducida): ")) - 1]
disponibles = int(input("¿Cuántos minutos tiene para llegar? "))

# Buscar en el dataset la ruta de ese viaje con esas condiciones
viaje = df[(df.origen == origen) & (df.destino == destino) & (df.lluvia == lluvia)
           & (df.hora_pico == hora_pico) & (df.perfil == perfil)].iloc[0]

viaje_nuevo = pd.DataFrame([[viaje.paradas, viaje.transbordos, viaje.camina,
                             lluvia, hora_pico, disponibles]], columns=X.columns)
prediccion = modelo.predict(viaje_nuevo)[0]
confianza = modelo.predict_proba(viaje_nuevo)[0].max() * 100   # qué tan seguro está el modelo

print(f"\nRuta: {viaje.ruta}")
print(f"({viaje.paradas} paradas, {viaje.transbordos} transbordo(s)"
      f"{', con caminata' if viaje.camina else ''})")
if prediccion == 1:
    print(f"✅ SÍ llega a tiempo  (confianza del modelo: {confianza:.0f}%)")
else:
    print(f"❌ NO llega a tiempo  (confianza del modelo: {confianza:.0f}%). ¡Salga antes!")
