import os
from dotenv import load_dotenv

load_dotenv()

interfaz = os.getenv("TIPO_INTERFAZ", "streamlit")
puerto = os.getenv("PUERTO", "8501")

if interfaz == "streamlit":
    print(f" Ejecutando interfaz Streamlit en el puerto {puerto}...")
    os.system(f"streamlit run app/visualizacion/interfaz.py --server.port={puerto} --server.address=0.0.0.0")
else:
    print("Ejecutando en modo terminal (sin interfaz gráfica)")