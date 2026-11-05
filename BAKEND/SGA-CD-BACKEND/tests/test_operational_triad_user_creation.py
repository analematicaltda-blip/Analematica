import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status

from app.schemas.user import UserCreate
from app.api.v1.endpoints.admin import create_user_by_empresa

class TestOperationalTriadUserCreation(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_current_user = MagicMock()
        self.mock_current_user.inquilino_id = 100

    def test_jefe_area_can_create_whitelisted_roles(self):
        self.mock_current_user.role_codes = ["jefe_area"]
        whitelisted = ["profesor", "jefe_escenarios", "almacenista"]

        for target in whitelisted:
            user_in = UserCreate(
                nombre_usuario=f"user_{target}",
                correo=f"{target}@example.com",
                email=f"{target}@example.com",
                password="SecurePassword123!",
                nombre_completo=f"Test {target.capitalize()}",
                rol=target,
                inquilino_id=100
            )
            with patch("app.crud.user.create_user") as mock_crud_create:
                mock_crud_create.return_value = MagicMock(id=1, nombre_usuario=f"user_{target}")
                self.mock_db.query().filter().first.return_value = None

                result = create_user_by_empresa(
                    db=self.mock_db,
                    user_in=user_in,
                    current_user=self.mock_current_user
                )
                self.assertIsNotNone(result)

    def test_profesional_area_can_create_whitelisted_roles(self):
        self.mock_current_user.role_codes = ["profesional_area"]
        whitelisted = ["profesor", "jefe_escenarios", "almacenista"]

        for target in whitelisted:
            user_in = UserCreate(
                nombre_usuario=f"user_prof_{target}",
                correo=f"prof_{target}@example.com",
                email=f"prof_{target}@example.com",
                password="SecurePassword123!",
                nombre_completo=f"Test Prof {target.capitalize()}",
                rol=target,
                inquilino_id=100
            )
            with patch("app.crud.user.create_user") as mock_crud_create:
                mock_crud_create.return_value = MagicMock(id=2, nombre_usuario=f"user_prof_{target}")
                self.mock_db.query().filter().first.return_value = None

                result = create_user_by_empresa(
                    db=self.mock_db,
                    user_in=user_in,
                    current_user=self.mock_current_user
                )
                self.assertIsNotNone(result)

    def test_tecnico_area_can_create_whitelisted_roles(self):
        self.mock_current_user.role_codes = ["tecnico_area"]
        whitelisted = ["profesor", "jefe_escenarios", "almacenista"]

        for target in whitelisted:
            user_in = UserCreate(
                nombre_usuario=f"user_tec_{target}",
                correo=f"tec_{target}@example.com",
                email=f"tec_{target}@example.com",
                password="SecurePassword123!",
                nombre_completo=f"Test Tec {target.capitalize()}",
                rol=target,
                inquilino_id=100
            )
            with patch("app.crud.user.create_user") as mock_crud_create:
                mock_crud_create.return_value = MagicMock(id=3, nombre_usuario=f"user_tec_{target}")
                self.mock_db.query().filter().first.return_value = None

                result = create_user_by_empresa(
                    db=self.mock_db,
                    user_in=user_in,
                    current_user=self.mock_current_user
                )
                self.assertIsNotNone(result)

    def test_operational_triad_cannot_create_forbidden_roles(self):
        # profesional_area y tecnico_area no pueden crear coordinadores ni superiores
        strict_triad_roles = [["profesional_area"], ["tecnico_area"]]
        forbidden_targets = ["coordinador", "admin_empresa", "jefe_area", "profesional_area", "tecnico_area", "admin_general"]

        for role_code in strict_triad_roles:
            self.mock_current_user.role_codes = role_code
            for forbidden_target in forbidden_targets:
                user_in = UserCreate(
                    nombre_usuario="bad_creation",
                    correo="bad@example.com",
                    email="bad@example.com",
                    password="SecurePassword123!",
                    nombre_completo="Bad Creation",
                    rol=forbidden_target,
                    inquilino_id=100
                )
                with self.assertRaises(HTTPException) as ctx:
                    create_user_by_empresa(
                        db=self.mock_db,
                        user_in=user_in,
                        current_user=self.mock_current_user
                    )
                self.assertEqual(ctx.exception.status_code, status.HTTP_403_FORBIDDEN)
                self.assertIn("autorización para dar de alta a: profesor, jefe_escenarios y almacenista", ctx.exception.detail)

    def test_cross_tenant_creation_rejected(self):
        self.mock_current_user.role_codes = ["jefe_area"]
        user_in = UserCreate(
            nombre_usuario="cross_tenant",
            correo="cross@example.com",
            email="cross@example.com",
            password="SecurePassword123!",
            nombre_completo="Cross Tenant",
            rol="profesor",
            inquilino_id=999 # Different than current_user.inquilino_id = 100
        )
        with self.assertRaises(HTTPException) as ctx:
            create_user_by_empresa(
                db=self.mock_db,
                user_in=user_in,
                current_user=self.mock_current_user
            )
        self.assertEqual(ctx.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Cannot create user for another tenant", ctx.exception.detail)

if __name__ == "__main__":
    unittest.main()
