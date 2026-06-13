import pandas as pd
import hashlib
from sqlalchemy import create_engine, text
from pathlib import Path
from datetime import datetime

engine = create_engine("postgresql://postgres@localhost:5432/cip_db")

REQUIRED_FIELDS = [
    "source", "event_type", "subtype", "severity",
    "latitude", "longitude", "confidence",
    "timestamp", "ingestion_time", "event_hash"
]

def create_events_table():
    """Crea o actualiza la tabla events con el esquema completo."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS events_v3 (
                id              SERIAL PRIMARY KEY,
                source          VARCHAR(50),
                event_type      VARCHAR(50),
                subtype         VARCHAR(50),
                severity        VARCHAR(20),
                latitude        FLOAT,
                longitude       FLOAT,
                confidence      FLOAT,
                timestamp       TIMESTAMP,
                ingestion_time  TIMESTAMP,
                event_hash      VARCHAR(64) UNIQUE,
                raw_data        TEXT
            );
        """))
        conn.commit()
    print("✓ Tabla events_v3 lista")

def normalize_and_save(events):
    """
    Normaliza una lista de eventos y los guarda en PostGIS.
    Implementa deduplicación por event_hash.
    """
    if not events:
        print("Sin eventos para normalizar.")
        return 0

    df = pd.DataFrame(events)

    # Verificar campos requeridos
    missing = [f for f in REQUIRED_FIELDS if f not in df.columns]
    if missing:
        print(f"Campos faltantes: {missing}")
        return 0

    # Deduplicación — solo insertar eventos nuevos
    saved = 0
    skipped = 0

    with engine.connect() as conn:
        for _, row in df.iterrows():
            try:
                conn.execute(text("""
                    INSERT INTO events_v3
                    (source, event_type, subtype, severity,
                     latitude, longitude, confidence,
                     timestamp, ingestion_time, event_hash, raw_data)
                    VALUES
                    (:source, :event_type, :subtype, :severity,
                     :latitude, :longitude, :confidence,
                     :timestamp, :ingestion_time, :event_hash, :raw_data)
                    ON CONFLICT (event_hash) DO NOTHING;
                """), {
                    "source":        row["source"],
                    "event_type":    row["event_type"],
                    "subtype":       row["subtype"],
                    "severity":      row["severity"],
                    "latitude":      row["latitude"],
                    "longitude":     row["longitude"],
                    "confidence":    row["confidence"],
                    "timestamp":     row["timestamp"],
                    "ingestion_time":row["ingestion_time"],
                    "event_hash":    row["event_hash"],
                    "raw_data":      row.get("raw_data"),
                })
                saved += 1
            except Exception:
                skipped += 1
        conn.commit()

    print(f"✓ Eventos guardados: {saved} | Duplicados omitidos: {skipped}")
    return saved

def get_recent_events(hours=24):
    """Retorna eventos de las últimas N horas."""
    query = f"""
        SELECT * FROM events_v3
        WHERE ingestion_time >= NOW() - INTERVAL '{hours} hours'
        ORDER BY ingestion_time DESC
    """
    return pd.read_sql(query, engine)


if __name__ == "__main__":
    create_events_table()
    print("✓ Event Normalizer listo")