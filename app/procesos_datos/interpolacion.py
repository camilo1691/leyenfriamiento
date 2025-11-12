import numpy as np
import pandas as pd

# Intento cargar la herramienta para hacer curvas suaves (SciPy)
try:
    from scipy.interpolate import CubicSpline
    SCIPY_AVAILABLE = True  # ¡Bien! Tengo la herramienta de curvas suaves
except:
    SCIPY_AVAILABLE = False  # Ups, no tengo la herramienta de curvas suaves



# 1. INTERPOLACIÓN LINEAL - Conecto puntos con líneas rectas

def interpolacion_lineal(t, datos, default=25):
    """
    Yo calculo la temperatura en cualquier momento usando líneas rectas entre los puntos que conozco.
    """

    # Primero verifico si me dieron datos para trabajar
    if datos is None:
        return default  # Si no hay datos, uso el valor por defecto

    # Reviso que los datos tengan las columnas que necesito
    if "tiempo" not in datos.columns or "Tam" not in datos.columns:
        return default  # Si faltan columnas importantes, uso el valor por defecto

    # Extraigo los tiempos y temperaturas que conozco
    tiempos = datos["tiempo"].values    # Estos son los momentos donde sé la temperatura exacta
    temperaturas = datos["Tam"].values  # Estas son las temperaturas que medí en esos momentos

    # Ahora veo dónde está el tiempo que me preguntan
    if t <= tiempos.min():
        return temperaturas[0]  # Si me preguntan por un tiempo muy temprano, uso la primera temperatura que tengo

    if t >= tiempos.max():
        return temperaturas[-1]  # Si me preguntan por un tiempo muy tarde, uso la última temperatura que tengo

    # Aquí hago la magia: calculo la temperatura exacta en cualquier punto intermedio
    # Tomo los dos puntos más cercanos y trazo una línea recta entre ellos
    return float(np.interp(t, tiempos, temperaturas))



# 2. INTERPOLACIÓN SPLINE - Conecto puntos con curvas suaves

def interpolacion_spline(t, datos, default=25):
    """
    Yo calculo la temperatura usando curvas suaves que pasan por todos los puntos.
    """

    # Primero verifico si tengo la herramienta para hacer curvas suaves
    if not SCIPY_AVAILABLE:
        # Si no tengo la herramienta, uso el método de líneas rectas
        return interpolacion_lineal(t, datos, default)

    # Verifico si me dieron datos para trabajar
    if datos is None:
        return default  # Si no hay datos, uso el valor por defecto

    # Extraigo los tiempos y temperaturas que conozco
    tiempos = datos["tiempo"].values
    temperaturas = datos["Tam"].values

    # Aquí creo una curva suave que pasa exactamente por todos mis puntos conocidos
    spline = CubicSpline(tiempos, temperaturas, bc_type="natural")

    # Uso mi curva suave para calcular la temperatura en el tiempo exacto que me preguntan
    return float(spline(t))



# 3. FUNCIÓN PRINCIPAL - Yo decido qué método usar

def temperatura_ambiente(t, datos, default=25, metodo="lineal"):
    """
    Yo soy la función principal que te dice la temperatura en cualquier momento.
    Decido si usar líneas rectas, curvas suaves, o temperatura constante.
    """

    # Si no me dan datos, simplemente devuelvo la temperatura constante
    if datos is None:
        return default

    # Si eligen el método de curvas suaves Y tengo la herramienta disponible
    if metodo == "spline" and SCIPY_AVAILABLE:
        # Uso mi método favorito de curvas suaves
        return interpolacion_spline(t, datos, default)

    # Por defecto, uso el método confiable de líneas rectas
    return interpolacion_lineal(t, datos, default)