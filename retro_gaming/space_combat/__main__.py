"""Launch a standalone round with an operator-adjustable score objective."""

import argparse

from retro_gaming.space_combat.game import DEFAULT_SCORE_TARGET
from retro_gaming.space_combat.window import run


def positive_score(value: str) -> int:
    try:
        score = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Le score cible doit être un entier positif.") from None
    if score <= 0:
        raise argparse.ArgumentTypeError("Le score cible doit être un entier positif.")
    return score


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combat spatial autonome — manche de trois vies.")
    parser.add_argument("--score-target", type=positive_score, default=DEFAULT_SCORE_TARGET,
                        help=f"score de victoire (défaut : {DEFAULT_SCORE_TARGET}, à calibrer en jeu)")
    run(score_target=parser.parse_args().score_target)
