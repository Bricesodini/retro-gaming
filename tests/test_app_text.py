import unittest
from unittest.mock import patch

import pygame

from retro_gaming.app import _draw_countdown, _draw_game, _ordinary_key, _reset_matches, _wrap_text
from retro_gaming.space_combat.game import Game


class AppTextLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()
        cls.possession_font = pygame.font.SysFont(
            "menlo,monaco,couriernew,monospace", 22, bold=True)
        cls.elf_font = pygame.font.SysFont(
            "menlo,monaco,couriernew,monospace", 25, bold=True)

    def assert_lines_fit(self, lines, font, width):
        self.assertGreater(len(lines), 1)
        for line in lines:
            with self.subTest(line=line):
                self.assertLessEqual(font.size(line)[0], width)

    def test_possession_message_stays_inside_its_left_panel(self):
        text = "DEMOGORGON // Ce terminal m'appartient. Vous êtes pris au piège."

        lines = _wrap_text(text, self.possession_font, 690)

        self.assert_lines_fit(lines, self.possession_font, 690)

    def test_elf_heading_stays_in_its_column_beside_the_portrait(self):
        text = "ELF // C'est moi, Elf. Je retiens cette présence."

        lines = _wrap_text(text, self.elf_font, 750)

        self.assert_lines_fit(lines, self.elf_font, 750)

    def test_countdown_is_green_before_arrival_and_in_free_mode(self):
        surface = pygame.Surface((1200, 760))
        with patch("retro_gaming.app._label") as label:
            _draw_countdown(surface, 42, False, False)

        countdown = next(call for call in label.call_args_list
                         if call.args[2] == "00:42")
        self.assertGreaterEqual(countdown.args[1].get_height(), 48)
        self.assertEqual(countdown.args[4], (91, 232, 153))

        with patch("retro_gaming.app._label") as label:
            _draw_countdown(surface, 42, False, True, free_mode=True)
        countdown = next(call for call in label.call_args_list
                         if call.args[2] == "00:42")
        self.assertEqual(countdown.args[4], (91, 232, 153))

    def test_countdown_turns_red_when_entity_arrives(self):
        surface = pygame.Surface((1200, 760))
        with patch("retro_gaming.app._label") as label:
            _draw_countdown(surface, 42, False, True)
        countdown = next(call for call in label.call_args_list
                         if call.args[2] == "00:42")
        self.assertEqual(countdown.args[4], (255, 80, 80))

    def test_reset_chord_takes_priority_over_ordinary_first_key(self):
        modifiers = pygame.KMOD_CTRL | pygame.KMOD_ALT | pygame.KMOD_GUI
        reset = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=modifiers)
        letter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, mod=0)
        modified_letter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a,
                                             mod=pygame.KMOD_CTRL)
        shift = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LSHIFT,
                                   mod=pygame.KMOD_SHIFT)
        escape = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0)
        self.assertTrue(_reset_matches(reset))
        self.assertFalse(_ordinary_key(reset))
        self.assertTrue(_ordinary_key(letter))
        self.assertTrue(_ordinary_key(modified_letter))
        self.assertFalse(_ordinary_key(shift))
        self.assertFalse(_ordinary_key(escape))


if __name__ == "__main__":
    unittest.main()
