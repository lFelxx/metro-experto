"""
MODELO SUPERVISADO 1: REGRESIÓN LINEAL
¿Cuántos minutos tarda un viaje en el metro?

  X (entradas): paradas, transbordos, camina, lluvia, hora_pico
  y (salida):   minutos del viaje

Es SUPERVISADO porque cada viaje del dataset trae la respuesta correcta
(los minutos), y el modelo aprende de esos ejemplos.
Es REGRESIÓN porque lo que predice es un NÚMERO.

Ejecución:  python regresion_lineal.py
"""
import os

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

print("==============================================")
print(" EJERCICIO: REGRESIÓN LINEAL - TIEMPO DE VIAJE ")
print("==============================================")

# 1. Preparación de los datos
# Cargamos el dataset de viajes creado con ruta_metro.py (carpeta datos/)
carpeta = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(carpeta, "..", "datos", "viajes_metro.csv"))

print(f"\nViajes en el dataset: {len(df)}")
print(df[["origen", "destino", "paradas", "transbordos", "camina", "lluvia", "hora_pico", "minutos"]].head())

# Definimos las características (X) y la variable objetivo (y)
X = df[["paradas", "transbordos", "camina", "lluvia", "hora_pico"]]   # entradas del modelo
y = df["minutos"]                                                     # lo que queremos predecir

# Separamos los datos: 80% para entrenar y 20% para probar con viajes que el modelo no ha visto
X_entreno, X_prueba, y_entreno, y_prueba = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Creación y entrenamiento del modelo
modelo = LinearRegression()
modelo.fit(X_entreno, y_entreno)        # el modelo "aprende" la relación entre X e y

# 3. ¿Qué aprendió el modelo?
# La regresión lineal aprende una fórmula:
#   minutos = b0 + b1*paradas + b2*transbordos + b3*camina + b4*lluvia + b5*hora_pico
print("\nLo que aprendió el modelo (minutos que suma cada factor):")
for nombre, coeficiente in zip(X.columns, modelo.coef_):
    print(f"  {nombre:12} {coeficiente:+.2f} min")
print(f"  {'base':12} {modelo.intercept_:+.2f} min")

# 4. Evaluación con los datos de prueba
y_predicho = modelo.predict(X_prueba)
print("\nEvaluación con los viajes de prueba:")
print(f"  Error promedio (MAE): {mean_absolute_error(y_prueba, y_predicho):.2f} minutos")
print(f"  R² (1 = perfecto):    {r2_score(y_prueba, y_predicho):.3f}")

# 5. Gráfica: tiempo real vs. tiempo predicho
# Si el modelo fuera perfecto, todos los puntos quedarían sobre la línea roja
plt.scatter(y_prueba, y_predicho, alpha=0.4, label="Viajes de prueba")
plt.plot([0, y.max()], [0, y.max()], "r--", label="Predicción perfecta")
plt.xlabel("Minutos reales")
plt.ylabel("Minutos predichos")
plt.title("Regresión lineal: tiempo de viaje")
plt.legend()
plt.savefig(os.path.join(carpeta, "grafica_regresion.png"))
print("\nGráfica guardada: grafica_regresion.png")

# 6. Predecir un viaje nuevo
print("\n--- Predecir un viaje nuevo ---")
paradas = int(input("¿Cuántas paradas tiene el viaje? "))
transbordos = int(input("¿Cuántos transbordos? (0 o 1) "))
camina = 1 if input("¿Camina de Alpujarra a Cisneros? (s/n) ").lower() == "s" else 0
lluvia = 1 if input("¿Está lloviendo? (s/n) ").lower() == "s" else 0
hora_pico = 1 if input("¿Es hora pico? (s/n) ").lower() == "s" else 0

viaje_nuevo = pd.DataFrame([[paradas, transbordos, camina, lluvia, hora_pico]], columns=X.columns)
prediccion = modelo.predict(viaje_nuevo)[0]
print(f"\nEl modelo predice que el viaje tardará {prediccion:.1f} minutos.")
