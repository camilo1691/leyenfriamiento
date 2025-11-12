import numpy as np
import pandas as pd

# Voy a intentar cargar la herramienta scipy para hacer ajustes de curvas
try:
    from scipy.optimize import curve_fit
    SCIPY_AVAILABLE = True  # ¡Perfecto! Tengo la herramienta disponible
except:
    SCIPY_AVAILABLE = False  # Ups, no tengo scipy instalado



# 1. DEFINO MI MODELO DE TEMPERATURA CON FORMA DE ONDA

def modelo_sinusoidal(t, alpha, beta, gamma, phi):
    """
    Esta es la fórmula que uso para describir cómo cambia la temperatura durante el día:
    Temperatura(t) = temperatura_promedio + amplitud * seno(frecuencia*tiempo + fase)
    
    Pienso en esto como una ola de temperatura que sube y baja durante el día
    """
    return alpha + beta * np.sin(gamma * t + phi)



# 2. FUNCIÓN PRINCIPAL: ENCUENTRO LOS MEJORES PARÁMETROS PARA LA CURVA

def ajustar_sinusoidal(datos):
    """
    Yo tomo los datos reales de temperatura y encuentro la curva sinusoidal 
    que mejor se ajusta a esos datos.
    
    Es como encontrar la ola perfecta que pasa por la mayoría de puntos
    """

    # Primero verifico si tengo la herramienta necesaria
    if not SCIPY_AVAILABLE:
        raise ImportError(
            "Necesito SciPy para hacer este trabajo. Instálalo con: pip install scipy"
        )

    # Verifico que me hayan dado datos para trabajar
    if datos is None:
        raise ValueError("No me diste ningún dato para ajustar la curva.")

    # Me aseguro de que los datos tengan las columnas correctas
    if "tiempo" not in datos.columns or "Tam" not in datos.columns:
        raise ValueError("Necesito que los datos tengan columnas llamadas 'tiempo' y 'Tam'")

    # Extraigo los tiempos y temperaturas de la tabla
    tiempos = datos["tiempo"].values
    temperaturas = datos["Tam"].values

    # Ahora hago una estimación inicial de los parámetros para ayudar al ajuste
    # Empiezo con valores razonables basados en los datos
    alpha_0 = np.mean(temperaturas)  # Tomo el promedio de temperatura como punto de partida
    beta_0 = (temperaturas.max() - temperaturas.min()) / 2  # Calculo cuánto varía la temperatura
    gamma_0 = 2 * np.pi / 24  # Supongo que el patrón se repite cada 24 horas
    phi_0 = 0  # Empiezo con fase cero

    # Junto todas mis estimaciones iniciales
    p0 = [alpha_0, beta_0, gamma_0, phi_0]

    try:
        # Aquí está la magia: le digo a curve_fit que encuentre los mejores parámetros
        # para que mi curva sinusoidal pase lo más cerca posible de todos los puntos reales
        parametros, _ = curve_fit(
            modelo_sinusoidal, tiempos, temperaturas, p0=p0
        )
    except Exception as e:
        raise RuntimeError(f"No pude ajustar la curva a tus datos: {e}")

    # Separo los parámetros que encontré
    alpha, beta, gamma, phi = parametros

    # Ahora creo una función práctica que cualquiera puede usar
    def Tam_ajustada(t):
        # Esta función ya sabe calcular la temperatura en cualquier momento
        # usando la curva que acabo de encontrar
        return modelo_sinusoidal(t, alpha, beta, gamma, phi)

    # Devuelvo tanto los parámetros como la función lista para usar
    return (alpha, beta, gamma, phi), Tam_ajustada



# 3. FUNCIÓN PARA GENERAR UNA CURVA SUAVE A PARTIR DE LOS PARÁMETROS

def generar_curva_ajustada(parametros, t_min=0, t_max=24, muestras=200):
    """
    Yo tomo los parámetros de la curva ajustada y genero una tabla con 
    muchos puntos para dibujar una curva suave y bonita
    """
    alpha, beta, gamma, phi = parametros

    # Creo muchos puntos de tiempo entre el mínimo y máximo
    t = np.linspace(t_min, t_max, muestras)
    
    # Calculo la temperatura para cada uno de esos tiempos
    T = modelo_sinusoidal(t, alpha, beta, gamma, phi)

    # Devuelvo una tabla ordenada con tiempos y temperaturas
    return pd.DataFrame({
        "tiempo": t,
        "Tam": T
    })