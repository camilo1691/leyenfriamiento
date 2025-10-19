import os
from dotenv import load_dotenv

# Aquí cargo las variables de entorno desde el archivo .env para poder usarlas en el programa
load_dotenv()

# En esta línea obtengo el tipo de interfaz que quiero usar (por defecto será "streamlit")
interfaz = os.getenv("TIPO_INTERFAZ", "streamlit")

# Aquí obtengo el número de puerto desde las variables de entorno (si no hay, uso el 8501)
puerto = os.getenv("PUERTO", "8501")

# En esta condición verifico si debo ejecutar la aplicación con la interfaz de Streamlit
if interfaz == "streamlit":
    # Si la interfaz es Streamlit, muestro un mensaje indicando en qué puerto se ejecutará
    print(f" Ejecutando interfaz Streamlit en el puerto {puerto}...")
    
    # Aquí lanzo el servidor de Streamlit en el puerto y dirección especificados
    os.system(f"streamlit run app/visualizacion/interfaz.py --server.port={puerto} --server.address=0.0.0.0")

# Si la interfaz no es Streamlit, ejecuto el programa en modo terminal (sin interfaz gráfica)
else:
    print("Ejecutando en modo terminal (sin interfaz gráfica)")