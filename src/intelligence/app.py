import streamlit as st
import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys
import os

sys.path.append(str(Path(__file__).parent))
from pdf_exporter import generate_brief
from recommendation_engine import get_recomendacion, get_impacto_potencial

BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
INPUT = BASE / "data/processed/events_v2.geojson"

# ── Config ────────────────────────────────────────────
st.set_page_config(
    page_title="Corridor Intelligence Platform",
    page_icon="🛣️",
    layout="wide"
)

# ── Cargar datos ──────────────────────────────────────
@st.cache_data
def load_data():
    gdf = gpd.read_file(INPUT)
    gdf["event_date"] = pd.to_datetime(gdf["event_date"]).dt.date
    return gdf

gdf = load_data()

# ── Header ────────────────────────────────────────────
st.title("🛣️ Corridor Intelligence Platform")
st.caption("Risk Brief Generator — Misión 05")

# ── Métricas generales ────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Eventos", len(gdf))
col2.metric("Eventos ALTO", len(gdf[gdf["risk_level"] == "ALTO"]))
col3.metric("Eventos MEDIO", len(gdf[gdf["risk_level"] == "MEDIO"]))
col4.metric("Eventos BAJO", len(gdf[gdf["risk_level"] == "BAJO"]))

st.divider()

# ── Filtros ───────────────────────────────────────────
st.subheader("🔍 Filtros")
col_a, col_b, col_c = st.columns(3)

with col_a:
    corredor_sel = st.selectbox(
        "Corredor",
        ["Todos"] + sorted(gdf["corredor"].unique().tolist())
    )
with col_b:
    riesgo_sel = st.selectbox(
        "Nivel de Riesgo",
        ["Todos", "ALTO", "MEDIO", "BAJO"]
    )
with col_c:
    tipo_sel = st.selectbox(
        "Tipo de Evento",
        ["Todos"] + sorted(gdf["event_type"].unique().tolist())
    )

# Aplicar filtros
df_filtered = gdf.copy()
if corredor_sel != "Todos":
    df_filtered = df_filtered[df_filtered["corredor"] == corredor_sel]
if riesgo_sel != "Todos":
    df_filtered = df_filtered[df_filtered["risk_level"] == riesgo_sel]
if tipo_sel != "Todos":
    df_filtered = df_filtered[df_filtered["event_type"] == tipo_sel]

st.divider()

# ── Tabla de eventos ──────────────────────────────────
st.subheader(f"📋 Eventos ({len(df_filtered)})")

display_cols = ["event_id", "event_date", "corredor", "event_type",
                "subtipo", "severidad_cat", "score_v2", "risk_level"]

def color_risk(val):
    colors = {"ALTO": "#e74c3c", "MEDIO": "#f39c12", "BAJO": "#27ae60"}
    color = colors.get(val, "white")
    return f"background-color: {color}; color: white; font-weight: bold"

st.dataframe(
    df_filtered[display_cols].style.map(color_risk, subset=["risk_level"]),
    use_container_width=True,
    height=300
)

st.divider()

# ── Generador de Risk Brief ───────────────────────────
st.subheader("🧠 Generador de Risk Brief")

event_options = df_filtered.apply(
    lambda r: f"#{r['event_id']} — {r['corredor']} | {r['subtipo']} | {r['risk_level']}",
    axis=1
).tolist()

if len(event_options) == 0:
    st.warning("No hay eventos con los filtros seleccionados.")
else:
    selected = st.selectbox("Seleccioná un evento", event_options)
    event_id = int(selected.split("#")[1].split("—")[0].strip())
    event = gdf[gdf["event_id"] == event_id].iloc[0]

    # Preview del brief
    col_prev, col_btn = st.columns([3, 1])

    with col_prev:
        risk_colors = {"ALTO": "🔴", "MEDIO": "🟡", "BAJO": "🟢"}
        st.markdown(f"""
        **RISK BRIEF PREVIEW**
        | Campo | Detalle |
        |-------|---------|
        | Corredor | {event['corredor']} |
        | Fecha | {event['event_date']} |
        | Tipo | {event['event_type'].capitalize()} |
        | Subtipo | {event['subtipo'].replace('_', ' ').capitalize()} |
        | Severidad | {event['severidad_cat']} |
        | Score | {event['score_v2']:.3f} |
        | Riesgo | {risk_colors[event['risk_level']]} {event['risk_level']} |

        **Impacto:** {get_impacto_potencial(event['event_type'], event['subtipo'])}

        **Recomendación:** {get_recomendacion(event['event_type'], event['subtipo'], event['risk_level'])}
        """)

    with col_btn:
        st.write("")
        st.write("")
        if st.button("📄 Generar PDF", use_container_width=True):
            with st.spinner("Generando brief..."):
                brief_num = event_id
                pdf_path = generate_brief(event, brief_num)
            st.success("✓ Brief generado")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=f,
                    file_name=f"risk_brief_{brief_num:03d}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )