import sys, os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# CONFIGURACIÓN DE RUTA BASE PARA RENDER O LOCAL
# ------------------------------------------------------------
RUTA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if RUTA_BASE not in sys.path:
    sys.path.append(RUTA_BASE)

# ------------------------------------------------------------
# IMPORTS (compatibles con Render y local)
# ------------------------------------------------------------
try:
    from app.simulacion.solucion_rk4 import ejecutar_simulacion
except ModuleNotFoundError:
    from simulacion.solucion_rk4 import ejecutar_simulacion

# ------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ------------------------------------------------------------
st.set_page_config(page_title="Simulador Ley de Enfriamiento", page_icon="🌡️", layout="centered")

st.title(" Simulador de la Ley de Enfriamiento de Newton")

st.markdown("""
Simula el comportamiento térmico de un cuerpo bajo distintas condiciones
de temperatura ambiente, aplicando el método numérico de **Runge-Kutta (RK4)**.
""")

# ------------------------------------------------------------
# SELECCIÓN DE MODO DE DATOS
# ------------------------------------------------------------
modo = st.radio(
    "Selecciona el modo de ingreso de datos:",
    ["Manual", "Archivo CSV", "Automático"],
    horizontal=True
)

T0 = k = t_total = None
archivo = None
lista_manual = None

# ------------------------------------------------------------
# 1 MODO MANUAL
# ------------------------------------------------------------
if modo == "Manual":
    st.subheader(" Ingreso manual de parámetros")

    T0 = st.number_input("Temperatura inicial (°C):", value=90.0)
    k = st.number_input("Constante de enfriamiento (k):", value=-0.05, step=0.01)
    t_total = st.number_input("Duración total (horas):", value=10.0)

    st.markdown("#### Ingreso de temperaturas ambientales (horas vs °C)")
    st.info("Agrega los valores de temperatura ambiente a lo largo del día.")

    data_inicial = pd.DataFrame({
        "tiempo": [0, 6, 12, 18, 24],
        "Tam": [15, 18, 25, 20, 16]
    })
    tabla = st.data_editor(data_inicial, num_rows="dynamic", use_container_width=True)
    lista_manual = list(zip(tabla["tiempo"], tabla["Tam"]))

# ------------------------------------------------------------
# 2 MODO CSV
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

#
# 3 MODO AUTOMÁTICO
#
else:
    st.subheader("Modo automático")
    st.info("Usa una curva ambiental típica de día y noche.")

    T0 = st.number_input("Temperatura inicial del cuerpo (°C):", value=90.0)
    k = st.number_input("Constante de enfriamiento (k):", value=-0.06, step=0.01)
    t_total = st.number_input("Duración total (horas):", value=24.0)


# OPCIÓN: USAR MODELO SINUSOIDAL

# st.markdown("---")
# usar_sinusoidal = st.checkbox("Usar modelo sinusoidal ajustado a los datos", value=False)
# st.markdown("---")


# BOTÓN PARA EJECUTAR LA SIMULACIÓN

if st.button(" Ejecutar simulación"):
    st.info("Ejecutando simulación...")

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

        st.success(" Simulación completada correctamente")

        
        # GRÁFICA
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(resultados["Tiempo (h)"], resultados["Temperatura (°C)"],
                label="Temperatura del cuerpo", color="tab:blue", linewidth=2)
        ax.plot(resultados["Tiempo (h)"], resultados["Tamiente (°C)"],
                label="Temperatura ambiente", color="tab:orange", linestyle="--")
        ax.set_xlabel("Tiempo (h)")
        ax.set_ylabel("Temperatura (°C)")
        ax.set_title("Evolución de la Temperatura del Cuerpo y del Ambiente")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        
        # TABLA Y DESCARGA
        
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
