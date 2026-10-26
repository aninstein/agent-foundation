import os
import secrets
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from agent_foundation.app import create_app


class StarterApiTests(unittest.TestCase):
    def test_authenticated_status_and_wiki(self):
        password = secrets.token_urlsafe(24)
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "APP_DATA_DIR": tmp,
            "APP_ADMIN_USERNAME": "sample-user",
            "APP_ADMIN_PASSWORD": password,
            "MODEL_CONFIG_JSON": '[{"provider":"ollama","model":"local"}]',
            "PRIMARY_MODEL": "local",
        }, clear=True):
            client = TestClient(create_app())
            self.assertEqual(client.get("/v1/status").status_code, 401)
            self.assertEqual(client.get("/readyz").status_code, 200)
            self.assertEqual(client.get("/v1/status", auth=("sample-user", "x" * 32)).status_code, 401)
            self.assertEqual(client.get("/v1/status", auth=("other-user", password)).status_code, 401)
            self.assertTrue(client.get("/v1/status", auth=("sample-user", password)).json()["configured"])
            created = client.put("/v1/wiki/long-term/note.md", auth=("sample-user", password),
                                 json={"text": "Remember this", "source": "user-confirmed"})
            self.assertEqual(created.status_code, 200)
            conflict = client.put("/v1/wiki/long-term/note.md", auth=("sample-user", password),
                                  json={"text": "Overwrite", "source": "user-confirmed"})
            self.assertEqual(conflict.status_code, 409)
            self.assertEqual(client.get("/v1/wiki/long-term/note.md", auth=("sample-user", password)).json()["sha256"],
                             created.json()["sha256"])

    def test_missing_deployment_credentials_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "APP_DATA_DIR": tmp,
            "MODEL_CONFIG_JSON": '[{"provider":"ollama","model":"local"}]',
        }, clear=True):
            client = TestClient(create_app())
            self.assertEqual(client.get("/readyz").status_code, 503)
            self.assertEqual(client.get("/v1/status").status_code, 503)


if __name__ == "__main__":
    unittest.main()
