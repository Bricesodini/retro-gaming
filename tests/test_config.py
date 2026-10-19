import json
import tempfile
import unittest
from pathlib import Path

import pygame

from retro_gaming.config import load_config
from retro_gaming.session import Phase, Session


class TriggerConfigurationTest(unittest.TestCase):
    def test_configured_variants_follow_the_same_session_journey(self):
        common = {
            "session_seconds": 30,
            "possession_seconds": 8,
            "warning_seconds": 10,
            "trigger": {"key": "space", "modifiers": ["ctrl", "alt", "meta"]},
        }
        journeys = []
        with tempfile.TemporaryDirectory() as directory:
            for variant in ("Mystère", "Tension"):
                path = Path(directory) / f"{variant}.json"
                path.write_text(json.dumps({**common, "variant": variant}), encoding="utf-8")
                config = load_config(path)
                session = Session(config.session_seconds, config.possession_seconds,
                                  config.warning_seconds)
                journeys.append([
                    session.advance(0, "declencher_mystere"),
                    session.advance(6, None),
                    session.advance(2, None),
                    session.advance(12, None),
                    session.advance(10, None),
                ])
        self.assertEqual(journeys[0], journeys[1])
        self.assertEqual([state.phase for state in journeys[0]],
                         [Phase.POSSESSION, Phase.POSSESSION, Phase.ELF, Phase.ELF, Phase.FIN])
        self.assertEqual([state.remaining_seconds for state in journeys[0]],
                         [30, 24, 22, 10, 0])
        self.assertEqual([state.events for state in journeys[0]],
                         [(), (), (), ("avertissement",), ("alarme",)])
        self.assertIn("ELF", " ".join(journeys[0][1].messages))
        self.assertIn("Un défi", " ".join(journeys[0][2].messages))

    def test_variant_is_explicit_and_unknown_value_is_rejected(self):
        data = {
            "session_seconds": 300,
            "possession_seconds": 12,
            "warning_seconds": 60,
            "trigger": {"key": "space", "modifiers": ["ctrl", "alt", "meta"]},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            for variant in ("Mystère", "Tension"):
                data["variant"] = variant
                path.write_text(json.dumps(data), encoding="utf-8")
                self.assertEqual(load_config(path).variant, variant)
            data["variant"] = "Horreur"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Mystère.*Tension"):
                load_config(path)
            del data["variant"]
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "variant"):
                load_config(path)

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
            "variant": "Mystère",
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
