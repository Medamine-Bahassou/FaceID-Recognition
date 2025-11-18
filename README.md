# Système de Reconnaissance Faciale en Temps Réel

Ce projet est une application Python permettant d'identifier des personnes en temps réel à partir d'un flux vidéo (webcam). Le système compare les visages détectés à une base de données d'images pré-enregistrées, et ce, de manière évolutive pour gérer un grand nombre d'identités.

L'architecture est conçue pour être facilement maintenable : pour ajouter une nouvelle personne au système, il suffit de créer un dossier à son nom et d'y ajouter ses photos, sans aucune modification du code source.

## Fonctionnalités Clés

-   **Base de Données Dynamique** : Charge automatiquement les identités et les visages à partir d'une simple structure de dossiers.
-   **Pipeline de Reconnaissance Complet** : Intègre les étapes essentielles :
    1.  **Détection** des visages dans l'image.
    2.  **Extraction de Caractéristiques** (création d'un "encoding" facial).
    3.  **Comparaison et Identification** par calcul de similarité.
-   **Performances Optimisées** : Pour garantir une fluidité en temps réel, le script ne traite qu'une trame vidéo sur deux et opère sur une image redimensionnée (1/4 de la taille originale).
-   **Visualisation Claire** : Affiche le nom de la personne identifiée (ou "Inconnu") dans un cadre autour de son visage directement sur le flux vidéo.

## Comment ça marche ? Le concept

L'application suit un pipeline logique pour accomplir la reconnaissance faciale.

### 1. Chargement de la Base de Données (Phase d'Apprentissage)

Au lancement, le script exécute la fonction `load_known_faces()`. Cette fonction parcourt le dossier `database/` :
-   Chaque **nom de sous-dossier** est considéré comme le **nom d'une personne**.
-   Toutes les images (`.jpg`, `.png`, etc.) à l'intérieur de ce dossier sont chargées.
-   Pour chaque image, la bibliothèque `face_recognition` détecte le visage et le transforme en une représentation mathématique unique : un vecteur de 128 nombres, appelé **"face encoding"** (encodage facial).
-   Tous les encodages et les noms correspondants sont stockés en mémoire pour être utilisés lors de la phase d'identification.

### 2. Traitement en Temps Réel

Une fois la base de données chargée, le script active la webcam et entre dans une boucle infinie pour traiter le flux vidéo trame par trame.

-   **Étape A : Détection des Visages**
    Pour chaque trame capturée, la première tâche est de localiser tous les visages présents. La fonction `face_recognition.face_locations()` renvoie les coordonnées (haut, droite, bas, gauche) de chaque visage détecté.

-   **Étape B : Extraction des Caractéristiques**
    Pour chaque visage localisé, un **encodage facial** (le même vecteur de 128 nombres) est calculé, exactement comme pour les images de la base de données.

-   **Étape C : Comparaison et Identification**
    C'est le cœur de l'identification. L'encodage du visage détecté dans la trame est comparé à **tous les encodages** stockés depuis la base de données.
    -   La comparaison se fait en calculant la **"distance faciale"** (distance euclidienne) entre l'encodage du visage inconnu et chaque encodage connu.
    -   Plus la distance est faible, plus les deux visages sont similaires.
    -   Le nom associé à l'encodage connu ayant la **plus petite distance** est assigné au visage détecté.
    -   Un **seuil de tolérance** (ici, `tolerance=0.6`) est utilisé. Si la plus petite distance mesurée est supérieure à ce seuil, le visage est considéré comme "Inconnu", même s'il est techniquement plus proche d'une personne de la base de données.

## Structure du Projet

Pour que le script fonctionne correctement, vos fichiers doivent être organisés comme suit :

```
votre_projet/
├── reconnaissance_faciale.py  # Le script principal que vous exécutez
└── database/
    ├── Barack_Obama/
    │   ├── obama1.jpg
    │   └── obama_autre_photo.png
    ├── Joe_Biden/
    │   ├── biden1.jpeg
    │   └── biden_autre_angle.jpg
    └── Autre_Personne/
        └── photo.jpg
```

## Prérequis

Assurez-vous que Python 3 est installé. Vous devrez ensuite installer les bibliothèques nécessaires. La bibliothèque `dlib` peut parfois nécessiter des outils de compilation C++ (comme `build-essential` sur Linux ou les outils de build de Visual Studio sur Windows).

-   `face_recognition`
-   `opencv-python`
-   `numpy`
-   `dlib`

## Installation

Ouvrez un terminal ou une invite de commande et exécutez la commande suivante pour installer toutes les dépendances :

```bash
pip install -r requirements.txt
```

## Utilisation

1.  **Clonez ou téléchargez** ce projet sur votre machine.
2.  **Créez le dossier `database/`** à la racine du projet.
3.  **Populez la base de données** :
    -   Créez un sous-dossier dans `database/` pour chaque personne que vous souhaitez identifier. Le nom du dossier sera le nom affiché à l'écran.
    -   Ajoutez une ou plusieurs photos de bonne qualité de cette personne dans son dossier.
4.  **Lancez le script** depuis votre terminal :
    ```bash
    python reconnaissance_faciale.py
    ```
5.  Une fenêtre affichant le flux de votre webcam devrait s'ouvrir. Placez-vous ou d'autres personnes connues devant la caméra.
6.  Pour arrêter l'application, assurez-vous que la fenêtre de la webcam est active et appuyez sur la touche **'q'** de votre clavier.