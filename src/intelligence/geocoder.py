import requests
from pathlib import Path

# Coordenadas fijas de las estaciones SMN relevantes
# Usamos coordenadas fijas para evitar llamadas innecesarias a Nominatim
COORDENADAS_FIJAS = {
    "Neuquén":               {"lat": -38.9543, "lon": -68.0751},
    "Cutral Co":             {"lat": -38.9371, "lon": -69.2297},
    "Zapala":                {"lat": -38.8979, "lon": -70.0633},
    "Cipolletti":            {"lat": -38.9334, "lon": -67.9976},
    "General Roca":          {"lat": -39.0280, "lon": -67.5739},
    "Villa La Angostura":    {"lat": -40.7643, "lon": -71.6415},
    "Chapelco":              {"lat": -40.1314, "lon": -71.1994},
    "San Martín de Los Andes":{"lat": -40.1550, "lon": -71.3533},
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode_fijo(nombre):
    """Busca coordenadas en el diccionario fijo primero."""
    return COORDENADAS_FIJAS.get(nombre)

def geocode_nominatim(lugar):
    """Fallback a Nominatim si no está en el diccionario fijo."""
    try:
        params = {
            "q": f"{lugar}, Neuquén, Argentina",
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "CorridorIntelligencePlatform/1.0"}
        response = requests.get(NOMINATIM_URL, params=params,
                                headers=headers, timeout=5)
        results = response.json()
        if results:
            return {
                "lat": float(results[0]["lat"]),
                "lon": float(results[0]["lon"])
            }
    except Exception as e:
        print(f"  Error Nominatim para {lugar}: {e}")
    return None

def geocode(nombre):
    """Geocodifica un lugar usando diccionario fijo o Nominatim."""
    coords = geocode_fijo(nombre)
    if coords:
        return coords
    print(f"  Buscando coordenadas para: {nombre}")
    return geocode_nominatim(nombre)

def enriquecer_eventos(eventos):
    """Agrega coordenadas precisas a cada evento."""
    enriquecidos = []
    for evento in eventos:
        coords = geocode(evento["estacion"])
        if coords:
            evento["latitude"]  = coords["lat"]
            evento["longitude"] = coords["lon"]
            evento["geocoded"]  = True
        else:
            evento["geocoded"] = False
        enriquecidos.append(evento)
    return enriquecidos

if __name__ == "__main__":
    # Test con las estaciones del output anterior
    estaciones_test = [
        "Neuquén", "Cutral Co", "Zapala",
        "Cipolletti", "General Roca", "Villa La Angostura"
    ]
    print("── Test Geocoder ─────────────────────────────────────")
    for nombre in estaciones_test:
        coords = geocode(nombre)
        if coords:
            print(f"✓ {nombre}: {coords['lat']}, {coords['lon']}")
        else:
            print(f"✗ {nombre}: no encontrado")