# funnels/runtime/events.py

class FunnelEventType:
    PAGE_VIEW = "PAGE_VIEW"
    FORM_SUBMIT = "FORM_SUBMIT"
    # Futuros eventos podrían incluir:
    # CTA_CLICK = "CTA_CLICK"
    # VIDEO_WATCH = "VIDEO_WATCH"

# Podríamos añadir validadores de schema para el payload de cada evento si fuera necesario.
SUPPORTED_EVENTS = [
    FunnelEventType.PAGE_VIEW,
    FunnelEventType.FORM_SUBMIT,
]

def is_event_supported(event_type: str) -> bool:
    return event_type in SUPPORTED_EVENTS
