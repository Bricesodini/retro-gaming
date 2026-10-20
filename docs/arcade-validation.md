# Validation des trois jeux d’arcade — 19 octobre 2026

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
