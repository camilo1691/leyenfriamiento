import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Importar los módulos de simulación
from app.simulacion.solucion_rk4 import ejecutar_simulacion

# ------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ------------------------------------------------------------
st.set_page_config(
    page_title="Simulador Ley de Enfriamiento",
    page_icon="🌡️",
    layout="centered"
)

st.title(" Simulador de la Ley de Enfriamiento de Newton")

st.markdown("""
Este simulador permite observar el comportamiento de un cuerpo
que se enfría con el tiempo bajo distintas condiciones de temperatura ambiente.
""")

# ------------------------------------------------------------
# SELECCIÓN DE MODO DE DATOS
# ------------------------------------------------------------
modo = st.radio(
    "Selecciona el modo de ingreso de datos:",
    ["Manual", "Archivo CSV", "Automático"],
    horizontal=True
)

# Variables comunes
T0 = k = t_total = Tamb = archivo = None
lista_manual = None
usar_sinusoidal = False

# ------------------------------------------------------------
# 1 MODO MANUAL
# ------------------------------------------------------------
if modo == "Manual":
    st.subheader(" Ingreso manual de parámetros")

    T0 = st.number_input("Temperatura inicial del cuerpo (°C):", value=90.0)
    k = st.number_input("Constante de enfriamiento (k):", value=-0.05, step=0.01)
    t_total = st.number_input("Duración total (horas):", value=10.0)
    Tamb = st.number_input("Temperatura ambiente base (°C):", value=25.0)

    st.markdown("#### Ingreso de temperaturas variables (horas vs °C)")
    st.info("Puedes agregar manualmente algunos puntos representativos de temperatura ambiente durante el día.")

    # Crea una tabla editable para ingresar las temperaturas
    data_inicial = pd.DataFrame({
        "tiempo": [0, 6, 12, 18, 24],
        "Tam": [14, 18, 25, 20, 15]
    })
    tabla = st.data_editor(data_inicial, num_rows="dynamic", use_container_width=True)
    lista_manual = list(zip(tabla["tiempo"], tabla["Tam"]))

# ------------------------------------------------------------
# 2 MODO ARCHIVO CSV
# ------------------------------------------------------------
elif modo == "Archivo CSV":
    st.subheader(" Cargar archivo CSV")
    st.info("El archivo debe contener columnas: `tiempo` y `Tam` (en °C).")

    archivo = st.file_uploader("Selecciona tu archivo CSV", type=["csv"])
    if archivo is not None:
        datos_csv = pd.read_csv(archivo)
        st.success("Archivo cargado correctamente ")
        st.dataframe(datos_csv.head())

    T0 = st.number_input("Temperatura inicial del cuerpo (°C):", value=85.0)
    k = st.number_input("Constante de enfriamiento (k):", value=-0.05, step=0.01)
    t_total = st.number_input("Duración total (horas):", value=8.0)

# ------------------------------------------------------------
# 3 MODO AUTOMÁTICO
# ------------------------------------------------------------
else:
    st.subheader(" Modo automático")
    st.info("Se generará internamente una curva típica de temperatura ambiental diaria.")

    T0 = st.number_input("Temperatura inicial del cuerpo (°C):", value=90.0)
    k = st.number_input("Constante de enfriamiento (k):", value=-0.06, step=0.01)
    t_total = st.number_input("Duración total (horas):", value=24.0)

# ------------------------------------------------------------
# OPCIÓN DE AJUSTE SINUSOIDAL
# ------------------------------------------------------------
st.markdown("---")
usar_sinusoidal = st.checkbox("Usar modelo sinusoidal ajustado a los datos", value=False)
st.markdown("---")

# ------------------------------------------------------------
# BOTÓN PARA EJECUTAR LA SIMULACIÓN
# ------------------------------------------------------------
if st.button(" Ejecutar simulación"):
    st.info("Ejecutando simulación... por favor espera unos segundos.")

    try:
        resultados = ejecutar_simulacion(
            T0=T0,
            k=k,
            t_total=t_total,
            modo_datos=(
                "manual" if modo == "Manual" else
                "csv" if modo == "Archivo CSV" else
                "automatica"
            ),
            archivo=archivo,
            lista_manual=lista_manual,
            usar_sinusoidal=usar_sinusoidal,
            pasos=250
        )

        st.success(" Simulación completada exitosamente")

        # --------------------------------------------------------
        # GRÁFICA DE RESULTADOS
        # --------------------------------------------------------
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(resultados["Tiempo (h)"], resultados["Temperatura (°C)"],
                label="Temperatura del cuerpo", color="tab:blue", linewidth=2)
        ax.plot(resultados["Tiempo (h)"], resultados["Tamiente (°C)"],
                label="Temperatura ambiente", color="tab:orange", linestyle="--")
        ax.set_title("Evolución de la Temperatura del Cuerpo y del Ambiente")
        ax.set_xlabel("Tiempo (h)")
        ax.set_ylabel("Temperatura (°C)")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        # --------------------------------------------------------
        # TABLA Y DESCARGA
        # --------------------------------------------------------
        st.subheader(" Resultados de la simulación")
        st.dataframe(resultados, use_container_width=True)

        csv = resultados.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=" Descargar resultados (CSV)",
            data=csv,
            file_name="resultados_simulacion.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f" Error durante la simulación: {e}")