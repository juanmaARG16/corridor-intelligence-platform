import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent))
from impact_rules import get_impact_rule

engine = create_engine("postgresql://postgres@localhost:5432/cip_db")

CORREDOR_MAP = {1: "Neuquén-Añelo", 2: "Añelo-Rincón", 3: "Neuquén-Catriel"}

SEVERITY_ORDER = {"BAJO": 1, "MEDIO": 2, "ALTO": 3, "CRÍTICO": 4}

def calculate_impacts():
    # Leer alertas de PostGIS
    try:
        alerts = pd.read_sql("SELECT * FROM alerts", engine)
    except Exception as e:
        print(f"Error leyendo alerts: {e}")
        return

    if len(alerts) == 0:
        print("Sin alertas para procesar.")
        return

    print(f"Procesando {len(alerts)} alertas...")

    impacts = []
    for _, alert in alerts.iterrows():
        rule = get_impact_rule(alert["event_type"], alert["subtipo"])

        impacts.append({
            "event_id":       int(alert["id"]),
            "corridor_id":    int(alert["corridor_id"]),
            "corridor_name":  CORREDOR_MAP.get(int(alert["corridor_id"]), "Desconocido"),
            "estacion":       alert["estacion"],
            "event_type":     alert["event_type"],
            "subtipo":        alert["subtipo"],
            "impact_type":    rule["impact_type"],
            "severity":       rule["severity"],
            "severity_order": SEVERITY_ORDER.get(rule["severity"], 0),
            "recommendation": rule["recommendation"],
            "duration_hs":    rule["duration_hs"],
            "created_at":     datetime.now(),
        })

    df = pd.DataFrame(impacts)

    # Guardar en PostGIS
    df.to_sql("operational_impacts", engine, if_exists="replace", index=False)
    print(f"✓ Tabla operational_impacts cargada: {len(df)} filas")

    # Resumen por corredor
    print("\n── Impactos por corredor ─────────────────────────────")
    resumen = df.groupby(["corridor_name", "severity"]).size().reset_index(name="total")
    for _, row in resumen.iterrows():
        print(f"  {row['corridor_name']:<25} {row['severity']:<10} {row['total']} evento(s)")

    # Corredor más expuesto
    print("\n── Corredor más expuesto ─────────────────────────────")
    exposicion = df.groupby("corridor_name")["severity_order"].sum().reset_index()
    exposicion = exposicion.sort_values("severity_order", ascending=False)
    top = exposicion.iloc[0]
    print(f"  {top['corridor_name']} — Score de exposición: {top['severity_order']}")

    return df

if __name__ == "__main__":
    calculate_impacts()