import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path

BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
OUTPUT = BASE / "data/synthetic/synthetic_corridor_events.geojson"

# Eventos plausibles por corredor
# corridor_id 1 = Neuquén-Añelo
# corridor_id 2 = Añelo-Rincón
# corridor_id 3 = Neuquén-Catriel

eventos = [

    # ── Neuquén-Añelo (40 eventos) ────────────────────────────────────────
    # Protestas — alta frecuencia por tráfico Vaca Muerta
    {"corridor_id":1,"event_type":"protesta","subtipo":"bloqueo_sindical",   "severidad":4,"event_date":"2023-02-10","latitude":-38.65,"longitude":-68.90},
    {"corridor_id":1,"event_type":"protesta","subtipo":"bloqueo_sindical",   "severidad":4,"event_date":"2023-04-22","latitude":-38.62,"longitude":-68.85},
    {"corridor_id":1,"event_type":"protesta","subtipo":"comunidad_mapuche",  "severidad":4,"event_date":"2023-06-15","latitude":-38.60,"longitude":-68.80},
    {"corridor_id":1,"event_type":"protesta","subtipo":"comunidad_mapuche",  "severidad":4,"event_date":"2023-09-03","latitude":-38.58,"longitude":-68.75},
    {"corridor_id":1,"event_type":"protesta","subtipo":"bloqueo_sindical",   "severidad":4,"event_date":"2024-01-18","latitude":-38.55,"longitude":-68.70},
    {"corridor_id":1,"event_type":"protesta","subtipo":"bloqueo_sindical",   "severidad":4,"event_date":"2024-03-07","latitude":-38.63,"longitude":-68.88},
    {"corridor_id":1,"event_type":"protesta","subtipo":"comunidad_mapuche",  "severidad":4,"event_date":"2024-07-14","latitude":-38.61,"longitude":-68.83},
    {"corridor_id":1,"event_type":"protesta","subtipo":"bloqueo_sindical",   "severidad":4,"event_date":"2024-09-25","latitude":-38.59,"longitude":-68.78},
    {"corridor_id":1,"event_type":"protesta","subtipo":"bloqueo_sindical",   "severidad":4,"event_date":"2025-01-30","latitude":-38.57,"longitude":-68.73},
    {"corridor_id":1,"event_type":"protesta","subtipo":"comunidad_mapuche",  "severidad":4,"event_date":"2025-04-11","latitude":-38.64,"longitude":-68.86},
    # Accidentes — frecuentes por tráfico pesado
    {"corridor_id":1,"event_type":"accidente","subtipo":"camion_volcado",    "severidad":3,"event_date":"2023-03-05","latitude":-38.66,"longitude":-68.92},
    {"corridor_id":1,"event_type":"accidente","subtipo":"colision_multiple", "severidad":3,"event_date":"2023-05-19","latitude":-38.64,"longitude":-68.87},
    {"corridor_id":1,"event_type":"accidente","subtipo":"camion_volcado",    "severidad":3,"event_date":"2023-08-22","latitude":-38.61,"longitude":-68.82},
    {"corridor_id":1,"event_type":"accidente","subtipo":"colision_multiple", "severidad":3,"event_date":"2023-11-14","latitude":-38.59,"longitude":-68.77},
    {"corridor_id":1,"event_type":"accidente","subtipo":"camion_volcado",    "severidad":3,"event_date":"2024-02-08","latitude":-38.67,"longitude":-68.93},
    {"corridor_id":1,"event_type":"accidente","subtipo":"colision_multiple", "severidad":3,"event_date":"2024-04-16","latitude":-38.65,"longitude":-68.89},
    {"corridor_id":1,"event_type":"accidente","subtipo":"camion_volcado",    "severidad":3,"event_date":"2024-06-29","latitude":-38.62,"longitude":-68.84},
    {"corridor_id":1,"event_type":"accidente","subtipo":"colision_multiple", "severidad":3,"event_date":"2024-10-03","latitude":-38.60,"longitude":-68.79},
    {"corridor_id":1,"event_type":"accidente","subtipo":"camion_volcado",    "severidad":3,"event_date":"2025-02-17","latitude":-38.58,"longitude":-68.74},
    {"corridor_id":1,"event_type":"accidente","subtipo":"colision_multiple", "severidad":3,"event_date":"2025-05-08","latitude":-38.63,"longitude":-68.86},
    # Clima extremo — nevadas e inundaciones invernales
    {"corridor_id":1,"event_type":"clima","subtipo":"nevada",               "severidad":4,"event_date":"2023-07-10","latitude":-38.64,"longitude":-68.88},
    {"corridor_id":1,"event_type":"clima","subtipo":"alud",                 "severidad":4,"event_date":"2023-08-05","latitude":-38.62,"longitude":-68.83},
    {"corridor_id":1,"event_type":"clima","subtipo":"nevada",               "severidad":4,"event_date":"2024-06-18","latitude":-38.60,"longitude":-68.78},
    {"corridor_id":1,"event_type":"clima","subtipo":"inundacion",           "severidad":4,"event_date":"2024-08-22","latitude":-38.58,"longitude":-68.73},
    {"corridor_id":1,"event_type":"clima","subtipo":"nevada",               "severidad":4,"event_date":"2025-07-03","latitude":-38.66,"longitude":-68.91},
    # Clima leve
    {"corridor_id":1,"event_type":"clima","subtipo":"viento_fuerte",        "severidad":2,"event_date":"2023-09-14","latitude":-38.65,"longitude":-68.90},
    {"corridor_id":1,"event_type":"clima","subtipo":"lluvia",               "severidad":2,"event_date":"2024-04-25","latitude":-38.63,"longitude":-68.85},
    {"corridor_id":1,"event_type":"clima","subtipo":"viento_fuerte",        "severidad":2,"event_date":"2025-03-19","latitude":-38.61,"longitude":-68.80},
    # Congestión
    {"corridor_id":1,"event_type":"congestion","subtipo":"trafico_pesado",  "severidad":2,"event_date":"2023-10-06","latitude":-38.64,"longitude":-68.87},
    {"corridor_id":1,"event_type":"congestion","subtipo":"trafico_pesado",  "severidad":2,"event_date":"2024-05-13","latitude":-38.62,"longitude":-68.82},
    {"corridor_id":1,"event_type":"congestion","subtipo":"trafico_pesado",  "severidad":2,"event_date":"2025-01-07","latitude":-38.60,"longitude":-68.77},
    # Obra vial
    {"corridor_id":1,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2023-11-20","latitude":-38.63,"longitude":-68.84},
    {"corridor_id":1,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2024-03-28","latitude":-38.61,"longitude":-68.79},
    {"corridor_id":1,"event_type":"obra_vial","subtipo":"corte_total",      "severidad":1,"event_date":"2024-08-15","latitude":-38.59,"longitude":-68.74},
    {"corridor_id":1,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2025-02-04","latitude":-38.64,"longitude":-68.86},
    {"corridor_id":1,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2025-06-10","latitude":-38.62,"longitude":-68.81},
    {"corridor_id":1,"event_type":"obra_vial","subtipo":"corte_total",      "severidad":1,"event_date":"2023-04-17","latitude":-38.60,"longitude":-68.76},
    {"corridor_id":1,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2023-12-09","latitude":-38.58,"longitude":-68.71},
    {"corridor_id":1,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2024-11-22","latitude":-38.66,"longitude":-68.93},
    {"corridor_id":1,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2025-05-30","latitude":-38.64,"longitude":-68.88},

    # ── Añelo-Rincón de los Sauces (25 eventos) ───────────────────────────
    {"corridor_id":2,"event_type":"accidente","subtipo":"camion_volcado",   "severidad":3,"event_date":"2023-03-18","latitude":-38.35,"longitude":-68.79},
    {"corridor_id":2,"event_type":"accidente","subtipo":"colision_multiple","severidad":3,"event_date":"2023-07-24","latitude":-38.20,"longitude":-68.50},
    {"corridor_id":2,"event_type":"accidente","subtipo":"camion_volcado",   "severidad":3,"event_date":"2023-11-09","latitude":-38.05,"longitude":-68.20},
    {"corridor_id":2,"event_type":"accidente","subtipo":"colision_multiple","severidad":3,"event_date":"2024-02-14","latitude":-37.90,"longitude":-67.90},
    {"corridor_id":2,"event_type":"accidente","subtipo":"camion_volcado",   "severidad":3,"event_date":"2024-06-05","latitude":-37.75,"longitude":-67.60},
    {"corridor_id":2,"event_type":"accidente","subtipo":"colision_multiple","severidad":3,"event_date":"2024-09-17","latitude":-38.30,"longitude":-68.70},
    {"corridor_id":2,"event_type":"accidente","subtipo":"camion_volcado",   "severidad":3,"event_date":"2025-01-22","latitude":-38.15,"longitude":-68.40},
    {"corridor_id":2,"event_type":"clima","subtipo":"nevada",               "severidad":4,"event_date":"2023-07-15","latitude":-38.25,"longitude":-68.60},
    {"corridor_id":2,"event_type":"clima","subtipo":"inundacion",           "severidad":4,"event_date":"2023-09-28","latitude":-38.10,"longitude":-68.30},
    {"corridor_id":2,"event_type":"clima","subtipo":"alud",                 "severidad":4,"event_date":"2024-07-08","latitude":-37.95,"longitude":-68.00},
    {"corridor_id":2,"event_type":"clima","subtipo":"nevada",               "severidad":4,"event_date":"2025-06-19","latitude":-37.80,"longitude":-67.70},
    {"corridor_id":2,"event_type":"clima","subtipo":"viento_fuerte",        "severidad":2,"event_date":"2023-10-12","latitude":-38.28,"longitude":-68.65},
    {"corridor_id":2,"event_type":"clima","subtipo":"lluvia",               "severidad":2,"event_date":"2024-04-03","latitude":-38.13,"longitude":-68.35},
    {"corridor_id":2,"event_type":"clima","subtipo":"viento_fuerte",        "severidad":2,"event_date":"2024-11-27","latitude":-37.98,"longitude":-68.05},
    {"corridor_id":2,"event_type":"clima","subtipo":"lluvia",               "severidad":2,"event_date":"2025-03-14","latitude":-37.83,"longitude":-67.75},
    {"corridor_id":2,"event_type":"protesta","subtipo":"bloqueo_sindical",  "severidad":4,"event_date":"2023-05-06","latitude":-38.32,"longitude":-68.74},
    {"corridor_id":2,"event_type":"protesta","subtipo":"bloqueo_sindical",  "severidad":4,"event_date":"2024-08-19","latitude":-38.17,"longitude":-68.44},
    {"corridor_id":2,"event_type":"protesta","subtipo":"comunidad_mapuche", "severidad":4,"event_date":"2025-02-25","latitude":-38.02,"longitude":-68.14},
    {"corridor_id":2,"event_type":"congestion","subtipo":"trafico_pesado",  "severidad":2,"event_date":"2023-08-30","latitude":-38.22,"longitude":-68.55},
    {"corridor_id":2,"event_type":"congestion","subtipo":"trafico_pesado",  "severidad":2,"event_date":"2024-05-16","latitude":-38.07,"longitude":-68.25},
    {"corridor_id":2,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2023-12-14","latitude":-37.92,"longitude":-67.95},
    {"corridor_id":2,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2024-03-09","latitude":-37.77,"longitude":-67.65},
    {"corridor_id":2,"event_type":"obra_vial","subtipo":"corte_total",      "severidad":1,"event_date":"2024-10-21","latitude":-38.27,"longitude":-68.62},
    {"corridor_id":2,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2025-04-07","latitude":-38.12,"longitude":-68.32},
    {"corridor_id":2,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2025-07-01","latitude":-37.97,"longitude":-68.02},

    # ── Neuquén-Catriel (15 eventos) ──────────────────────────────────────
    {"corridor_id":3,"event_type":"clima","subtipo":"viento_fuerte",        "severidad":2,"event_date":"2023-06-08","latitude":-38.80,"longitude":-68.40},
    {"corridor_id":3,"event_type":"clima","subtipo":"nevada",               "severidad":4,"event_date":"2023-08-19","latitude":-38.60,"longitude":-68.10},
    {"corridor_id":3,"event_type":"clima","subtipo":"lluvia",               "severidad":2,"event_date":"2024-05-22","latitude":-38.40,"longitude":-67.80},
    {"corridor_id":3,"event_type":"clima","subtipo":"inundacion",           "severidad":4,"event_date":"2024-09-14","latitude":-38.20,"longitude":-67.50},
    {"corridor_id":3,"event_type":"clima","subtipo":"viento_fuerte",        "severidad":2,"event_date":"2025-03-31","latitude":-38.00,"longitude":-67.20},
    {"corridor_id":3,"event_type":"accidente","subtipo":"camion_volcado",   "severidad":3,"event_date":"2023-04-25","latitude":-38.70,"longitude":-68.25},
    {"corridor_id":3,"event_type":"accidente","subtipo":"colision_multiple","severidad":3,"event_date":"2023-10-17","latitude":-38.50,"longitude":-67.95},
    {"corridor_id":3,"event_type":"accidente","subtipo":"camion_volcado",   "severidad":3,"event_date":"2024-07-03","latitude":-38.30,"longitude":-67.65},
    {"corridor_id":3,"event_type":"accidente","subtipo":"colision_multiple","severidad":3,"event_date":"2025-01-15","latitude":-38.10,"longitude":-67.35},
    {"corridor_id":3,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2023-11-28","latitude":-38.75,"longitude":-68.30},
    {"corridor_id":3,"event_type":"obra_vial","subtipo":"corte_parcial",    "severidad":1,"event_date":"2024-04-10","latitude":-38.55,"longitude":-68.00},
    {"corridor_id":3,"event_type":"obra_vial","subtipo":"corte_total",      "severidad":1,"event_date":"2024-12-05","latitude":-38.35,"longitude":-67.70},
    {"corridor_id":3,"event_type":"congestion","subtipo":"trafico_pesado",  "severidad":2,"event_date":"2023-09-06","latitude":-38.65,"longitude":-68.18},
    {"corridor_id":3,"event_type":"protesta","subtipo":"bloqueo_sindical",  "severidad":4,"event_date":"2024-02-28","latitude":-38.45,"longitude":-67.88},
    {"corridor_id":3,"event_type":"protesta","subtipo":"comunidad_mapuche", "severidad":4,"event_date":"2025-05-16","latitude":-38.25,"longitude":-67.58},
]

# Crear GeoDataFrame
df = pd.DataFrame(eventos)
df.insert(0, "event_id", range(1, len(df) + 1))
df["event_date"] = pd.to_datetime(df["event_date"])
df["geometry"] = df.apply(lambda r: Point(r["longitude"], r["latitude"]), axis=1)

gdf = gpd.GeoDataFrame(df, crs="EPSG:4326")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
gdf.to_file(OUTPUT, driver="GeoJSON")
print(f"✓ Dataset sintético guardado: {len(gdf)} eventos")
print(f"\nDistribución por corredor:")
print(gdf.groupby("corridor_id").size().reset_index(name="eventos"))
print(f"\nDistribución por tipo:")
print(gdf.groupby(["event_type","subtipo"]).size().reset_index(name="total"))