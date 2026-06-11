def get_recomendacion(event_type, subtipo, risk_level):
    
    # Reglas por subtipo específico
    reglas_subtipo = {
        "alud":             "Suspender tránsito inmediatamente. Activar protocolo de emergencia.",
        "nevada":           "Reducir velocidad operativa. Evaluar cierre preventivo del corredor.",
        "inundacion":       "Suspender tránsito pesado. Monitorear niveles de agua.",
        "bloqueo_sindical": "Evaluar rutas alternativas. Contactar área de relaciones laborales.",
        "comunidad_mapuche":"Evaluar rutas alternativas. Escalar a área legal y relaciones institucionales.",
        "camion_volcado":   "Desviar tránsito. Estimar tiempo de despeje antes de retomar operaciones.",
        "colision_multiple":"Desviar tránsito. Coordinar con fuerzas de seguridad locales.",
        "viento_fuerte":    "Reducir velocidad en vehículos de alto perfil. Monitorear evolución.",
        "lluvia":           "Monitorear condiciones. Precaución en curvas y pendientes.",
        "trafico_pesado":   "Escalonar salidas. Evaluar horarios alternativos de tránsito.",
        "corte_parcial":    "Coordinar con vialidad. Estimar duración y planificar desvíos.",
        "corte_total":      "Suspender operaciones en el corredor. Activar ruta alternativa.",
    }

    # Reglas por nivel de riesgo como fallback
    reglas_nivel = {
        "ALTO":  "Escalar a gerencia operativa. Activar plan de contingencia.",
        "MEDIO": "Monitorear evolución. Mantener alerta operativa.",
        "BAJO":  "Registrar evento. Sin acción inmediata requerida.",
    }

    return reglas_subtipo.get(subtipo, reglas_nivel.get(risk_level, "Sin recomendación disponible."))


def get_impacto_potencial(event_type, subtipo):
    
    impactos = {
        "alud":             "Corte total del corredor. Riesgo para vehículos en tránsito.",
        "nevada":           "Reducción severa de visibilidad. Riesgo de accidentes.",
        "inundacion":       "Daño en infraestructura vial. Posible corte del corredor.",
        "bloqueo_sindical": "Interrupción total del tránsito. Retrasos logísticos críticos.",
        "comunidad_mapuche":"Interrupción total del tránsito. Posible escalada del conflicto.",
        "camion_volcado":   "Corte parcial o total. Demoras en cadena logística.",
        "colision_multiple":"Corte de carril. Retrasos significativos en operaciones.",
        "viento_fuerte":    "Riesgo para vehículos de alto perfil. Posibles demoras.",
        "lluvia":           "Reducción de velocidad operativa. Riesgo moderado.",
        "trafico_pesado":   "Demoras operativas. Impacto en tiempos de entrega.",
        "corte_parcial":    "Reducción de capacidad vial. Demoras programadas.",
        "corte_total":      "Interrupción completa. Activar rutas alternativas.",
    }

    return impactos.get(subtipo, "Impacto operacional en evaluación.")


if __name__ == "__main__":
    # Test rápido
    casos = [
        ("protesta",  "bloqueo_sindical", "ALTO"),
        ("clima",     "nevada",           "ALTO"),
        ("accidente", "camion_volcado",   "MEDIO"),
        ("obra_vial", "corte_total",      "BAJO"),
    ]
    print("── Test Motor de Recomendaciones ────────────────────")
    for event_type, subtipo, risk_level in casos:
        rec = get_recomendacion(event_type, subtipo, risk_level)
        imp = get_impacto_potencial(event_type, subtipo)
        print(f"\nEvento : {subtipo}")
        print(f"Impacto: {imp}")
        print(f"Recom. : {rec}")