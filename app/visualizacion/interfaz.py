import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
from app.simulacion.solucion_rk4 import ejecutar_simulacion
from app.visualizacion.graficador import graficar_resultados

# Aquí configuro la página de Streamlit con un título, un ícono y un diseño centrado
st.set_page_config(page_title="Simulador Ley de Enfriamiento", page_icon="🌡️", layout="centered")

# En esta línea muestro el título principal del simulador en la interfaz
st.title(" Simulador de la Ley de Enfriamiento de Newton")

# Aquí le doy al usuario la opción de escoger cómo quiere ingresar los datos: manualmente o desde un archivo CSV
modo = st.radio("Selecciona el modo de ingreso de datos:", ["Manual", "Archivo CSV"])

# --- Modo de ingreso manual ---
if modo == "Manual":
    # En esta sección creo los campos para que el usuario ingrese los valores de forma manual
    st.subheader(" Ingreso manual de parámetros")
    
    # Aquí capturo la temperatura inicial del cuerpo
    T0 = st.number_input("Temperatura inicial (°C):", value=90.0)
    
    # En esta línea permito ingresar la constante de enfriamiento
    k = st.number_input("Constante de enfriamiento (k):", value=-0.05)
    
    # Aquí pido la duración total del proceso en horas
    t_total = st.number_input("Duración (horas):", value=5.0)
    
    # En esta línea capturo la temperatura ambiente
    Tamb = st.number_input("Temperatura ambiente (°C):", value=25.0)
    
    # Indico que en este modo no se cargan datos desde archivo
    datos = None

# --- Modo de ingreso desde archivo CSV ---
else:
    # Aquí muestro la opción para cargar un archivo CSV con datos de temperatura
    st.subheader(" Cargar archivo CSV de temperaturas ambientales")
    
    # En esta línea permito que el usuario seleccione el archivo CSV
    archivo = st.file_uploader("Selecciona tu archivo CSV", type=["csv"])
    
    # Si el usuario carga correctamente un archivo, lo leo y lo muestro
    if archivo is not None:
        datos = pd.read_csv(archivo)
        st.success(" Archivo cargado correctamente")
        st.dataframe(datos.head())
    
    # Si no se ha cargado ningún archivo, muestro una advertencia
    else:
        st.warning("Por favor, carga un archivo CSV para continuar.")
        datos = None
    
    # En este caso las variables del modo manual no se usan
    T0 = k = t_total = Tamb = None

# --- Ejecución de la simulación ---
if st.button(" Ejecutar simulación"):
    # Cuando el usuario presiona el botón, informo que la simulación está en proceso
    st.info("Ejecutando simulación...")

    # Aquí llamo a la función que realiza la simulación usando el método RK4 con los datos ingresados
    resultados = ejecutar_simulacion(
        T0=T0, k=k, t_total=t_total, Tamb=Tamb, datos=datos
    )

    # Muestro un mensaje indicando que la simulación terminó correctamente
    st.success(" Simulación completada")
    
    # Finalmente, llamo a la función que genera y muestra la gráfica con los resultados obtenidos
    graficar_resultados(resultados)