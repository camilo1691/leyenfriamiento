'''
import streamlit as st
import matplotlib.pyplot as plt

def graficar_resultados(df):
    # Aquí creo una figura y un eje para la gráfica donde voy a mostrar los resultados
    fig, ax = plt.subplots()
    
    # En esta línea dibujo la curva que representa cómo cambia la temperatura con el tiempo
    # Uso los datos de las columnas "Tiempo (h)" y "Temperatura (°C)" del DataFrame que recibo
    ax.plot(df["Tiempo (h)"], df["Temperatura (°C)"], marker='o', color="tab:blue")
    
    # En esta línea le pongo un título a la gráfica para indicar qué información estoy mostrando
    ax.set_title("Evolución de la Temperatura")
    
    # Aquí asigno el nombre al eje X para indicar que representa el tiempo en horas
    ax.set_xlabel("Tiempo (h)")
    
    # En esta línea nombro el eje Y para aclarar que muestra la temperatura en grados Celsius
    ax.set_ylabel("Temperatura (°C)")
    
    # Aquí desactivo la cuadrícula para que la gráfica se vea más limpia
    ax.grid(False)
    
    # Finalmente, en esta línea muestro la gráfica en la interfaz de Streamlit
    st.pyplot(fig)'''

import streamlit as st
import plotly.graph_objects as go

def graficar_resultados(df):
    fig = go.Figure()

    # Línea 1
    fig.add_trace(go.Scatter(
        x=df["Tiempo (h)"],
        y=df["Temperatura (°C)"],
        mode="lines+markers",
        name="Temperatura real",   # 👈 Notación (nombre en la leyenda)
        hovertemplate="<b>Tiempo:</b> %{x} h<br><b>Temp real:</b> %{y} °C<extra></extra>"
    ))

    # Línea 2
    fig.add_trace(go.Scatter(
        x=df["Tiempo (h)"],
        y=df["Temperatura estimada (°C)"],
        mode="lines+markers",
        name="Temperatura estimada",   # 👈 Notación
        hovertemplate="<b>Tiempo:</b> %{x} h<br><b>Temp estimada:</b> %{y} °C<extra></extra>"
    ))

    fig.update_layout(
        title="Comparación de Temperaturas",
        xaxis_title="Tiempo (h)",
        yaxis_title="Temperatura (°C)",
        legend_title="Leyenda"  # 👈 Título del cuadro de notaciones
    )

    st.plotly_chart(fig, use_container_width=True)
