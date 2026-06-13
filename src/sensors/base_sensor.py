import hashlib
import json
from datetime import datetime
from abc import ABC, abstractmethod


class BaseSensor(ABC):
    """
    Clase base para todos los sensores de la plataforma.
    Todos los sensores deben heredar de esta clase y producir
    eventos en el formato estándar definido aquí.
    """

    def __init__(self, source_name, confidence):
        self.source_name = source_name
        self.confidence  = confidence
        self.events      = []

    @abstractmethod
    def collect(self):
        """Captura datos de la fuente externa."""
        pass

    @abstractmethod
    def normalize(self, raw_data):
        """Convierte datos crudos al formato estándar."""
        pass

    def run(self):
        """Ejecuta el pipeline completo del sensor."""
        print(f"[{self.source_name}] Iniciando sensor...")
        raw_data    = self.collect()
        self.events = self.normalize(raw_data)
        print(f"[{self.source_name}] {len(self.events)} eventos normalizados")
        return self.events

    def create_event(self, event_type, subtype, severity,
                     latitude, longitude, raw_data=None):
        """Crea un evento en el formato estándar de la plataforma."""
        timestamp = datetime.now().isoformat()

        # Generar event_hash para deduplicación
        hash_input = f"{self.source_name}_{event_type}_{subtype}_{round(latitude,3)}_{round(longitude,3)}_{datetime.now().strftime('%Y%m%d%H')}"
        event_hash = hashlib.md5(hash_input.encode()).hexdigest()

        return {
            "source":        self.source_name,
            "event_type":    event_type,
            "subtype":       subtype,
            "severity":      severity,
            "latitude":      latitude,
            "longitude":     longitude,
            "confidence":    self.confidence,
            "timestamp":     timestamp,
            "ingestion_time":timestamp,
            "event_hash":    event_hash,
            "raw_data":      json.dumps(raw_data, ensure_ascii=False)
                             if raw_data else None,
        }

    @staticmethod
    def severity_from_number(n):
        """Convierte severidad numérica a categórica."""
        if n >= 4:   return "CRÍTICO"
        elif n >= 3: return "ALTO"
        elif n >= 2: return "MEDIO"
        else:        return "BAJO"


if __name__ == "__main__":
    print("BaseSensor cargado correctamente.")
    print("Campos del evento estándar:")
    campos = [
        "source", "event_type", "subtype", "severity",
        "latitude", "longitude", "confidence",
        "timestamp", "ingestion_time", "event_hash", "raw_data"
    ]
    for c in campos:
        print(f"  - {c}")