from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.core_erp.inventory.inventory_engine import InventoryEngine
from unittest.mock import MagicMock

class InventoryEngineTest(TestCase):
    def test_validate_movement_ok(self):
        movement = MagicMock(quantity=Decimal('10.0'))
        InventoryEngine.validate_movement(movement)

    def test_validate_movement_fail(self):
        movement = MagicMock(quantity=Decimal('-5.0'))
        with self.assertRaises(ValidationError):
            InventoryEngine.validate_movement(movement)

    def test_process_movement(self):
        movement = MagicMock(quantity=Decimal('10.0'))
        result = InventoryEngine.process_movement(movement)
        self.assertTrue(result)
