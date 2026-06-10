import geopandas as gpd
from sqlalchemy import create_engine
from pathlib import Path

# Conexión
engine = create_engine(
    "postgresql://postgres@localhost:5432/cip_db"
)

# Ruta
BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
PATH_EVENTS = BASE / "data/processed/events.geojson"

# Cargar eventos
events = gpd.read_file(PATH_EVENTS)
events.to_postgis("events", engine, if_exists="replace", index=False)
print(f"✓ Tabla events cargada: {len(events)} filas")