# Motor de reglas de impacto operacional
# Cada regla define: impacto, nivel, recomendación y duración estimada

IMPACT_RULES = {
    # ── Clima ─────────────────────────────────────────────────────────────
    ("clima", "lluvia"): {
        "impact_type":   "Visibilidad reducida",
        "severity":      "MEDIO",
        "recommendation":"Reducir velocidad operativa. Precaución en curvas y pendientes.",
        "duration_hs":   "2-4 horas",
    },
    ("clima", "baja_visibilidad"): {
        "impact_type":   "Riesgo de accidente por visibilidad",
        "severity":      "MEDIO",
        "recommendation":"Reducir velocidad. Aumentar distancia entre vehículos. Usar luces.",
        "duration_hs":   "1-3 horas",
    },
    ("clima", "niebla"): {
        "impact_type":   "Visibilidad nula o casi nula",
        "severity":      "ALTO",
        "recommendation":"Detener operaciones hasta mejora de condiciones. Activar balizas.",
        "duration_hs":   "2-6 horas",
    },
    ("clima", "nevada"): {
        "impact_type":   "Posible interrupción por acumulación de nieve",
        "severity":      "ALTO",
        "recommendation":"Evaluar cierre preventivo del corredor. Coordinar con Vialidad.",
        "duration_hs":   "12-48 horas",
    },
    ("clima", "viento_fuerte"): {
        "impact_type":   "Riesgo para vehículos de alto perfil",
        "severity":      "MEDIO",
        "recommendation":"Restringir circulación de camiones. Reducir velocidad máxima.",
        "duration_hs":   "3-8 horas",
    },
    ("clima", "viento_extremo"): {
        "impact_type":   "Interrupción probable del corredor",
        "severity":      "ALTO",
        "recommendation":"Suspender operaciones temporalmente. Aguardar parte meteorológico.",
        "duration_hs":   "6-12 horas",
    },
    ("clima", "alud"): {
        "impact_type":   "Corte total del corredor",
        "severity":      "CRÍTICO",
        "recommendation":"Suspender tránsito inmediatamente. Activar protocolo de emergencia.",
        "duration_hs":   "24-72 horas",
    },
    ("clima", "tormenta"): {
        "impact_type":   "Condiciones de tránsito peligrosas",
        "severity":      "ALTO",
        "recommendation":"Suspender operaciones. Aguardar normalización meteorológica.",
        "duration_hs":   "4-12 horas",
    },
    ("clima", "granizo"): {
        "impact_type":   "Daño potencial a vehículos y visibilidad reducida",
        "severity":      "ALTO",
        "recommendation":"Detener operaciones. Buscar refugio para vehículos y personal.",
        "duration_hs":   "1-3 horas",
    },
    ("clima", "inundacion"): {
        "impact_type":   "Daño en infraestructura vial. Posible corte",
        "severity":      "CRÍTICO",
        "recommendation":"Suspender tránsito pesado. Monitorear niveles. Contactar Vialidad.",
        "duration_hs":   "12-48 horas",
    },

    # ── Protestas ─────────────────────────────────────────────────────────
    ("protesta", "bloqueo_sindical"): {
        "impact_type":   "Corte total del corredor",
        "severity":      "ALTO",
        "recommendation":"Activar ruta alternativa. Contactar área de relaciones laborales.",
        "duration_hs":   "Indefinido",
    },
    ("protesta", "comunidad_mapuche"): {
        "impact_type":   "Corte total del corredor",
        "severity":      "ALTO",
        "recommendation":"Activar ruta alternativa. Escalar a área legal e institucional.",
        "duration_hs":   "Indefinido",
    },

    # ── Accidentes ────────────────────────────────────────────────────────
    ("accidente", "camion_volcado"): {
        "impact_type":   "Corte parcial o total del corredor",
        "severity":      "MEDIO",
        "recommendation":"Desviar tránsito liviano. Estimar tiempo de despeje.",
        "duration_hs":   "2-6 horas",
    },
    ("accidente", "colision_multiple"): {
        "impact_type":   "Reducción de capacidad vial",
        "severity":      "MEDIO",
        "recommendation":"Desviar tránsito. Coordinar con fuerzas de seguridad locales.",
        "duration_hs":   "1-4 horas",
    },

    # ── Congestión ────────────────────────────────────────────────────────
    ("congestion", "trafico_pesado"): {
        "impact_type":   "Demoras operativas en cadena logística",
        "severity":      "BAJO",
        "recommendation":"Escalonar salidas. Evaluar horarios alternativos de tránsito.",
        "duration_hs":   "1-3 horas",
    },

    # ── Obra vial ─────────────────────────────────────────────────────────
    ("obra_vial", "corte_parcial"): {
        "impact_type":   "Reducción de capacidad vial programada",
        "severity":      "BAJO",
        "recommendation":"Coordinar con Vialidad. Planificar desvíos con anticipación.",
        "duration_hs":   "Variable",
    },
    ("obra_vial", "corte_total"): {
        "impact_type":   "Interrupción completa programada",
        "severity":      "MEDIO",
        "recommendation":"Suspender operaciones en el corredor. Activar ruta alternativa.",
        "duration_hs":   "Variable",
    },
}

# Regla por defecto si no hay match
DEFAULT_RULE = {
    "impact_type":   "Impacto operacional en evaluación",
    "severity":      "BAJO",
    "recommendation":"Monitorear evolución del evento.",
    "duration_hs":   "Desconocida",
}

SEVERITY_ORDER = {"BAJO": 1, "MEDIO": 2, "ALTO": 3, "CRÍTICO": 4}

def get_impact_rule(event_type, subtipo):
    return IMPACT_RULES.get((event_type, subtipo), DEFAULT_RULE)


if __name__ == "__main__":
    # Test rápido
    casos = [
        ("clima",     "lluvia"),
        ("clima",     "nevada"),
        ("clima",     "niebla"),
        ("protesta",  "bloqueo_sindical"),
        ("accidente", "camion_volcado"),
    ]
    print("── Test Impact Rules ─────────────────────────────────")
    for event_type, subtipo in casos:
        rule = get_impact_rule(event_type, subtipo)
        print(f"\n{event_type} / {subtipo}")
        print(f"  Impacto  : {rule['impact_type']}")
        print(f"  Nivel    : {rule['severity']}")
        print(f"  Duración : {rule['duration_hs']}")
        print(f"  Recom.   : {rule['recommendation']}")