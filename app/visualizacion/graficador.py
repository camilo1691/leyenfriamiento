import streamlit as st
import matplotlib.pyplot as plt

def graficar_resultados(df):
    fig, ax = plt.subplots()
    ax.plot(df["Tiempo (h)"], df["Temperatura (°C)"], marker='o', color="tab:blue")
    ax.set_title("Evolución de la Temperatura")
    ax.set_xlabel("Tiempo (h)")
    ax.set_ylabel("Temperatura (°C)")
    ax.grid(True)
    st.pyplot(fig)