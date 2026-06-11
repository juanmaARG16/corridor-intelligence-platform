import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

engine = create_engine("postgresql://postgres@localhost:5432/cip_db")

BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
PATH_SYNTHETIC = BASE / "data/synthetic/synthetic_corridor_events.geojson"

# Cargar dataset sintético
events = gpd.read_file(PATH_SYNTHETIC)

# ── Métricas por corredor ─────────────────────────────────────────────────
metrics = events.groupby("corridor_id").agg(
    cantidad_eventos=("event_id", "count"),
    suma_severidad=("severidad", "sum")
).reset_index()

# ── Fórmula de riesgo ─────────────────────────────────────────────────────
# Normalizar entre 0 y 100
max_eventos   = metrics["cantidad_eventos"].max()
max_severidad = metrics["suma_severidad"].max()

metrics["score_eventos"]   = (metrics["cantidad_eventos"] / max_eventos) * 100
metrics["score_severidad"] = (metrics["suma_severidad"]   / max_severidad) * 100

# Score final
metrics["score"] = (
    0.6 * metrics["score_eventos"] +
    0.4 * metrics["score_severidad"]
).round(1)

# ── Clasificación ─────────────────────────────────────────────────────────
def classify(score):
    if score <= 30:
        return "BAJO"
    elif score <= 60:
        return "MEDIO"
    else:
        return "ALTO"

metrics["risk_level"] = metrics["score"].apply(classify)
metrics["created_at"] = pd.Timestamp.now()

# ── Nombres de corredores ─────────────────────────────────────────────────
nombres = {1: "Neuquén-Añelo", 2: "Añelo-Rincón", 3: "Neuquén-Catriel"}
metrics["corridor_name"] = metrics["corridor_id"].map(nombres)

# ── Guardar en PostGIS ────────────────────────────────────────────────────
risk_scores = metrics[[
    "corridor_id", "corridor_name",
    "cantidad_eventos", "suma_severidad",
    "score", "risk_level", "created_at"
]].copy()
risk_scores.insert(0, "id", range(1, len(risk_scores) + 1))

risk_scores.to_sql("risk_scores", engine, if_exists="replace", index=False)
print("✓ Tabla risk_scores cargada en PostGIS")

# ── Ranking ejecutivo ─────────────────────────────────────────────────────
print("\n── Ranking de Riesgo Operacional ────────────────────────────────")
print(f"{'Corredor':<25} {'Eventos':>8} {'Score':>7} {'Riesgo':>8}")
print("─" * 52)
for _, row in risk_scores.sort_values("score", ascending=False).iterrows():
    print(f"{row['corridor_name']:<25} {row['cantidad_eventos']:>8} {row['score']:>7} {row['risk_level']:>8}")