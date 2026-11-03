"""
Automated Test Suite for Catalog Endpoints, Specialization Management & On-The-Fly Creation (Phase 8.13.5).
"""
import unittest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.models.catalog import CatalogoEspecialidad, EmpresaEspecialidad
from app.models.tenancy import Inquilino
from app.api.v1.endpoints.catalogo import (
    search_catalogo_especialidades,
    create_custom_especialidad_on_the_fly,
    get_my_company_specialties,
    update_tenant_vocacion,
    CustomSpecialtyCreate,
    UpdateVocacionRequest,
    seed_catalogo_if_empty,
)
from app.core.catalogo_data import CATALOGO_OFICIAL


class DummyUser:
    def __init__(self, id=1, inquilino_id=10, role_codes=None):
        self.id = id
        self.inquilino_id = inquilino_id
        self.role_codes = role_codes or ["admin_empresa"]


class TestCatalogoEndpoints(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.user = DummyUser(id=1, inquilino_id=10)

    def test_01_catalogo_data_integrity(self):
        """Verify 1,000 official catalog items (500 Deporte + 500 Cultura)."""
        self.assertEqual(len(CATALOGO_OFICIAL), 1000)
        dep_items = [i for i in CATALOGO_OFICIAL if i["vertical"] == "deporte"]
        cul_items = [i for i in CATALOGO_OFICIAL if i["vertical"] == "cultura"]
        self.assertEqual(len(dep_items), 500)
        self.assertEqual(len(cul_items), 500)

    def test_02_seed_catalogo_if_empty(self):
        """Verify seed function inserts objects into DB if count is 0."""
        self.db.query.return_value.scalar.return_value = 0
        self.db.query.return_value.all.return_value = []

        seed_catalogo_if_empty(self.db)

        self.db.bulk_save_objects.assert_called_once()
        self.db.commit.assert_called_once()

    def test_03_create_custom_especialidad_on_the_fly_new_item(self):
        """Verify on-the-fly creation of a new non-standard specialty."""
        self.db.query.return_value.scalar.return_value = 1000
        # No existing spec found
        self.db.query.return_value.filter.return_value.first.return_value = None

        payload = CustomSpecialtyCreate(
            vertical="deporte",
            nombre="Gimnasia Estética de Grupo",
            categoria="Gimnasia Especializada"
        )

        res = create_custom_especialidad_on_the_fly(payload=payload, db=self.db, current_user=self.user)

        self.assertEqual(res["inquilino_id"], 10)
        self.db.add.assert_called()
        self.db.commit.assert_called()

    def test_04_create_custom_especialidad_existing_item_adoption(self):
        """Verify on-the-fly creation matches existing master item without duplicating master entry."""
        self.db.query.return_value.scalar.return_value = 1000
        existing_spec = CatalogoEspecialidad(
            id=42,
            vertical="deporte",
            categoria="Deportes de Combate y Artes Marciales",
            codigo_canonico="dep_001_taekwondo_wt_itf",
            nombre="Taekwondo (WT/ITF)",
            es_estandar=True,
        )

        def query_side_effect(model):
            q = MagicMock()
            model_name = getattr(model, "__name__", str(model))
            if "CatalogoEspecialidad" in model_name:
                q.filter.return_value.first.return_value = existing_spec
            elif "EmpresaEspecialidad" in model_name:
                q.filter.return_value.first.return_value = None
            else:
                q.filter.return_value.first.return_value = None
            return q

        self.db.query.side_effect = query_side_effect

        payload = CustomSpecialtyCreate(
            vertical="deporte",
            nombre="Taekwondo (WT/ITF)",
            categoria="Deportes de Combate"
        )

        res = create_custom_especialidad_on_the_fly(payload=payload, db=self.db, current_user=self.user)

        self.assertEqual(res["especialidad_id"], 42)
        self.assertEqual(res["nombre"], "Taekwondo (WT/ITF)")

    def test_05_update_tenant_vocacion(self):
        """Verify tenant institutional vocation update ('deportiva' | 'cultural')."""
        tenant = Inquilino(id=10, nombre_empresa="IMDER", vocacion_institucional="deportiva")
        self.db.query.return_value.filter.return_value.first.return_value = tenant

        payload = UpdateVocacionRequest(vocacion_institucional="cultural")
        res = update_tenant_vocacion(payload=payload, db=self.db, current_user=self.user)

        self.assertEqual(res["vocacion_institucional"], "cultural")
        self.assertEqual(tenant.vocacion_institucional, "cultural")
        self.db.commit.assert_called_once()

    def test_06_update_tenant_vocacion_invalid_rejected(self):
        """Verify invalid vocation string is rejected with HTTP 400 Bad Request."""
        payload = UpdateVocacionRequest(vocacion_institucional="invalido")
        with self.assertRaises(HTTPException) as cm:
            update_tenant_vocacion(payload=payload, db=self.db, current_user=self.user)

        self.assertEqual(cm.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
