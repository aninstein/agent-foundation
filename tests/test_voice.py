import secrets
import unittest

from agent_foundation.config import ConfigurationError
from agent_foundation.voice import speech_endpoint


class VoiceConfigurationTests(unittest.TestCase):
    def test_disabled_by_default(self):
        self.assertIsNone(speech_endpoint("stt", {}))

    def test_key_must_be_server_environment_reference(self):
        env = {"VOICE_STT_BASE_URL": "https://voice.example/v1", "VOICE_STT_MODEL": "asr",
               "VOICE_STT_API_KEY_ENV": "VOICE_KEY", "VOICE_KEY": secrets.token_urlsafe(24)}
        self.assertEqual(speech_endpoint("stt", env).key_env, "VOICE_KEY")
        del env["VOICE_KEY"]
        with self.assertRaises(ConfigurationError):
            speech_endpoint("stt", env)


if __name__ == "__main__":
    unittest.main()
