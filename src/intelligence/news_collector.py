import requests
import json
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
OUTPUT = BASE / "data/raw/news"

# Estaciones relevantes para los corredores de Neuquén
ESTACIONES_NEUQUEN = [
    "Neuquén",
    "Cutral Co",
    "Zapala",
    "Cipolletti",
    "General Roca"
]

SMN_URL = "https://ws.smn.gob.ar/map_items/weather"

def fetch_smn_data():
    print("Conectando con SMN...")
    response = requests.get(SMN_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    print(f"✓ {len(data)} estaciones recibidas")
    return data

def filter_neuquen(data):
    estaciones = [
        s for s in data
        if s.get("name") in ESTACIONES_NEUQUEN
        or s.get("province") == "Neuquén"
    ]
    print(f"✓ {len(estaciones)} estaciones de Neuquén encontradas")
    return estaciones

def save_raw(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = OUTPUT / f"smn_{timestamp}.json"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Datos guardados: {output_file}")
    return output_file

def display_conditions(estaciones):
    print("\n── Condiciones actuales en zona de corredores ───────")
    for e in estaciones:
        w = e.get("weather", {})
        print(f"\n{e['name']} ({e['province']})")
        print(f"  Temperatura : {w.get('temp')} °C")
        print(f"  Viento      : {w.get('wind_speed')} km/h {w.get('wing_deg')}")
        print(f"  Visibilidad : {w.get('visibility')} km")
        print(f"  Estado      : {w.get('description')}")

if __name__ == "__main__":
    data       = fetch_smn_data()
    estaciones = filter_neuquen(data)
    save_raw(estaciones)
    display_conditions(estaciones)