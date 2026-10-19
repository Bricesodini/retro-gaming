# Conception de l’animation

État : cadrage synthétisé dans la spec du premier POC, publiée dans le ticket GitHub #1 avec le label ready-for-agent. Les points ouverts ci-dessous restent à éprouver ; aucun code applicatif n’est encore implémenté.

## Choix validés

- Accueil sous forme de faux ordinateur de laboratoire de 1986.
- Possession déclenchée volontairement pendant l’animation, puis prise de relais par l’ordinateur pour le défi.
- Elf, le personnage de Onze (Eleven) dans Stranger Things, remplace le robot HAWK-80. Elle intervient avec ses pouvoirs pour contrer la possession et aider les participants ; elle transmet les règles du défi.
- Univers inspiré de Stranger Things : laboratoire abandonné, dimension parallèle, racines organiques et interférences rouges. La référence explicite à Elf remplace le choix antérieur d’une fiction entièrement originale ; les trois jeux et les ressources produites restent originaux.
- Public pouvant être relativement jeune ; des POC doivent permettre de calibrer l’intensité.
- Le chronomètre global démarre au déclenchement de la possession et inclut la mise en scène ; l’accueil n’est pas chronométré.
- Pas de commandes dédiées de pause du chronomètre ou de coupure des effets pour gérer les réactions du public : l’équipe d’animation gère la situation sur place.
- Après épuisement des tentatives, écran d’échec sans révélation automatique du chiffre. L’animateur peut accorder une tentative supplémentaire.
- Premier POC centré sur la séquence laboratoire → déclenchement → possession → intervention de Elf, avec deux intensités à comparer. Il sert à éprouver le déclenchement et la réaction du public avant la production complète des effets.
- Déclencheur du POC sur Mac : Contrôle + Option + Commande + Espace. F9 écarté pour des raisons pratiques sur ordinateur portable. La réception effective de la combinaison doit être validée sur la machine ; le choix d’une télécommande reste ouvert.
- À l’accueil, le terminal affiche seul ses diagnostics et sert de décor pendant l’introduction. Elf apparaît lors de la possession comme une alliée qui reprend contact.
- Premier test sans voix : texte lisible, consignes conservées à l’écran et bips originaux. La nécessité d’une voix sera évaluée après ce test, notamment pour les plus jeunes ; le choix d’une voix robotique concernait l’ancien personnage et n’est pas retenu pour Elf à ce stade.
- Deux variantes de possession, environ 12 secondes chacune, durée configurable : « Mystère » (diagnostics anormaux, parasites légers, racines, intervention de Elf) et « Tension » (mêmes informations, déformations plus marquées, silhouette abstraite, grondement plus présent). Sans flash rapide ni sursaut brutal.
- Après l’alarme finale, retour manuel réservé à l’animateur : effacement du chiffre affiché, des tentatives et du chronomètre, puis rétablissement du laboratoire de 1986 pour la prochaine équipe.
- Après la victoire, Elf reprend le contrôle, révèle le chiffre et déverrouille les trois jeux. Quelques traces de possession restent visibles dans une ambiance devenue rassurante.
- L’entité disparaît mais annonce qu’elle reviendra : la victoire dans cette salle est provisoire et prépare un nouveau combat plus tard dans le parcours.

## Contexte du parcours

Les équipes traversent plusieurs salles et y récupèrent des chiffres. Leur collecte leur permet d’accéder à l’ascenseur, qui les conduit en bas, dans le « monde à l’envers » de l’animation. Le départ de l’entité doit annoncer une menace future cohérente avec cette suite. Le texte exact de cette annonce reste à proposer ; il n’a pas été validé.

## Contraintes du MVP demandées

- Python/Pygame, développement et déploiement sur macOS Apple Silicon. Linux et Omarchy ne sont pas des plateformes cibles.
- Trois jeux originaux inspirés du labyrinthe à vider, du combat spatial par vagues et de l’empilement de blocs avec objectif de lignes.
- Un joueur à la fois, trois tentatives par défaut, changement de joueur possible entre les tentatives et même jeu pendant le défi.
- Objectifs, difficulté, nombre de tentatives, chiffre secret, durée globale et avertissement configurables extérieurement.
- Révélation du chiffre à la réussite, puis accès libre aux trois jeux jusqu’à expiration du temps global.
- Avertissement avant expiration et alarme finale ; écrans d’accueil, choix, jeu, résultat et fin ; mode test.
- Code, README, instructions d’installation et tests basiques ; aucune ROM ni ressource sous copyright à intégrer.

## Questions ouvertes

- Support du déclenchement : touche, clic, clavier déporté, télécommande Bluetooth ou matériel réutilisable. Aucun matériel choisi ni testé à ce stade.
- Intensité adaptée au public, à fixer après essais.
- Matériel définitif du déclenchement et prise en charge effective de la combinaison sur les systèmes cibles.

## Prochaine étape

Réaliser le premier POC de mise en scène décrit dans le ticket https://github.com/Bricesodini/retro-gaming/issues/1. Le MVP complet à trois jeux reste l’objectif de livraison après cette étape de calibration.

## État du dépôt

Le 19 octobre 2026, le dossier local et le dépôt GitHub ont été constatés vides avant création de ces documents. Aucun jeu n’est encore implémenté.
