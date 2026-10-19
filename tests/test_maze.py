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
        self.assertEqual(single.advance(0.01).enemies, (Position(5, 1),))
        split.advance(0.2)
        self.assertEqual(split.advance(0.25).enemies, single.state.enemies)

    def test_contact_with_stationary_enemy_loses_and_freezes(self):
        game = Game(("#####", "#PE.#", "#####"))
        lost = game.advance(0.15, PlayerInput(right=True))
        self.assertEqual(lost.result, Result.DEFEAT)
        self.assertEqual(game.advance(5, PlayerInput(right=True)), lost)

    def test_enemy_reaching_player_loses(self):
        game = Game(("#####", "#EP.#", "#####"))
        lost = game.advance(0.45)
        self.assertEqual(lost.enemies, (Position(2, 1),))
        self.assertEqual(lost.result, Result.DEFEAT)


if __name__ == "__main__":
    unittest.main()
