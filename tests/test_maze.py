"""Player-visible rules at the maze game's window-free seam."""

import unittest

from retro_gaming.maze.game import Game, PlayerInput, Position, Result


class MazeTests(unittest.TestCase):
    def test_player_moves_in_four_directions_and_walls_block(self):
        game = Game((
            "#####",
            "#P..#",
            "#.#.#",
            "#...#",
            "#####",
        ))
        self.assertEqual(game.advance(0.15, PlayerInput(right=True)).player,
                         Position(2, 1))
        self.assertEqual(game.advance(0.15, PlayerInput(down=True)).player,
                         Position(2, 1))
        self.assertEqual(game.advance(0.15, PlayerInput(left=True)).player,
                         Position(1, 1))
        self.assertEqual(game.advance(0.15, PlayerInput(down=True)).player,
                         Position(1, 2))
        self.assertEqual(game.advance(0.15, PlayerInput(up=True)).player,
                         Position(1, 1))
        self.assertEqual(game.advance(1, PlayerInput(left=True)).player,
                         Position(1, 1))

    def test_collecting_pellets_updates_board_and_last_one_wins(self):
        game = Game(("#####", "#P..#", "#####"))
        first = game.advance(0.15, PlayerInput(right=True))
        self.assertEqual(first.pellets, frozenset({Position(3, 1)}))
        self.assertEqual(first.result, Result.PLAYING)
        won = game.advance(0.15, PlayerInput(right=True))
        self.assertEqual(won.pellets, frozenset())
        self.assertEqual(won.result, Result.VICTORY)
        self.assertEqual(game.advance(5, PlayerInput(left=True)), won)

    def test_enemy_moves_along_corridor_with_elapsed_time(self):
        rows = ("#######", "#P..E.#", "#######")
        single = Game(rows)
        split = Game(rows)
        self.assertEqual(single.advance(0.44).enemies, (Position(4, 1),))
        self.assertEqual(single.advance(0.01).enemies, (Position(3, 1),))
        split.advance(0.2)
        self.assertEqual(split.advance(0.25).enemies, single.state.enemies)

    def test_power_pellet_makes_ghost_edible_then_ghost_returns(self):
        game = Game(("#########", "#PoE....#", "#########"))
        powered = game.advance(0.15, PlayerInput(right=True))
        self.assertEqual(powered.score, 50)
        self.assertGreater(powered.frightened_seconds, 0)
        self.assertEqual(powered.ghosts[0].mode, "frightened")
        eaten = game.advance(0.15, PlayerInput(right=True))
        self.assertEqual(eaten.lives, 3)
        self.assertEqual(eaten.score, 250)
        self.assertEqual(eaten.ghosts[0].mode, "returning")
        game.advance(0.3, PlayerInput(right=True))
        returned = game.advance(1.8)
        self.assertNotEqual(returned.ghosts[0].mode, "returning")

    def test_default_board_has_four_distinct_ghosts_and_reachable_pellets(self):
        game = Game()
        self.assertEqual(len(game.state.ghosts), 4)
        self.assertEqual(len({g.behavior for g in game.state.ghosts}), 4)
        seen = {game.state.player}
        todo = list(seen)
        while todo:
            p = todo.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = Position(p.x + dx, p.y + dy)
                if (0 <= q.y < len(game.state.rows) and 0 <= q.x < len(game.state.rows[0])
                        and game.state.rows[q.y][q.x] != "#" and q not in seen):
                    seen.add(q)
                    todo.append(q)
        self.assertTrue((game.state.pellets | game.state.power_pellets) <= seen)
        self.assertEqual(game.advance(6).frightened_seconds, 0)

    def test_power_expiry_and_respawn_are_independent_of_frame_partition(self):
        rows = ("#########", "#Po.....#", "#########")
        one, split = Game(rows), Game(rows)
        one.advance(0.15, PlayerInput(right=True))
        split.advance(0.05, PlayerInput(right=True))
        split.advance(0.1, PlayerInput(right=True))
        self.assertEqual(one.advance(6.03).frightened_seconds, 0)
        for dt in (0.03, 1, 2, 3):
            split.advance(dt)
        self.assertEqual(one.state, split.state)
        one, split = Game(("#####", "#PE.#", "#####")), Game(("#####", "#PE.#", "#####"))
        expected = one.advance(2.507, PlayerInput(right=True))
        for dt in (0.001, 0.006, 0.5, 1, 1):
            split.advance(dt, PlayerInput(right=True))
        self.assertEqual(expected, split.state)

    def test_four_ghosts_choose_different_routes_without_crossing_walls(self):
        one, split = Game(), Game()
        starts = one.state.enemies
        expected = one.advance(2.7)
        for _ in range(27):
            split.advance(0.1)
        self.assertEqual(expected.enemies, split.state.enemies)
        self.assertEqual(len(set(expected.enemies)), 4)
        self.assertTrue(all(a != b for a, b in zip(starts, expected.enemies)))
        for p in expected.enemies:
            self.assertNotEqual(expected.rows[p.y][p.x], "#")

    def test_contact_costs_one_life_then_respawns_and_third_loss_freezes(self):
        game = Game(("#####", "#PE.#", "#####"))
        for remaining in (2, 1, 0):
            state = game.advance(0.15, PlayerInput(right=True))
            self.assertEqual(state.lives, remaining)
            if remaining:
                self.assertEqual(state.player, Position(1, 1))
                self.assertEqual(state.result, Result.PLAYING)
                game.advance(1.0)  # grace period after respawn
        self.assertEqual(state.result, Result.DEFEAT)
        self.assertEqual(game.advance(5, PlayerInput(right=True)), state)


if __name__ == "__main__":
    unittest.main()
