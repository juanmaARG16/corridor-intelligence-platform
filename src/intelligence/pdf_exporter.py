from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
from pathlib import Path
from datetime import datetime
import geopandas as gpd
import sys
import os

sys.path.append(str(Path(__file__).parent))
from recommendation_engine import get_recomendacion, get_impacto_potencial

BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
INPUT  = BASE / "data/processed/events_v2.geojson"
OUTPUT = BASE / "data/briefs"

# Colores por nivel de riesgo
RISK_COLORS = {
    "ALTO":  colors.HexColor("#e74c3c"),
    "MEDIO": colors.HexColor("#f39c12"),
    "BAJO":  colors.HexColor("#27ae60"),
}

def generate_brief(event, brief_number):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    filename = OUTPUT / f"risk_brief_{brief_number:03d}.pdf"

    doc = SimpleDocTemplate(
        str(filename),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # Header
    header_style = ParagraphStyle(
        "header",
        parent=styles["Normal"],
        fontSize=20,
        textColor=colors.HexColor("#1a334a"),
        spaceAfter=5,
        fontName="Helvetica-Bold"
    )
    sub_style = ParagraphStyle(
        "sub",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20
    )

    elements.append(Paragraph(f"RISK BRIEF #{brief_number:03d}", header_style))
    elements.append(Paragraph(
        f"Corridor Intelligence Platform — {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        sub_style
    ))

    # Tabla principal
    risk_color = RISK_COLORS.get(event["risk_level"], colors.grey)
    fecha = str(event["event_date"])[:10]

    data = [
        ["Campo", "Detalle"],
        ["Fecha", fecha],
        ["Corredor", event["corredor"]],
        ["Tipo de Evento", event["event_type"].capitalize()],
        ["Subtipo", event["subtipo"].replace("_", " ").capitalize()],
        ["Severidad", event["severidad_cat"]],
        ["Score de Riesgo", f"{event['score_v2']:.3f}"],
        ["Nivel de Riesgo", event["risk_level"]],
    ]

    table = Table(data, colWidths=[5*cm, 12*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1a334a")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 11),
        ("BACKGROUND",  (0, 7), (-1, 7), risk_color),
        ("TEXTCOLOR",   (0, 7), (-1, 7), colors.white),
        ("FONTNAME",    (0, 7), (-1, 7), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("FONTSIZE",    (0, 1), (-1, -1), 10),
        ("PADDING",     (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))

    # Impacto potencial
    section_style = ParagraphStyle(
        "section",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#1a334a"),
        fontName="Helvetica-Bold",
        spaceBefore=15,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=10,
        leading=14
    )

    impacto = get_impacto_potencial(event["event_type"], event["subtipo"])
    recomendacion = get_recomendacion(event["event_type"], event["subtipo"], event["risk_level"])

    elements.append(Paragraph("IMPACTO POTENCIAL", section_style))
    elements.append(Paragraph(impacto, body_style))

    elements.append(Paragraph("RECOMENDACIÓN OPERATIVA", section_style))
    elements.append(Paragraph(recomendacion, body_style))

    # Footer
    footer_style = ParagraphStyle(
        "footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
        spaceBefore=30
    )
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph(
        "Este informe fue generado automáticamente por Corridor Intelligence Platform. "
        "La información es de carácter operativo y confidencial.",
        footer_style
    ))

    doc.build(elements)
    return filename


if __name__ == "__main__":
    gdf = gpd.read_file(INPUT)

    # Generar briefs para los 5 eventos de mayor riesgo
    top_events = gdf.sort_values("score_v2", ascending=False).head(5)

    print("── Generando Risk Briefs ─────────────────────────────")
    for i, (_, event) in enumerate(top_events.iterrows(), 1):
        path = generate_brief(event, i)
        print(f"✓ risk_brief_{i:03d}.pdf — {event['corredor']} | {event['subtipo']} | {event['risk_level']}")

    print(f"\n✓ Briefs guardados en: {OUTPUT}")