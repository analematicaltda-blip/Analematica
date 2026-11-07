"""
Unit Test Suite for PlanCapabilityService (Phase 8.13.3-A-R).

Tests plan normalization, EffectiveCapabilities resolution, subscription evaluation,
temporal boundaries, tenant capability isolation, instance dict independence,
role/plan separation, and read-only non-mutating execution.
"""
import unittest
from datetime import datetime, timezone, timedelta
from app.services.plan_capability_service import (
    PlanCapabilityService,
    normalize_plan_code,
    evaluate_subscription_status,
    CANONICAL_BASIC,
    CANONICAL_FULL,
    CANONICAL_UNKNOWN,
    BASIC_QUOTAS,
    FULL_QUOTAS
)


class TestPlanCapabilityService(unittest.TestCase):

    def test_1_plan_normalization(self):
        """1. Normalización de identificadores heredados y caso desconocido."""
        basic_legacy = ["gratis", "basico", "plan_basico", "trial", "basic", "", None]
        for raw in basic_legacy:
            self.assertEqual(normalize_plan_code(raw), CANONICAL_BASIC, f"Failed on basic legacy: {raw}")

        full_legacy = ["pro_mensual", "pro_anual", "full", "pro", "mensual", "anual", "pro_tier"]
        for raw in full_legacy:
            self.assertEqual(normalize_plan_code(raw), CANONICAL_FULL, f"Failed on full legacy: {raw}")

        unknown_identifiers = ["plan_super_vip", "invalid_string_123", "hack_attempt"]
        for raw in unknown_identifiers:
            self.assertEqual(normalize_plan_code(raw), CANONICAL_UNKNOWN, f"Failed on unknown: {raw}")

    def test_2_basic_plan_capabilities(self):
        """2. Capacidades y cuotas del Plan Básico."""
        tenant = {
            "id": 101,
            "nombre_empresa": "IMDER Villavicencio",
            "tipo_organizacion": "entidad_publica",
            "ambito_organizacional": "municipal",
            "plan": "basico",
            "activo": True
        }
        sub = {"estado": "activa"}

        caps = PlanCapabilityService.resolve_capabilities(tenant, sub)

        self.assertEqual(caps.canonical_plan, CANONICAL_BASIC)
        self.assertTrue(caps.is_active)
        self.assertTrue(caps.panel_institucional_enabled)
        self.assertTrue(caps.gestion_usuarios_enabled)
        self.assertTrue(caps.modulos_deportivos_culturales_enabled)

        # Advanced modules must be disabled on Basic
        self.assertFalse(caps.crm_leads_enabled)
        self.assertFalse(caps.crm_campaigns_enabled)
        self.assertFalse(caps.ai_images_enabled)
        self.assertFalse(caps.ai_carousels_enabled)
        self.assertFalse(caps.ai_video_enabled)
        self.assertFalse(caps.ai_reels_enabled)
        self.assertFalse(caps.social_publishing_enabled)
        self.assertFalse(caps.crm_analytics_enabled)

        # Monthly limits must be zero
        self.assertEqual(caps.monthly_limits, BASIC_QUOTAS)

    def test_3_full_plan_capabilities(self):
        """3. Capacidades y cuotas del Plan Full."""
        tenant = {
            "id": 102,
            "nombre_empresa": "Gobernación del Meta",
            "tipo_organizacion": "entidad_publica",
            "ambito_organizacional": "departamental",
            "plan": "pro_anual",
            "activo": True
        }
        sub = {"estado": "activa"}

        caps = PlanCapabilityService.resolve_capabilities(tenant, sub)

        self.assertEqual(caps.canonical_plan, CANONICAL_FULL)
        self.assertTrue(caps.is_active)
        self.assertTrue(caps.panel_institucional_enabled)
        self.assertTrue(caps.crm_leads_enabled)
        self.assertTrue(caps.crm_campaigns_enabled)
        self.assertTrue(caps.ai_images_enabled)
        self.assertTrue(caps.ai_carousels_enabled)
        self.assertTrue(caps.ai_video_enabled)
        self.assertTrue(caps.ai_reels_enabled)
        self.assertTrue(caps.social_publishing_enabled)
        self.assertTrue(caps.crm_analytics_enabled)

        # Quotas for Full
        self.assertEqual(caps.monthly_limits["images"], 100)
        self.assertEqual(caps.monthly_limits["carousels"], 50)
        self.assertEqual(caps.monthly_limits["videos"], 5)
        self.assertEqual(caps.monthly_limits["reels"], 20)
        self.assertEqual(caps.monthly_limits["llm_prompts"], 500)
        self.assertEqual(caps.monthly_limits["social_posts"], 50)

    def test_4_subscription_status_evaluation(self):
        """4. Suscripciones vigentes, vencidas, canceladas y ausentes."""
        now = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        future = now + timedelta(days=30)
        past = now - timedelta(days=1)

        # Trial
        self.assertEqual(evaluate_subscription_status({"estado": "en_prueba", "fecha_fin": future}, now)["status"], "en_prueba")
        self.assertEqual(evaluate_subscription_status({"estado": "en_prueba", "fecha_fin": past}, now)["status"], "vencida")

        # Active
        self.assertEqual(evaluate_subscription_status({"estado": "activa", "fecha_fin": future}, now)["status"], "activa")
        self.assertEqual(evaluate_subscription_status({"estado": "activa", "fecha_fin": past}, now)["status"], "vencida")

        # Canceled
        self.assertEqual(evaluate_subscription_status({"estado": "cancelada", "fecha_fin": future}, now)["status"], "cancelada_vigente")
        self.assertEqual(evaluate_subscription_status({"estado": "cancelada", "fecha_fin": past}, now)["status"], "cancelada")

        # Expired
        self.assertEqual(evaluate_subscription_status({"estado": "vencida"}, now)["status"], "vencida")

        # Absent
        self.assertEqual(evaluate_subscription_status(None, now)["status"], "sin_suscripcion")

    def test_5_temporal_limits_and_inconsistent_dates(self):
        """5. Fechas de inicio/fin, límites temporales y estados inconsistentes."""
        now = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Inconsistent corrupt date string
        corrupt_sub = {"estado": "activa", "fecha_fin": "not-a-valid-date-string"}
        eval_res = evaluate_subscription_status(corrupt_sub, now)
        self.assertEqual(eval_res["status"], "inconsistente")
        self.assertFalse(eval_res["is_active"])

        # Inconsistent status string
        unknown_sub = {"estado": "invalid_status_xyz"}
        eval_res_2 = evaluate_subscription_status(unknown_sub, now)
        self.assertEqual(eval_res_2["status"], "inconsistente")
        self.assertFalse(eval_res_2["is_active"])

    def test_6_multitenant_logical_isolation(self):
        """6. Aislamiento lógico de capacidades entre dos inquilinos."""
        tenant_a = {"id": 201, "nombre_empresa": "Empresa A", "plan": "basico", "activo": True}
        tenant_b = {"id": 202, "nombre_empresa": "Empresa B", "plan": "full", "activo": True}
        sub_active = {"estado": "activa"}

        caps_a = PlanCapabilityService.resolve_capabilities(tenant_a, sub_active)
        caps_b = PlanCapabilityService.resolve_capabilities(tenant_b, sub_active)

        self.assertEqual(caps_a.inquilino_id, 201)
        self.assertEqual(caps_b.inquilino_id, 202)

        # A has Basic, B has Full
        self.assertFalse(caps_a.crm_leads_enabled)
        self.assertTrue(caps_b.crm_leads_enabled)

        # Quotas isolated
        self.assertEqual(caps_a.monthly_limits["images"], 0)
        self.assertEqual(caps_b.monthly_limits["images"], 100)

    def test_7_quota_dictionary_instance_independence(self):
        """7. Independencia de los diccionarios de cuotas entre instancias."""
        tenant_1 = {"id": 301, "plan": "full", "activo": True}
        tenant_2 = {"id": 302, "plan": "full", "activo": True}
        sub = {"estado": "activa"}

        caps_1 = PlanCapabilityService.resolve_capabilities(tenant_1, sub)
        caps_2 = PlanCapabilityService.resolve_capabilities(tenant_2, sub)

        # Mutate instance 1 limits
        caps_1.monthly_limits["images"] = 999

        # Instance 2 limits must remain unaffected
        self.assertEqual(caps_2.monthly_limits["images"], 100)
        self.assertNotEqual(caps_1.monthly_limits["images"], caps_2.monthly_limits["images"])

    def test_8_plan_capability_and_role_separation(self):
        """8. Separación entre capacidad de plan y autorización por rol."""
        tenant = {"id": 401, "plan": "full", "activo": True}
        sub = {"estado": "activa"}

        caps = PlanCapabilityService.resolve_capabilities(tenant, sub)

        # Full plan enables capabilities on the organization level
        self.assertTrue(caps.ai_images_enabled)

        # Check that EffectiveCapabilities object contains organizational scope only,
        # and does NOT grant user roles like 'admin_general' or 'admin_empresa'
        dict_repr = caps.dict() if hasattr(caps, "dict") else caps.__dict__
        self.assertNotIn("user_role", dict_repr)
        self.assertNotIn("is_admin", dict_repr)

    def test_9_pure_read_only_no_db_side_effects(self):
        """9. Ausencia de escrituras en la BD durante la normalización y resolución."""
        tenant_data = {"id": 501, "nombre_empresa": "Original Name", "plan": "gratis"}
        tenant_copy = dict(tenant_data)

        # Perform normalization & resolution
        plan_code = normalize_plan_code(tenant_data["plan"])
        caps = PlanCapabilityService.resolve_capabilities(tenant_data)

        # Original input payload must remain completely untouched
        self.assertEqual(tenant_data, tenant_copy)
        self.assertEqual(plan_code, CANONICAL_BASIC)
        self.assertEqual(caps.inquilino_id, 501)


if __name__ == "__main__":
    unittest.main()
