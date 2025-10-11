import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
from app.simulacion.solucion_rk4 import ejecutar_simulacion
from app.visualizacion.graficador import graficar_resultados

st.set_page_config(page_title="Simulador Ley de Enfriamiento", page_icon="🌡️", layout="centered")

st.title(" Simulador de la Ley de Enfriamiento de Newton")

# --- Modo de ingreso ---
modo = st.radio("Selecciona el modo de ingreso de datos:", ["Manual", "Archivo CSV"])

# --- Modo manual ---
if modo == "Manual":
    st.subheader(" Ingreso manual de parámetros")
    T0 = st.number_input("Temperatura inicial (°C):", value=90.0)
    k = st.number_input("Constante de enfriamiento (k):", value=-0.05)
    t_total = st.number_input("Duración (horas):", value=5.0)
    Tamb = st.number_input("Temperatura ambiente (°C):", value=25.0)
    datos = None

# --- Modo CSV ---
else:
    st.subheader(" Cargar archivo CSV de temperaturas ambientales")
    archivo = st.file_uploader("Selecciona tu archivo CSV", type=["csv"])
    if archivo is not None:
        datos = pd.read_csv(archivo)
        st.success(" Archivo cargado correctamente")
        st.dataframe(datos.head())
    else:
        st.warning("Por favor, carga un archivo CSV para continuar.")
        datos = None
    T0 = k = t_total = Tamb = None

# --- Ejecutar simulación ---
if st.button(" Ejecutar simulación"):
    st.info("Ejecutando simulación...")

    resultados = ejecutar_simulacion(
        T0=T0, k=k, t_total=t_total, Tamb=Tamb, datos=datos
    )

    st.success(" Simulación completada")
    graficar_resultados(resultados)