import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DB_PATH = Path("data/processed/online_retail.db")
FIG_DIR = Path("reports/figures")

# Lectura desde db SQLite
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM ventas", conn, parse_dates=["InvoiceDate"])
conn.close()

# Importe de cada línea: medida de ventas en libras
df["Importe"] = df["Quantity"] * df["UnitPrice"]

# Serie temporal. Ventas mensuales
mensual = df.set_index("InvoiceDate").resample("MS")["Importe"].sum() / 1000
print("Ventas mensuales (miles de £):")
print(mensual.round(1).to_string())

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(mensual.index[:-1], mensual.values[:-1], marker="o",
        label="Mes completo", zorder=3)   # zorder: se dibuja encima del tramo gris
ax.plot(mensual.index[-2:], mensual.values[-2:], marker="o", linestyle="--",
        color="gray", label="Dic 2011 (incompleto: hasta el día 9)")
ax.annotate(f"Máximo: £{mensual.max():,.0f} mil",
            xy=(mensual.idxmax(), mensual.max()),
            xytext=(-140, -10), textcoords="offset points",
            arrowprops=dict(arrowstyle="->"))
ax.set_xticks(mensual.index, mensual.index.strftime("%Y-%m"), rotation=45)
ax.set(title="Ventas mensuales", xlabel="Mes", ylabel="Ventas (miles de £)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / "01_ventas_mensuales.png", dpi=150)
plt.close(fig)

# Mapa de calor. Facturas por día de la semana y hora
facturas = df.drop_duplicates("InvoiceNo")   # una fila por factura (compra)
tabla = pd.crosstab(facturas["InvoiceDate"].dt.dayofweek,
                    facturas["InvoiceDate"].dt.hour)
tabla = tabla.reindex(range(7), fill_value=0)  # incluye días sin facturas
tabla.index = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
print("\nFacturas por día y hora:")
print(tabla.to_string())

fig, ax = plt.subplots(figsize=(11, 4.5))
sns.heatmap(tabla, cmap="YlOrRd", annot=True, fmt="d", linewidths=0.5,
            cbar_kws={"label": "Número de facturas"}, ax=ax)
ax.set(title="Facturas por día de la semana y hora",
       xlabel="Hora del día", ylabel="")
fig.tight_layout()
fig.savefig(FIG_DIR / "02_facturas_dia_hora.png", dpi=150)
plt.close(fig)

# Histograma en escala logarítmica. Cantidad por línea
q = df["Quantity"]
print(f"\nQuantity -> mediana: {q.median():.0f} | p99: {q.quantile(0.99):.0f} | máx: {q.max():,}")

bins = np.unique(np.logspace(0, np.log10(q.max() + 1), 40).round())
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(q, bins=bins, edgecolor="white")
ax.set_xscale("log")
ax.set_yscale("log")
ax.axvline(q.median(), color="black", linestyle="--",
           label=f"Mediana: {q.median():.0f} unidades")
ax.axvline(q.quantile(0.99), color="red", linestyle="--",
           label=f"Percentil 99: {q.quantile(0.99):.0f} unidades")
ax.set(title="Distribución de la cantidad por línea de factura",
       xlabel="Cantidad (escala log)", ylabel="Número de líneas (escala log)")
ax.legend()
fig.tight_layout()
fig.savefig(FIG_DIR / "03_distribucion_cantidad.png", dpi=150)
plt.close(fig)

print(f"\nFiguras guardadas en {FIG_DIR}")