"""Playable platform rules through the window-free public seam."""

import unittest

from retro_gaming.platformer.game import (
    Game, Ladder, Level, Obstacle, Platform, PlayerInput, Result,
)


def small_level(*, obstacles=()):
    return Level(
        width=400, height=320,
        platforms=(Platform(40, 360, 280), Platform(40, 360, 160)),
        ladders=(Ladder(300, 160, 280),),
        exit_x=70, exit_y=160, start_x=80, start_y=280,
        obstacles=obstacles,
    )


class PlatformerTests(unittest.TestCase):
    def test_walk_jump_and_platform_landing_follow_elapsed_time(self):
        game = Game(small_level())
        self.assertAlmostEqual(game.advance(0.2, PlayerInput(right=True)).player_x, 114, delta=1)
        airborne = game.advance(0.2, PlayerInput(jump=True))
        self.assertLess(airborne.player_y, 240)
        landed = game.advance(0.8)
        self.assertAlmostEqual(landed.player_y, 280, delta=1)
        self.assertEqual(landed.result, Result.PLAYING)

    def test_zero_elapsed_time_does_not_consume_jump_press(self):
        game = Game(small_level())
        still = game.advance(0, PlayerInput(jump=True))
        self.assertEqual(still.player_y, 280)
        airborne = game.advance(0.1, PlayerInput(jump=True))
        self.assertLess(airborne.player_y, 280)

    def test_ladder_reaches_upper_platform_then_exit_wins_and_freezes(self):
        game = Game(small_level())
        game.advance(1.3, PlayerInput(right=True))
        self.assertAlmostEqual(game.state.player_x, 300, delta=2)
        climbed = game.advance(1.0, PlayerInput(up=True))
        self.assertAlmostEqual(climbed.player_y, 160, delta=1)
        won = game.advance(1.35, PlayerInput(left=True))
        self.assertEqual(won.result, Result.VICTORY)
        self.assertEqual(game.advance(5, PlayerInput(right=True)), won)

    def test_obstacle_moves_in_elapsed_time_and_contact_loses(self):
        level = small_level(obstacles=(Obstacle(220, 280, 100, 260, 60),))
        one, split = Game(level), Game(level)
        self.assertAlmostEqual(one.advance(0.5).obstacles[0].x, 250, delta=1)
        split.advance(0.2)
        self.assertAlmostEqual(split.advance(0.3).obstacles[0].x, 250, delta=1)
        contact = one.advance(1.0, PlayerInput(right=True))
        self.assertEqual(contact.result, Result.DEFEAT)
        self.assertEqual(one.advance(2), contact)

    def test_jump_can_clear_obstacle_and_walking_off_edge_loses(self):
        level = small_level(obstacles=(Obstacle(135, 280, 135, 135, 0),))
        game = Game(level)
        game.advance(0.45, PlayerInput(right=True, jump=True))
        self.assertEqual(game.state.result, Result.PLAYING)
        edge = Game(small_level())
        lost = edge.advance(3.0, PlayerInput(left=True))
        self.assertEqual(lost.result, Result.DEFEAT)

    def test_down_climbs_and_invalid_time_is_rejected(self):
        level = Level(400, 320, (Platform(40, 360, 280), Platform(40, 360, 160)),
                      (Ladder(300, 160, 280),), 70, 160, 300, 160, ())
        game = Game(level)
        self.assertGreater(game.advance(0.4, PlayerInput(down=True)).player_y, 160)
        with self.assertRaises(ValueError):
            game.advance(float("nan"))


if __name__ == "__main__":
    unittest.main()
