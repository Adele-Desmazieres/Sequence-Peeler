# Carnet de Laboratoire de stage

**Auteur** : Adèle DESMAZIERES

Stage à l'Institut Pasteur dans l'équipe SeqBio, du 05/06/23 au 04/08/23.

## Liens utiles

- https://email.pasteur.fr/owa/#path=/mail/inbox

## Lundi 5 juin

### Réunion avec Yoann Dufresne

#### Manière de travailler

- poser des questions si bloquée
- code sur github en licence **GNU Affero GPL3**
- carnet de laboratoire sur github, écrire les comptes-rendus de réunion
- écrire résumés d'articles scientifiques sur github
- réunion avec Yoann 1h par semaine

#### Projet

**Objectif du projet** : un outil de data fuzzing qui permet de trouver l'entrée minimale d'un logiciel provoquant une sortie spécifique. Plus précisément trouver la ou les fragments de séquences d'un fichier fasta qui provoquent une erreur avec le logiciel de Yoann, par exemple. 

toto.fasta + binaire -> $ bin toto.fasta -> seg fault

Mon logiciel permettrait d'isoler les lignes de tot.fasta provoquant l'erreur automatiquement, sans chercher à la main. 

**Principe** : l'outil prend une à une les séquences contenues dans le fichier fasta, et recherche l'exemple minimal provoquant le bug par algorithme de dichotomie. Découper la séquences en 2 sous-séquences de même taille, tester si le logiciel renvoie la sortie erreur sur la 1ere moitité, si oui répéter la recherche sur cette partie, si non tester l'autre moitié, et répéter la recherche dessus si elle renvoie une erreur. Si aucune des deux moitiées ne renvoie d'erreur, il y existe deux explications possibles : 
- la séquence fautive est à la jonction des deux moitiées, dans ce cas il faut faire de la récurence sur une moitié centrale de la séquence
- il y a deux séquences qui sont fautives quand elles sont ensemble, dans ce cas on sépare ces deux moitiées dans des séquences à part et on fait de la récurrence sur chacune d'entre elles

**Extensions possibles** : 
- paralléliser l'exécution du binaire sur les fichiers fasta réduits
- prendre plusieurs fichiers fasta en entrée
- tester la correspondance à n'importe quel type de sortie, pas seulement la sortie erreur

---

Mise en place d'une clef SSH entre mon github Adele-Desmazieres et l'ordinateur. 

### Présentation sur les bonnes pratiques de développement

Tests :
- tests fonctionnels : global, input dans logiciel puis comparaison de la sortie avec une sortie attendue
- tests unitaires : teste les fonctions individuellement
- continuous integration tests : teste tout au long du développement du logiciel

Git branch : 
- main : branche principale PROPRE, peut être utilisées par des utilisateurs
- dev : branche de développement propre
- feature 1, 2, 3... : branches de développement d'une feature en particulier, peut contenir un projet qui ne fonctionne pas

Utilisation des branches : 
- coder sur une branche de feature F (commit et push), tester
- tirer dev sur F, tester
- merge F sur dev, tester
- merge dev sur main

Tester vitesse d'éxecution : `/usr/bin/time -v prog`

Optimisation : ne pas optimiser prématurément. La complexité théorique ne reflète pas toujours la complexité réelle. Pour Python, voir **nprofil** pour créer des flamecharts, qui permettent de visualiser le temps d'exécution de chaque fonction du programme relativement les unes aux autres. 

--- 








