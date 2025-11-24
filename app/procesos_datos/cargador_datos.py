
import pandas as pd  
import numpy as np   


# 1. FUNCIÓN PARA REVISAR Y ARREGLAR LOS DATOS

def validar_dataframe(df):
    """
    Esta función revisa que nuestra tabla de datos tenga la forma correcta,
    convierte los números a formato que la computadora pueda entender,
    y ordena los datos por tiempo.
    """

    # Aquí definimos qué columnas NECESITAMOS que tenga nuestra tabla
    columnas_necesarias = ["tiempo", "Tam"]

    # Si no nos pasaron ninguna tabla de datos, devolvemos nada
    if df is None:
        return None

    # Vamos a revisar columna por columna que estén presentes
    for col in columnas_necesarias:
        if col not in df.columns:
            raise ValueError(f"El archivo CSV debe contener la columna '{col}'.")

    # Ahora convertimos las columnas a números (por si vienen como texto)
    # 'errors="coerce"' significa: si encuentras algo que no es número, conviértelo a vacío
    df["tiempo"] = pd.to_numeric(df["tiempo"], errors="coerce")
    df["Tam"] = pd.to_numeric(df["Tam"], errors="coerce")

    # Eliminamos las filas que tengan datos vacíos o inválidos en nuestras columnas importantes
    df = df.dropna(subset=["tiempo", "Tam"])

    # Ordenamos toda la tabla por la columna de tiempo, de menor a mayor
    df = df.sort_values(by="tiempo").reset_index(drop=True)

    return df


# 2. FUNCIÓN PARA LEER ARCHIVOS CSV

def cargar_csv(archivo):
    """
    Esta función lee un archivo CSV y lo convierte en una tabla de datos
    """
    try:
        # Leemos el archivo CSV y lo convertimos en tabla
        df = pd.read_csv(archivo)
        # Llamamos a nuestra función de validación para revisar que esté bien
        return validar_dataframe(df)
    except Exception as e:
        # Si algo sale mal, mostramos un mensaje de error entendible
        raise ValueError(f"Error al leer el archivo CSV: {str(e)}")


# 3. FUNCIÓN PARA CREAR TEMPERATURAS PREDEFINIDAS

def generar_modelo_variable_por_defecto():
    """
    Esta función crea un modelo de temperatura automático que simula
    cómo cambia la temperatura durante un día normal:
    - Mañana fresca
    - Mediodía caluroso  
    - Tarde templada
    - Noche fría
    """

    # Definimos los horarios del día que nos interesan (en horas)
    tiempos = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    
    # Definimos las temperaturas correspondientes a cada hora
    temperaturas = [12.2, 11.7, 11.7, 11.1, 10.6, 10.6, 10.0, 11.1, 13.3, 15.6, 17.8, 17.8, 17.8, 17.8, 17.2, 16.7, 16.1, 15.6, 14.4, 14.4, 13.9, 13.3, 12.2, 12.2]

    # Creamos una tabla con estos datos
    df = pd.DataFrame({
        "tiempo": tiempos,      # Columna de horas
        "Tam": temperaturas     # Columna de temperaturas
    })

    return df


# 4. FUNCIÓN PARA PROCESAR DATOS QUE ESCRIBE EL USUARIO

def procesar_datos_manual(lista_de_puntos):
    """
    Esta función toma los datos que una persona escribe manualmente
    y los convierte en una tabla organizada
    """

    # Si no nos dieron ningún dato, devolvemos nada
    if not lista_de_puntos:
        return None

    # Convertimos la lista de puntos en una tabla con columnas "tiempo" y "Tam"
    df = pd.DataFrame(lista_de_puntos, columns=["tiempo", "Tam"])

    # Llamamos a nuestra función de validación para revisar los datos
    return validar_dataframe(df)


# 5. FUNCIÓN PRINCIPAL - DECIDE QUÉ DATOS USAR

def obtener_datos(modo, archivo=None, lista_manual=None):
    """
    Esta es la función principal que decide de dónde tomar los datos
    según lo que elija el usuario:
    
    - Si elige "csv": usa un archivo de computadora
    - Si elige "manual": usa datos que escribe manualmente  
    - Si elige "automatica": usa temperaturas predefinidas
    """

    # Si el usuario eligió usar un archivo CSV
    if modo == "csv":
        if archivo is None:
            raise ValueError("No se ha proporcionado un archivo CSV.")
        # Leemos y validamos el archivo CSV
        return cargar_csv(archivo)

    # Si el usuario eligió escribir los datos manualmente
    elif modo == "manual":
        # Procesamos los datos que escribió
        return procesar_datos_manual(lista_manual)

    # Si el usuario eligió el modo automático
    elif modo == "automatica":
        # Usamos nuestras temperaturas predefinidas
        return generar_modelo_variable_por_defecto()

    # Si el usuario eligió un modo que no existe
    else:
        return None