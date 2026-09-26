import sqlite3
from pathlib import Path
import pandas as pd

PARQUET_PATH = Path("data/interim/online_retail_raw.parquet")
DB_PATH = Path("data/processed/online_retail.db")

# Códigos que no corresponden a productos
NO_PRODUCTOS = [
    "POST", "DOT", "C2", "M", "B", "BANK CHARGES", "AMAZONFEE", "S",
    "GIFT_0001_10", "GIFT_0001_20", "GIFT_0001_30", "GIFT_0001_40", "GIFT_0001_50",
]

# Lectura de datos
df = pd.read_parquet(PARQUET_PATH)
print(f"Filas iniciales: {len(df):,}")
print("\nNulos por columna:")
print(df.isna().sum().to_string())

# Limpieza de datos
print("\n--- Limpieza ---")

# [1] Duplicados exactos: filas idénticas en todas las columnas
n = len(df)
df = df.drop_duplicates()
print(f"[1] Duplicados exactos eliminados:         {n - len(df):>7,}")

# [2] Cancelaciones: InvoiceNo con prefijo 'C'.
n = len(df)
df = df[~df["InvoiceNo"].str.startswith("C")]
print(f"[2] Cancelaciones eliminadas:              {n - len(df):>7,}")

# [2b] Pedidos anulados
n = len(df)
df = df[~df["InvoiceNo"].isin(["541431", "581483"])]
print(f"[2b] Pedidos anulados:        {n - len(df):>7,}")

# [3] Cantidad o precio no positivos
n = len(df)
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
print(f"[3] Cantidad o precio <= 0 eliminados:     {n - len(df):>7,}")

# [4] Códigos que no son productos. Códigos que no siguen el patrón de 5 dígitos
fuera_patron = ~df["StockCode"].str.match(r"^\d{5}")
print("\nCódigos fuera del patrón documentado:")
print(
    df[fuera_patron]
    .groupby("StockCode")["Description"]
    .agg(["count", "first"])
    .sort_values("count", ascending=False)
    .to_string()
)

n = len(df)
df = df[~df["StockCode"].str.upper().isin(NO_PRODUCTOS)]
print(f"[4] Registros de no-productos eliminados:  {n - len(df):>7,}")

# Formato y tipos
df["Description"] = df["Description"].str.strip()      # evita duplicar productos al agrupar
df["CustomerID"] = df["CustomerID"].astype("Int64")    # entero que admite nulos

# Verificación del estado final
print(f"\nFilas finales: {len(df):,}")
print("\nNulos por columna tras la limpieza:")
print(df.isna().sum().to_string())

# Carga en SQLite
conn = sqlite3.connect(DB_PATH)
df.to_sql("ventas", conn, if_exists="replace", index=False)
n_db = pd.read_sql("SELECT COUNT(*) AS n FROM ventas", conn)["n"][0]
conn.close()
print(f"\nTabla 'ventas' guardada en {DB_PATH}: {n_db:,} filas")