# This file makes the 'models' directory a Python package.
# Import all models here so that Alembic can discover them.

from .base import Base
from .tenancy import Inquilino
from .user import (
    Usuario, Profesor, Alumno, JefeArea, Coordinador,
    Almacenista, JefeAlmacen, JefeEscenarios
)
from .academic import (
    ProcesoFormacion, Escenario, EscenarioParte, Reserva, Clase,
    Inscripcion, Asistencia, Evento, EventoParticipante, Notificacion, AuditLog
)
from .inventory import Elemento, Prestamo
from .gamification import (
    GamificacionAccion, GamificacionPuntosLog, GamificacionMedalla,
    GamificacionMedallaObtenida
)
from .curriculum import (
    PlanCurricular, PlanCurricularTema, PlanificadorClasesEventos,
    ProgresoAlumnoTema, ContenidoCurricular
)
from .billing import PaymentGateway, SubscriptionPlan, Subscription, Payment
from .communication import (
    ChatConversacion, ChatParticipante, ChatMensaje, ForoClase,
    ForoHilo, ForoPublicacion
)
from .dropdowns import (
    Genero, GrupoEtario, TipoDocumento, Escolaridad, Discapacidad,
    GrupoPoblacional, Barrio, Vereda, Resguardo, TipoEscenario
)
from .settings import Setting
