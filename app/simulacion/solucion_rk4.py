import numpy as np
import pandas as pd

def ejecutar_simulacion(T0=90.0, k=-0.05, t_total=5.0, Tamb=25.0, datos=None):
    """
    Esto simula la Ley de Enfriamiento con el método de Runge-Kutta de 4to orden.
    Si se pasa un DataFrame 'datos', se usa como temperatura ambiente variable.
    """

    # Aquí defino el número de pasos que voy a usar en la simulación
    n = 100

    # En esta línea calculo el tamaño del paso (intervalo de tiempo entre iteraciones)
    dt = t_total / n

    # Aquí genero un arreglo con los tiempos desde 0 hasta el total, dividido en n+1 puntos
    tiempos = np.linspace(0, t_total, n + 1)

    # En esta línea creo un arreglo para guardar los valores de temperatura en cada paso
    T = np.zeros(n + 1)

    # Aquí establezco la temperatura inicial con el valor que me pasen como parámetro
    T[0] = T0

    # En este ciclo recorro cada paso del tiempo para calcular la evolución de la temperatura
    for i in range(n):

        # Si tengo datos cargados (un DataFrame) y existe la columna "Tam", uso la temperatura ambiente variable
        if datos is not None and "Tam" in datos.columns:
            Tambiente = float(datos.iloc[i % len(datos)]["Tam"])
        # Si no, uso la temperatura ambiente constante que se haya pasado
        else:
            Tambiente = Tamb

        # Aquí defino la función que representa la derivada de la temperatura según la Ley de Enfriamiento
        def dTdt(Ti, t): return k * (Ti - Tambiente)

        # En estas líneas aplico el método de Runge-Kutta de 4to orden para integrar la ecuación diferencial
        k1 = dTdt(T[i], tiempos[i])
        k2 = dTdt(T[i] + 0.5 * dt * k1, tiempos[i] + 0.5 * dt)
        k3 = dTdt(T[i] + 0.5 * dt * k2, tiempos[i] + 0.5 * dt)
        k4 = dTdt(T[i] + dt * k3, tiempos[i] + dt)

        # Aquí actualizo el valor de la temperatura para el siguiente paso usando el promedio ponderado de las pendientes
        T[i + 1] = T[i] + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    # Finalmente, retorno un DataFrame con los resultados del tiempo y la temperatura correspondiente
    return pd.DataFrame({"Tiempo (h)": tiempos, "Temperatura (°C)": T})
