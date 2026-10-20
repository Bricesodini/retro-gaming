#!/bin/zsh

set -e
PROJECT_DIR="${0:A:h}"
cd "$PROJECT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  print "Environnement Python introuvable. Suivre d'abord les étapes d'installation du README.md."
  read "?Appuyer sur Entrée pour fermer cette fenêtre. "
  exit 1
fi

exec .venv/bin/python -m retro_gaming --fullscreen "$@"
