"""Observable behavior of the standalone space-combat wave."""

import unittest

from retro_gaming.space_combat.game import Game, PlayerInput, Result


class SpaceCombatTests(unittest.TestCase):
    def test_player_moves_both_ways_and_stays_inside_the_playfield(self):
        game = Game()
        start = game.state.player_x
        right = game.advance(0.25, PlayerInput(right=True))
        self.assertGreater(right.player_x, start)
        left = game.advance(0.5, PlayerInput(left=True))
        self.assertLess(left.player_x, start)
        game.advance(3, PlayerInput(left=True))
        self.assertGreaterEqual(game.state.player_x, game.state.player_half_width)
        game.advance(3, PlayerInput(right=True))
        self.assertLessEqual(game.state.player_x, game.state.width - game.state.player_half_width)

    def test_shots_remove_enemies_in_their_path(self):
        game = Game()
        original_count = len(game.state.enemies)
        game.advance(0.13, PlayerInput(right=True))
        fired = game.advance(0.01, PlayerInput(shoot=True))
        self.assertGreater(len(fired.shots), 0)
        after_flight = game.advance(0.8)
        self.assertLess(len(after_flight.enemies), original_count)

    def test_enemy_wave_traverses_and_descends_with_elapsed_time(self):
        single_step = Game()
        split_steps = Game()
        initial_y = single_step.state.enemies[0].y
        one = single_step.advance(20)
        split_steps.advance(8)
        two = split_steps.advance(12)
        self.assertAlmostEqual(one.enemies[0].x, two.enemies[0].x, places=4)
        self.assertAlmostEqual(one.enemies[0].y, two.enemies[0].y, places=4)
        self.assertGreater(one.enemies[0].y, initial_y)

    def test_destroying_the_whole_wave_wins_and_freezes_the_result(self):
        game = Game()
        for _ in range(2000):
            state = game.state
            if state.result is not Result.PLAYING:
                break
            target = min(state.enemies, key=lambda enemy: (-enemy.y, enemy.x))
            game.advance(0.02, PlayerInput(
                left=state.player_x > target.x + 8,
                right=state.player_x < target.x - 8,
                shoot=True,
            ))
        self.assertEqual(game.state.result, Result.VICTORY)
        self.assertEqual(game.state.enemies, ())
        finished = game.state
        self.assertEqual(game.advance(30, PlayerInput(shoot=True, right=True)), finished)

    def test_enemy_reaching_the_bottom_loses_and_freezes_the_result(self):
        game = Game()
        state = game.advance(200)
        self.assertEqual(state.result, Result.DEFEAT)
        self.assertTrue(any(enemy.y + 13 >= state.height for enemy in state.enemies))
        self.assertEqual(game.advance(30, PlayerInput(shoot=True)), state)


if __name__ == "__main__":
    unittest.main()
