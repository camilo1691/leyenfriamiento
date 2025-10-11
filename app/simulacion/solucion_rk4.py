import numpy as np
import pandas as pd

def ejecutar_simulacion(T0=90.0, k=-0.05, t_total=5.0, Tamb=25.0, datos=None):
    """
    Simula la Ley de Enfriamiento con el método de Runge-Kutta de 4to orden.
    Si se pasa un DataFrame 'datos', se usa como temperatura ambiente variable.
    """
    n = 100
    dt = t_total / n
    tiempos = np.linspace(0, t_total, n + 1)
    T = np.zeros(n + 1)
    T[0] = T0

    for i in range(n):
        if datos is not None and "Tam" in datos.columns:
            Tambiente = float(datos.iloc[i % len(datos)]["Tam"])
        else:
            Tambiente = Tamb

        def dTdt(Ti, t): return k * (Ti - Tambiente)

        k1 = dTdt(T[i], tiempos[i])
        k2 = dTdt(T[i] + 0.5 * dt * k1, tiempos[i] + 0.5 * dt)
        k3 = dTdt(T[i] + 0.5 * dt * k2, tiempos[i] + 0.5 * dt)
        k4 = dTdt(T[i] + dt * k3, tiempos[i] + dt)

        T[i + 1] = T[i] + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    return pd.DataFrame({"Tiempo (h)": tiempos, "Temperatura (°C)": T})
