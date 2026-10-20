# Laboratoire 1986 — borne rétro gaming

Application Pygame CE pour **macOS Apple Silicon**. Le laboratoire accueille l'équipe, l'animateur déclenche la possession, Elf propose trois jeux, puis la session conduit à une victoire de salle ou à un échec. Le chiffre de salle est révélé uniquement après une victoire. Les dessins et sons sont générés par le code ; aucun média de la série ni ROM n'est requis.

## Installer et lancer

Depuis la racine du dépôt, installer [uv](https://docs.astral.sh/uv/getting-started/installation/) puis exécuter :

```sh
uv python install 3.11.11
uv venv --python 3.11.11 --seed .venv
.venv/bin/python -m pip install --requirement requirements.txt
.venv/bin/python -m retro_gaming
```

`requirements.txt` fixe pygame-ce 2.5.8. Laisser la fenêtre au premier plan pour jouer. **Échap** ou le bouton de fermeture quitte l'application. Le parcours fonctionne dans une fenêtre de 1 200 × 760 pixels ; vérifier que l'écran de la borne peut l'afficher entièrement.

Pour afficher ce même canevas logique en plein écran, lancer `.venv/bin/python -m retro_gaming --fullscreen`. Pygame le met à l'échelle de l'écran ; **Échap** quitte aussi ce mode. L'option concerne le parcours intégré et peut être combinée avec `--config` et `--test-mode`. Le démarrage reste en fenêtre par défaut.

## Déroulement et commandes

| Phase | Action et affichage |
| --- | --- |
| Laboratoire | Diagnostics autonomes. Le chronomètre est inactif. L'animateur appuie sur **Contrôle + Option + Commande + Espace** pour déclencher la possession. |
| Possession et Elf | L'entité s'adresse à l'équipe, puis Elf demande son aide. Le temps global court dès le déclenchement. Appuyer sur **Entrée** quand Elf le propose. |
| Choix | Appuyer sur **1** (labyrinthe), **2** (combat spatial) ou **3** (plateformes). Les consignes restent affichées. |
| Partie | Chaque jeu offre trois vies. Le temps global continue pendant la partie. Une victoire remporte immédiatement le défi de salle. |
| Défaite d'un jeu | L'entité reprend le contrôle, Elf revient, puis **Entrée** ouvre le choix parmi les jeux encore disponibles. Un jeu perdu ne peut plus être choisi dans ce défi. |
| Troisième défaite | Après la reprise de l'entité et le retour d'Elf, l'écran d'échec reste affiché jusqu'à la fin du temps. Aucun chiffre ni quatrième jeu. |
| Victoire de salle | Elf révèle le chiffre configuré. Appuyer sur **Entrée** pour ouvrir le mode libre ; les trois jeux sont alors disponibles, y compris ceux déjà tentés. Le chronomètre est masqué mais continue. |
| Fin du temps | Avertissement au seuil configuré, puis signal de fin et message d'Elf pour rejoindre la salle suivante. La partie ou la scène en cours s'arrête. |

Depuis **toute phase**, **Contrôle + Option + Commande + Retour arrière** (`Backspace`) remet la borne à zéro pour une nouvelle équipe. Ce raccourci est distinct du déclencheur : il arrête les sons, efface le temps, les vies, les jeux tentés, le résultat, le chiffre affiché et les alertes, puis rétablit le laboratoire. Après la remise à zéro, utiliser à nouveau le déclencheur pour commencer le second parcours.

### Contrôles des jeux

| Jeu | Objectif et commandes |
| --- | --- |
| Labyrinthe | Ramasser la proportion configurée des pastilles (100 % par défaut : vider le plateau). **Flèches** ou **WASD** pour se déplacer. Les super-pastilles rendent temporairement les quatre fantômes vulnérables. |
| Combat spatial | Atteindre le score cible configuré (3 000 points par défaut) en détruisant les envahisseurs. **Gauche/Droite** ou **A/D** pour se déplacer ; maintenir **Espace** pour tirer. Les abris protègent puis se dégradent. |
| Plateformes | Atteindre la progression verticale configurée (100 % par défaut : rejoindre la princesse sur la terrasse), en évitant barriques, ennemis de feu et brasier. **Gauche/Droite** ou **A/D** pour marcher, **Haut/Bas** ou **W/S** pour les échelles, **Espace** pour sauter. |

Un seul joueur contrôle le jeu à la fois. Un changement de joueur peut se faire entre les vies sans quitter le jeu choisi. Les lanceurs autonomes restent disponibles :

```sh
.venv/bin/python -m retro_gaming.maze
.venv/bin/python -m retro_gaming.space_combat
.venv/bin/python -m retro_gaming.platformer
```

Le combat spatial autonome accepte `--score-target 3000` avec un entier positif. Cette option **ne règle pas** le score du parcours intégré.

## Configuration de la borne

Modifier `config.json` avant le lancement ou fournir une copie avec `--config` :

```sh
.venv/bin/python -m retro_gaming --config /chemin/vers/config.json
```

Le fichier livré contient les durées et le chiffre ci-dessous ainsi qu'un objet `games` avec les valeurs de jeu indiquées dans le tableau suivant. `games`, chaque jeu et chaque champ de jeu sont optionnels : une valeur absente reprend le défaut.

```json
{
  "session_seconds": 300,
  "possession_seconds": 12,
  "warning_seconds": 60,
  "room_digit": 4,
  "variant": "Mystère",
  "trigger": {"key": "space", "modifiers": ["ctrl", "alt", "meta"]},
  "games": {
    "maze": {"pellet_goal_percent": 100, "ghost_step_seconds": 0.45, "power_seconds": 6},
    "space_combat": {"score_target": 3000, "enemy_speed_px_per_second": 80, "salvo_interval_seconds": 1.3},
    "platformer": {
      "goal_progress_percent": 100,
      "barrel_interval_seconds": 4,
      "barrel_speed_px_per_second": 85,
      "barrel_speed_cap_px_per_second": 125,
      "fire_spawn_interval_seconds": 14,
      "fire_speed_px_per_second": 26
    }
  }
}
```

`warning_seconds` est le nombre de secondes **restant** lorsque l'avertissement est émis, et non une durée depuis le déclenchement. Les trois durées doivent être positives et finies ; possession et avertissement doivent être inférieurs à `session_seconds`. `room_digit` est un entier de 0 à 9. `variant` vaut exactement `Mystère` ou `Tension` ; les messages et le parcours restent les mêmes, tandis que Tension renforce progressivement la silhouette, les interférences et le grondement. Le déclencheur utilise un nom de touche pygame-ce et une liste unique, non vide, de `ctrl`, `alt`, `meta` (Commande sur Mac) et `shift`. Le raccourci de remise à zéro est réservé. Si macOS intercepte le déclencheur initial, essayer une autre combinaison dans la configuration, puis la vérifier sur la borne.

| Jeu | Réglage numérique | Sens et valeur livrée |
| --- | --- | --- |
| Labyrinthe | `pellet_goal_percent` | Part de toutes les pastilles et super-pastilles à ramasser pour gagner ; **100 %** vide le plateau. |
| Labyrinthe | `ghost_step_seconds` | Temps entre deux pas des fantômes : **0,45 s** ; plus petit les rend plus rapides. |
| Labyrinthe | `power_seconds` | Durée d'effet d'une super-pastille : **6 s**. |
| Combat spatial | `score_target` | Score de victoire, entier positif : **3 000 points**. Chaque envahisseur vaut 100 points. |
| Combat spatial | `enemy_speed_px_per_second` | Vitesse horizontale de base de la formation : **80 pixels/s**, à laquelle s'ajoutent 12 pixels/s par vague. |
| Combat spatial | `salvo_interval_seconds` | Intervalle de base entre salves ennemies : **1,3 s** ; il se raccourcit de 0,08 s par vague, sans passer sous 0,7 s. |
| Plateformes | `goal_progress_percent` | Hauteur à atteindre en étant sur une échelle ou une passerelle : **100 %** impose la princesse sur sa terrasse ; une valeur moindre termine le jeu plus tôt. |
| Plateformes | `barrel_interval_seconds` | Intervalle initial de lancer : **4 s** ; il peut diminuer pendant la montée, avec un plancher de 80 % du réglage ou 1 s. |
| Plateformes | `barrel_speed_px_per_second` | Vitesse initiale des barriques : **85 pixels/s**. |
| Plateformes | `barrel_speed_cap_px_per_second` | Plafond de vitesse des barriques dans les pentes : **125 pixels/s**, au moins égal à la vitesse initiale. |
| Plateformes | `fire_spawn_interval_seconds` | Délai entre apparitions de flammes supplémentaires : **14 s**, jusqu'à trois flammes mobiles. |
| Plateformes | `fire_speed_px_per_second` | Vitesse de base des nouvelles flammes : **26 pixels/s**. Les flammes initiales gardent leur écart relatif. |

Les pourcentages doivent être supérieurs à 0 et au plus égaux à 100 ; `score_target` doit être un entier positif. Les autres réglages de jeu doivent être des nombres positifs et finis. Une erreur de lecture, une clé obligatoire absente, une valeur invalide ou un nom de jeu/réglage inconnu produit `Configuration invalide dans …` avec le champ concerné avant l'ouverture de la fenêtre. Les réglages `games` s'appliquent uniquement au parcours intégré ; les trois lanceurs autonomes gardent leurs propres défauts et options.

## Mode test et répétition

```sh
.venv/bin/python -m retro_gaming --test-mode
```

Le badge **MODE TEST** identifie ce mode. Il multiplie **en mémoire** les trois durées de session, possession et avertissement par 0,1 ; `config.json` reste inchangé. Avec le fichier livré, cela donne 30 secondes de session, 1,2 seconde de possession et un avertissement à 6 secondes de la fin. Pendant une partie intégrée active, le temps de simulation du jeu avance **10 fois plus vite** que le temps réel ; les déplacements, ennemis et animations progressent donc plus vite. Les lanceurs autonomes gardent leur vitesse normale. Pour une répétition manuelle avec davantage de temps de réaction, préparer une copie de configuration avec une session plus longue, puis lancer `--config /chemin/vers/copie.json --test-mode`. Évaluer la difficulté destinée au public **en mode normal**.

Pour répéter les issues : déclencher, choisir un jeu et gagner pour vérifier le chiffre et le mode libre ; remettre à zéro ; déclencher et perdre les trois jeux différents pour vérifier l'échec sans chiffre ; attendre l'échéance dans chaque issue ; remettre à zéro et refaire un cycle. Vérifier aussi la remise à zéro depuis une scène et une partie. La grille d'observation détaillée est dans [docs/arcade-validation.md](docs/arcade-validation.md).

## Vérifier le code

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q retro_gaming tests
```

La suite contrôle le parcours `Session` avec un temps piloté, la configuration et les règles des trois jeux sans fenêtre. Ces tests ne prouvent ni la pression d'un clavier physique, ni la qualité du rendu ou du son sur la borne, ni l'équilibre des parties. Le [compte rendu de validation](docs/arcade-validation.md) distingue les essais exécutés des essais matériels encore à faire.
