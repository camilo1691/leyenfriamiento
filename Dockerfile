# Imagen base de Python
# FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor
# WORKDIR /app

# Copiar todos los archivos al contenedor
# COPY . .

# Instalar dependencias
# RUN pip install --no-cache-dir -r requirements.txt

# Comando por defecto (carga el main.py que abre Streamlit)
# CMD ["python", "app/main.py"]


# Imagen base de Python
FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar todos los archivos al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Comando para Render.com
CMD ["streamlit", "run", "app/visualizacion/interfaz.py", "--server.port=8501", "--server.address=0.0.0.0"]