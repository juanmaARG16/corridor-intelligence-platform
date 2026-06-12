import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from sqlalchemy import create_engine
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent))
from news_collector import fetch_smn_data, filter_neuquen, save_raw
from event_extractor import procesar_archivo
from geocoder import enriquecer_eventos

BASE   = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
engine = create_engine("postgresql://postgres@localhost:5432/cip_db")

def run_pipeline():
    print("═" * 55)
    print("  CORRIDOR INTELLIGENCE PLATFORM — PIPELINE SMN")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("═" * 55)

    # Paso 1 — Captura
    print("\n[1/5] Capturando datos SMN...")
    data       = fetch_smn_data()
    estaciones = filter_neuquen(data)
    raw_file   = save_raw(estaciones)

    # Paso 2 — Extracción de eventos
    print("\n[2/5] Extrayendo eventos...")
    eventos = procesar_archivo(raw_file)
    print(f"  {len(eventos)} eventos detectados")

    if not eventos:
        print("\n  Sin eventos críticos. Pipeline finalizado.")
        return

    # Paso 3 — Geocoding
    print("\n[3/5] Geocodificando eventos...")
    eventos = enriquecer_eventos(eventos)
    geocoded = sum(1 for e in eventos if e["geocoded"])
    print(f"  {geocoded}/{len(eventos)} eventos geocodificados")

    # Paso 4 — Cruce con corredores
    print("\n[4/5] Cruzando con corredores...")
    buf10 = gpd.read_file(BASE / "data/processed/buffers/Buffer__10km.geojson")
    buf10.columns = buf10.columns.str.lower()

    df = pd.DataFrame(eventos)
    df["geometry"] = df.apply(lambda r: Point(r["longitude"], r["latitude"]), axis=1)
    gdf_eventos = gpd.GeoDataFrame(df, crs="EPSG:4326")

    matches = gpd.sjoin(gdf_eventos, buf10, how="left", predicate="intersects")
    matches["corridor_id"] = matches["id"].fillna(0).astype(int)

    afectados = matches[matches["corridor_id"] > 0]
    print(f"  {len(afectados)} eventos dentro de corredores")

    # Paso 5 — Guardar en PostGIS
    print("\n[5/5] Guardando en PostGIS...")

    # Tabla eventos_raw
    eventos_df = matches[[
        "source", "confiabilidad", "estacion",
        "event_type", "subtipo", "severidad",
        "event_date", "timestamp", "latitude",
        "longitude", "corridor_id"
    ]].copy()
    eventos_df.insert(0, "id", range(1, len(eventos_df) + 1))
    eventos_df.to_sql("eventos_raw", engine, if_exists="replace", index=False)
    print(f"  ✓ eventos_raw: {len(eventos_df)} filas")

    # Tabla alertas
    if len(afectados) > 0:
        alertas = afectados[afectados["corridor_id"] > 0][[
            "estacion", "event_type", "subtipo",
            "severidad", "corridor_id", "timestamp"
        ]].copy()
        alertas.insert(0, "id", range(1, len(alertas) + 1))
        alertas["created_at"] = datetime.now()
        alertas.to_sql("alerts", engine, if_exists="replace", index=False)
        print(f"  ✓ alerts: {len(alertas)} alertas generadas")

    # Resumen final
    print("\n── Resumen del Pipeline ──────────────────────────────")
    corredor_map = {1: "Neuquén-Añelo", 2: "Añelo-Rincón", 3: "Neuquén-Catriel"}
    if len(afectados) > 0:
        for _, row in afectados.iterrows():
            corredor = corredor_map.get(int(row["corridor_id"]), "Desconocido")
            print(f"  ⚠ {row['estacion']} → {corredor} | {row['subtipo']} | Sev. {row['severidad']}")
    else:
        print("  Sin eventos dentro de corredores en este momento.")

    print("\n✓ Pipeline completado")

if __name__ == "__main__":
    run_pipeline()