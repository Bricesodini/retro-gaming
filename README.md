# Laboratoire 1986 — POC Mystère / Tension

Une fenêtre Pygame CE présente le terminal de laboratoire pendant l'introduction. L'animateur choisit Mystère ou Tension dans la configuration, puis déclenche discrètement la possession. Les diagnostics se dérèglent, des interférences et des racines apparaissent progressivement, puis Elf prend contact et annonce un défi. Tension amplifie les déformations, ajoute une silhouette abstraite dans la chambre du signal et rend le grondement plus présent. La trame et les messages sont identiques. Cette tranche s'arrête à l'annonce : aucun jeu n'est encore disponible.

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

L'accueil affiche des diagnostics autonomes, sans temps actif. Avec la fenêtre au premier plan, appuyer sur **Contrôle + Option + Commande + Espace** sur Mac pour commencer. Le chronomètre de session démarre alors, y compris pendant les douze secondes initiales de possession. Un appui prolongé ou répété ne relance rien. Elf apparaît ensuite avec un texte qui reste affiché. Le temps restant est affiché pendant la session. À 60 secondes de la fin par défaut, un avertissement visuel et sonore apparaît une seule fois. À expiration, une alarme retentit une seule fois et un écran de fin attend l’animateur. **Contrôle + Option + Commande + Retour arrière (Backspace)** réinitialise depuis toute phase : le laboratoire revient avec un chronomètre neuf et les sons précédents sont arrêtés. Ce geste est distinct du déclenchement. Fermer avec **Échap** ou le bouton de la fenêtre.

Les effets visuels, le grondement et les sons brefs, dont l’avertissement et l’alarme, sont produits par le code. Les mouvements sont progressifs, sans flash rapide ni sursaut brutal. Il n'y a ni voix, ni ROM, ni média extrait de la série.

## Configuration

Modifier `config.json` avant le lancement, ou fournir un autre fichier :

```sh
.venv/bin/python -m retro_gaming --config /chemin/vers/ma-configuration.json
```

Le fichier contient `session_seconds` (300 par défaut), `possession_seconds` (12), `warning_seconds` (60, le nombre de secondes avant expiration), `variant` et `trigger`. Choisir explicitement `"Mystère"` ou `"Tension"` pour `variant` ; une autre valeur est refusée avant l'animation. Les trois durées doivent être positives et finies ; la possession et l’avertissement doivent chacun tenir à l’intérieur de la session. `trigger.key` est un nom de touche pygame-ce comme `space` ; `trigger.modifiers` accepte `ctrl`, `alt`, `meta` (Commande sur Mac) et `shift`. Exemple de Tension avec une combinaison alternative si le système intercepte le raccourci initial :

```json
{"session_seconds": 300, "possession_seconds": 12, "warning_seconds": 60, "variant": "Tension", "trigger": {"key": "space", "modifiers": ["ctrl", "alt", "shift"]}}
```

Cette alternative est configurable mais n'a pas été essayée sur Omarchy. La combinaison réservée à la remise à zéro est refusée comme déclencheur, même si l’ordre des modificateurs change. Une configuration invalide affiche une erreur avant d'ouvrir la fenêtre.

## Mode test

Pour parcourir la session plus vite, lancer :

```sh
.venv/bin/python -m retro_gaming --test-mode
```

`--test-mode` ramène en mémoire les trois durées à **10 %** de leur valeur configurée : avec `config.json` fourni, la session dure 30 secondes, la possession 1,2 seconde et l’avertissement survient 6 secondes avant la fin. Un badge **MODE TEST** reste visible à l’écran. Le fichier de configuration normale n’est pas modifié.

## Vérification

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Les tests de session contrôlent le temps sans attendre : accueil inactif, déclenchement unique, ordre possession puis Elf, temps consommé pendant la possession et messages persistants, seuils d’avertissement et d’alarme, traversée des deux seuils en une avancée, expiration dans les deux phases, remise à zéro et second cycle.

### Comparer les deux ambiances

Garder les mêmes durées, le même volume de sortie et le même endroit d'observation. Jouer Mystère, remettre à zéro, puis changer uniquement `variant` dans `config.json`, relancer l'application et jouer Tension. Faire l'essai avec le raccourci réel, en laissant aller chaque séquence jusqu'au message persistant d'Elf. Pour chaque variante, relever séparément :

- **Compréhension** : les participants identifient-ils la présence, l'aide d'Elf et l'annonce du défi sans explication supplémentaire ?
- **Rythme** : les diagnostics, les anomalies et le message d'Elf laissent-ils assez de temps pour suivre la scène ?
- **Réaction** : quels signes d'intérêt, d'inconfort ou de distraction sont observés pendant le grondement et l'apparition de la silhouette ?

Consigner les observations dans les conditions de la salle, avec les personnes réellement présentes. Ce POC ne fixe pas d'intensité adaptée à un âge précis.

### Essai matériel du 19 octobre 2026

| Plateforme | Constat |
| --- | --- |
| macOS Apple Silicon | CPython 3.11.11 et pygame-ce 2.5.8 installés. Fenêtre Cocoa affichée. Un événement clavier envoyé par **System Events** à la fenêtre au premier plan avec Contrôle + Option + Commande + Espace a été reçu par Pygame : accueil → possession → Elf observés à l'écran. Aucun conflit système observé pendant cet essai. Il ne remplace pas un essai par pression physique du clavier ou d'un clavier déporté. La fenêtre a été fermée normalement. |
| Linux x86-64 / Omarchy | Non essayé. Affichage, raccourci, audio et matériel cible restent à vérifier sur la borne. |

Le mélangeur audio pygame-ce a été ouvert sur la machine disponible et les sons ont été générés et joués par l'application. La qualité sonore perçue et la calibration auprès du jeune public restent à évaluer en conditions d'animation.

### Inspection des variantes du 19 octobre 2026

Le premier essai sonore a été jugé trop discret dans la comparaison. Le candidat actuel renforce Tension : présence abstraite plus grande et plus contrastée, parasites plus denses sans clignotement, et grondement enrichi à 120, 180 et 240 Hz pour rester audible sur des haut-parleurs ordinaires. Mystère reste la base légère. Sur le Mac Apple Silicon disponible, deux images pygame-ce ont été rendues au même instant (8 secondes sur 12), et deux extraits WAV mono de quatre secondes ont été créés pour une nouvelle comparaison. Les fichiers locaux de cette inspection sont `/tmp/retro-gaming-ticket-5-round-2/mystere-8s.png`, `tension-8s.png`, `mystere-4s.wav` et `tension-4s.wav` dans ce même dossier. Le mélangeur audio s'est ouvert à 44,1 kHz ; les niveaux mesurés des grondements du nouveau candidat sont RMS 1 782 pour Mystère et 3 146 pour Tension, sans saturation numérique. Cette mesure ne prouve pas l'intensité ressentie : les nouveaux extraits restent à écouter et comparer par l'animateur. La capture de fenêtre du lancement interactif n'a renvoyé aucune fenêtre Pygame dans la session distante. Le rendu en fenêtre, le raccourci et l'intensité sonore perçue restent donc à vérifier sur la machine, puis sur Omarchy.

Les API de clavier, événement, affichage et son suivent la [documentation officielle pygame-ce](https://pyga.me/docs/).
