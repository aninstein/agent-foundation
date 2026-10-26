import json
import secrets
import unittest

from agent_foundation.config import ConfigurationError, admin_credentials, load_models
from agent_foundation.deerflow import build_config


class ModelConfigurationTests(unittest.TestCase):
    def test_admin_credentials_are_required(self):
        password = secrets.token_urlsafe(24)
        for env in ({}, {"APP_ADMIN_USERNAME": "sample-user"},
                    {"APP_ADMIN_USERNAME": "sample-user", "APP_ADMIN_PASSWORD": "x" * 8},
                    {"APP_ADMIN_USERNAME": "invalid:name", "APP_ADMIN_PASSWORD": password}):
            with self.subTest(env=tuple(env)), self.assertRaises(ConfigurationError):
                admin_credentials(env)

    def test_secret_reference_and_primary_selection(self):
        model_key = secrets.token_urlsafe(24)
        env = {"MODEL_CONFIG_JSON": json.dumps([
            {"provider": "ollama", "model": "local", "base_url": "http://ollama:11434"},
            {"provider": "openai", "model": "remote", "base_url": "https://example.test/v1", "api_key_env": "REMOTE_KEY"},
        ]), "PRIMARY_MODEL": "remote", "REMOTE_KEY": model_key}
        models = load_models(env)
        self.assertEqual(models[0].model, "remote")
        config = build_config(models[0])
        self.assertEqual(config["models"][0]["api_key"], "$AGENT_RUNTIME_MODEL_KEY")
        self.assertNotIn(model_key, json.dumps(config))

    def test_literal_secret_is_rejected(self):
        env = {"MODEL_CONFIG_JSON": json.dumps([{"provider": "openai", "model": "x", "base_url": "https://example.test/v1", "api_key": secrets.token_urlsafe(24)}])}
        with self.assertRaises(ConfigurationError):
            load_models(env)

    def test_tools_need_authorization(self):
        env = {"MODEL_CONFIG_JSON": '[{"provider":"ollama","model":"local"}]'}
        with self.assertRaises(ConfigurationError):
            build_config(load_models(env)[0], tools=[{"name": "data", "group": "application", "use": "app.tools:data"}])


if __name__ == "__main__":
    unittest.main()
