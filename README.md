# Laboratoire 1986 — POC Mystère

Une fenêtre Pygame CE présente le terminal de laboratoire pendant l'introduction. L'animateur déclenche discrètement la possession Mystère ; les diagnostics se dérèglent, des interférences et des racines apparaissent progressivement, puis Elf prend contact et annonce un défi. Cette tranche s'arrête à cette annonce : aucun jeu n'est encore disponible.

## Versions et installation

- CPython **3.11.11** (`.python-version`)
- pygame-ce **2.5.8** (`requirements.txt`)

Depuis la racine du dépôt, avec [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installé :

```sh
uv python install 3.11.11
uv venv --python 3.11.11 --seed .venv
.venv/bin/python -m pip install --requirement requirements.txt
```

Ces versions ont été installées et essayées sur macOS Apple Silicon. Sur Linux, une session graphique et une sortie audio compatibles SDL sont nécessaires ; Omarchy reste à essayer.

## Démontrer le parcours

```sh
.venv/bin/python -m retro_gaming
```

L'accueil affiche des diagnostics autonomes, sans temps actif. Avec la fenêtre au premier plan, appuyer sur **Contrôle + Option + Commande + Espace** sur Mac pour commencer. Le chronomètre de session démarre alors, y compris pendant les douze secondes initiales de possession. Un appui prolongé ou répété ne relance rien. Elf apparaît ensuite avec un texte qui reste affiché. Fermer avec **Échap** ou le bouton de la fenêtre.

Les effets visuels et les trois sons brefs sont produits par le code. Il n'y a ni voix, ni ROM, ni média extrait de la série. La suite du POC (expiration, alarme, remise à zéro, variante Tension) sera traitée dans les tickets suivants.

## Configuration

Modifier `config.json` avant le lancement, ou fournir un autre fichier :

```sh
.venv/bin/python -m retro_gaming --config /chemin/vers/ma-configuration.json
```

Le fichier contient `session_seconds` (300 par défaut), `possession_seconds` (12), et `trigger`. Le temps de possession doit être positif et inférieur au temps de session. `trigger.key` est un nom de touche pygame-ce comme `space` ; `trigger.modifiers` accepte `ctrl`, `alt`, `meta` (Commande sur Mac) et `shift`. Exemple de combinaison alternative si le système intercepte le raccourci initial :

```json
{"session_seconds": 300, "possession_seconds": 12, "trigger": {"key": "space", "modifiers": ["ctrl", "alt", "shift"]}}
```

Cette alternative est configurable mais n'a pas été essayée sur Omarchy. Une configuration invalide affiche une erreur avant d'ouvrir la fenêtre.

## Vérification

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Les tests de session contrôlent le temps sans attendre : accueil inactif, déclenchement unique, ordre possession puis Elf, temps consommé pendant la possession et messages persistants.

### Essai matériel du 19 octobre 2026

| Plateforme | Constat |
| --- | --- |
| macOS Apple Silicon | CPython 3.11.11 et pygame-ce 2.5.8 installés. Fenêtre Cocoa affichée. Un événement clavier envoyé par **System Events** à la fenêtre au premier plan avec Contrôle + Option + Commande + Espace a été reçu par Pygame : accueil → possession → Elf observés à l'écran. Aucun conflit système observé pendant cet essai. Il ne remplace pas un essai par pression physique du clavier ou d'un clavier déporté. La fenêtre a été fermée normalement. |
| Linux x86-64 / Omarchy | Non essayé. Affichage, raccourci, audio et matériel cible restent à vérifier sur la borne. |

Le mélangeur audio pygame-ce a été ouvert sur la machine disponible et les sons ont été générés et joués par l'application. La qualité sonore perçue et la calibration auprès du jeune public restent à évaluer en conditions d'animation.

Les API de clavier, événement, affichage et son suivent la [documentation officielle pygame-ce](https://pyga.me/docs/).
