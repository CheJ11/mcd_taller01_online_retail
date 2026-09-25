from pathlib import Path
import urllib.request
import zipfile
import pandas as pd

URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
RAW_DIR = Path("data/raw")
INTERIM_DIR = Path("data/interim")
ZIP_PATH = RAW_DIR / "online_retail.zip"
XLSX_PATH = RAW_DIR / "Online Retail.xlsx"
PARQUET_PATH = INTERIM_DIR / "online_retail_raw.parquet"

# Descargar y extraer el archivo original
if not XLSX_PATH.exists():
    print("Descargando dataset...")
    urllib.request.urlretrieve(URL, ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extractall(RAW_DIR)
    ZIP_PATH.unlink()
    XLSX_PATH.chmod(0o444)

# Leer el original
print("Leyendo Excel (puede tardar)...")
df = pd.read_excel(
    XLSX_PATH,
    dtype={"InvoiceNo": str, "StockCode": str, "Description": str},
)

# Guardar copia en parquet
df.to_parquet(PARQUET_PATH, index=False)

print(f"Copia de trabajo guardada en {PARQUET_PATH}")
print(f"Shape: {df.shape}")
print(df.dtypes)