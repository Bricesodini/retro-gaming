# Laboratoire 1986 — borne rétro gaming

Application Pygame CE pour **macOS Apple Silicon**. Le laboratoire accueille l'équipe ; sa première touche lance une attente de dix secondes avant la possession, Elf propose trois hommages d'arcade des années 80 — **Pac-Man**, **Space Invaders** et **Donkey Kong** — puis la session conduit à une victoire de salle ou à un échec. Le chiffre de salle est révélé uniquement après une victoire. Les ambiances sonores et musiques sont originales et synthétisées par le code ; les portraits pixel art d'Elf et du Démogorgon sont livrés dans les ressources du jeu. Aucune ROM n'est requise.

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

Pour démarrer la borne directement en plein écran depuis le Finder, double-cliquer sur **Lancer le laboratoire.command** à la racine du projet. Le lanceur utilise l'environnement `.venv` et transmet les éventuelles options supplémentaires au jeu.

## Déroulement et commandes

| Phase | Action et affichage |
| --- | --- |
| Laboratoire | Diagnostics autonomes. Le chronomètre est inactif jusqu'à la première touche ordinaire ; elle lance la session et affiche un compte à rebours vert pendant les dix secondes avant l'arrivée du Démogorgon. |
| Possession et Elf | À l'arrivée du Démogorgon, le compte à rebours devient rouge. Elf explique qu'il indique le temps restant pour repousser l'entité. Appuyer sur **Entrée** quand Elf le propose. |
| Choix | Appuyer sur **1** (Pac-Man), **2** (Space Invaders) ou **3** (Donkey Kong). Les consignes restent affichées. |
| Partie | Chaque jeu offre trois vies. Le temps global continue pendant la partie. Une victoire remporte immédiatement le défi de salle. |
| Défaite d'un jeu | Le Démogorgon reprend le contrôle, Elf revient, puis **Entrée** ouvre le choix parmi les jeux encore disponibles. Un jeu perdu ne peut plus être choisi dans ce défi. |
| Troisième défaite | Après la reprise du Démogorgon et le retour d'Elf, l'écran d'échec reste affiché jusqu'à la fin du temps. Aucun chiffre ni quatrième jeu. |
| Victoire de salle | Après le résultat gagnant, le chronomètre disparaît pendant la révélation du chiffre. Appuyer sur **Entrée** pour ouvrir le mode libre ; les trois jeux sont alors disponibles, y compris ceux déjà tentés, avec un compte à rebours vert qui continue. |
| Fin du temps | Avertissement au seuil configuré, puis signal de fin et message d'Elf pour rejoindre la salle suivante. La partie ou la scène en cours s'arrête. |

Après les dix secondes d'attente, le Démogorgon apparaît avec son portrait pixelisé, un unique flash rouge bref, une déchirure du signal, des parasites CRT et un grondement bas. Chaque jeu a sa propre musique chiptune originale d'environ **15 secondes**, avec plusieurs phrases avant la reprise et un niveau de lecture réduit. Quand une tentative est perdue, la reprise du signal devient une confrontation animée entre Elf et le Démogorgon ; elle dure environ **2,4 secondes** avec la configuration par défaut, puis Elf revient proposer un jeu encore disponible.

Depuis **toute phase**, y compris le laboratoire en attente, **Contrôle + Option + Commande + Espace** remet la borne à zéro pour une nouvelle équipe. Ce raccourci a priorité sur le déclenchement : il arrête les sons, efface le temps, les vies, les jeux tentés, le résultat, le chiffre affiché et les alertes, puis rétablit le laboratoire. Après la remise à zéro, la prochaine touche ordinaire commence un nouveau parcours.

### Contrôles des jeux

| Jeu | Objectif et commandes |
| --- | --- |
| Pac-Man | Ramasser la proportion configurée des pastilles (100 % par défaut : vider le plateau). **Flèches** ou **WASD** pour se déplacer. Les super-pastilles rendent temporairement les quatre fantômes vulnérables. |
| Space Invaders | Atteindre le score cible configuré (3 000 points par défaut) en détruisant les envahisseurs. **Gauche/Droite** ou **A/D** pour se déplacer ; maintenir **Espace** pour tirer. La formation rebondit sans descendre; les abris protègent puis se dégradent. |
| Donkey Kong | Atteindre la progression verticale configurée (100 % par défaut : rejoindre la princesse sur la terrasse), en évitant barriques, ennemis de feu et brasier. **Gauche/Droite** ou **A/D** pour marcher, **Haut/Bas** ou **W/S** pour les échelles, **Espace** pour sauter. |

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

`warning_seconds` est le nombre de secondes **restant** lorsque l'avertissement est émis, et non une durée depuis le déclenchement. Les trois durées doivent être positives et finies ; la session doit être plus longue que les dix secondes d'attente et la durée de possession réunies, et l'avertissement doit rester inférieur à `session_seconds`. `room_digit` est un entier de 0 à 9. `variant` vaut exactement `Mystère` ou `Tension` ; les messages et le parcours restent les mêmes, tandis que Tension renforce progressivement la silhouette, les interférences et le grondement. Le délai avant l'arrivée est fixe : dix secondes. Les touches de modification seules, Échap et le raccourci de remise à zéro ne déclenchent pas la session. Le champ `trigger` des anciennes configurations doit être supprimé.

| Jeu | Réglage numérique | Sens et valeur livrée |
| --- | --- | --- |
| Labyrinthe | `pellet_goal_percent` | Part de toutes les pastilles et super-pastilles à ramasser pour gagner ; **100 %** vide le plateau. |
| Labyrinthe | `ghost_step_seconds` | Temps entre deux pas des fantômes : **0,45 s** ; plus petit les rend plus rapides. |
| Labyrinthe | `power_seconds` | Durée d'effet d'une super-pastille : **6 s**. |
| Space Invaders | `score_target` | Score de victoire, entier positif : **3 000 points**. Un envahisseur vaut **30**, **20** ou **10** points selon sa rangée. |
| Space Invaders | `enemy_speed_px_per_second` | Vitesse horizontale de base de la formation : **80 pixels/s**, à laquelle s'ajoutent 12 pixels/s par vague. La formation rebondit sur les bords sans descendre. |
| Space Invaders | `salvo_interval_seconds` | Intervalle de base entre salves ennemies : **1,3 s** ; il se raccourcit de 0,08 s par vague, sans passer sous 0,7 s. |
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

Le badge **MODE TEST** reste visible dans toutes les phases. Il multiplie **en mémoire** les durées de session, possession, avertissement et attente du signal par 0,1 ; `config.json` reste inchangé. Avec le fichier livré, cela donne 30 secondes de session, une seconde d'attente, 1,2 seconde de possession et un avertissement à 6 secondes de la fin. Pendant une partie intégrée active, le temps de simulation du jeu avance **10 fois plus vite** que le temps réel ; les déplacements, ennemis et animations progressent donc plus vite. Les lanceurs autonomes gardent leur vitesse normale. Pour une répétition manuelle avec davantage de temps de réaction, préparer une copie de configuration avec une session plus longue, puis lancer `--config /chemin/vers/copie.json --test-mode`. Évaluer la difficulté destinée au public **en mode normal**.

Pour répéter les issues : déclencher, choisir un jeu et gagner pour vérifier le chiffre et le mode libre ; remettre à zéro ; déclencher et perdre les trois jeux différents pour vérifier l'échec sans chiffre ; attendre l'échéance dans chaque issue ; remettre à zéro et refaire un cycle. Vérifier aussi la remise à zéro depuis une scène et une partie. La grille d'observation détaillée est dans [docs/arcade-validation.md](docs/arcade-validation.md).

## Vérifier le code

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q retro_gaming tests
```

La suite contrôle le parcours `Session` avec un temps piloté, la configuration et les règles des trois jeux sans fenêtre. Ces tests ne prouvent ni la pression d'un clavier physique, ni la qualité du rendu ou du son sur la borne, ni l'équilibre des parties. Le [compte rendu de validation](docs/arcade-validation.md) distingue les essais exécutés des essais matériels encore à faire.
