import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from sqlalchemy import create_engine
from pathlib import Path

engine = create_engine("postgresql://postgres@localhost:5432/cip_db")

BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
PATH_BUF10 = BASE / "data/processed/buffers/Buffer__10km.geojson"

buf10 = gpd.read_file(PATH_BUF10)
buf10.columns = buf10.columns.str.lower()

# Eventos sintéticos sobre los corredores
eventos_sinteticos = [
    {"event_id": 9001, "event_date": "2024-03-15", "event_type": "Protests",  "latitude": -38.65, "longitude": -68.90},
    {"event_id": 9002, "event_date": "2024-05-20", "event_type": "Riots",     "latitude": -38.35, "longitude": -68.79},
    {"event_id": 9003, "event_date": "2024-07-10", "event_type": "Protests",  "latitude": -37.95, "longitude": -68.50},
    {"event_id": 9004, "event_date": "2024-09-01", "event_type": "Protests",  "latitude": -38.10, "longitude": -68.20},
    {"event_id": 9005, "event_date": "2024-11-15", "event_type": "Riots",     "latitude": -37.80, "longitude": -67.90},
]

df = pd.DataFrame(eventos_sinteticos)
df["geometry"] = df.apply(lambda r: Point(r["longitude"], r["latitude"]), axis=1)
events_test = gpd.GeoDataFrame(df, crs="EPSG:4326")

# Cruce espacial
matches = gpd.sjoin(events_test, buf10, how="inner", predicate="intersects")
print(f"Cruces encontrados: {len(matches)}")

corridor_events = matches[["event_id", "id"]].copy()
corridor_events.columns = ["event_id", "corridor_id"]
corridor_events = corridor_events.drop_duplicates()
corridor_events.insert(0, "id", range(1, len(corridor_events) + 1))

corridor_events.to_sql("corridor_events", engine, if_exists="replace", index=False)
print(f"✓ Tabla corridor_events cargada: {len(corridor_events)} cruces")

print("\n── Resumen por corredor ──────────────────────────")
resumen = corridor_events.groupby("corridor_id").size().reset_index(name="eventos")
print(resumen)