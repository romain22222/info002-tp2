# TP2 - Générateur de diplômes

## Objectif

L'objectif de ce TP est de créer un générateur de diplômes.

## Installation

`pip install -r requirements.txt`

## Utilisation
`python main.py help`</br>
Chaque commande présente dans la commande `help` est détaillée ci-dessous.

---
`python main.py invert_half <input> <output>`</br>
Inverse la moitié des bits de poids faible de l'image `input` et écrit le résultat dans `output`.

---
`python main.py storeMessage <input> <output> <message> <fromPos> <jumpBackAfterXChars>`</br>
Stocke le message `message` dans l'image `input` et écrit le résultat dans `output`. Le message est stocké à partir de la position `fromPos` et revient à la ligne tous les `jumpBackAfterXChars` bits.

---
`python main.py recoverMessage <input>`</br>
Permet de récupérer le message stocké dans l'image `input`.

---
`python main.py setupKeys <name>`</br>
Génère une paire de clés publique/privée et les stocke dans les fichiers `keys/public.pem` et `keys/private.pem`.

---
`python main.py sign <message>`</br>
Signe le message `message` avec la clé privée de l'établissement et affiche le résultat.

---
`python main.py checkSignature <message> <signature>`</br>
Vérifie la signature `signature` du message `message` avec la clé publique de l'établissement.

---
`python main.py setupDiplomeBkg <input>`</br>
Permet de préparer l'image `input` pour y stocker un diplôme.

---
`python main.py putClearInformations <input> <name> <surname> <birthDate> <obtentionDate> <diplomaNumber> <diplomaName> <diplomaFormation> <mean> <mention>`</br>
Via le fond préparé avec `setupDiplomeBkg` à l'endroit désigné par `input`, permet de stocker les informations en clair dans le diplôme.

---
`python main.py putHiddenInformations <input> <diplomaNumber> <name> <surname> <notes> <coefficients> <codes>`</br>
Via le fond préparé avec `setupDiplomeBkg` à l'endroit désigné par `input`, permet de stocker les informations cachées dans le diplôme. Les notes / coefficients / codes sont séparés par des "-".

---
`python main.py showDiff <input1> <input2> <output>`</br>
Affiche la différence entre les images `input1` et `input2` et écrit le résultat dans `output`.

---
`python main.py putAllInformations <input> <name> <surname> <birthDate> <obtentionDate> <diplomaNumber> <diplomaName> <diplomaFormation> <mean> <mention> <notes> <coefficients> <codes>`</br>
Permet de stocker toutes les informations dans le diplôme à partir du fond préparé avec `setupDiplomeBkg` à l'endroit désigné par `input`. Les notes / coefficients / codes sont séparés par des "-".

---
`python main.py checkDiplome <input>`</br>
Permet de vérifier le diplôme `input`. Si le diplôme est valide, affiche les informations cachées dans le diplôme. Sinon, affiche un message d'erreur.

## Quels informations stocker en clair dans le diplôme ?

* Numéro de diplôme
* Nom de l'étudiant
* Prénom de l'étudiant
* Date de naissance de l'étudiant
* Date d'obtention du diplôme
* Intitulé du diplôme
* Intitulé de la formation
* Nom de l'établissement
* Moyenne de l'étudiant
* Mention de l'étudiant

## Quels informations stocker chiffrées / stéganographiées dans le diplôme ?

* Numéro de diplôme
* Signature du diplôme
* Notes et coefficients de l'étudiant

## Qui peut vérifier le diplôme ?

Tout le monde peut vérifier le diplôme, mais seul l'établissement peut le générer.

La signature du diplôme est vérifiable avec la clé publique de l'établissement.

Cette clé publique est stockée dans le diplôme ainsi que dans le stockage de l'établissement.

## Comment générer le diplôme ?

1. On pose les informations en clair dans le diplôme
2. On stéganographie les informations supplémentaires (numéro de diplôme, notes, coefficients, nom, prénom de l'étudiant)
3. On signe le diplôme avec la clé privée de l'établissement
4. On ajoute la signature au diplôme en stéganographie dans une zone dans laquelle tous les bits de poids faible du rouge sont à 0

## Comment vérifier le diplôme ?

1. On récupère les informations stéganographiées
2. On retire la signature du diplôme (eg. on remet à 0 les bits de poids faible du rouge dans la zone de la signature)
3. On vérifie la signature avec la clé publique de l'établissement
4. On vérifie que les informations en clair correspondent aux informations stéganographiées (par exemple, on recalcule la moyenne de l'étudiant avec les notes et les coefficients stéganographiés, ou encore on vérifie que le numéro de diplôme correspond à celui stéganographié)
5. Si ce qui est vérifiable correspond à ce qui est stéganographié, on renvoie les informations cachées dans le diplôme afin que le vérificateur puisse vérifier que le diplôme n'a pas été modifié

