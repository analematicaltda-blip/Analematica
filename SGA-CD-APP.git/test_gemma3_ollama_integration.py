import unittest
import os
from unittest.mock import MagicMock, patch
import flet as ft
from agent import llm_service

class TestGemma3OllamaIntegration(unittest.TestCase):

    def setUp(self):
        # Reset global singleton state before each test
        llm_service._llm_instance = None
        llm_service._llm_status = "not_initialized"
        self.mock_page = MagicMock(spec=ft.Page)
        self.mock_page.platform = "windows"

    def test_01_initialize_llm_with_gemma3_success(self):
        """Test successful initialization and live invocation of Gemma 3 4B via Ollama."""
        config = {"llm_preference": "local"}
        llm_service.initialize_llm(self.mock_page, config)

        self.assertEqual(llm_service.get_llm_status(), "initialized")
        llm_instance = llm_service.get_llm_instance()
        self.assertIsNotNone(llm_instance)

        response = llm_instance.invoke("Responde en una sola palabra: FUNCIONAL")
        self.assertIn("FUNCIONAL", response.content.upper())

    def test_02_initialize_llm_env_overrides(self):
        """Test environment variable overrides OLLAMA_BASE_URL and OLLAMA_MODEL."""
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://localhost:11434", "OLLAMA_MODEL": "gemma3:4b"}):
            config = {"llm_preference": "local"}
            llm_service.initialize_llm(self.mock_page, config)
            self.assertEqual(llm_service.get_llm_status(), "initialized")
            self.assertEqual(llm_service.get_llm_instance().model, "gemma3:4b")

    def test_03_initialize_llm_service_offline_handled(self):
        """Test graceful handling when Ollama service is unreachable or offline."""
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://localhost:11439"}):
            config = {"llm_preference": "local"}
            llm_service.initialize_llm(self.mock_page, config)
            self.assertEqual(llm_service.get_llm_status(), "error_ollama_not_found")
            self.assertIsNone(llm_service.get_llm_instance())

    def test_04_initialize_llm_model_missing_handled(self):
        """Test graceful handling when non-existent model is requested."""
        with patch.dict(os.environ, {"OLLAMA_MODEL": "non_existent_model_12345"}):
            config = {"llm_preference": "local"}
            llm_service.initialize_llm(self.mock_page, config)
            self.assertEqual(llm_service.get_llm_status(), "error_ollama_not_found")
            self.assertIsNone(llm_service.get_llm_instance())


if __name__ == "__main__":
    unittest.main(verbosity=2)
