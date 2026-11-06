"""Add the seven assistance/control tables explicitly; never reset existing application data."""
from app.models.assistance import AssistanceSession, AssistanceEvent, AssistanceAdvice, ControlPairing, ControlDevice, ControlJob, ControlApproval

def install(bind=None):
    if bind is None:
        from app.db.session import engine
        bind = engine
    for model in [AssistanceSession, AssistanceEvent, AssistanceAdvice, ControlPairing, ControlDevice, ControlJob, ControlApproval]:
        model.__table__.create(bind, checkfirst=True)
    print('Tablas de asistencia preparadas; no se modificaron cuentas externas ni datos existentes.')

if __name__ == '__main__':
    install()
