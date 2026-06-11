import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
INPUT  = BASE / "data/synthetic/synthetic_corridor_events.geojson"
OUTPUT = BASE / "data/processed/events_v2.geojson"

# Mapeo de severidad numérica a categórica
severidad_map = {1: "Baja", 2: "Media", 3: "Alta", 4: "Crítica"}

# Probabilidad por tipo de evento — basada en frecuencia histórica plausible
probabilidad_map = {
    "protesta":   0.85,
    "accidente":  0.75,
    "clima":      0.70,
    "congestion": 0.60,
    "obra_vial":  0.90,
}

# Impacto por subtipo — qué tan grave es operacionalmente
impacto_map = {
    "bloqueo_sindical":   0.90,
    "comunidad_mapuche":  0.90,
    "camion_volcado":     0.75,
    "colision_multiple":  0.80,
    "nevada":             0.85,
    "alud":               0.95,
    "inundacion":         0.90,
    "viento_fuerte":      0.50,
    "lluvia":             0.40,
    "trafico_pesado":     0.55,
    "corte_parcial":      0.45,
    "corte_total":        0.70,
}

# Nombres de corredores
corredor_map = {1: "Neuquén-Añelo", 2: "Añelo-Rincón", 3: "Neuquén-Catriel"}

# Cargar dataset sintético
gdf = gpd.read_file(INPUT)

# Estandarizar campos
gdf["corredor"]     = gdf["corridor_id"].map(corredor_map)
gdf["severidad_cat"]= gdf["severidad"].map(severidad_map)
gdf["probabilidad"] = gdf["event_type"].map(probabilidad_map)
gdf["impacto"]      = gdf["subtipo"].map(impacto_map)
gdf["severidad_norm"]= gdf["severidad"] / 4  # normalizar entre 0 y 1

# Score V2
gdf["score_v2"] = (
    gdf["probabilidad"] * gdf["impacto"] * gdf["severidad_norm"]
).round(3)

# Clasificación
def classify(score):
    if score <= 0.30:
        return "BAJO"
    elif score <= 0.60:
        return "MEDIO"
    else:
        return "ALTO"

gdf["risk_level"] = gdf["score_v2"].apply(classify)

# Seleccionar campos finales
gdf_final = gdf[[
    "event_id", "event_date", "corredor", "corridor_id",
    "event_type", "subtipo", "severidad_cat",
    "probabilidad", "impacto", "severidad_norm",
    "score_v2", "risk_level", "geometry"
]]

# Guardar
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
gdf_final.to_file(OUTPUT, driver="GeoJSON")
print(f"✓ Dataset estandarizado guardado: {len(gdf_final)} eventos")
print(f"\nDistribución por nivel de riesgo:")
print(gdf_final["risk_level"].value_counts())
print(f"\nScore promedio por corredor:")
print(gdf_final.groupby("corredor")["score_v2"].mean().round(3))