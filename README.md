# Laboratoire 1986 — POC d'accueil

Une fenêtre Pygame CE présente un terminal de laboratoire fictif pendant l'introduction de l'animateur. Les diagnostics défilent seuls. La session est en attente : aucun chronomètre n'est lancé et Elf n'apparaît pas encore.

Cette première tranche ne lance pas la possession et ne contient aucun jeu. Les éléments graphiques sont dessinés par l'application ; aucune ROM ni aucun média de la série n'est utilisé.

## Versions

- CPython **3.11.11** (`.python-version`)
- pygame-ce **2.5.8** (`requirements.txt`)

L'installation et la boucle d'affichage suivent la [documentation officielle pygame-ce](https://pyga.me/docs/). L'installation réelle de ces deux versions a été vérifiée sur macOS Apple Silicon.

## Installer

Sur **macOS Apple Silicon** ou **Linux x86-64**, depuis la racine du dépôt, installer d'abord [`uv`](https://docs.astral.sh/uv/getting-started/installation/), puis exécuter :

```sh
uv python install 3.11.11
uv venv --python 3.11.11 --seed .venv
.venv/bin/python -m pip install --requirement requirements.txt
```

`uv` télécharge la version exacte de Python, puis crée l'environnement isolé `.venv`. La dépendance Pygame CE est fixée dans `requirements.txt`. Sur Linux, lancer la fenêtre dans une session graphique disposant d'un affichage ; le rendu sur Omarchy n'a pas encore été essayé.

## Lancer et fermer

```sh
.venv/bin/python -m retro_gaming
```

Fermer avec **Échap** ou le bouton de fermeture de la fenêtre. Les lignes du journal et la courbe de signal évoluent automatiquement tant que la fenêtre reste ouverte. Le pied de page indique « SESSION EN ATTENTE » ; aucune durée ne s'écoule à l'accueil.

## Vérification

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Le test vérifie le parcours observable de la session : phase laboratoire, absence de temps restant actif et absence d'alertes, même après une longue attente simulée. Ce point de test pourra recevoir les futures actions de l'animateur et les transitions de la session.

### État des plateformes

| Plateforme | État constaté |
| --- | --- |
| macOS Apple Silicon | CPython 3.11.11 et pygame-ce 2.5.8 installés dans `.venv` ; fenêtre Cocoa 1200 × 760 rendue et fermée normalement. |
| Linux x86-64 / Omarchy | Cible prévue, **non exécutée**. Une roue `manylinux2014_x86_64` de pygame-ce 2.5.8 pour CPython 3.11 est disponible au téléchargement ; affichage, clavier et installation sur la borne restent à vérifier. |
