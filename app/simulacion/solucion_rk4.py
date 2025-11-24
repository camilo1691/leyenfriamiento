import numpy as np
import pandas as pd
from typing import Optional, List, Tuple

# ------------------------------------------------------------
# IMPORTS DEPENDIENTES DE LA ESTRUCTURA DEL PROYECTO
# ------------------------------------------------------------

try:
    from procesos_datos.cargador_datos import obtener_datos
except Exception:
    try:
        from app.procesos_datos.cargador_datos import obtener_datos
    except Exception:
        obtener_datos = None

try:
    from procesos_datos.interpolacion import temperatura_ambiente
except Exception:
    try:
        from app.procesos_datos.interpolacion import temperatura_ambiente
    except Exception:
        temperatura_ambiente = None

try:
    from procesos_datos.ajuste_curvas import ajustar_sinusoidal
    _AJUSTE_DISPONIBLE = True
except Exception:
    try:
        from app.procesos_datos.ajuste_curvas import ajustar_sinusoidal
        _AJUSTE_DISPONIBLE = True
    except Exception:
        ajustar_sinusoidal = None
        _AJUSTE_DISPONIBLE = False


# ------------------------------------------------------------
# FUNCIÓN INTERNA: ECUACIÓN DIFERENCIAL DE ENFRIAMIENTO
# ------------------------------------------------------------
def _f_enfriamiento(Ti: float, t: float, k: float, datos: Optional[pd.DataFrame],
                    Tam_const: float, metodo_interp: str = "lineal") -> float:
    """
    Calcula la derivada dT/dt = k * (T - Tam(t))
    """
    if temperatura_ambiente is None:
        Tam_t = Tam_const
    else:
        Tam_t = temperatura_ambiente(t, datos, default=Tam_const, metodo=metodo_interp)
    return k * (Ti - Tam_t)



# FUNCIÓN PRINCIPAL: EJECUTAR SIMULACIÓN RK4

def ejecutar_simulacion(
    T0: float = 90.0,
    k: float = -0.13,
    t_total: float = 5.0,
    modo_datos: str = "automatica",
    archivo=None,
    lista_manual: Optional[List[Tuple[float, float]]] = None,
    usar_sinusoidal: bool = False,
    pasos: int = 200,
    metodo_interp: str = "lineal",
    Tam_const: float = 25.0
) -> pd.DataFrame:
    """
    Ejecuta la simulación del enfriamiento con temperatura ambiente variable
    usando el método RK4.

    Parámetros:
    -----------
    T0 : float
        Temperatura inicial del objeto (°C)
    k : float
        Constante de enfriamiento (negativa para enfriamiento)
    t_total : float
        Duración total de la simulación (horas)
    modo_datos : str
        Fuente de datos de temperatura ambiente: 'csv', 'manual', 'automatica'
    archivo : str o archivo
        Ruta o archivo CSV si modo_datos == 'csv'
    lista_manual : list[tuple]
        Lista de puntos [(tiempo, Tam)] si modo_datos == 'manual'
    usar_sinusoidal : bool
        Si True, ajusta una función sinusoidal a los datos y la usa como Tam(t)
    pasos : int
        Número de pasos RK4 (a mayor número, mayor precisión)
    metodo_interp : str
        Método de interpolación para Tam (lineal o spline)
    Tam_const : float
        Temperatura ambiente constante de respaldo

    Retorna:
    --------
    pandas.DataFrame con columnas:
        "Tiempo (h)" | "Temperatura (°C)" | "Tamiente (°C)"
    """

    
    # 1 Obtener los datos base
    
    datos = None
    if modo_datos == "csv":
        if obtener_datos is None:
            raise RuntimeError("No se pudo acceder a 'obtener_datos' para modo CSV.")
        datos = obtener_datos("csv", archivo=archivo)

    elif modo_datos == "manual":
        if obtener_datos is None:
            raise RuntimeError("No se pudo acceder a 'obtener_datos' para modo manual.")
        datos = obtener_datos("manual", lista_manual=lista_manual)

    elif modo_datos == "automatica":
        if obtener_datos is not None:
            datos = obtener_datos("automatica")
        else:
            # Generar modelo base si no hay cargador
            tiempos = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
            temperaturas = [12.2, 11.7, 11.7, 11.1, 10.6, 10.6, 10.0, 11.1, 13.3, 15.6, 17.8, 17.8, 17.8, 17.8, 17.2, 16.7, 16.1, 15.6, 14.4, 14.4, 13.9, 13.3, 12.2, 12.2]
            datos = pd.DataFrame({"tiempo": tiempos, "Tam": temperaturas})

    else:
        raise ValueError("Modo de datos inválido. Usa: 'csv', 'manual' o 'automatica'.")

    
    # 2 Ajuste sinusoidal (opcional)
    
    Tam_func_ajustada = None
    if usar_sinusoidal and _AJUSTE_DISPONIBLE:
        try:
            parametros, Tam_func_ajustada = ajustar_sinusoidal(datos)
        except Exception as e:
            print(f"⚠ No se pudo ajustar modelo sinusoidal: {e}")
            Tam_func_ajustada = None
    elif usar_sinusoidal:
        print("⚠ Módulo de ajuste sinusoidal no disponible (falta scipy o ajuste_curvas).")

    
    # 3 Preparar arreglos de tiempo y temperatura
    
    pasos = max(10, int(pasos))
    dt = t_total / pasos
    tiempos = np.linspace(0.0, t_total, pasos + 1)
    T = np.zeros(pasos + 1)
    T[0] = float(T0)
    Tam_usada = np.zeros(pasos + 1)

    
    # 4 Bucle RK4 principal
    
    for i in range(pasos):
        t_i = float(tiempos[i])

        # Determinar Tam actual (según modo o función ajustada)
        if Tam_func_ajustada is not None:
            Tam_i = float(Tam_func_ajustada(t_i))
        elif temperatura_ambiente is not None:
            Tam_i = float(temperatura_ambiente(t_i, datos, default=Tam_const, metodo=metodo_interp))
        else:
            Tam_i = float(Tam_const)

        Tam_usada[i] = Tam_i

        def f(Ti, t):
            if Tam_func_ajustada is not None:
                Tam_t = float(Tam_func_ajustada(t))
            elif temperatura_ambiente is not None:
                Tam_t = float(temperatura_ambiente(t, datos, default=Tam_const, metodo=metodo_interp))
            else:
                Tam_t = float(Tam_const)
            return k * (Ti - Tam_t)

        # Método RK4
        k1 = f(T[i], tiempos[i])
        k2 = f(T[i] + 0.5 * dt * k1, tiempos[i] + 0.5 * dt)
        k3 = f(T[i] + 0.5 * dt * k2, tiempos[i] + 0.5 * dt)
        k4 = f(T[i] + dt * k3, tiempos[i] + dt)
        T[i + 1] = T[i] + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

    # Último punto
    t_last = float(tiempos[-1])
    if Tam_func_ajustada is not None:
        Tam_usada[-1] = float(Tam_func_ajustada(t_last))
    elif temperatura_ambiente is not None:
        Tam_usada[-1] = float(temperatura_ambiente(t_last, datos, default=Tam_const, metodo=metodo_interp))
    else:
        Tam_usada[-1] = float(Tam_const)

    
    # 5 Resultado final
    
    df = pd.DataFrame({
        "Tiempo (h)": tiempos,
        "Temperatura (°C)": T,
        "Tamiente (°C)": Tam_usada
    })

    return df
