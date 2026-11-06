import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status

from app.schemas.user import UserCreate
from app.api.v1.endpoints.admin import create_user_by_empresa, toggle_user_status

class TestCoordinadorGovernance(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_current_user = MagicMock()
        self.mock_current_user.inquilino_id = 100

    def test_jefe_area_can_create_coordinador(self):
        self.mock_current_user.role_codes = ["jefe_area"]
        user_in = UserCreate(
            nombre_usuario="coord_norte",
            correo="coord.norte@example.com",
            email="coord.norte@example.com",
            password="SecurePassword123!",
            nombre_completo="Coordinador Sede Norte",
            rol="coordinador",
            inquilino_id=100
        )
        with patch("app.crud.user.create_user") as mock_crud_create:
            mock_crud_create.return_value = MagicMock(id=10, nombre_usuario="coord_norte")
            self.mock_db.query().filter().first.return_value = None

            result = create_user_by_empresa(
                db=self.mock_db,
                user_in=user_in,
                current_user=self.mock_current_user
            )
            self.assertIsNotNone(result)

    def test_profesional_and_tecnico_cannot_create_coordinador(self):
        for role_code in [["profesional_area"], ["tecnico_area"]]:
            self.mock_current_user.role_codes = role_code
            user_in = UserCreate(
                nombre_usuario="illegal_coord",
                correo="illegal@example.com",
                email="illegal@example.com",
                password="SecurePassword123!",
                nombre_completo="Illegal Coord",
                rol="coordinador",
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

    def test_jefe_area_can_deactivate_coordinador(self):
        self.mock_current_user.role_codes = ["jefe_area"]
        mock_target = MagicMock(id=20, inquilino_id=100, activo=True)
        self.mock_db.query().filter().first.return_value = mock_target
        self.mock_db.execute().fetchall.return_value = [("coordinador",)]

        updated_user = toggle_user_status(
            user_id=20,
            active=False,
            db=self.mock_db,
            current_user=self.mock_current_user
        )
        self.assertFalse(updated_user.activo)

if __name__ == "__main__":
    unittest.main()
