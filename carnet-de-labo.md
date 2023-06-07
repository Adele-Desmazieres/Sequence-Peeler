# Carnet de Laboratoire de stage

**Auteur** : Adèle DESMAZIERES

Stage à l'Institut Pasteur dans l'équipe SeqBio, du 05/06/23 au 04/08/23.

## Liens utiles

- Webcampus, the pasteur portal for everything: https://webcampus.pasteur.fr/
- The webmail location: https://email.pasteur.fr/
- Informatics resources: http://confluence.pasteur.fr/
- Restaurant app: https://app.foodi.fr/

--- 

## Lundi 5 juin : premier jour

### Réunion avec Yoann Dufresne

#### Manière de travailler

- poser des questions si bloquée
- code sur github en licence **GNU Affero GPL3**
- carnet de laboratoire sur github, écrire les comptes-rendus de réunion
- écrire résumés d'articles scientifiques sur github
- réunion avec Yoann 1h par semaine

#### Projet

**Objectif du projet** : un outil de data fuzzing qui permet de trouver l'entrée minimale utilisée dans un logiciel provoquant une sortie spécifique. Plus précisément trouver la ou les fragments de séquences d'un fichier fasta qui provoquent une erreur avec n'importe quel logiciel.

toto.fasta + binaire -> `$ bin toto.fasta` -> Segmentation Fault

Mon logiciel permettrait d'isoler automatiquement les lignes de toto.fasta provoquant l'erreur, sans les chercher à la main. 

**Principe** : l'outil prend une à une les séquences contenues dans le fichier fasta, et recherche l'exemple minimal provoquant le bug par algorithme de dichotomie. Découper la séquences en 2 sous-séquences de même taille, tester si le logiciel renvoie la sortie erreur sur la 1ere moitité, si oui répéter la recherche sur cette partie, si non tester l'autre moitié, et répéter la recherche dessus si elle renvoie une erreur. Si aucune des deux moitiées ne renvoie l'erreur, il y a deux explications possibles : 
- soit la séquence fautive est à la jonction des deux moitiées, dans ce cas il faut faire de la récurence sur une moitié centrale de la séquence
- soit il y a deux séquences qui sont fautives quand elles sont ensemble, dans ce cas on sépare ces deux moitiées dans des séquences à part et on fait de la récurrence sur chacune d'entre elles

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

## Mercredi 7 juin : réunion de projet

- séparer le github du projet et le github du carnet de labo
- documenter le projet en anglais : 
    * faire un README qui explique comment le lancer
    * documenter les foncions (commentaires suffisants ? -> traduits en anglais)
    * faire un wiki qui explique l'implémentation algorithique du projet ainsi que les choix que je suis amenée à faire et leur raison
- faire des exécutables variés : 
    * match un pattern précis
    * match une collection de patterns
    * match des patterns qui se chevauchent
    * match coocurrence de patterns à une distance spécifique
    * match les k+1-mers dont le suffixe est inverse complément de leur préfixe (expl : k=5 ACCGGT)
- utilisre les données du site ncbi avec le génome de Sars-cov2, de Ecoli et de l'humain
- cluster :
    * donner mon identifiant à Yoann pour qu'il me donne accès aux machines seqbio
    * je ne vais pas faire des soumission de job au cluster mais requérir les ressources d'une machine ssh pour travailler directement dessus
    * voir le manuel de `tmux [-a]` et  `salloc` que j'utiliserai à la place de `srun` et `sbatch`, et voir `ssh-copy-id` pour éviter de devoir rentrer mon mdp à chaque connexion
    * utiliser ces commandes depuis la tête du cluster, accessible avec `ssh adesmazi@maestro.pasteur.fr` 

--- 



