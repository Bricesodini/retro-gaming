# Installer la borne sur OS X Lion 10.7.5 (Mac Intel, 2 Go)

Recherche du 21 octobre 2026. Cette note décrit les contraintes vérifiées et un chemin de fabrication ; elle ne certifie pas encore une version exécutable sur le Mac cible.

## Verdict

Le projet actuel ne peut pas être simplement copié dans un dossier d'installation pour OS X 10.7.5. Le README installe Python 3.11 et `pygame-ce==2.5.8` ; l'installeur officiel Python 3.11 exige macOS 10.9 ou ultérieur, et la roue `pygame-ce` 2.5.8 pour CPython 3.11 exige macOS 10.11 ou ultérieur. Ces exigences viennent des fichiers distribués par les deux projets, indépendamment du fait que le Mac soit Intel. [Python 3.11](https://www.python.org/downloads/release/python-3110/) ; [pygame-ce 2.5.8](https://pypi.org/project/pygame-ce/2.5.8/).

Un paquet `.app` créé sur un Mac récent ne corrige pas cela : PyInstaller explique que les bibliothèques compilées et les composants du système rendent l'application compatible avec le macOS de construction et les versions suivantes ; pour garantir un ancien système, il recommande de figer l'application sur ce système ancien. [PyInstaller, compatibilité macOS](https://pyinstaller.org/en/stable/usage.html#making-macos-apps-forward-compatible).

## Ce que permettent les versions anciennes

- Python 3.7.3 possède un installeur officiel **64 bits/32 bits pour OS X 10.6 et ultérieur**. Il peut donc servir de base à un prototype Lion, sous réserve de vérifier la machine réelle. Attention : la version 3.7.9 n'a déjà plus cet installeur 10.6+, et Python 3.7 est aujourd'hui en fin de support. [Python 3.7.3](https://www.python.org/downloads/release/python-373/) ; [Python 3.7.9](https://www.python.org/downloads/release/python-379/) ; [fin de support Python 3.7](https://www.python.org/downloads/release/python-3717/).
- Les roues précompilées trouvées pour `pygame` 2.0.1 sur Mac Intel sont étiquetées **10.9+** ; celles de `pygame` 1.9.6 sont **10.11+**. Elles ne constituent donc pas une installation prête pour Lion. Le site officiel de Pygame conserve un installeur ancien **1.9.2 préversion pour Python 2.7 fourni par Lion**, mais cet installeur ne peut pas exécuter le projet Python 3 actuel. [pygame 2.0.1](https://pypi.org/project/pygame/2.0.1/) ; [pygame 1.9.6](https://pypi.org/project/pygame/1.9.6/) ; [anciens téléchargements Pygame](https://www.pygame.org/download.shtml).
- Pygame documente la compilation depuis les sources avec ses dépendances SDL ; son guide Lion décrit une compilation ancienne avec Python 2.7 et Pygame 1.9.1. Cela prouve l'existence d'une voie de compilation sous Lion, **pas** la compatibilité d'une version Pygame 2 avec ce Mac. La combinaison Python 3.7 + Pygame 2 compilé sur Lion reste à établir sur la machine. [Compilation Pygame](https://www.pygame.org/wiki/MacCompile) ; [guide historique Lion](https://www.pygame.org/wiki/MacLionCompile).

## Adaptation du jeu nécessaire

Le code du dépôt utilise `X | Y` pour les types, ajouté en Python 3.10, ainsi que `list[T]` et `str.removeprefix`, ajoutés en Python 3.9. Pour Python 3.7, il faut adapter ces expressions dans l'ensemble des modules et vérifier les autres écarts de langage. [Fonctionnalités Python 3.10](https://www.python.org/downloads/release/python-31011/) ; [nouveautés Python 3.9](https://docs.python.org/3/whatsnew/3.9.html) ; exemples du dépôt : `retro_gaming/session.py`, `retro_gaming/app.py`.

L'interface emploie aussi `border_radius` de `pygame.draw.rect` et le mode `pygame.SCALED`. Pygame indique que ces fonctions sont apparues en 2.0. Une solution fondée sur le vieil installeur Pygame 1.9.2 demanderait donc d'adapter aussi le rendu et le plein écran. [pygame.draw.rect](https://www.pygame.org/docs/ref/draw.html) ; [pygame.display](https://www.pygame.org/docs/ref/display.html) ; exemples du dépôt : `retro_gaming/app.py`, `retro_gaming/maze/window.py`.

## Chemin recommandé

1. **Relever la machine cible** : architecture du processeur et résolution de l'écran dans « À propos de ce Mac » ; vérifier que le jeu peut afficher une sortie 1280 × 1024 (5:4), adaptée au CRT IBM E74 (`README.md`). Garder trace des versions exactes du système et du matériel.
2. **Faire un prototype Python 3 sur Lion** : installer l'archive officielle Python 3.7.3 10.6+, puis compiler une version choisie de Pygame 2 avec les dépendances SDL compatibles. Essayer d'abord une fenêtre, un rendu de texte, le chargement PNG, le clavier et la lecture audio. Consigner les versions et chaque erreur. La disponibilité de SDL/Pygame sur ce système est le principal risque technique encore ouvert.
3. **Adapter le projet à Python 3.7 et à la version Pygame réellement obtenue**. Tester ensuite tout le parcours (dossier, arrivée de l'entité et chronomètre, trois jeux, son, victoire, mode libre, fin et remise à zéro) sur le Mac de 2 Go. Une simple compilation syntaxique sur un Mac récent ne prouvera pas le fonctionnement sur Lion.
4. **Construire un dossier hors ligne, depuis l'environnement Lion validé** : installeur Python compatible ; paquet Pygame et dépendances SDL effectivement validés ; code et ressources du jeu ; `config.json` ; lanceur Finder ; notice courte et versions/checksums des composants. Le dossier doit permettre un nouvel essai sans télécharger des paquets depuis Lion. Une fois ce dossier éprouvé, une application `.app` peut être figée **sur Lion**, puis testée sur un second compte ou une installation propre de Lion. [PyInstaller, compatibilité macOS](https://pyinstaller.org/en/stable/usage.html#making-macos-apps-forward-compatible).

**Niveau de confiance :** élevé pour l'incompatibilité des distributions actuelles et les différences Python/Pygame documentées ; incertain pour la faisabilité de compiler Pygame 2 et ses bibliothèques sur OS X 10.7.5. Aucun essai n'a encore eu lieu sur le Mac cible. Le dossier d'installation final doit attendre ce premier essai matériel pour éviter de présenter une archive non exécutable comme prête à installer.
