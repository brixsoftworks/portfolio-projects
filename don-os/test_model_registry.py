import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import model_registry


class ModelRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name) / "config"
        self.registry_path = self.config_dir / "models.json"
        self.keyring_set = patch.object(model_registry.keyring, "set_password")
        self.keyring_get = patch.object(model_registry.keyring, "get_password", return_value="test-secret")
        self.keyring_delete = patch.object(model_registry.keyring, "delete_password")
        self.keyring_set.start()
        self.keyring_get.start()
        self.keyring_delete.start()
        self.addCleanup(self.keyring_set.stop)
        self.addCleanup(self.keyring_get.stop)
        self.addCleanup(self.keyring_delete.stop)
        self.config_dir_patch = patch.object(model_registry, "APP_CONFIG_DIR", self.config_dir)
        self.registry_patch = patch.object(model_registry, "REGISTRY_PATH", self.registry_path)
        self.config_dir_patch.start()
        self.registry_patch.start()
        self.addCleanup(self.config_dir_patch.stop)
        self.addCleanup(self.registry_patch.stop)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_hosted_api_key_only_goes_to_keyring(self):
        model = model_registry.add_model(
            "OpenRouter Claude",
            "openai-compatible",
            "anthropic/claude-3.7-sonnet",
            "https://openrouter.ai/api/v1",
            "test-secret",
        )
        saved = self.registry_path.read_text(encoding="utf-8")
        self.assertNotIn("test-secret", saved)
        self.assertNotIn("api_key", saved)
        self.assertEqual(self.registry_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.config_dir.stat().st_mode & 0o777, 0o700)
        self.assertTrue(model["has_api_key"])
        self.assertNotIn("test-secret", json.dumps(model))

    def test_hosted_model_builds_openai_compatible_chat_client(self):
        model = model_registry.add_model(
            "Local Gateway",
            "openai-compatible",
            "model-x",
            "https://api.example.test/v1",
            "credential",
        )
        with patch.object(model_registry, "ChatOpenAI") as chat_openai:
            model_registry.get_chat_model(model["id"])
        chat_openai.assert_called_once_with(
            model="model-x",
            api_key="test-secret",
            base_url="https://api.example.test/v1",
            temperature=0.2,
            timeout=45,
            max_retries=0,
        )

    def test_ollama_uses_loopback_and_needs_no_key(self):
        model = model_registry.add_model(
            "Qwen Local",
            "ollama",
            "qwen3:8b",
            model_registry.DEFAULT_OLLAMA_URL,
        )
        self.assertFalse(model["has_api_key"])
        with patch.object(model_registry, "ChatOpenAI") as chat_openai:
            model_registry.get_chat_model(model["id"])
        self.assertEqual(chat_openai.call_args.kwargs["api_key"], "ollama")

    def test_rejects_missing_hosted_key_and_nonlocal_ollama(self):
        with self.assertRaisesRegex(model_registry.ModelRegistryError, "requires an API key"):
            model_registry.add_model("Hosted", "openai-compatible", "model", "https://example.test/v1")
        with self.assertRaisesRegex(model_registry.ModelRegistryError, "localhost"):
            model_registry.add_model("Remote Ollama", "ollama", "model", "https://example.test/v1")

    def test_active_selection_and_removal_fall_back_to_default(self):
        model = model_registry.add_model(
            "Test model",
            "openai-compatible",
            "model",
            "https://example.test/v1",
            "secret",
        )
        model_registry.set_active_model(model["id"])
        self.assertEqual(model_registry.list_models()["active_model_id"], model["id"])
        model_registry.remove_model(model["id"])
        result = model_registry.list_models()
        self.assertEqual(result["active_model_id"], "default")
        self.assertFalse(any(item["id"] == model["id"] for item in result["models"]))

    def test_gemini_default_reflects_environment_key_presence(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "configured"}):
            self.assertTrue(model_registry.list_models()["models"][0]["available"])
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(model_registry.list_models()["models"][0]["available"])


if __name__ == "__main__":
    unittest.main()
