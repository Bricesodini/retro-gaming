# Conception de l’animation

État : cadrage synthétisé dans la spec du premier POC, publiée dans le ticket GitHub #1 avec le label ready-for-agent. Les points ouverts ci-dessous restent à éprouver ; aucun code applicatif n’est encore implémenté.

## Choix validés

- Accueil sous forme de faux ordinateur de laboratoire de 1986.
- Possession déclenchée volontairement pendant l’animation, puis prise de relais par l’ordinateur pour le défi.
- Elf, le personnage de Onze (Eleven) dans Stranger Things, remplace le robot HAWK-80. Elle intervient avec ses pouvoirs pour contrer la possession et aider les participants ; elle transmet les règles du défi.
- Univers inspiré de Stranger Things : laboratoire abandonné, dimension parallèle, racines organiques et interférences rouges. La référence explicite à Elf remplace le choix antérieur d’une fiction entièrement originale ; les trois jeux et les ressources produites restent originaux.
- Public pouvant être relativement jeune ; des POC doivent permettre de calibrer l’intensité.
- La première touche ordinaire démarre le chronomètre global et une attente de dix secondes avant l’arrivée du Démogorgon ; le temps inclut ensuite la possession, les scènes et les parties. Le laboratoire reste hors chronomètre tant que personne n’a appuyé.
- Pas de commandes dédiées de pause du chronomètre ou de coupure des effets pour gérer les réactions du public : l’équipe d’animation gère la situation sur place.
- Après épuisement des tentatives, écran d’échec sans révélation automatique du chiffre. L’animateur peut accorder une tentative supplémentaire.
- Premier POC centré sur la séquence laboratoire → déclenchement → possession → intervention de Elf, avec deux intensités à comparer. Il sert à éprouver le déclenchement et la réaction du public avant la production complète des effets.
- Sur Mac, Contrôle + Option + Commande + Espace remet la borne à l’état initial. La première touche ordinaire lance le parcours ; Échap quitte l’application.
- À l’accueil, le terminal affiche seul ses diagnostics et sert de décor pendant l’introduction. Elf apparaît lors de la possession comme une alliée qui reprend contact.
- Premier test sans voix : texte lisible, consignes conservées à l’écran et bips originaux. La nécessité d’une voix sera évaluée après ce test, notamment pour les plus jeunes ; le choix d’une voix robotique concernait l’ancien personnage et n’est pas retenu pour Elf à ce stade.
- Deux variantes de possession, environ 12 secondes chacune, durée configurable : « Mystère » (diagnostics anormaux, parasites légers, racines, intervention de Elf) et « Tension » (mêmes informations, déformations plus marquées, portrait du Démogorgon, grondement plus présent). L'arrivée comporte un seul flash rouge bref, demandé ultérieurement ; aucun flash n'est répété et aucun sursaut brutal n'est ajouté.
- Après l’alarme finale, remise à zéro réservée à l’animateur : effacement du chiffre affiché, des tentatives et du chronomètre, puis rétablissement du laboratoire de 1986 pour la prochaine équipe.
- Après la victoire, Elf reprend le contrôle, révèle le chiffre et déverrouille les trois jeux. Le chronomètre reste visible jusqu'à l'entrée en mode libre, puis disparaît sans arrêter le temps. Quelques traces de possession restent visibles dans une ambiance devenue rassurante.
- L’entité disparaît mais annonce qu’elle reviendra : la victoire dans cette salle est provisoire et prépare un nouveau combat plus tard dans le parcours.

## Contexte du parcours

Les équipes traversent plusieurs salles et y récupèrent des chiffres. Leur collecte leur permet d’accéder à l’ascenseur, qui les conduit en bas, dans le « monde à l’envers » de l’animation. Le départ de l’entité doit annoncer une menace future cohérente avec cette suite. Le texte exact de cette annonce reste à proposer ; il n’a pas été validé.

## Contraintes du MVP demandées

- Python/Pygame, développement et déploiement sur macOS Apple Silicon. Linux et Omarchy ne sont pas des plateformes cibles.
- Trois hommages aux jeux d’arcade des années 80 : **Pac-Man** (labyrinthe à vider), **Space Invaders** (combat spatial par vagues, formation horizontale qui ne descend pas) et **Donkey Kong** (jeu de plateformes 2D). Le jeu de plateformes comporte un niveau fixe avec plateformes et échelles; le participant se déplace et grimpe avec les flèches ou WASD, et saute avec Espace. Atteindre la sortie en haut gagne la manche; le contact avec un obstacle mobile ou une chute la fait perdre.
- Un joueur à la fois, trois tentatives par défaut, changement de joueur possible entre les tentatives et même jeu pendant le défi.
- Objectifs, difficulté, nombre de tentatives, chiffre secret, durée globale et avertissement configurables extérieurement.
- Révélation du chiffre à la réussite, puis accès libre aux trois jeux jusqu’à expiration du temps global.
- Avertissement avant expiration et alarme finale ; écrans d’accueil, choix, jeu, résultat et fin ; mode test.
- Code, README, instructions d’installation et tests basiques ; aucune ROM ni ressource sous copyright à intégrer.

## Questions ouvertes

- Intensité adaptée au public, à fixer après essais.
- Vérifier sur le Mac de la salle la réception du clavier, le raccourci de remise à zéro, le plein écran et le niveau sonore.

## Prochaine étape

Réaliser le premier POC de mise en scène décrit dans le ticket https://github.com/Bricesodini/retro-gaming/issues/1. Le MVP complet à trois jeux reste l’objectif de livraison après cette étape de calibration.

## État du dépôt

Le 19 octobre 2026, le dossier local et le dépôt GitHub ont été constatés vides avant création de ces documents. Aucun jeu n’est encore implémenté.
