import requests
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from base_sensor import BaseSensor
from event_normalizer import normalize_and_save

# Términos de búsqueda relevantes para los corredores
KEYWORDS = [
    "Vaca Muerta", "Añelo", "Neuquén ruta",
    "Rincón de los Sauces", "corte ruta Neuquén",
    "bloqueo Neuquén", "accidente ruta 7 Neuquén",
    "protesta Neuquén", "logística Neuquén"
]

# Clasificación de eventos por palabras clave en título
EVENT_CLASSIFIER = {
    "accidente":  ("accidente", "incidente_vial",    "MEDIO"),
    "choque":     ("accidente", "colision",           "MEDIO"),
    "volcó":      ("accidente", "camion_volcado",     "MEDIO"),
    "corte":      ("protesta",  "corte_ruta",         "ALTO"),
    "bloqueo":    ("protesta",  "bloqueo",            "ALTO"),
    "protesta":   ("protesta",  "manifestacion",      "MEDIO"),
    "paro":       ("protesta",  "paro_sindical",      "ALTO"),
    "huelga":     ("protesta",  "huelga",             "ALTO"),
    "incendio":   ("incendio",  "incendio_vial",      "ALTO"),
    "nevada":     ("clima",     "nevada",             "ALTO"),
    "tormenta":   ("clima",     "tormenta",           "ALTO"),
    "inundación": ("clima",     "inundacion",         "ALTO"),
}

# Coordenadas por defecto para noticias sin geocoding
COORDS_NEUQUEN = {"lat": -38.9543, "lon": -68.0751}

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

class GDELTSensor(BaseSensor):

    def __init__(self):
        super().__init__(source_name="GDELT", confidence=0.70)

    def collect(self):
        all_articles = []
        for keyword in KEYWORDS[:3]:
            try:
                params = {
                    "query":      f'"{keyword}"',
                    "mode":       "artlist",
                    "maxrecords": 10,
                    "format":     "json",
                    "sourcelang": "spanish",
                    "timespan":   "24h",
                }
                response = requests.get(GDELT_URL, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    print(f"  '{keyword}' → {len(articles)} artículos")
                    all_articles.extend(articles)
                elif response.status_code == 429:
                    print(f"  Rate limit alcanzado. Esperando...")
                time.sleep(6)
            except Exception as e:
                print(f"  Error buscando '{keyword}': {e}")

        # Deduplicar por URL
        seen = set()
        unique = []
        for a in all_articles:
            url = a.get("url", "")
            if url not in seen:
                seen.add(url)
                unique.append(a)

        print(f"  Total únicos: {len(unique)} artículos")
        return unique

    def normalize(self, raw_data):
        eventos = []
        for article in raw_data:
            title = article.get("title", "").lower()
            url   = article.get("url", "")
            date  = article.get("seendate", "")

            event_type = "informacion"
            subtype    = "noticia_general"
            severity   = "BAJO"

            for keyword, (et, st, sev) in EVENT_CLASSIFIER.items():
                if keyword in title:
                    event_type = et
                    subtype    = st
                    severity   = sev
                    break

            eventos.append(self.create_event(
                event_type, subtype, severity,
                COORDS_NEUQUEN["lat"],
                COORDS_NEUQUEN["lon"],
                raw_data={
                    "title":  article.get("title"),
                    "url":    url,
                    "source": article.get("domain"),
                    "date":   date,
                }
            ))

        return eventos


if __name__ == "__main__":
    sensor = GDELTSensor()
    eventos = sensor.run()

    if eventos:
        saved = normalize_and_save(eventos)
        print(f"✓ GDELT Sensor completado — {saved} eventos nuevos en events_v3")
        print("\nTítulos capturados:")
        for e in eventos[:5]:
            import json
            raw = json.loads(e["raw_data"])
            print(f"  [{e['subtype']}] {raw.get('title', 'Sin título')[:80]}")
    else:
        print("✓ GDELT Sensor completado — Sin artículos relevantes")