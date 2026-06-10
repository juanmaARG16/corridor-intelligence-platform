import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

# Rutas
BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
INPUT  = BASE / "data/raw/Events/Conflicts_Argentina_2023a2026.xlsx"
OUTPUT = BASE / "data/processed/events.geojson"

# Leer Excel
df = pd.read_excel(INPUT)
print(f"Filas cargadas: {len(df)}")
print(f"Columnas: {list(df.columns)}")

# Limpiar coordenadas (el Excel usa coma como decimal)
df["CENTROID_LATITUDE"]  = df["CENTROID_LATITUDE"].astype(str).str.replace(",", ".").astype(float)
df["CENTROID_LONGITUDE"] = df["CENTROID_LONGITUDE"].astype(str).str.replace(",", ".").astype(float)

# Normalizar campos
df["event_id"]   = df["ID"]
df["event_date"] = pd.to_datetime(df["WEEK"], dayfirst=True)
df["event_type"] = df["EVENT_TYPE"]
df["latitude"]   = df["CENTROID_LATITUDE"]
df["longitude"]  = df["CENTROID_LONGITUDE"]

# Crear geometría
df["geometry"] = df.apply(lambda row: Point(row["longitude"], row["latitude"]), axis=1)

# Crear GeoDataFrame
gdf = gpd.GeoDataFrame(
    df[["event_id", "event_date", "event_type", "latitude", "longitude", "geometry"]],
    crs="EPSG:4326"
)

# Guardar
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
gdf.to_file(OUTPUT, driver="GeoJSON")
print(f"✓ events.geojson guardado: {len(gdf)} eventos")