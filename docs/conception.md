# Conception de l’animation

État : l’application Pygame et les trois jeux sont présents dans le dépôt. Cette conception consigne le nouvel accueil au commissariat et son déclenchement ; le texte de l’issue GitHub #1 décrit encore l’ancien accueil de laboratoire et devra être synchronisé.

## Choix validés

- L’interface d’accueil représente un poste informatique de commissariat et affiche le dossier de personne disparue de Will Byers avec son portrait pixelisé et le statut « disparu ». Le reste de l’univers narratif n’est pas modifié par ce changement d’interface.
- Possession déclenchée volontairement pendant l’animation, puis prise de relais par l’ordinateur pour le défi.
- Elf, le personnage de Onze (Eleven) dans Stranger Things, remplace le robot HAWK-80. Elle intervient avec ses pouvoirs pour contrer la possession et aider les participants ; elle transmet les règles du défi.
- Univers inspiré de Stranger Things : dimension parallèle, racines organiques et interférences rouges. La référence explicite à Elf remplace le choix antérieur d’une fiction entièrement originale ; les trois jeux et les ressources produites restent originaux.
- Public pouvant être relativement jeune ; des POC doivent permettre de calibrer l’intensité.
- La touche Entrée ouvre le dossier avec une animation ; trois secondes après l’ouverture, le Démogorgon arrive et démarre l’unique chronomètre global. L’accueil et l’ouverture du dossier ne consomment pas le temps. Le même chronomètre continue pendant les scènes et les parties jusqu’à l’échéance globale.
- Le chronomètre commence à l’arrivée de l’entité, puis son affichage rouge apparaît sur l’écran de transmission d’Elf.
- Pas de commandes dédiées de pause du chronomètre ou de coupure des effets pour gérer les réactions du public : l’équipe d’animation gère la situation sur place.
- Après épuisement des tentatives, écran d’échec sans révélation automatique du chiffre. L’animateur peut accorder une tentative supplémentaire.
- La séquence d’accueil est : dossier de Will Byers en attente → appui sur Entrée → animation d’ouverture → dossier ouvert pendant trois secondes → arrivée du Démogorgon et démarrage du chronomètre global → possession et intervention d’Elf.
- Sur Mac, Contrôle + Option + Commande + Espace remet la borne à l’état initial. Entrée ouvre le dossier ; Échap quitte l’application.
- L’accueil affiche le dossier et une touche Entrée fixe qui clignote doucement pour inviter à l’ouverture. Les diagnostics du laboratoire et les libellés d’état du terminal sont retirés ; aucun autre fait d’histoire n’est ajouté à la fiche.
- Premier test sans voix : texte lisible, consignes conservées à l’écran et bips originaux. La nécessité d’une voix sera évaluée après ce test, notamment pour les plus jeunes ; le choix d’une voix robotique concernait l’ancien personnage et n’est pas retenu pour Elf à ce stade.
- Deux variantes de possession, environ 12 secondes chacune, durée configurable : « Mystère » (diagnostics anormaux, parasites légers, racines, intervention de Elf) et « Tension » (mêmes informations, déformations plus marquées, portrait du Démogorgon, grondement plus présent). L'arrivée comporte un seul flash rouge bref, demandé ultérieurement ; aucun flash n'est répété et aucun sursaut brutal n'est ajouté.
- Après l’alarme finale, l’écran invite à rejoindre la salle suivante et reste affiché jusqu’à la remise à zéro de l’animateur. La remise à zéro efface le chiffre, les tentatives et le chronomètre, puis rétablit l’accueil du commissariat.
- Après la victoire, Elf reprend le contrôle, remercie l’équipe et révèle le chiffre en grand, au centre. Le chronomètre global reste visible en vert et continue de s’écouler pendant la révélation et le mode libre.
- La réplique de fin reste courte et suggère que l’entité pourrait revenir : « Il est parti… mais je ne crois pas que ce soit fini. »
- En mode libre, les touches 1, 2 et 3 lancent les jeux ; M ramène au choix depuis une partie. La musique des jeux est moins forte que les autres sons.

## Contexte du parcours

Les équipes traversent plusieurs salles et y récupèrent des chiffres. Leur collecte leur permet d’accéder à l’ascenseur, qui les conduit en bas, dans le « monde à l’envers » de l’animation.

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

Synchroniser l’issue GitHub #1 avec le nouvel accueil et le démarrage du chronomètre à l’arrivée de l’entité avant de demander une nouvelle implémentation de ce scénario.

## État du dépôt

Le 19 octobre 2026, le dépôt était initialement vide avant la création des documents. Il contient désormais l’application Pygame et les trois jeux ; l’issue #1 et certaines spécifications locales reflètent encore le cadrage initial.
