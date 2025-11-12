import pandas as pd
from app.simulacion.solucion_rk4 import ejecutar_simulacion


# ------------------------------------------------------------
# 1️⃣ PRUEBA BÁSICA: modo automático
# ------------------------------------------------------------
print("\n--- Prueba 1: Modo automático ---")
df_auto = ejecutar_simulacion(
    T0=85.0,
    k=-0.07,
    t_total=10.0,
    modo_datos="automatica",
    pasos=200
)
print(df_auto.head())
df_auto.to_csv("resultado_auto.csv", index=False)
print("✅ Resultado guardado en resultado_auto.csv")


# ------------------------------------------------------------
# 2️⃣ PRUEBA: modo manual (lista definida en código)
# ------------------------------------------------------------
print("\n--- Prueba 2: Modo manual ---")
lista_manual = [
    (0, 15),
    (4, 20),
    (8, 30),
    (12, 26),
    (16, 22),
    (20, 18),
    (24, 15),
]
df_manual = ejecutar_simulacion(
    T0=90.0,
    k=-0.06,
    t_total=12.0,
    modo_datos="manual",
    lista_manual=lista_manual,
    pasos=180
)
print(df_manual.head())
df_manual.to_csv("resultado_manual.csv", index=False)
print("✅ Resultado guardado en resultado_manual.csv")


# ------------------------------------------------------------
# 3️⃣ PRUEBA: modo CSV (si tienes un archivo)
# ------------------------------------------------------------
try:
    print("\n--- Prueba 3: Modo CSV ---")
    archivo = "temperaturas.csv"  # cambia por el nombre real si existe
    df_csv = ejecutar_simulacion(
        T0=95.0,
        k=-0.05,
        t_total=8.0,
        modo_datos="csv",
        archivo=archivo,
        pasos=150
    )
    print(df_csv.head())
    df_csv.to_csv("resultado_csv.csv", index=False)
    print("✅ Resultado guardado en resultado_csv.csv")
except Exception as e:
    print(f"⚠ No se pudo ejecutar prueba CSV: {e}")


# ------------------------------------------------------------
# 4️⃣ PRUEBA OPCIONAL: usando modelo sinusoidal ajustado
# ------------------------------------------------------------
try:
    print("\n--- Prueba 4: Modo automático con ajuste sinusoidal ---")
    df_sin = ejecutar_simulacion(
        T0=80.0,
        k=-0.08,
        t_total=24.0,
        modo_datos="automatica",
        usar_sinusoidal=True,
        pasos=240
    )
    print(df_sin.head())
    df_sin.to_csv("resultado_sinusoide.csv", index=False)
    print("✅ Resultado guardado en resultado_sinusoide.csv")
except Exception as e:
    print(f"⚠ Prueba sinusoidal omitida: {e}")