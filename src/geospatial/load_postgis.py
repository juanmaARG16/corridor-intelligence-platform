import geopandas as gpd
from sqlalchemy import create_engine, text

# Conexión
engine = create_engine(
    "postgresql://postgres:postgres@localhost:5432/cip_db"
)

# Activar PostGIS
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    conn.commit()
    print("✓ PostGIS activado")

from pathlib import Path

BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
PATH_CORRIDORS = BASE / "data" / "processed" / "corridors" / "combinado_final.geojson"
PATH_BUF5      = BASE / "data" / "processed" / "buffers" / "Buffer__5km.geojson"
PATH_BUF10     = BASE / "data" / "processed" / "buffers" / "Buffer__10km.geojson"

# Cargar corredores
corridors = gpd.read_file(PATH_CORRIDORS)
corridors.columns = corridors.columns.str.lower()
corridors = corridors[["id", "name", "type", "geometry"]]
corridors.to_postgis("corridors", engine, if_exists="replace", index=False)
print(f"✓ Tabla corridors cargada: {len(corridors)} filas")

# Cargar buffers
buf5  = gpd.read_file(PATH_BUF5)
buf10 = gpd.read_file(PATH_BUF10)

import pandas as pd
buffers = pd.concat([buf5, buf10], ignore_index=True)
buffers.columns = buffers.columns.str.lower()
buffers = buffers[["id", "name", "buffer_type", "geometry"]]
buffers = buffers.rename(columns={"id": "corridor_id"})
buffers.insert(0, "id", range(1, len(buffers) + 1))

buffers.to_postgis("corridor_buffers", engine, if_exists="replace", index=False)
print(f"✓ Tabla corridor_buffers cargada: {len(buffers)} filas")

print("\n── Todo cargado correctamente ──") 