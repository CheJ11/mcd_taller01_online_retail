import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/processed/online_retail.db")

# Lectura desde db SQLite
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM ventas", conn, parse_dates=["InvoiceDate"])
conn.close()

# SQLite devuelve CustomerID como float por los valores NULL, se restaura el tipo
df["CustomerID"] = df["CustomerID"].astype("Int64")
print(f"Filas: {len(df):,} | Columnas: {df.shape[1]}")

# Metadata por campo
metadata = pd.DataFrame({
    "tipo": df.dtypes.astype(str),
    "nulos": df.isna().sum(),
    "pct_nulos": (df.isna().mean() * 100).round(2),
    "valores_unicos": df.nunique(),
})
print("\n--- Metadata por campo ---")
print(metadata.to_string())

# Campos numéricos: distribución
print("\n--- Quantity y UnitPrice ---")
print(df[["Quantity", "UnitPrice"]].describe().round(2).to_string())

# Campo temporal: cobertura
print("\n--- InvoiceDate ---")
print(f"Rango: {df['InvoiceDate'].min()} -> {df['InvoiceDate'].max()}")
print("Líneas por mes:")
print(df["InvoiceDate"].dt.to_period("M").value_counts().sort_index().to_string())

# Campo geográfico: distribución
print("\n--- Country (10 principales, % de líneas) ---")
print((df["Country"].value_counts(normalize=True) * 100).round(2).head(10).to_string())