"""Playable platform rules through the window-free public seam."""

import unittest

from retro_gaming.platformer.game import (
    Barrel, DEFAULT_LEVEL, Game, Ladder, Level, Platform, PlayerInput, Result,
)


def small_level(*, barrels=()):
    return Level(
        width=400, height=320,
        platforms=(Platform(40, 360, 280), Platform(40, 360, 160)),
        ladders=(Ladder(300, 160, 280),),
        exit_x=70, exit_y=160, start_x=80, start_y=280,
        barrels=barrels,
    )


class PlatformerTests(unittest.TestCase):
    def test_level_tuning_updates_existing_and_future_hazards(self):
        tuned = DEFAULT_LEVEL.with_tuning(
            barrel_interval_seconds=5, barrel_speed_px_per_second=70,
            barrel_speed_cap_px_per_second=100, fire_spawn_interval_seconds=20,
            fire_speed_px_per_second=39)
        state = Game(tuned).state
        self.assertEqual(state.level.barrel_interval, 5)
        self.assertEqual(state.level.barrels[0].speed, 70)
        self.assertEqual(state.level.fire_enemies[0].speed, 42)
        self.assertEqual(state.level.fire_speed, 39)
        self.assertEqual(DEFAULT_LEVEL.barrels[0].speed, 85)

    def test_numeric_progress_goal_can_end_at_a_lower_reached_height(self):
        game = Game(small_level(), goal_progress_percent=50)
        state = game.advance(1.29, PlayerInput(right=True))
        self.assertEqual(state.result, Result.PLAYING)
        state = game.advance(0.5, PlayerInput(up=True))
        self.assertEqual(state.result, Result.VICTORY)

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

    def test_barrel_rolls_in_elapsed_time_and_contact_costs_a_life(self):
        level = small_level(barrels=(Barrel(220, 280, 0, speed=60),))
        one, split = Game(level), Game(level)
        self.assertAlmostEqual(one.advance(0.5).barrels[0].x, 250, delta=1)
        split.advance(0.2)
        self.assertAlmostEqual(split.advance(0.3).barrels[0].x, 250, delta=1)
        contact = one.advance(1.5, PlayerInput(right=True))
        self.assertEqual(contact.lives, 2)
        self.assertEqual(contact.result, Result.PLAYING)

    def test_jump_can_clear_barrel_and_walking_off_edge_uses_three_lives(self):
        level = small_level(barrels=(Barrel(135, 280, 0, speed=0),))
        game = Game(level)
        game.advance(0.45, PlayerInput(right=True, jump=True))
        self.assertEqual(game.state.result, Result.PLAYING)
        edge = Game(small_level())
        lost = edge.advance(12.0, PlayerInput(left=True))
        self.assertEqual(lost.result, Result.DEFEAT)

    def test_walk_follows_sloped_girder(self):
        level = Level(400, 320, (Platform(40, 360, 250, slope=0.1),), (),
                      350, 281, 80, 254)
        game = Game(level)
        state = game.advance(1, PlayerInput(right=True))
        self.assertAlmostEqual(state.player_x, 250, delta=1)
        self.assertAlmostEqual(state.player_y, 271, delta=1)

    def test_barrels_fall_at_edges_and_every_third_can_use_a_ladder(self):
        falling = Game(small_level(barrels=(Barrel(350, 160, 1, speed=120),)))
        edge = falling.advance(0.2).barrels[0]
        self.assertEqual(edge.phase, "falling")
        lower = falling.advance(0.7).barrels[0]
        self.assertEqual(lower.platform, 0)
        self.assertEqual(lower.direction, -1)
        ladder = Game(small_level(barrels=(Barrel(280, 160, 1, speed=60, serial=3),)))
        descending = ladder.advance(0.5).barrels[0]
        self.assertEqual(descending.phase, "ladder")
        self.assertEqual(descending.x, 300)
        self.assertGreater(descending.y, 160)
        self.assertEqual(ladder.advance(1.5).barrels[0].platform, 0)

    def test_launcher_pressure_increases_while_climbing(self):
        from dataclasses import replace
        game = Game(replace(small_level(), barrel_interval=3.2))
        initial_interval = game.state.launch_interval
        game.advance(1.3, PlayerInput(right=True))
        climbing = game.advance(0.6, PlayerInput(up=True))
        self.assertTrue(climbing.climbing)
        self.assertGreater(climbing.progress, 0.5)
        self.assertLess(climbing.launch_interval, initial_interval)
        fired = game.advance(0.8)
        self.assertGreater(fired.barrels_launched, 0)
        self.assertGreater(len(fired.barrels), 0)

    def test_three_collisions_respawn_at_start_then_defeat_freezes(self):
        game = Game(small_level(barrels=(Barrel(120, 280, 0, speed=0),)))
        for lives in (2, 1, 0):
            state = game.advance(0.15, PlayerInput(right=True))
            self.assertEqual(state.lives, lives)
            self.assertEqual(state.player_x, 80)
            if lives:
                game.advance(1.0)
        self.assertEqual(state.result, Result.DEFEAT)
        self.assertEqual(game.advance(20, PlayerInput(jump=True)), state)

    def test_fixed_step_is_independent_of_frame_partition_including_jump(self):
        one, split = Game(small_level()), Game(small_level())
        buttons = PlayerInput(right=True, jump=True)
        expected = one.advance(0.503, buttons)
        for delta in (0.001, 0.052, 0.15, 0.3):
            split.advance(delta, buttons)
        self.assertEqual(expected, split.state)

    def test_barrel_ladder_and_collision_results_do_not_depend_on_frame_partition(self):
        for barrel in (Barrel(280, 160, 1, speed=60, serial=3),
                       Barrel(120, 280, 0, speed=0)):
            one, split = Game(small_level(barrels=(barrel,))), Game(small_level(barrels=(barrel,)))
            buttons = PlayerInput(right=True)
            expected = one.advance(2.507, buttons)
            for dt in (0.001, 0.006, 0.5, 1, 1):
                split.advance(dt, buttons)
            self.assertEqual(expected, split.state)

    def test_short_tap_and_jump_press_survive_an_input_change_between_ticks(self):
        game = Game(small_level())
        game.advance(0.004, PlayerInput(right=True, jump=True))
        changed = game.advance(0.005, PlayerInput(left=True))
        self.assertGreater(changed.player_x, 80)
        self.assertLess(changed.player_y, 280)
        self.assertEqual(game.advance(0, PlayerInput(right=True)), changed)

    def test_all_default_slopes_and_ladders_connect_to_princess(self):
        from dataclasses import replace
        game = Game(replace(DEFAULT_LEVEL, barrel_interval=None, fire_enemies=(), fire_interval=None, barrels=()))
        for floor, target in enumerate((750, 110, 750, 110, 750)):
            ladder = next(l for l in DEFAULT_LEVEL.ladders if l.x == target
                          and abs(l.bottom - DEFAULT_LEVEL.platforms[floor].height_at(target)) < 1)
            distance = ladder.x - game.state.player_x
            game.advance(abs(distance) / 170, PlayerInput(left=distance < 0, right=distance > 0))
            game.advance((ladder.bottom - ladder.top) / 145 + 0.02, PlayerInput(up=True))
            if floor == len(DEFAULT_LEVEL.platforms) - 2:
                self.assertLessEqual(game.state.player_y, ladder.top)
                self.assertGreater(game.state.player_y, ladder.top - 4)
            else:
                self.assertAlmostEqual(game.state.player_y, ladder.top, delta=0.1)
        rescue_ladder = DEFAULT_LEVEL.ladders[-1]
        game.advance((rescue_ladder.bottom - rescue_ladder.top) / 145 + 0.02, PlayerInput(up=True))
        distance = DEFAULT_LEVEL.exit_x - game.state.player_x
        game.advance(abs(distance) / 170 + 0.1, PlayerInput(left=distance < 0, right=distance > 0))
        self.assertEqual(game.state.result, Result.VICTORY)

    def test_fire_enemy_chases_player_on_a_girder_and_contact_costs_one_life(self):
        from dataclasses import replace
        from retro_gaming.platformer.game import FireEnemy
        level = replace(small_level(), fire_enemies=(FireEnemy(160, 280, 0, speed=40),))
        game = Game(level)
        chasing = game.advance(0.5)
        self.assertAlmostEqual(chasing.fire_enemies[0].x, 140, delta=1)
        hit = game.advance(0.3, PlayerInput(right=True))
        self.assertEqual(hit.lives, 2)
        self.assertEqual(hit.player_x, 80)
        self.assertEqual(hit.result, Result.PLAYING)

    def test_fire_enemy_uses_ladder_to_follow_player_between_floors(self):
        from dataclasses import replace
        from retro_gaming.platformer.game import FireEnemy
        level = replace(small_level(), fire_enemies=(FireEnemy(300, 160, 1, speed=60),))
        game = Game(level)
        climbing = game.advance(0.5).fire_enemies[0]
        self.assertEqual(climbing.ladder, 0)
        self.assertGreater(climbing.y, 160)
        self.assertLess(climbing.y, 280)
        lower = game.advance(1.7).fire_enemies[0]
        self.assertEqual(lower.platform, 0)
        self.assertEqual(lower.ladder, -1)
        self.assertLess(lower.x, 300)

    def test_fire_spawn_is_bounded_and_enemies_can_be_jumped(self):
        from dataclasses import replace
        from retro_gaming.platformer.game import FireEnemy
        level = replace(small_level(), start_x=300, start_y=160, fire_interval=0.3, oil_x=55)
        game = Game(level)
        spawned = game.advance(1.3)
        self.assertEqual(len(spawned.fire_enemies), 4)
        self.assertEqual(game.advance(0.2).fire_spawned, 4)
        jumper = Game(replace(small_level(), fire_enemies=(FireEnemy(135, 280, 0, speed=0),)))
        jumped = jumper.advance(0.45, PlayerInput(right=True, jump=True))
        self.assertEqual(jumped.lives, 3)

    def test_ape_winds_up_then_releases_barrel_and_player_pose_follows_input(self):
        from dataclasses import replace
        level = replace(small_level(), barrel_interval=2.0)
        game = Game(level)
        waiting = game.advance(1.8)
        self.assertEqual(waiting.ape_action, "windup")
        released = game.advance(0.21)
        self.assertEqual(released.ape_action, "throw")
        self.assertEqual(released.barrels_launched, 1)
        self.assertGreater(len(released.barrels), 0)
        walking = game.advance(0.1, PlayerInput(right=True))
        self.assertEqual(walking.player_motion, "walk")
        self.assertEqual(walking.player_facing, 1)
        jumping = game.advance(0.1, PlayerInput(jump=True))
        self.assertEqual(jumping.player_motion, "jump")

    def test_default_ladders_stay_at_alternating_edges_and_face_downhill_barrels(self):
        game = Game()
        self.assertEqual(len(game.state.fire_enemies), 2)
        self.assertEqual(game.state.lives, 3)
        self.assertEqual(len(DEFAULT_LEVEL.ladders), len(DEFAULT_LEVEL.platforms))
        previous_x = DEFAULT_LEVEL.start_x
        for lower, upper, ladder in zip(DEFAULT_LEVEL.platforms, DEFAULT_LEVEL.platforms[1:], DEFAULT_LEVEL.ladders):
            self.assertTrue(ladder.x < 170 or ladder.x > 690)
            self.assertAlmostEqual(ladder.top, upper.height_at(ladder.x))
            self.assertAlmostEqual(ladder.bottom, lower.height_at(ladder.x))
            self.assertLess(lower.slope * (ladder.x - previous_x), 0)
            previous_x = ladder.x

    def test_barrel_rolls_down_slope_even_when_initial_heading_points_uphill(self):
        from dataclasses import replace
        level = replace(small_level(),
                        platforms=(Platform(40, 360, 250, slope=-0.08),), ladders=(),
                        start_x=80, start_y=246.8, exit_x=350, exit_y=225.2,
                        barrels=(Barrel(250, 233.2, 0, direction=1, speed=80),))
        game = Game(level)
        rolling = game.advance(0.5).barrels[0]
        self.assertLess(rolling.x, 250)
        self.assertGreater(rolling.y, 233.2)
        self.assertEqual(rolling.direction, -1)
        self.assertGreater(rolling.speed, 80)
        self.assertAlmostEqual(rolling.y, level.platforms[0].height_at(rolling.x))

    def test_fire_and_animation_state_are_independent_of_frame_partition(self):
        from dataclasses import replace
        level = replace(DEFAULT_LEVEL, barrels=(), barrel_interval=None, fire_interval=7)
        one, split = Game(level), Game(level)
        expected = one.advance(7.507)
        for dt in (0.001, 0.006, 0.5, 2, 5):
            split.advance(dt)
        self.assertEqual(expected, split.state)
        self.assertGreater(expected.fire_spawned, 0)
        self.assertGreater(len(expected.fire_enemies), 2)

    def test_fire_enemy_three_lives_and_respawn_pause_preserve_final_result(self):
        from dataclasses import replace
        from retro_gaming.platformer.game import FireEnemy
        game = Game(replace(small_level(), fire_enemies=(FireEnemy(120, 280, 0, speed=0),)))
        for lives in (2, 1, 0):
            state = game.advance(0.15, PlayerInput(right=True))
            self.assertEqual(state.lives, lives)
            self.assertEqual(state.player_x, 80)
            if lives:
                self.assertEqual(game.advance(0.5).fire_enemies, state.fire_enemies)
                game.advance(0.5)
        self.assertEqual(state.result, Result.DEFEAT)
        self.assertEqual(game.advance(20, PlayerInput(jump=True)), state)

    def test_player_can_jump_a_downhill_barrel_then_reach_the_edge_ladder(self):
        from dataclasses import replace
        level = replace(DEFAULT_LEVEL, platforms=DEFAULT_LEVEL.platforms[:2],
                        ladders=DEFAULT_LEVEL.ladders[:1], barrels=DEFAULT_LEVEL.barrels[:1],
                        barrel_interval=None, fire_enemies=(), fire_interval=None,
                        exit_x=750, exit_y=DEFAULT_LEVEL.ladders[0].top, rescue_platform=None)
        game = Game(level)
        for _ in range(900):
            state = game.state
            if state.result is not Result.PLAYING:
                break
            if abs(state.player_x - 750) < 2:
                buttons = PlayerInput(up=True)
            else:
                grounded = abs(state.player_y - level.platforms[0].height_at(state.player_x)) < 0.5
                incoming = any(0 < barrel.x - state.player_x < barrel.speed * 0.35 + 10 and barrel.platform == 0
                               for barrel in state.barrels)
                buttons = PlayerInput(right=grounded and not incoming,
                                      jump=grounded and incoming)
            game.advance(1 / 60, buttons)
        self.assertEqual(game.state.result, Result.VICTORY)
        self.assertEqual(game.state.lives, 3)

    def test_barrel_descends_every_default_ramp_without_ever_rolling_uphill(self):
        from dataclasses import replace
        top = DEFAULT_LEVEL.platforms[-1]
        level = replace(DEFAULT_LEVEL, barrel_interval=None, fire_interval=None, fire_enemies=(),
                        barrels=(Barrel(150, top.height_at(150), 5),))
        game = Game(level)
        visited = {5}
        previous_y = game.state.barrels[0].y
        for _ in range(1000):
            barrel = game.advance(0.05).barrels[0]
            self.assertGreaterEqual(barrel.y + 1e-8, previous_y)
            previous_y = barrel.y
            visited.add(barrel.platform)
            if barrel.platform == 0:
                break
        self.assertEqual(visited, {0, 1, 2, 3, 4, 5})

    def test_burning_oil_drum_is_a_real_hazard_and_can_be_jumped(self):
        from dataclasses import replace
        level = replace(small_level(), fire_interval=10, oil_x=120)
        walker = Game(level)
        self.assertEqual(walker.advance(0.15, PlayerInput(right=True)).lives, 2)
        jumper = Game(level)
        jumper.advance(0.14, PlayerInput(jump=True))
        clear = jumper.advance(0.4, PlayerInput(right=True, jump=True))
        self.assertEqual(clear.lives, 3)
        self.assertGreater(clear.player_x, 120)

    def test_princess_has_a_raised_terrace_reached_by_the_edge_ladder(self):
        from dataclasses import replace
        terrace = DEFAULT_LEVEL.rescue_platform
        self.assertIsNotNone(terrace)
        self.assertLess(terrace.y, DEFAULT_LEVEL.platforms[-1].y - 60)
        ramp = DEFAULT_LEVEL.platforms[-1]
        level = replace(DEFAULT_LEVEL, start_x=750, start_y=ramp.height_at(750),
                        barrels=(), barrel_interval=None, fire_enemies=(), fire_interval=None)
        game = Game(level)
        self.assertEqual(game.state.result, Result.PLAYING)
        climbed = game.advance(0.8, PlayerInput(up=True))
        self.assertAlmostEqual(climbed.player_y, terrace.y, delta=0.1)
        won = game.advance(0.6, PlayerInput(left=True))
        self.assertEqual(won.result, Result.VICTORY)

    def test_summit_launches_leave_time_between_barrels(self):
        from dataclasses import replace
        level = replace(small_level(), barrel_interval=2.8, barrel_speed=0)
        game = Game(level)
        game.advance(1.3, PlayerInput(right=True))
        upper = game.advance(1, PlayerInput(up=True))
        self.assertGreaterEqual(upper.launch_interval, 2.2)
        launched_before = upper.barrels_launched
        later = game.advance(6.5)
        self.assertLessEqual(later.barrels_launched - launched_before, 3)
        self.assertEqual(later.lives, 3)

    def test_down_climbs_and_invalid_time_is_rejected(self):
        level = Level(400, 320, (Platform(40, 360, 280), Platform(40, 360, 160)),
                      (Ladder(300, 160, 280),), 70, 160, 300, 160, ())
        game = Game(level)
        self.assertGreater(game.advance(0.4, PlayerInput(down=True)).player_y, 160)
        with self.assertRaises(ValueError):
            game.advance(float("nan"))


if __name__ == "__main__":
    unittest.main()
