import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine

sys.path.append(str(Path(__file__).parent))
from smn_sensor import SMNSensor
from firms_sensor import FIRMSSensor
from gdelt_sensor import GDELTSensor
from event_normalizer import normalize_and_save, get_recent_events

engine = create_engine("postgresql://postgres@localhost:5432/cip_db")

CORREDOR_MAP = {1: "Neuquén-Añelo", 2: "Añelo-Rincón", 3: "Neuquén-Catriel"}

SEVERITY_ORDER = {"BAJO": 1, "MEDIO": 2, "ALTO": 3, "CRÍTICO": 4}

def run_all_sensors():
    print("═" * 55)
    print("  CORRIDOR INTELLIGENCE PLATFORM")
    print("  MULTI-SENSOR FUSION ENGINE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("═" * 55)

    all_events = []

    # SMN
    try:
        smn = SMNSensor()
        events = smn.run()
        saved = normalize_and_save(events)
        all_events.extend(events)
    except Exception as e:
        print(f"[SMN] Error: {e}")

    # NASA FIRMS
    try:
        firms = FIRMSSensor()
        events = firms.run()
        if events:
            saved = normalize_and_save(events)
            all_events.extend(events)
    except Exception as e:
        print(f"[FIRMS] Error: {e}")

    # GDELT
    try:
        gdelt = GDELTSensor()
        events = gdelt.run()
        if events:
            saved = normalize_and_save(events)
            all_events.extend(events)
    except Exception as e:
        print(f"[GDELT] Error: {e}")

    return all_events

def spatial_matching(events):
    """Cruza eventos con corredores usando buffers."""
    import geopandas as gpd
    from shapely.geometry import Point

    if not events:
        return pd.DataFrame()

    BASE   = Path(__file__).parent.parent.parent
    buf10  = gpd.read_file(BASE / "data/processed/buffers/Buffer__10km.geojson")
    buf10.columns = buf10.columns.str.lower()

    df = pd.DataFrame(events)
    df["geometry"] = df.apply(
        lambda r: Point(r["longitude"], r["latitude"]), axis=1
    )
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326")

    matches = gpd.sjoin(gdf, buf10, how="left", predicate="intersects")
    matches["corridor_id"] = matches["id"].fillna(0).astype(int)

    afectados = matches[matches["corridor_id"] > 0].copy()
    print(f"\n✓ Spatial Matching — {len(afectados)} eventos dentro de corredores")
    return afectados

def generate_consolidated_brief(afectados):
    """Genera el briefing ejecutivo consolidado."""
    print("\n" + "═" * 55)
    print("  OPERATIONAL INTELLIGENCE BRIEF")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("═" * 55)

    if len(afectados) == 0:
        print("\n  Sin eventos activos en corredores.")
        return

    for corridor_id, nombre in CORREDOR_MAP.items():
        df_c = afectados[afectados["corridor_id"] == corridor_id]
        if len(df_c) == 0:
            continue

        # Severidad máxima
        severidades = df_c["severity"].map(SEVERITY_ORDER).fillna(0)
        max_sev_num = severidades.max()
        max_sev = {v: k for k, v in SEVERITY_ORDER.items()}.get(
            int(max_sev_num), "BAJO"
        )

        print(f"\n{'─' * 55}")
        print(f"  CORREDOR : {nombre}")
        print(f"  ESTADO   : {max_sev}")
        print(f"  EVENTOS  : {len(df_c)}")
        print(f"{'─' * 55}")

        for source in df_c["source"].unique():
            df_s = df_c[df_c["source"] == source]
            print(f"\n  [{source}]")
            for _, row in df_s.iterrows():
                print(f"    • {row['subtype'].replace('_', ' ').upper()}"
                      f" — Severidad: {row['severity']}")

    print(f"\n{'═' * 55}")
    print("  RESUMEN")
    print(f"{'═' * 55}")
    print(f"  Total eventos en corredores : {len(afectados)}")
    print(f"  Fuentes activas             : {', '.join(afectados['source'].unique())}")
    print(f"  Generado                    : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'═' * 55}")


if __name__ == "__main__":
    # 1 — Correr todos los sensores
    all_events = run_all_sensors()

    # 2 — Spatial matching
    afectados = spatial_matching(all_events)

    # 3 — Brief consolidado
    generate_consolidated_brief(afectados)