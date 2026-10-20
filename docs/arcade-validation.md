# Validation de la borne rétro gaming

Les sections datées du 19 octobre ci-dessous conservent l'historique des essais des jeux autonomes. La section du 20 octobre distingue le parcours intégré du ticket #14, les preuves disponibles et les essais restant à réaliser sur la borne.

Ce compte rendu concerne l’[issue #10](https://github.com/Bricesodini/retro-gaming/issues/10). Les trois jeux restent des lanceurs autonomes (`python -m retro_gaming.maze`, `python -m retro_gaming.space_combat`, `python -m retro_gaming.platformer`) ; le POC de possession, sa session et sa configuration ne changent pas. Chaque moteur expose `Game.advance(temps, entrées) -> GameState`, ce qui permet de vérifier ses règles sans fenêtre.

## Vérifications effectuées

- Dans `.venv`, CPython **3.11.11**, pygame-ce **2.5.8** et SDL **2.32.10** : `python -m unittest discover -s tests -q` termine avec **45 tests réussis**.
- Les trois fenêtres ont été lancées avec le pilote vidéo **Cocoa**. Une première capture du labyrinthe a bloqué ; un nouvel essai a réussi. Les métriques des essais aboutis sont dans les fichiers temporaires `native-maze.json`, `native-space_combat.json` et `native-platformer.json` : respectivement **212**, **213** et **222** images, `moved: true` et `escape_seen: true` pour chaque jeu.
- L’essai Cocoa a **injecté par logiciel** la touche `d` maintenue, avec `Espace` maintenue pour le combat spatial et les plateformes, puis `Échap`. Il atteste la réception des commandes, un déplacement et la fermeture normale ; il ne constitue pas un essai de touches pressées physiquement.
- Les captures de jeu actif `maze.png`, `space.png` et `platformer.png`, ainsi que les captures de fenêtres macOS `cocoa-maze.png`, `cocoa-space_combat.png` et `cocoa-platformer.png`, sont dans `/tmp/retro-gaming-arcade-validation/`. Les six images `*-victory-render-fixture.png` et `*-defeat-render-fixture.png` sont des **états de rendu fabriqués pour l’inspection des écrans de résultat** : elles ne prouvent pas qu’une manche complète a été gagnée ou perdue en jouant. Tous ces fichiers sont temporaires et ne sont pas intégrés au dépôt.

## Revue visuelle

La comparaison avec les fenêtres du commit `ab61395` montre la continuité de l’arcade existante : fonds sombres, couleurs vives, typographie monospace et personnages dessinés par Pygame. Les éléments sont produits par des formes et du texte procéduraux, sans ressources graphiques externes. Le labyrinthe conserve une grille lisible et distingue joueur, quatre fantômes et super-pastilles ; le combat affiche score, vies, abris et tirs ; les plateformes montrent les passerelles inclinées, échelles, singe, princesse et **plusieurs barriques visibles**. La correction antérieure de lisibilité des tirs ennemis apparaît bien résolue sur la capture active du combat. Les captures spatiales à deux instants différents ont des pixels d’étoiles différents, cohérents avec leur défilement.

## Limites restantes

Le score cible initial de **3 000 points** et les cadences de jeu demandent un réglage manuel en conditions d’animation. Aucun essai auprès d’enfants ni validation de la difficulté en salle n’a été réalisé. Les captures et l’injection de commandes ne remplacent pas une partie complète avec un clavier physique.

## Reprise des plateformes après essai — 19 octobre 2026

À la demande de l’utilisateur (« il manque des ennemis », revoir l’animation en regardant les niveaux originaux), la scène a été enrichie après la première validation ci-dessus. Les références consultées sont les tableaux [25 m](https://www.mariowiki.com/25m), [50 m](https://www.mariowiki.com/50m), [75 m](https://www.mariowiki.com/75m) et [100 m](https://www.mariowiki.com/100m), ainsi que le [manuel Nintendo de la version NES](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAEE_en.pdf). Ce dernier décrit trois stages et ne documente pas à lui seul les quatre tableaux de l’arcade. L’adaptation conserve une scène unique ; les boules de feu et le brasier viennent surtout du principe du tableau à poutrelles, les autres références guidant la variété des chemins et la pression des ennemis.

Deux ennemis de feu sont visibles dès le départ. Ils poursuivent le joueur sur les poutrelles et montent ou descendent les échelles. Le brasier produit un nouvel ennemi toutes les sept secondes, avec quatre ennemis mobiles au maximum ; son contact est dangereux lui aussi. Huit échelles donnent deux routes par changement d’étage. L’intervalle initial des barriques est de 2,4 secondes et diminue pendant l’ascension. Les trois vies et la victoire auprès de la princesse sont conservées.

Le singe a une préparation de lancer, un geste de libération et une récupération liés à la génération réelle des barriques. Marche, grimpe, saut et orientation du personnage suivent la simulation ; la rotation des barriques suit leur déplacement. Les animations de jeu s’arrêtent avec la simulation pendant la pause de réapparition et après le résultat.

La suite complète passe désormais avec **54 tests**. Elle couvre aussi poursuite, échelles des ennemis, apparition plafonnée, collision avec les flammes et le brasier, évitement par saut, trois vies, synchronisation du lancer et indépendance du découpage temporel. Un parcours de simulation termine la scène par défaut avec les ennemis et les barriques actifs, en conservant trois vies : cela établit l’existence d’un parcours gagnant, pas une calibration de difficulté pour le public.

Un nouvel essai natif Cocoa a reçu `d` et `Espace`, constaté un déplacement et fermé par `Échap` (**230 images**). Les preuves temporaires sont dans `/tmp/retro-gaming-platformer-rework/` : `native-platformer.json`, `cocoa-platformer.png`, six captures `scene-*.png` et `animation.gif` (séquence déterministe de sept secondes à 15 images/s). Les captures illustrent le rendu ; l’essai clavier reste une injection logicielle. La relecture indépendante des règles n’a pas relevé de défaut matériel ; le brasier décoratif initial a été rendu dangereux pour correspondre à son apparence. L’essai physique et le réglage de difficulté restent à faire avec l’utilisateur.

## Correction du parcours et des pentes — 19 octobre 2026

Nouveau retour utilisateur : retirer les échelles centrales et faire suivre aux barriques le dénivelé pour qu’elles constituent de vrais obstacles. Cette correction remplace la disposition à huit échelles décrite plus haut : **six poutrelles, cinq échelles uniquement aux extrémités**, alternativement à droite et à gauche. Chaque traversée vers la prochaine échelle monte à contre-pente, face aux barriques descendantes. Le singe reste en haut à gauche. Deux barriques sont en circulation dès le départ, dont une sur la poutrelle du joueur.

Le sens de roulement dépend de la pente réelle, même si une barrique a été initialisée dans le sens opposé ; la vitesse augmente dans la pente, avec une limite. Les chutes en bout de poutrelle suivent la gravité et reprennent le sens de descente de la poutrelle inférieure. Le saut a été raccourci pour permettre de franchir les barriques tout en restant sous l’écart entre deux étages.

**56 tests passent**, dont 25 pour les plateformes. Les nouveaux scénarios protègent l’absence d’échelles centrales, l’orientation de chaque montée face aux barriques, le roulement dans le sens descendant, la traversée des six poutrelles par une barrique sans jamais remonter, et un saut de barrique venant de face suivi d’une victoire par l’échelle de bord dans une scène à deux étages. Le parcours complet sans dangers reste vérifié. Le parcours gagnant de la version précédente utilisait les raccourcis centraux ; il ne valide pas la difficulté du nouveau parcours complet avec tous les dangers actifs, qui reste à essayer en jeu.

Le nouvel essai Cocoa a reçu déplacement, saut et Échap, avec **215 images** et fermeture normale. Captures et aperçu de six secondes dans `/tmp/retro-gaming-platformer-slopes/` (`scene-000.png`, `scene-045.png`, `scene-090.png`, `cocoa-platformer.png`, `animation.gif`, `native-platformer.json`). L’aperçu montre aussi une perte de vie et la pause de reprise. Les relectures indépendantes des règles n’ont pas relevé de défaut matériel sur cette correction. Il s’agit toujours d’entrées injectées par logiciel, sans essai physique du clavier.

## Ajustement de difficulté et terrasse de la princesse — 19 octobre 2026

Après le retour « un poil trop dur », l’intervalle initial des lancers passe de **2,4 à 2,8 secondes** et la vitesse maximale des barriques de **185 à 170 px/s**. Les pentes, les échelles aux bords, les ennemis et les trois vies sont conservés. La princesse occupe maintenant une petite terrasse surélevée au-dessus du singe, accessible par une dernière section d’échelle au bord droit. Les barriques continuent à partir de la poutrelle du singe ; elles ne naissent pas sur la terrasse de sauvetage.

Les **57 tests** passent, dont l’accès à la terrasse par la jonction des deux sections d’échelle, la victoire sur cette terrasse et le parcours complet sans dangers. L’inspection des captures `start.png` et `terrace.png` dans `/tmp/retro-gaming-platformer-princess/` confirme la hauteur de la princesse et la place de sa couronne et de son libellé sous le HUD. La fenêtre mesure désormais 860 × 832 pixels. Un essai Cocoa de **219 images** a reçu déplacement/saut et Échap, avec déplacement constaté et fermeture normale ; preuve temporaire `native-platformer.json` et capture `cocoa-platformer.png` dans le même dossier. La relecture visuelle n’a pas relevé de défaut matériel. La préférence de difficulté reste à confirmer par un nouvel essai utilisateur.

## Espacement des barriques au sommet — 19 octobre 2026

Retour utilisateur : trop de barriques en arrivant en haut. La montée en cadence reste identique au début, puis elle est plafonnée : l’intervalle ne descend plus sous 80 % de sa valeur initiale, soit **2,24 secondes** avec le réglage de 2,8 secondes. Auparavant, la courbe pouvait descendre à 1,12 seconde. Le nouveau test fait monter le joueur sur un étage supérieur et vérifie l’espacement ainsi que le nombre de lancers sur 6,5 secondes. **58 tests passent** ; aucun changement de disposition ni de rendu.

## Réduction plus nette de la pression — 19 octobre 2026

Après le retour « trop dur encore », le réglage par défaut passe à **4 secondes entre les lancers**, avec un minimum de **3,2 secondes au sommet**. Les barriques partent à **85 px/s** et sont plafonnées à **125 px/s**, contre 170 auparavant. Une seule barrique est présente au départ, contre deux. Les deux flammes initiales passent à 28 et 24 px/s ; le brasier génère une flamme après 14 secondes au lieu de 7, avec trois flammes mobiles au maximum au lieu de quatre. Le parcours, les pentes et la terrasse restent identiques.

Les **58 tests passent**. Le scénario de saut utilise désormais la vitesse observable de la barrique pour attendre son approche avant de sauter : une barrique plus lente exige d’attendre davantage, plutôt que de conserver une distance de déclenchement fixe. Ces vérifications établissent les règles ; l’utilisateur doit encore confirmer son ressenti avec ce nouveau réglage.

## Parcours intégré et préparation de la borne — 20 octobre 2026, ticket #14

### Vérifications exécutées dans le worktree du ticket

Machine d'exécution : macOS 27.0.1 sur architecture `arm64`. Environnement créé depuis la racine du dépôt avec les commandes suivantes :

```sh
uv python install 3.11.11
uv venv --python 3.11.11 --seed .venv
.venv/bin/python -m pip install --requirement requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q retro_gaming tests
```

L'installation a donné CPython 3.11.11 et pygame-ce 2.5.8. La suite `unittest` s'est terminée avec **79 tests réussis**, sans erreur. Elle vérifie notamment les deux variantes, le déclenchement unique, le seuil d'avertissement et l'alarme uniques, le choix des trois jeux, leurs trois vies, les victoires, les trois échecs distincts, la révélation du chiffre configuré, le mode libre, la priorité de l'échéance, les réglages numériques de jeu et plusieurs remises à zéro suivies d'un second cycle. Ces preuves sont des tests contrôlés du modèle ; elles ne démontrent pas un parcours effectivement joué au clavier dans la fenêtre.

Un essai court de `retro_gaming.app.run()` avec `--fullscreen --test-mode`, `SDL_VIDEODRIVER=cocoa` et sortie audio SDL simulée s'est terminé normalement après **70 images**. Le canevas logique mesurait **1 200 × 760** et la fenêtre plein écran **2 056 × 1 290** sur l'écran disponible. Des événements Pygame **injectés par logiciel** ont déclenché successivement laboratoire, possession et Elf, puis Échap a quitté l'application. Cet essai vérifie l'ouverture du plein écran Cocoa, l'échelle logique et le traitement de ces événements synthétiques ; il ne prouve ni la pression d'un clavier physique, ni la lisibilité à distance, ni la qualité de la sortie audio réelle.

Après correction du mode test, un second essai Cocoa de `retro_gaming.app.run() --test-mode`, avec sortie audio SDL simulée, a injecté par logiciel le déclencheur, Entrée, le choix **2** et une touche **Droite** maintenue, puis Échap. Les **56 images** ont traversé laboratoire, possession, Elf, choix et combat spatial. Les huit appels à `Game.advance` de la partie ont reçu chacun **0,35 seconde simulée** pour environ **0,035 seconde réelle** par image, soit **2,8 secondes de jeu simulé** ; le vaisseau a atteint `x = 936` depuis `x = 480`. Cela prouve l'accélération et un mouvement observé dans le parcours intégré avec **entrées synthétiques**, pas la jouabilité au clavier physique.

Les essais Cocoa antérieurs consignés plus haut et dans le README précédent avaient employé **System Events ou des entrées injectées par logiciel**. Ils indiquent que Pygame a reçu des événements, que les fenêtres et certains sprites ont été rendus et que le mélangeur s'est initialisé. Ils ne constituent pas une pression physique du clavier, une écoute acoustique indépendante, ni une partie complète de chacun des trois jeux dans le parcours intégré. Les captures temporaires mentionnées plus haut peuvent ne plus être présentes sur une autre machine.

### Procédure manuelle à effectuer sur le Mac Apple Silicon de la salle

1. Suivre l'[installation du README](../README.md), choisir la sortie audio réellement utilisée et vérifier que la fenêtre de 1 200 × 760 pixels est entièrement visible. Lancer aussi `--fullscreen` et vérifier l'échelle, les éventuelles bandes, la lisibilité et la sortie avec Échap. Dupliquer `config.json` pour les essais. Noter modèle du Mac, version de macOS, écran, clavier, sortie et volume audio, variante et fichier de configuration.
2. Lancer `.venv/bin/python -m retro_gaming --config /chemin/vers/copie.json`. Observer l'accueil sans chronomètre. **Appuyer physiquement** sur une touche ordinaire ; vérifier que le temps global démarre aussitôt et qu'un signal inconnu annonce l'arrivée pendant dix secondes. Vérifier ensuite la montée sombre de l'entité, l'audibilité du grondement et le portrait d'Elf. Essayer le raccourci Contrôle + Option + Commande + Espace avant et pendant cette attente : il doit remettre le laboratoire en veille sans armer l'arrivée. Refaire avec `Mystère` puis `Tension` en gardant le même volume.
3. Appuyer sur **Entrée**, puis **1**, **2** ou **3**. Vérifier les contrôles du [README](../README.md), l'affichage des trois vies, des scores et des objectifs, ainsi que la musique originale propre à chaque jeu. Jouer réellement chaque jeu avec le clavier physique : au labyrinthe, inspecter personnage, fantômes, super-pastilles et collisions ; au combat, vaisseau, abris, projectiles des deux camps, collisions et étoiles en mouvement ; aux plateformes, personnages, barriques, flammes, échelles, sauts et collisions. Essayer aussi chaque lanceur autonome et le fermer par **Échap**.
4. Jouer une issue gagnante pour **chacun des trois jeux**, avec remise à zéro entre les cycles. Vérifier que le chiffre de salle apparaît, que les trois jeux sont accessibles en mode libre, que le chronomètre n'est plus affiché et que l'échéance interrompt le jeu libre avec l'invitation d'Elf à rejoindre la salle suivante.
5. Perdre les trois vies d'un jeu ; constater que la reprise du signal est une courte confrontation animée distincte de la possession initiale, puis qu'Elf repropose rapidement un jeu encore disponible. Vérifier que le portrait reste lisible et que les musiques s'arrêtent/changent aux transitions. Perdre les trois jeux différents ; vérifier l'écran d'échec sans chiffre ni quatrième jeu, son maintien jusqu'à l'échéance et le signal final.
6. Essayer la remise à zéro depuis le laboratoire en veille et le signal en attente, la possession, le choix, chacun des jeux, un résultat, la victoire, le mode libre, l'échec et la fin. Confirmer l'arrêt des sons et le retour de l'accueil. Refaire ensuite un parcours complet : aucun chiffre, jeu tenté, vie, message, avertissement ou résultat de l'équipe précédente ne doit subsister.
7. Lancer `--test-mode` avec une copie de configuration adaptée : vérifier le badge, les durées réduites à 10 % (dont l'attente ramenée à une seconde), le jeu actif accéléré 10 fois et l'absence de modification du fichier normal. Régler la durée de la copie assez haut pour pouvoir terminer une partie. Faire la calibration destinée au public en mode normal.

Pour chaque jeu, consigner **durée réelle, vies restantes, causes des collisions, score ou progression atteinte, lisibilité des sprites et projectiles, et éventuelle gêne sonore ou visuelle**. Ne régler le score cible ni les cadences qu'après ces essais dans la salle avec le public prévu. Aucun réglage de difficulté n'est déduit d'une simulation.

### État des critères du ticket #14

| Critère | État vérifiable au 20 octobre 2026 |
| --- | --- |
| Durées, seuil, variante et chiffre de salle extérieurs au code | Présents dans `config.json` et vérifiés en partie par `tests/test_config.py`. La première touche et le raccourci de remise à zéro sont fixes. |
| Objectifs et difficultés des trois jeux extérieurs au code | Section optionnelle `games` intégrée, documentée dans le README. Les tests contrôlent le chargement et des effets de paramètres au point d'entrée public des jeux. La calibration des valeurs sur la borne reste à faire. |
| Configuration invalide expliquée avant affichage | Contrôles présents pour les champs connus, y compris les nombres de jeu, noms de jeu et de réglage inconnus ; tests de variante, chiffre, ancien champ `trigger` et valeurs de jeu invalides. Essai visuel du message d'erreur encore à faire. |
| Mode test et remise à zéro sans état résiduel | Comportements couverts par le code et les tests de `Session` ; essai physique des raccourcis et des sons encore à faire. |
| Portraits d'Elf et du Démogorgon, musique, flash rouge au déclenchement, parasites CRT et reprise de signal | Présents dans la version locale ; vérifier que le flash reste ponctuel, que les phrases musicales d'environ 15 secondes paraissent variées et restent en retrait, et que les parasites restent lisibles sur la borne. |
| Parcours complet, audio, affichage, plein écran et second cycle sur la borne | **En attente d'un essai manuel complet** sur le Mac et avec le clavier, l'écran et la sortie audio réellement prévus. |
| Trois jeux autonomes au clavier physique ; calibration du score et des cadences | **En attente de parties physiques complètes en salle**. Les anciens essais injectés et les tests de moteur ne prouvent pas ce critère. |
