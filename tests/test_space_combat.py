"""Observable behavior of the standalone space-combat wave."""

import unittest
from dataclasses import replace

from retro_gaming.space_combat.game import Enemy, Game, PlayerInput, Result, Shot


class SpaceCombatTests(unittest.TestCase):
    def test_numeric_speed_and_salvo_cadence_change_play_through_game_advance(self):
        standard = Game()
        configured = Game(score_target=100, enemy_speed_px_per_second=160,
                          salvo_interval_seconds=0.8)
        standard_state = standard.advance(0.8)
        state = configured.advance(0.8)
        self.assertGreater(state.enemies[0].x, standard_state.enemies[0].x)
        self.assertTrue(state.enemy_shots)
        self.assertFalse(standard_state.enemy_shots)
        self.assertEqual(state.score_target, 100)

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

    def test_destroyed_enemy_leaves_a_short_lived_explosion(self):
        game = Game()
        enemy = game.state.enemies[0]
        game.state = replace(game.state, shots=(Shot(enemy.x, enemy.y + 3),))

        hit = game.advance(1 / 120)

        self.assertEqual(len(hit.enemies), 54)
        self.assertEqual(len(hit.explosions), 1)
        self.assertAlmostEqual(hit.explosions[0].x, enemy.x + 80 / 120)
        self.assertEqual(hit.explosions[0].y, enemy.y)
        self.assertEqual(hit.explosions[0].points, 30)
        self.assertEqual(hit.score, 30)
        self.assertEqual(game.advance(0.4).explosions, ())

    def test_formation_uses_classic_rows_and_points(self):
        enemies = Game().state.enemies
        self.assertEqual(len(enemies), 55)
        self.assertEqual([enemies[row * 11].kind for row in range(5)], [0, 1, 1, 2, 2])
        self.assertEqual([enemies[row * 11].points for row in range(5)],
                         [30, 20, 20, 10, 10])

    def test_enemy_wave_bounces_horizontally_without_descending(self):
        single_step = Game()
        split_steps = Game()
        initial = single_step.state.enemies
        one = single_step.advance(20)
        split_steps.advance(8)
        two = split_steps.advance(12)
        self.assertAlmostEqual(one.enemies[0].x, two.enemies[0].x, places=4)
        self.assertAlmostEqual(one.enemies[0].y, two.enemies[0].y, places=4)
        self.assertTrue(all(after.y == before.y for before, after in zip(initial, one.enemies)))
        self.assertNotEqual(one.enemies[0].x, initial[0].x)

    def test_enemy_salvos_and_both_sides_damage_shelters(self):
        game = Game()
        initial = sum(b.health for b in game.state.shelters)
        fired = game.advance(1.3)
        self.assertGreater(len(fired.enemy_shots), 0)
        game.advance(3)
        self.assertLess(sum(b.health for b in game.state.shelters), initial)
        player = Game()
        player.advance(1 / 3, PlayerInput(left=True))
        player.advance(1, PlayerInput(shoot=True))
        self.assertLess(sum(b.health for b in player.state.shelters), initial)

    def test_incoming_shot_costs_a_life_before_formation_reaches_ship(self):
        game = Game()
        game.state = replace(game.state, enemy_shots=(Shot(480, 545),))
        hit = game.advance(1 / 120)
        self.assertEqual(hit.lives, 2)
        self.assertEqual(hit.player_x, 480)
        self.assertGreater(hit.respawn_seconds, 0)
        self.assertTrue(all(enemy.y < 300 for enemy in hit.enemies))

    def test_score_threshold_can_win_with_enemies_still_on_screen(self):
        game = Game(score_target=10)
        game.advance(0.13, PlayerInput(right=True))
        game.advance(0.01, PlayerInput(shoot=True))
        won = game.advance(0.8)
        self.assertEqual(won.result, Result.VICTORY)
        self.assertEqual(won.score, 10)
        self.assertGreater(len(won.enemies), 0)
        self.assertEqual(game.advance(10), won)

    def test_three_lives_respawn_and_final_result_persists(self):
        game = Game()
        previous = game.state.lives
        for _ in range(3000):
            state = game.advance(0.1)
            if state.lives < previous:
                self.assertEqual(state.player_x, 480)
                self.assertEqual(state.lives, previous - 1)
                previous = state.lives
            if state.result is not Result.PLAYING:
                break
        self.assertEqual(state.lives, 0)
        self.assertEqual(state.result, Result.DEFEAT)
        self.assertEqual(game.advance(30, PlayerInput(shoot=True)), state)

    def test_salvos_shelters_and_respawn_are_independent_of_frame_partition(self):
        one, split = Game(), Game()
        expected = one.advance(18.507)
        for dt in (0.001, 0.106, 0.4, 8, 10):
            split.advance(dt)
        self.assertEqual(split.state, expected)

    def test_zero_time_shoot_is_preserved_and_short_direction_taps_are_not_reversed(self):
        game = Game()
        self.assertEqual(len(game.advance(0, PlayerInput(shoot=True)).shots), 1)
        self.assertEqual(len(game.advance(0, PlayerInput(shoot=True)).shots), 1)
        game = Game()
        game.advance(0.004, PlayerInput(right=True))
        changed = game.advance(0.005, PlayerInput(left=True))
        self.assertGreater(changed.player_x, 480)
        self.assertEqual(game.advance(0, PlayerInput(right=True)), changed)

    def test_zero_time_shot_starts_after_previous_elapsed_movement(self):
        game = Game()
        game.advance(0.004, PlayerInput(right=True))
        fired = game.advance(0, PlayerInput(shoot=True))
        self.assertAlmostEqual(fired.player_x, 481.44)
        self.assertAlmostEqual(fired.shots[0].x, 481.44)
        self.assertEqual(fired.shots[0].y, 546)
        self.assertEqual(game.advance(0.005, PlayerInput(shoot=True)).shots, fired.shots)

    def test_score_target_must_be_a_positive_integer(self):
        for value in (0, -1, 1.5, float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Game(score_target=value)

    def test_score_persists_across_waves_until_configured_threshold(self):
        game = Game()
        game.state = replace(game.state, score=990, enemies=(Enemy(500, 100, 2),),
                             shots=(Shot(500, 103),))
        next_wave = game.advance(1 / 120)
        self.assertEqual(next_wave.wave, 2)
        self.assertEqual(next_wave.score, 1000)
        self.assertEqual(next_wave.result, Result.PLAYING)


if __name__ == "__main__":
    unittest.main()
