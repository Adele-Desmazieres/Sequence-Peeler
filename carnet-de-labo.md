# Carnet de Laboratoire de stage

**Auteur** : Adèle DESMAZIERES

Stage à l'Institut Pasteur dans l'équipe SeqBio, du 05/06/23 au 04/08/23.

## Liens utiles

- https://email.pasteur.fr/owa/#path=/mail/inbox

## Lundi 5 juin

### Réunion avec Yoann Dufresne

#### Manière de travailler

- poser des questions si bloquée
- code sur github en licence GNU Affero GPL3
- carnet de laboratoire sur github, comptes-rendus de réunion
- résumés d'articles scientifiques sur github
- réunion avec Yoann 1h par semaine

#### Projet

**Objectif du projet** : un outil de data fuzzing qui permet de trouver l'entrée minimale d'un logiciel provoquant une sortie spécifique. Plus précisément trouver la ou les fragments de séquences d'un fichier fasta qui provoquent une erreur avec le logiciel de Yoann, par exemple. 

toto.fasta + binaire -> $ bin toto.fasta -> seg fault

Mon logiciel permettrait d'isoler les lignes de tot.fasta provoquant l'erreur automatiquement, sans chercher à la main. 

**Principe** : l'outil prend une à une les séquences contenues dans le fichier fasta, et recherche l'exemple minimal provoquant le bug par algorithme de dichotomie. Découper la séquences en 2 sous-séquences de même taille, tester si le logiciel renvoie la sortie erreur sur la 1ere moitité, si oui répéter la recherche sur cette partie, si non tester l'autre moitié, et répéter la recherche dessus si elle renvoie une erreur. Si aucune des deux moitiées ne renvoie d'erreur, il y existe deux explications possibles : 
- la séquence fautive est à la jonction des deux moitiées, dans ce cas il faut faire de la récurence sur une moitié centrale de la séquence
- il y a deux séquences qui sont fautives quand elles sont ensemble, dans ce cas on sépare ces deux moitiées dans des séquences à part et on fait de la récurrence sur chacune d'entre elles

**Extensions possibles** : 
- paralléliser l'exécution du binaire sur le fichier fasta réduit
- prendre plusieurs fichiers fasta en entrée
- tester la correpsondance à n'importe quel type de sortie, pas seulement la sortie erreur

---

Mis en place une clef SSH entre mon github Adele-Desmazieres et l'ordinateur. 


