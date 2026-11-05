from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import Perfil
from api.models import (
    CustomUser,
    Artesano,
    Publicacion,
    AsistenciaCapacitacion,
    Resena,
    ScoringRule
)

class ScoringSystemTests(TestCase):
    """
    Pruebas para el sistema de puntuación unificado.
    Verifica que las señales y los métodos de recálculo funcionen correctamente.
    """

    def setUp(self):
        # --- Crear usuarios y perfiles ---
        self.prestador_user = CustomUser.objects.create_user(
            'prestador_puntuado', 'prestador_puntuado@example.com', 'password123', role=CustomUser.Role.PRESTADOR
        )
        self.prestador_profile = Perfil.objects.create(
            usuario=self.prestador_user, nombre_comercial="Hotel Puntuado"
        )

        self.turista_user = CustomUser.objects.create_user(
            'turista_puntuador', 'turista_puntuador@example.com', 'password123', role=CustomUser.Role.TURISTA
        )

        # --- Crear una capacitación ---
        self.capacitacion = Publicacion.objects.create(
            titulo="Capacitación de Prueba de Puntuación",
            slug="capacitacion-de-prueba-puntuacion",
            tipo=Publicacion.Tipo.CAPACITACION,
            puntos_asistencia=15  # Puntos personalizados para esta capacitación
        )

        # --- Cargar las reglas de puntuación ---
        self.scoring_rules = ScoringRule.load()
        self.scoring_rules.puntos_asistencia_capacitacion = 10
        self.scoring_rules.puntos_por_estrella_reseña = 5
        self.scoring_rules.puntos_completar_formulario = 20
        self.scoring_rules.save()


    def test_recalcular_puntuacion_total(self):
        """Verifica que el método de recálculo promedia correctamente las puntuaciones."""
        from decimal import Decimal
        self.prestador_profile.puntuacion_calidad = Decimal('4.5')
        self.prestador_profile.puntuacion_servicio = Decimal('3.5')
        self.prestador_profile.puntuacion_precio = Decimal('5.0')
        self.prestador_profile.save()

        self.prestador_profile.recalcular_puntuacion_total()
        self.prestador_profile.refresh_from_db()

        expected_total = (Decimal('4.5') + Decimal('3.5') + Decimal('5.0')) / 3
        self.assertAlmostEqual(self.prestador_profile.puntuacion_total, expected_total, places=2)

    def test_scoring_rules_singleton(self):
        """Verifica que el modelo ScoringRule se comporte como un Singleton."""
        rule1 = ScoringRule.load()
        rule2 = ScoringRule.load()
        self.assertEqual(rule1.pk, 1)
        self.assertEqual(rule1.pk, rule2.pk)

        # Verificar que no se pueden crear nuevas instancias
        with self.assertRaises(Exception):
             ScoringRule.objects.create(puntos_asistencia_capacitacion=100)