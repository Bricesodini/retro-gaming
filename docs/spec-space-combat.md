## Objectif

Comme participant, je veux jouer à un combat spatial original afin de terminer une vague en détruisant tous les ennemis.

Ce ticket livre le premier jeu jouable du MVP, séparément du parcours POC actuel. Il ne laisse pas entendre que les deux autres jeux existent.

## Comportement attendu

- Le jeu se lance séparément avec `python -m retro_gaming.space_combat`; lancer `python -m retro_gaming` conserve le parcours POC actuel.
- Le joueur déplace son vaisseau à gauche et à droite avec les flèches ou A/D, et tire avec Espace.
- Une vague d’ennemis originale traverse la zone de jeu et descend progressivement. Le joueur peut détruire les ennemis en les touchant avec ses tirs.
- Détruire tous les ennemis termine la vague par une victoire.
- Si un ennemi atteint le bas de la zone de jeu, la vague se termine par un échec.
- Les écrans de victoire et d’échec restent visibles jusqu’à la fermeture du jeu.
- Le jeu ne présente ni ROM, ni média sous copyright, ni choix donnant l’impression que les deux jeux non livrés sont disponibles.
- Cible : macOS Apple Silicon.

## Hors périmètre de ce ticket

- Intégration à la séquence du POC ou à un écran de sélection des jeux.
- Tentatives du défi, changement de joueur, révélation du chiffre, mode libre, durée globale et avertissement de fin.
- Deux autres jeux, équilibrage final, configuration externe de difficulté ou calibration auprès du public.

## Critères d’acceptation

- [ ] La commande dédiée ouvre une fenêtre jouable; la commande POC existante garde son comportement et son aide.
- [ ] Un joueur peut déplacer son vaisseau dans les deux directions sans sortir de la zone de jeu.
- [ ] Appuyer sur Espace tire; les tirs peuvent toucher et retirer des ennemis.
- [ ] Les ennemis traversent la zone et descendent progressivement; le mouvement dépend du temps écoulé, pas du nombre de tours de boucle.
- [ ] Quand tous les ennemis sont détruits, l’état observable devient « victoire » et l’écran correspondant reste affiché.
- [ ] Quand un ennemi atteint le bas, l’état observable devient « échec » et l’écran correspondant reste affiché.
- [ ] L’état de partie peut être piloté et observé sans fenêtre ni attente réelle : le seam public reçoit le temps écoulé et les entrées du joueur, puis expose la progression et le résultat (victoire/échec).
- [ ] Des tests automatisés couvrent déplacement, tir/destruction, victoire et échec au seam public approuvé.
- [ ] Les graphismes et sons éventuels sont originaux; le projet reste ciblé sur macOS Apple Silicon.

## Contraintes

Réutiliser Python et pygame-ce du dépôt. Préserver le parcours POC par défaut. Garder la simulation testable sans affichage; le rendu Pygame adapte les entrées et présente l’état du jeu.
