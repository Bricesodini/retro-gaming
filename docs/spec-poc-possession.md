## Problem Statement

L’équipe d’animation prépare un escape game dans lequel les participants traversent plusieurs salles, récupèrent un chiffre dans chacune, puis utilisent les chiffres pour accéder à un ascenseur. Celui-ci les conduit dans le « monde à l’envers », où une nouvelle confrontation les attend.

Dans la salle rétro gaming, l’ordinateur doit sembler être un terminal de laboratoire de 1986 avant d’être possédé à un moment choisi par l’animateur. Elf, le personnage de Onze dans Stranger Things, intervient pour aider les participants. Avant de produire les trois jeux du MVP, l’équipe doit éprouver cette transition, son déclenchement et son intensité auprès d’un public pouvant être relativement jeune.

Le dépôt ne contient actuellement que le glossaire et les notes de conception. Aucun jeu, application, prototype ou test existant ne peut servir de base.

## Solution

Livrer un premier POC exécutable en Python/Pygame sur macOS Apple Silicon, qui sera la plateforme de déploiement. Il présente un terminal autonome de laboratoire, reçoit un déclenchement volontaire, joue une séquence de possession puis fait intervenir Elf par des messages lisibles accompagnés de sons originaux. Le POC s’arrête narrativement à l’annonce du défi ; il ne prétend pas proposer les trois jeux. Linux et Omarchy ne font pas partie des plateformes à prendre en charge ni à valider.

Deux variantes, « Mystère » et « Tension », permettent de comparer les réactions. Le temps global démarre au déclenchement. L’application gère son avertissement, son expiration et une remise à zéro manuelle pour l’équipe suivante. Les paramètres de calibration sont externes au code.

## User Stories

1. As an animateur, I want lancer le POC sur mon Mac Apple Silicon, so that je peux préparer la séance sur ma machine de développement.
2. As an animateur, I want des instructions d’installation et de lancement reproductibles sur Mac Apple Silicon, so that je peux préparer la machine de l’animation.
3. As a participant, I want découvrir un terminal de laboratoire de 1986, so that je rentre dans l’ambiance avant le défi.
4. As an animateur, I want des diagnostics qui défilent seuls à l’accueil, so that le terminal sert de décor pendant mon introduction.
5. As an animateur, I want un accueil sans chronomètre actif, so that je peux choisir le moment de démarrer l’épreuve.
6. As an animateur, I want déclencher la possession avec Contrôle + Option + Commande + Espace sur Mac, so that je peux lancer la séquence discrètement sans touche de fonction.
7. As an animateur, I want modifier le raccourci dans la configuration, so that je peux adapter le lancement à la machine et tester un clavier déporté.
8. As an animateur, I want qu’un appui prolongé ne relance pas la possession, so that une seule action démarre une seule session.
9. As a participant, I want voir le terminal progressivement envahi par des anomalies, so that je comprends qu’une présence a pris le contrôle.
10. As an animateur, I want une variante Mystère, so that je peux tester une ambiance inquiétante légère.
11. As an animateur, I want une variante Tension avec les mêmes informations narratives, so that je peux comparer l’intensité sans changer la compréhension du scénario.
12. As an animateur, I want modifier la durée de la possession, so that je peux ajuster son rythme après les essais.
13. As a jeune participant, I want une mise en scène sans flash rapide ni sursaut brutal, so that je peux suivre la séquence sans que ces effets dominent l’expérience.
14. As a participant, I want recevoir les messages d’Elf pendant la possession, so that j’identifie mon alliée face à l’entité.
15. As a participant, I want des consignes lisibles qui restent affichées, so that j’ai le temps de comprendre le défi annoncé.
16. As an animateur, I want tester d’abord le texte et les sons sans voix, so that je peux juger si une voix est nécessaire pour les plus jeunes.
17. As an animateur, I want que le chronomètre démarre au déclenchement et continue pendant la mise en scène, so that la séquence compte dans le créneau de l’équipe.
18. As an animateur, I want configurer la durée globale et le délai d’avertissement, so that je peux adapter le POC au rythme du parcours.
19. As a participant, I want recevoir un avertissement avant la fin puis une alarme finale, so that je comprends quand mon créneau se termine.
20. As an animateur, I want que l’expiration mette fin à la séquence depuis chaque phase active, so that la rotation des groupes reste maîtrisée.
21. As an animateur, I want réinitialiser manuellement la borne, so that l’équipe suivante retrouve le laboratoire initial et un chronomètre neuf.
22. As an animateur, I want un mode test qui accélère les délais, so that je peux vérifier les transitions sans attendre une session complète.
23. As an animateur, I want des images et sons produits pour ce POC sans ROM ni extrait de la série, so that le projet fonctionne sans collecte de médias externes.
24. As an animateur, I want comparer les deux variantes en conditions réelles, so that je peux choisir une intensité adaptée avant la réalisation du MVP.

## Implementation Decisions

- Périmètre : POC de mise en scène en premier, puis MVP complet dans une étape ultérieure. Les règles du MVP ci-dessous constituent une continuité de produit, pas des fonctions à simuler comme si elles étaient jouables dans ce POC.
- Base technique : Python avec Pygame-ce, ciblé sur macOS Apple Silicon. La version de Python et de la dépendance sera fixée à l’implémentation après vérification documentaire et installation réelle.
- Organisation proposée : un contrôleur de session possède les phases et le chronomètre ; la présentation Pygame traduit les entrées utilisateur, affiche ces phases et joue les sons. Le point de test principal est la session entière vue par ses entrées et sorties observables.
- Phases du POC : accueil laboratoire → possession → intervention d’Elf et annonce du défi. À expiration, passage à un écran de fin qui attend la remise à zéro. L’annonce du défi reste affichée jusqu’à expiration ou remise à zéro ; aucun faux bouton ne doit laisser croire à un jeu disponible.
- L’accueil affiche des diagnostics fictifs autonomes. Elf n’y est pas encore présente.
- Le déclenchement est volontaire et actif seulement depuis l’accueil. Sur Mac : Contrôle + Option + Commande + Espace. La réception réelle doit être vérifiée ; un conflit système doit être documenté et une combinaison alternative peut être définie par configuration.
- Le raccourci Mac doit être essayé sur macOS Apple Silicon. Une alternative peut être configurée si un conflit système est observé.
- Un clavier déporté peut être essayé comme source de la même entrée. Aucune compatibilité de télécommande Bluetooth n’est promise à ce stade.
- Mystère : diagnostics anormaux, parasites légers et racines qui envahissent l’écran, puis contact d’Elf. Tension : même trame, déformations plus marquées, silhouette abstraite et grondement plus présent. Durée initiale d’environ douze secondes, configurable. Aucun flash rapide ni sursaut brutal.
- Elf remplace entièrement HAWK-80 : c’est une alliée humaine dotée de pouvoirs, pas un robot. Le premier essai utilise du texte persistant et des sons originaux, sans voix. Les dialogues exacts seront écrits dans cet esprit et évalués pendant le POC.
- Le temps global commence à la réception du déclenchement, inclut la possession, puis continue pendant l’intervention d’Elf. L’avertissement est émis une seule fois au seuil prévu et l’alarme une seule fois à expiration ; le temps ne devient pas négatif.
- Configuration externe minimale : durée globale, durée de possession, délai d’avertissement, variante et raccourci. Les valeurs incohérentes doivent produire un message compréhensible avant le début de l’animation. Le mode test doit être identifiable et ne pas réécrire la configuration normale.
- Pas de commandes de pause du chronomètre ou de coupure d’urgence des effets ajoutées pour gérer le public : l’équipe a choisi une gestion sur place. La fermeture normale de l’application reste possible.
- La remise à zéro est réservée à l’animateur, distincte du déclenchement, et restaure l’accueil, le temps initial et l’état des alertes ; elle arrête les sons et effets de la session précédente. Son geste exact est un détail d’implémentation à documenter.
- Les ressources visuelles et sonores sont créées pour l’application : pas de ROM, musique, photographie, séquence vidéo ou voix extraite de la série.
- Fournir un README d’installation, lancement, configuration, commandes, mode test et validation sur Mac Apple Silicon. Ne pas annoncer de prise en charge d’une autre plateforme.

## Testing Decisions

- Une frontière de test principale au niveau du contrôleur de session : fournir les actions d’animateur et le temps écoulé, puis observer la phase, le temps restant et les événements d’avertissement ou d’alarme. Le temps doit être contrôlable dans les tests pour éviter les attentes réelles.
- Tester les comportements externes, sans figer le découpage interne, les noms de méthodes ou le dessin exact de chaque image.
- Couvrir l’accueil sans consommation du temps, le déclenchement unique malgré les répétitions, l’ordre des transitions, le temps consommé pendant la possession et la persistance des messages d’Elf.
- Couvrir chaque variante avec une durée configurable, l’avertissement unique, l’alarme unique et l’expiration pendant la possession comme pendant l’annonce du défi.
- Couvrir la remise à zéro et un second cycle complet : aucune ancienne alerte, aucun ancien message et aucun état de session ne doit persister.
- Vérifier le rejet des durées et seuils incohérents ainsi que l’isolation du mode test.
- Compléter ces tests par un lancement réel Pygame : réception du raccourci, lisibilité des textes, rendu des deux variantes, son, expiration et retour à l’accueil. Les tests sans écran ne valident ni le raccourci système, ni le matériel audio, ni l’intensité perçue.
- Faire une vérification visuelle et sonore sur Mac Apple Silicon. Consigner les vérifications effectuées et les points restant à vérifier sur cette plateforme.
- La calibration auprès du public est un essai d’usage : comparer compréhension, rythme et réaction aux deux variantes. Aucune intensité finale ni borne d’âge précise n’est considérée validée avant ces essais.
- Aucun précédent de test n’existe dans le dépôt. Les tests de session décrits ici sont le premier point de référence, plutôt qu’une nouvelle infrastructure dispersée entre les effets.
- Ce parcours de test a été présenté dans l’entretien avant l’invocation de cette synthèse ; aucune validation matérielle n’a encore été effectuée.

## Out of Scope

- Les trois jeux réellement jouables, leurs objectifs de victoire et leur équilibrage : réservés au MVP suivant.
- Dans ce POC, les tentatives, le changement de joueur, la révélation du chiffre, le mode libre et le résultat d’une partie ne sont pas implémentés.
- Le choix, l’achat et l’intégration d’une télécommande Bluetooth, d’un bouton physique ou d’un déclencheur réseau.
- La manette pour jouer, la voix d’Elf, une imitation vocale et la production de médias issus de la série.
- L’intégration avec les autres salles, le calcul du code final et le pilotage réel de l’ascenseur.
- L’autolancement de la borne au démarrage du système, les services réseau et le suivi des équipes.

## Further Notes

Le MVP reste l’objectif global : trois jeux originaux inspirés d’un labyrinthe à vider, d’un combat spatial avec vague ou niveau à terminer et d’un empilement de blocs avec nombre de lignes cible. Un joueur à la fois choisit un jeu ; trois tentatives par défaut restent sur ce jeu et autorisent un changement de joueur entre les essais. Objectifs, difficulté, chiffre secret, tentatives, durée et avertissement sont configurables.

Après épuisement des tentatives, aucun chiffre n’est révélé automatiquement ; l’animateur peut accorder une tentative supplémentaire. Après réussite, Elf reprend le contrôle, le chiffre de salle est révélé et les trois jeux deviennent accessibles jusqu’à expiration du temps. L’entité disparaît mais annonce son retour : il s’agit d’une victoire de salle, pas de sa défaite définitive. Quelques traces de possession restent visibles dans une ambiance devenue rassurante.

Le futur dialogue de départ doit préparer une confrontation ultérieure sans révéler prématurément la destination de l’ascenseur. Les phrases suggérées pendant l’entretien sont des propositions, pas des répliques définitives.

Le POC sera jugé utile si l’animateur peut lancer la possession au moment choisi, comparer les deux intensités, faire comprendre l’intervention d’Elf et remettre la borne en état pour une nouvelle équipe. Il n’atteste pas encore de la jouabilité des trois jeux ni de l’équilibrage du parcours complet.
