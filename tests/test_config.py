import json
import tempfile
import unittest
from pathlib import Path

import pygame

from retro_gaming.config import load_config


class TriggerConfigurationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_trigger_cannot_reuse_animator_reset_shortcut(self):
        data = {
            "session_seconds": 300,
            "possession_seconds": 12,
            "warning_seconds": 60,
            "trigger": {"key": "backspace", "modifiers": ["meta", "ctrl", "alt"]},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "remise à zéro"):
                load_config(path)

            data["trigger"]["modifiers"].append("shift")
            path.write_text(json.dumps(data), encoding="utf-8")
            config = load_config(path)
            self.assertEqual(config.trigger_modifiers, ("meta", "ctrl", "alt", "shift"))
