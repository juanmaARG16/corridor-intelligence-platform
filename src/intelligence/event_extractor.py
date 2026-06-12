import json
from pathlib import Path
from datetime import datetime

# Umbrales para generar eventos
UMBRALES = {
    "viento_fuerte":  {"campo": "wind_speed", "operador": ">",  "valor": 60},
    "viento_extremo": {"campo": "wind_speed", "operador": ">",  "valor": 90},
    "niebla":         {"campo": "visibility", "operador": "<",  "valor": 2},
    "baja_visibilidad":{"campo": "visibility","operador": "<",  "valor": 5},
}

# Palabras clave en descripción
KEYWORDS = {
    "nevada":      ["nevada", "nieve"],
    "tormenta":    ["tormenta"],
    "granizo":     ["granizo"],
    "niebla":      ["niebla", "neblina"],
    "lluvia":      ["lluvia", "llovizna"],
    "viento":      ["ventisca", "viento"],
}

# Confiabilidad de la fuente
CONFIABILIDAD_SMN = 0.95

def detectar_eventos(estacion):
    eventos = []
    w = estacion.get("weather", {})
    nombre = estacion.get("name")
    lat = float(estacion.get("lat", 0))
    lon = float(estacion.get("lon", 0))
    descripcion = w.get("description", "").lower()
    viento = w.get("wind_speed")
    visibilidad = w.get("visibility")

    # Detección por umbrales numéricos
    if viento and viento > 90:
        eventos.append(_crear_evento(nombre, lat, lon, "clima", "viento_extremo", 4))
    elif viento and viento > 60:
        eventos.append(_crear_evento(nombre, lat, lon, "clima", "viento_fuerte", 3))

    if visibilidad and visibilidad < 2:
        eventos.append(_crear_evento(nombre, lat, lon, "clima", "niebla", 3))
    elif visibilidad and visibilidad < 5:
        eventos.append(_crear_evento(nombre, lat, lon, "clima", "baja_visibilidad", 2))

    # Detección por descripción
    for subtipo, palabras in KEYWORDS.items():
        for palabra in palabras:
            if palabra in descripcion:
                severidad = 4 if subtipo in ["nevada", "tormenta", "granizo"] else 2
                eventos.append(_crear_evento(nombre, lat, lon, "clima", subtipo, severidad))
                break

    return eventos

def _crear_evento(nombre, lat, lon, event_type, subtipo, severidad):
    return {
        "source":        "SMN",
        "confiabilidad": CONFIABILIDAD_SMN,
        "estacion":      nombre,
        "latitude":      lat,
        "longitude":     lon,
        "event_type":    event_type,
        "subtipo":       subtipo,
        "severidad":     severidad,
        "event_date":    datetime.now().strftime("%Y-%m-%d"),
        "timestamp":     datetime.now().isoformat(),
        "status":        "raw"
    }

def procesar_archivo(path):
    with open(path, encoding="utf-8") as f:
        estaciones = json.load(f)

    todos_eventos = []
    for estacion in estaciones:
        eventos = detectar_eventos(estacion)
        todos_eventos.extend(eventos)

    return todos_eventos

if __name__ == "__main__":
    BASE = Path(r"C:\Users\msi\OneDrive\Desktop\corridor-intelligence-platform")
    
    # Buscar el archivo más reciente
    news_dir = BASE / "data/raw/news"
    archivos = sorted(news_dir.glob("smn_*.json"), reverse=True)
    
    if not archivos:
        print("No hay archivos SMN. Corré news_collector.py primero.")
        exit()

    ultimo = archivos[0]
    print(f"Procesando: {ultimo.name}")
    
    eventos = procesar_archivo(ultimo)
    
    if eventos:
        print(f"\n── Eventos detectados: {len(eventos)} ────────────────────")
        for e in eventos:
            print(f"\n  Estación  : {e['estacion']}")
            print(f"  Tipo      : {e['event_type']} / {e['subtipo']}")
            print(f"  Severidad : {e['severidad']}")
            print(f"  Fuente    : {e['source']} (confiabilidad: {e['confiabilidad']})")
    else:
        print("\nSin eventos críticos detectados en este momento.")