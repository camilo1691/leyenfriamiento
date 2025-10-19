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
    st.pyplot(fig)