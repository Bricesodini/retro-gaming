import json
import tempfile
import unittest
from pathlib import Path

import pygame

from retro_gaming.config import load_config
from retro_gaming.session import Phase, Session


class TriggerConfigurationTest(unittest.TestCase):
    def test_optional_game_numbers_load_and_invalid_values_explain_the_field(self):
        base = {"session_seconds": 300, "possession_seconds": 12,
                "warning_seconds": 60, "variant": "Mystère"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(base), encoding="utf-8")
            defaults = load_config(path).games
            self.assertEqual(defaults.maze.pellet_goal_percent, 100)
            self.assertEqual(defaults.space_combat.score_target, 3000)
            self.assertEqual(defaults.platformer.barrel_interval_seconds, 4)
            base["games"] = {
                "maze": {"pellet_goal_percent": 50, "ghost_step_seconds": 0.9,
                         "power_seconds": 4},
                "space_combat": {"score_target": 1200, "enemy_speed_px_per_second": 100,
                                 "salvo_interval_seconds": 1.1},
                "platformer": {"goal_progress_percent": 80, "barrel_interval_seconds": 5,
                               "barrel_speed_px_per_second": 75,
                               "barrel_speed_cap_px_per_second": 100,
                               "fire_spawn_interval_seconds": 20, "fire_speed_px_per_second": 22},
            }
            path.write_text(json.dumps(base), encoding="utf-8")
            configured = load_config(path).games
            self.assertEqual(configured.maze.pellet_goal_percent, 50)
            self.assertEqual(configured.space_combat.score_target, 1200)
            self.assertEqual(configured.platformer.goal_progress_percent, 80)
            for field, value in (("pellet_goal_percent", 0), ("ghost_step_seconds", -1),
                                 ("power_seconds", "long")):
                bad = json.loads(json.dumps(base))
                bad["games"]["maze"][field] = value
                path.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, field):
                    load_config(path)
            bad = json.loads(json.dumps(base))
            bad["games"]["platformer"]["barrel_speed_cap_px_per_second"] = 70
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "barrel_speed_cap_px_per_second"):
                load_config(path)

    def test_room_digit_loads_and_rejects_invalid_values(self):
        data = {"session_seconds": 30, "possession_seconds": 2,
                "warning_seconds": 5, "variant": "Mystère",
                "room_digit": 8}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(load_config(path).room_digit, 8)
            for invalid in (-1, 10, 1.5, True, "7"):
                data["room_digit"] = invalid
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "chiffre de salle"):
                    load_config(path)

    def test_session_must_fit_arrival_delay_and_possession(self):
        data = {"session_seconds": 20, "possession_seconds": 12,
                "warning_seconds": 5, "variant": "Mystère"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "délai d'arrivée de 10 secondes"):
                load_config(path)

    def test_configured_variants_follow_the_same_session_journey(self):
        common = {
            "session_seconds": 30,
            "possession_seconds": 8,
            "warning_seconds": 10,
        }
        journeys = []
        with tempfile.TemporaryDirectory() as directory:
            for variant in ("Mystère", "Tension"):
                path = Path(directory) / f"{variant}.json"
                path.write_text(json.dumps({**common, "variant": variant}), encoding="utf-8")
                config = load_config(path)
                session = Session(config.session_seconds, config.possession_seconds,
                                  config.warning_seconds)
                journey = [
                    session.advance(600, None),
                    session.advance(0, "declencher_mystere"),
                    session.advance(6, "declencher_mystere"),
                    session.advance(2, None),
                    session.advance(12, None),
                    session.advance(10, None),
                    session.advance(20, "declencher_mystere"),
                    session.advance(0, "reinitialiser"),
                    session.advance(600, None),
                    session.advance(0, "declencher_mystere"),
                    session.advance(6, None),
                    session.advance(2, None),
                    session.advance(12, None),
                    session.advance(10, None),
                    session.advance(10, None),
                ]
                journeys.append(journey)
        self.assertEqual(journeys[0], journeys[1])
        self.assertEqual([state.phase for state in journeys[0]],
                         [Phase.LABORATOIRE, Phase.POSSESSION, Phase.POSSESSION,
                          Phase.ELF, Phase.ELF, Phase.FIN, Phase.FIN,
                          Phase.LABORATOIRE, Phase.LABORATOIRE,
                          Phase.POSSESSION, Phase.POSSESSION, Phase.ELF,
                          Phase.ELF, Phase.FIN, Phase.FIN])
        self.assertEqual([state.remaining_seconds for state in journeys[0]],
                         [None, 30, 24, 22, 10, 0, 0, None, None,
                          30, 24, 22, 10, 0, 0])
        self.assertEqual([state.events for state in journeys[0]],
                         [(), (), (), (), ("avertissement",), ("alarme",),
                          (), (), (), (), (), (), ("avertissement",),
                          ("alarme",), ()])
        self.assertIn("ELF", " ".join(journeys[0][2].messages))
        self.assertIn("Un défi", " ".join(journeys[0][3].messages))
        self.assertEqual(journeys[0][3].messages, journeys[0][4].messages)
        self.assertEqual(journeys[0][7].messages, ())
        self.assertEqual(journeys[0][9].messages, ())
        self.assertEqual(journeys[0][11].messages, journeys[0][12].messages)

    def test_variant_is_explicit_and_unknown_value_is_rejected(self):
        data = {
            "session_seconds": 300,
            "possession_seconds": 12,
            "warning_seconds": 60,
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

    def test_obsolete_trigger_is_rejected(self):
        data = {
            "session_seconds": 300,
            "possession_seconds": 12,
            "warning_seconds": 60,
            "variant": "Mystère",
            "trigger": {"key": "space", "modifiers": ["meta", "ctrl", "alt"]},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "trigger n'est plus configurable"):
                load_config(path)
