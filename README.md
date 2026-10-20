# Laboratoire 1986 — borne arcade

Une fenêtre Pygame CE présente le terminal de laboratoire pendant l'introduction. L'animateur choisit Mystère ou Tension dans la configuration, puis déclenche discrètement la possession. Les diagnostics se dérèglent, des interférences et des racines apparaissent progressivement, puis Elf prend contact et annonce un défi. Tension amplifie les déformations, ajoute une silhouette abstraite dans la chambre du signal et rend le grondement plus présent. La trame et les messages sont identiques. L'entité adresse maintenant son propre message ; Elf demande l'aide de l'équipe, qui choisit ensuite l'un des trois jeux dans cette même fenêtre. Les lanceurs autonomes restent disponibles.

## Versions et installation

- CPython **3.11.11** (`.python-version`)
- pygame-ce **2.5.8** (`requirements.txt`)

Depuis la racine du dépôt, avec [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installé :

```sh
uv python install 3.11.11
uv venv --python 3.11.11 --seed .venv
.venv/bin/python -m pip install --requirement requirements.txt
```

Ces versions ont été installées et essayées sur macOS Apple Silicon, la plateforme de déploiement visée. Linux et Omarchy ne font pas partie du périmètre de prise en charge.

## Démontrer le parcours

```sh
.venv/bin/python -m retro_gaming
```

L'accueil affiche des diagnostics autonomes, sans temps actif. Avec la fenêtre au premier plan, appuyer sur **Contrôle + Option + Commande + Espace** sur Mac pour commencer. Le chronomètre de session démarre alors, y compris pendant les douze secondes initiales de possession. Un appui prolongé ou répété ne relance rien. Elf apparaît ensuite, explique la possession et demande de l'aide. Appuyer sur **Entrée** pour afficher le choix persistant, puis sur **1** pour le labyrinthe, **2** pour le combat spatial ou **3** pour les plateformes. Les consignes et les vies restent visibles pendant la partie. Son résultat reste affiché dans la borne ; la suite du défi après ce résultat sera reliée par l'issue #12. Le temps restant est affiché pendant les scènes, le choix et la partie. À 60 secondes de la fin par défaut, un avertissement visuel et sonore apparaît une seule fois. À expiration, une alarme retentit une seule fois et un écran de fin attend l’animateur. **Contrôle + Option + Commande + Retour arrière (Backspace)** réinitialise depuis toute phase : le laboratoire revient avec un chronomètre neuf et les sons précédents sont arrêtés. Ce geste est distinct du déclenchement. Fermer avec **Échap** ou le bouton de la fenêtre.

Les effets visuels, le grondement et les sons brefs, dont l’avertissement et l’alarme, sont produits par le code. Les mouvements sont progressifs, sans flash rapide ni sursaut brutal. Il n'y a ni voix, ni ROM, ni média extrait de la série.

## Jouer au combat spatial

```sh
.venv/bin/python -m retro_gaming.space_combat
```

Déplacer le vaisseau avec les flèches gauche/droite ou **A/D**. Maintenir **Espace** pour tirer. Esquiver les salves et utiliser les quatre abris : les tirs des deux camps les dégradent. Chaque envahisseur vaut 100 points ; une nouvelle vague arrive tant que le score cible n'est pas atteint. Les étoiles défilent derrière l'action. Un tir reçu ou une formation arrivée au vaisseau coûte une vie ; la manche dispose de **trois vies**. Après un impact, le vaisseau repart au centre, avec une courte pause.

La victoire arrive au score cible, réglable avant la manche :

```sh
.venv/bin/python -m retro_gaming.space_combat --score-target 3000
```

La valeur initiale de 3 000 points et les cadences restent à calibrer en conditions d'animation. Le score se conserve entre les vagues et les vies. Les abris restent endommagés ; une invasion replace la formation en haut. Le résultat reste affiché jusqu'à **Échap** ou la fermeture de la fenêtre. Ce lanceur autonome reste disponible.

## Jouer au labyrinthe

```sh
.venv/bin/python -m retro_gaming.maze
```

Déplacer le personnage jaune avec les flèches ou **WASD** pour vider le plateau. Les murs bloquent le passage. Quatre fantômes poursuivent, anticipent, alternent entre chasse et détour, ou explorent les coins du labyrinthe. Une pastille vaut 10 points ; une super-pastille vaut 50 points et rend les fantômes vulnérables pendant six secondes. Manger un fantôme ajoute 200 points ; il revient après deux secondes.

Le contact avec un fantôme en chasse coûte une des **trois vies**. Le joueur et les fantômes repartent à leurs positions initiales après une courte pause ; les pastilles déjà collectées et le score restent acquis. Ramasser toutes les pastilles et super-pastilles gagne. Le résultat reste affiché jusqu'à **Échap** ou la fermeture de la fenêtre. Le lanceur autonome du labyrinthe reste disponible.

## Jouer au jeu de plateformes

```sh
.venv/bin/python -m retro_gaming.platformer
```

Déplacer le personnage à gauche et à droite avec les flèches ou **A/D**. Monter et descendre les échelles avec **↑/↓** ou **W/S** ; **Espace** fait sauter. Parcourir les passerelles inclinées en zigzag jusqu'à la princesse au sommet. Un grand singe original prépare puis lance ses barriques : elles roulent, tombent aux extrémités et certaines empruntent les échelles. Leur cadence et leur vitesse augmentent pendant l'ascension. Deux ennemis de feu sont actifs dès le départ ; ils poursuivent le joueur et changent d'étage par les échelles. Le brasier du bas en fait apparaître un autre après quatorze secondes, jusqu'à trois ; le brasier lui-même est dangereux au contact. Cinq échelles placées uniquement aux extrémités imposent une montée en zigzag sur six poutrelles. Une dernière échelle au bord droit mène à la terrasse de la princesse, au-dessus du singe. Les pentes alternent : les barriques descendent à la rencontre du joueur, accélèrent dans la pente et chutent sous la gravité en bout de passerelle. Une seule barrique est déjà en circulation au début de la manche. Les lancers commencent à 4 secondes d’intervalle et restent espacés d’au moins 3,2 secondes au sommet ; les barriques partent à 85 pixels par seconde et leur vitesse est plafonnée à 125 pixels par seconde. Les flammes avancent plus lentement. Le saut est assez court pour franchir les dangers sans sauter un étage. Les poses de marche, de grimpe et de saut du personnage, ainsi que le lancer du singe et la rotation des barriques, suivent l'état réel du jeu.

Une collision ou une chute coûte une des **trois vies** et ramène au départ avec une courte pause. Atteindre la princesse gagne la manche. Le résultat reste affiché jusqu'à **Échap** ou la fermeture de la fenêtre. Le lanceur autonome des plateformes reste disponible.

Dans les trois jeux, une manche contient trois vies. Le jeu choisi dans la borne consomme le temps global ; les lanceurs autonomes ne modifient pas sa session.

## Configuration

Modifier `config.json` avant le lancement, ou fournir un autre fichier :

```sh
.venv/bin/python -m retro_gaming --config /chemin/vers/ma-configuration.json
```

Le fichier contient `session_seconds` (300 par défaut), `possession_seconds` (12), `warning_seconds` (60, le nombre de secondes avant expiration), `variant` et `trigger`. Choisir explicitement `"Mystère"` ou `"Tension"` pour `variant` ; une autre valeur est refusée avant l'animation. Les trois durées doivent être positives et finies ; la possession et l’avertissement doivent chacun tenir à l’intérieur de la session. `trigger.key` est un nom de touche pygame-ce comme `space` ; `trigger.modifiers` accepte `ctrl`, `alt`, `meta` (Commande sur Mac) et `shift`. Exemple de Tension avec une combinaison alternative si le système intercepte le raccourci initial :

```json
{"session_seconds": 300, "possession_seconds": 12, "warning_seconds": 60, "variant": "Tension", "trigger": {"key": "space", "modifiers": ["ctrl", "alt", "shift"]}}
```

Cette alternative est configurable pour macOS si un conflit système est observé. La combinaison réservée à la remise à zéro est refusée comme déclencheur, même si l’ordre des modificateurs change. Une configuration invalide affiche une erreur avant d'ouvrir la fenêtre.

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

Les tests de session contrôlent le temps sans attendre : accueil inactif, déclenchement unique, ordre possession puis Elf, temps consommé pendant la possession et messages persistants, seuils d’avertissement et d’alarme, traversée des deux seuils en une avancée, expiration pendant les scènes et la partie, résultat du jeu, remise à zéro et second cycle.

Les tests des trois jeux passent par `Game.advance(temps, entrées) -> GameState`, sans fenêtre. Ils couvrent vies et réapparitions, résultats persistants, murs et collecte, super-pastilles et retour des quatre fantômes, tirs ennemis et joueur, abris, score et vagues, passerelles inclinées, saut et échelles, trajectoires des barriques et pression pendant l'ascension. Des scénarios à temps découpé différemment vérifient aussi collisions, transitions et commandes brèves.

La vérification automatisée ne remplace pas l'essai physique du clavier ni le réglage de la difficulté en salle. Voir [le compte rendu des jeux d'arcade](docs/arcade-validation.md) pour les preuves et les limites des essais.

### Comparer les deux ambiances

Garder les mêmes durées, le même volume de sortie et le même endroit d'observation. Jouer Mystère, remettre à zéro, puis changer uniquement `variant` dans `config.json`, relancer l'application et jouer Tension. Faire l'essai avec le raccourci réel, en laissant aller chaque séquence jusqu'au message persistant d'Elf. Pour chaque variante, relever séparément :

- **Compréhension** : les participants identifient-ils la présence, l'aide d'Elf et l'annonce du défi sans explication supplémentaire ?
- **Rythme** : les diagnostics, les anomalies et le message d'Elf laissent-ils assez de temps pour suivre la scène ?
- **Réaction** : quels signes d'intérêt, d'inconfort ou de distraction sont observés pendant le grondement et l'apparition de la silhouette ?
- **Intensité perçue** : chaque personne distingue-t-elle les deux versions, et laquelle juge-t-elle adaptée au groupe dans la salle et avec le volume prévus ?

Consigner les observations dans les conditions de la salle, avec les personnes réellement présentes. Ce POC ne fixe pas d'intensité adaptée à un âge précis.

### Essai matériel du 19 octobre 2026

| Plateforme | Constat |
| --- | --- |
| macOS Apple Silicon | CPython 3.11.11 et pygame-ce 2.5.8 installés. Fenêtre Cocoa affichée. Un événement clavier envoyé par **System Events** à la fenêtre au premier plan avec Contrôle + Option + Commande + Espace a été reçu par Pygame : accueil → possession → Elf observés à l'écran. Aucun conflit système observé pendant cet essai. Il ne remplace pas un essai par pression physique du clavier ou d'un clavier déporté. La fenêtre a été fermée normalement. |

Le mélangeur audio pygame-ce a été ouvert sur le Mac et l'application a déclenché ses sons générés. Aucun enregistrement acoustique indépendant ni jugement de qualité sonore n'a été effectué ; l'écoute en conditions d'animation et la calibration auprès du jeune public restent à faire.

### Inspection des variantes du 19 octobre 2026

Le candidat actuel renforce Tension : présence abstraite plus grande et plus contrastée, parasites plus denses sans clignotement, et grondement enrichi à 120, 180 et 240 Hz. Mystère reste la base légère. Sur le Mac Apple Silicon disponible, deux images pygame-ce ont été rendues au même instant (8 secondes sur 12), et deux extraits WAV mono de quatre secondes ont été créés pour préparer la comparaison. Les fichiers locaux de cette inspection sont `/tmp/retro-gaming-ticket-5-round-2/mystere-8s.png`, `tension-8s.png`, `mystere-4s.wav` et `tension-4s.wav` dans ce même dossier. Le mélangeur audio s'est ouvert à 44,1 kHz ; les niveaux mesurés des grondements du nouveau candidat sont RMS 1 782 pour Mystère et 3 146 pour Tension, sans saturation numérique. Ces mesures décrivent le signal, pas son rendu acoustique. L'utilisateur a ensuite comparé les deux variantes dans le jeu et indiqué « la version 2 est mieux » ; la version 2 correspondait à Tension. Ce retour établit une préférence pour l'expérience globale sur le Mac essayé, sans attribuer cette préférence au son seul ni valider l'intensité auprès d'enfants ou en conditions d'animation. La capture automatique de la fenêtre lors d'un autre lancement distant n'avait montré aucune fenêtre Pygame ; elle ne contredit pas l'essai en jeu effectué par l'utilisateur. La pression physique du raccourci Mac reste à vérifier.

Les API de clavier, événement, affichage et son suivent la [documentation officielle pygame-ce](https://pyga.me/docs/).

### Vérification intégrée du 19 octobre 2026 — ticket #6

Sur le Mac Apple Silicon disponible, un environnement virtuel isolé a été créé avec CPython 3.11.11 et `pygame-ce==2.5.8` installé depuis `requirements.txt`. Le parcours Pygame a été exécuté avec une sortie vidéo et audio SDL simulée : **Mystère et Tension**, chacune pendant deux sessions complètes séparées par une remise à zéro. Pour chaque session, les images Pygame et les sorties du contrôleur ont confirmé accueil sans temps actif, déclenchement, possession, contact d'Elf, annonce persistante, avertissement unique, expiration avec alarme unique et accueil rétabli avant la session suivante. Le mélangeur SDL était actif pendant le parcours. Les images produites ont été inspectées pour l'accueil, la possession des deux variantes, le texte d'Elf et l'accueil après remise à zéro. Un défaut de relancement dans le même processus (polices en cache invalidées après fermeture de Pygame) a été corrigé puis le parcours a été rejoué avec succès.

Un second essai sur le Mac M4 Max a affiché la fenêtre Pygame Cocoa. Avec cette fenêtre au premier plan, **System Events** a envoyé Contrôle + Option + Commande + Espace : la possession puis Elf ont été observés. En mode test, avec une configuration de 60 secondes de session, 12 secondes de possession et 30 secondes d'avertissement avant réduction à 10 %, l'avertissement visuel est apparu à **00:03**, puis l'écran de fin. Contrôle + Option + Commande + Retour arrière a rendu l'accueil sans chronomètre ; un nouveau déclenchement avec la même configuration a lancé une deuxième session, affichée à **00:05**. Tension a également été lancé en fenêtre visible, avec sa silhouette et ses interférences. Le mélangeur audio s'est initialisé à 44,1 kHz, en mono signé 16 bits ; la sortie système sélectionnée était les haut-parleurs du MacBook Pro. Les captures `mac-mystere-reset-config60.png` et `mac-mystere-elf-run2-config60.png`, ainsi que les configurations de cet essai, sont conservées dans le checkout principal sous `.scratch/orchestration/retro-gaming-poc-20261019/evidence/ticket-6/`.

Le raccourci a été envoyé par logiciel, sans pression physique sur le clavier. L'initialisation du mélangeur ne mesure ni la qualité sonore perçue ni le niveau adapté à des enfants ; aucune calibration auprès du public n'a eu lieu. Les validations produit visent uniquement macOS Apple Silicon.
