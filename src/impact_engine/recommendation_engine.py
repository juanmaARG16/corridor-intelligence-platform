import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent))
from impact_rules import get_impact_rule, SEVERITY_ORDER

engine = create_engine("postgresql://postgres@localhost:5432/cip_db")

CORREDOR_MAP = {1: "Neuquén-Añelo", 2: "Añelo-Rincón", 3: "Neuquén-Catriel"}

def generate_operational_brief():
    try:
        impacts = pd.read_sql("SELECT * FROM operational_impacts", engine)
    except Exception as e:
        print(f"Error leyendo operational_impacts: {e}")
        return

    print(f"Filas leídas: {len(impacts)}")

    if len(impacts) == 0:
        print("Sin impactos para procesar.")
        return

    print("═" * 55)
    print("  OPERATIONAL IMPACT BRIEF")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("═" * 55)

    corredores = impacts["corridor_name"].unique()

    for corredor in sorted(corredores):
        df_c = impacts[impacts["corridor_name"] == corredor]
        max_sev_order = df_c["severity_order"].max()
        max_sev = {v: k for k, v in SEVERITY_ORDER.items()}.get(max_sev_order, "BAJO")
        eventos_unicos = df_c[["subtipo", "impact_type",
                                "recommendation", "duration_hs"]].drop_duplicates()

        print(f"\n{'─' * 55}")
        print(f"  CORREDOR : {corredor}")
        print(f"  ESTADO   : {max_sev}")
        print(f"  EVENTOS  : {len(df_c)}")
        print(f"{'─' * 55}")

        for _, row in eventos_unicos.iterrows():
            print(f"\n  Evento      : {row['subtipo'].replace('_', ' ').upper()}")
            print(f"  Impacto     : {row['impact_type']}")
            print(f"  Duración    : {row['duration_hs']}")
            print(f"  Recomend.   : {row['recommendation']}")

    print(f"\n{'═' * 55}")
    print("  RESUMEN EJECUTIVO")
    print(f"{'═' * 55}")

    exposicion = impacts.groupby("corridor_name")["severity_order"].sum()
    top_corredor = exposicion.idxmax()
    print(f"\n  Corredor más expuesto : {top_corredor}")
    print(f"  Total impactos activos: {len(impacts)}")

    dist = impacts["severity"].value_counts()
    print(f"\n  Distribución:")
    for nivel, total in dist.items():
        print(f"    {nivel:<10} {total} impacto(s)")

    print(f"\n  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'═' * 55}")


if __name__ == "__main__":
    generate_operational_brief()