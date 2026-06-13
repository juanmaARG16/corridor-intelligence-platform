import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from base_sensor import BaseSensor
from event_normalizer import normalize_and_save

SMN_URL = "https://ws.smn.gob.ar/map_items/weather"

ESTACIONES_NEUQUEN = [
    "Neuquén", "Cutral Co", "Zapala",
    "Cipolletti", "General Roca",
    "Villa La Angostura", "Chapelco",
    "San Martín de Los Andes"
]

KEYWORDS = {
    "nevada":          ("clima", "nevada",          "ALTO"),
    "tormenta":        ("clima", "tormenta",         "ALTO"),
    "granizo":         ("clima", "granizo",          "ALTO"),
    "niebla":          ("clima", "niebla",           "ALTO"),
    "neblina":         ("clima", "niebla",           "MEDIO"),
    "lluvia":          ("clima", "lluvia",           "MEDIO"),
    "llovizna":        ("clima", "lluvia",           "MEDIO"),
    "ventisca":        ("clima", "viento_extremo",   "ALTO"),
}

class SMNSensor(BaseSensor):

    def __init__(self):
        super().__init__(source_name="SMN", confidence=0.95)

    def collect(self):
        response = requests.get(SMN_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [
            s for s in data
            if s.get("name") in ESTACIONES_NEUQUEN
            or s.get("province") == "Neuquén"
        ]

    def normalize(self, raw_data):
        eventos = []
        for estacion in raw_data:
            w           = estacion.get("weather", {})
            nombre      = estacion.get("name")
            lat         = float(estacion.get("lat", 0))
            lon         = float(estacion.get("lon", 0))
            descripcion = w.get("description", "").lower()
            viento      = w.get("wind_speed")
            visibilidad = w.get("visibility")

            # Detección por umbrales
            if viento and viento > 90:
                eventos.append(self.create_event(
                    "clima", "viento_extremo", "ALTO", lat, lon,
                    raw_data={"estacion": nombre, "wind_speed": viento}
                ))
            elif viento and viento > 60:
                eventos.append(self.create_event(
                    "clima", "viento_fuerte", "MEDIO", lat, lon,
                    raw_data={"estacion": nombre, "wind_speed": viento}
                ))

            if visibilidad and visibilidad < 2:
                eventos.append(self.create_event(
                    "clima", "niebla", "ALTO", lat, lon,
                    raw_data={"estacion": nombre, "visibility": visibilidad}
                ))
            elif visibilidad and visibilidad < 5:
                eventos.append(self.create_event(
                    "clima", "baja_visibilidad", "MEDIO", lat, lon,
                    raw_data={"estacion": nombre, "visibility": visibilidad}
                ))

            # Detección por descripción
            for keyword, (event_type, subtype, severity) in KEYWORDS.items():
                if keyword in descripcion:
                    eventos.append(self.create_event(
                        event_type, subtype, severity, lat, lon,
                        raw_data={"estacion": nombre, "description": descripcion}
                    ))
                    break

        return eventos


if __name__ == "__main__":
    sensor = SMNSensor()
    eventos = sensor.run()
    saved = normalize_and_save(eventos)
    print(f"✓ SMN Sensor completado — {saved} eventos nuevos en events_v3")