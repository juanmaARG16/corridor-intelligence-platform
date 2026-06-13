import requests
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from base_sensor import BaseSensor
from event_normalizer import normalize_and_save

# Bounding box de Neuquén y zona de corredores
# min_lon, min_lat, max_lon, max_lat
BBOX_NEUQUEN = "-71.0,-40.0,-66.0,-36.0"

FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

class FIRMSSensor(BaseSensor):

    def __init__(self):
        super().__init__(source_name="NASA_FIRMS", confidence=0.90)
        self.api_key = os.getenv("FIRMS_API_KEY", "28dde09dbd7d08bfcd8bb929ba49c4cc")

    def collect(self):
        # VIIRS S-NPP — últimas 24 horas
        url = f"{FIRMS_URL}/{self.api_key}/VIIRS_SNPP_NRT/{BBOX_NEUQUEN}/1"
        print(f"  Consultando NASA FIRMS...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        # Parsear CSV
        lines = response.text.strip().split("\n")
        if len(lines) <= 1:
            print("  Sin focos térmicos detectados en la zona.")
            return []

        headers = lines[0].split(",")
        records = []
        for line in lines[1:]:
            values = line.split(",")
            if len(values) == len(headers):
                records.append(dict(zip(headers, values)))

        print(f"  {len(records)} focos térmicos recibidos")
        return records

    def normalize(self, raw_data):
        eventos = []
        for record in raw_data:
            try:
                lat  = float(record.get("latitude",  0))
                lon  = float(record.get("longitude", 0))
                frp  = float(record.get("frp", 0))  # Fire Radiative Power
                conf = record.get("confidence", "n")

                # Clasificar severidad por FRP (Fire Radiative Power en MW)
                if frp > 100:
                    severity = "CRÍTICO"
                    subtype  = "incendio_mayor"
                elif frp > 30:
                    severity = "ALTO"
                    subtype  = "incendio"
                else:
                    severity = "MEDIO"
                    subtype  = "foco_termico"

                # Solo procesar focos con confianza nominal o alta
                if conf.lower() in ["n", "h", "nominal", "high"]:
                    eventos.append(self.create_event(
                        "incendio", subtype, severity, lat, lon,
                        raw_data={
                            "frp":        frp,
                            "confidence": conf,
                            "acq_date":   record.get("acq_date"),
                            "acq_time":   record.get("acq_time"),
                        }
                    ))
            except Exception as e:
                continue

        return eventos


if __name__ == "__main__":
    sensor = FIRMSSensor()
    eventos = sensor.run()

    if eventos:
        saved = normalize_and_save(eventos)
        print(f"✓ FIRMS Sensor completado — {saved} eventos nuevos en events_v3")
    else:
        print("✓ FIRMS Sensor completado — Sin focos térmicos en zona de corredores")