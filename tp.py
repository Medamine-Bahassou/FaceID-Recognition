import face_recognition
import cv2
import numpy as np
import os
import glob # Utilisé pour trouver les chemins des fichiers images

# --- 1. Chargement de la base de données et encodage des visages ---

def load_known_faces(database_path='database'):
    """
    Charge les images et encode les visages à partir d'une structure de dossiers.
    
    :param database_path: Le chemin vers le dossier racine de la base de données.
    :return: Deux listes : les encodages de visage connus et les noms correspondants.
    """
    known_face_encodings = []
    known_face_names = []

    print("Chargement de la base de données de visages...")

    # Parcourir chaque sous-dossier (chaque personne) dans le dossier de la base de données
    for person_name in os.listdir(database_path):
        person_dir = os.path.join(database_path, person_name)
        
        # S'assurer que c'est bien un dossier
        if not os.path.isdir(person_dir):
            continue

        # Trouver toutes les images dans le dossier de la personne
        # Prend en charge les formats jpg, png, jpeg
        image_paths = glob.glob(os.path.join(person_dir, '*.[jJ][pP][gG]')) + \
                      glob.glob(os.path.join(person_dir, '*.[pP][nN][gG]')) + \
                      glob.glob(os.path.join(person_dir, '*.[jJ][pP][eE][gG]'))

        # Encoder chaque image de la personne
        for image_path in image_paths:
            print(f"Traitement de {image_path} pour {person_name}")
            try:
                image = face_recognition.load_image_file(image_path)
                # On suppose qu'il n'y a qu'un seul visage par image dans la base de données
                face_encoding_list = face_recognition.face_encodings(image)
                
                if face_encoding_list:
                    face_encoding = face_encoding_list[0]
                    known_face_encodings.append(face_encoding)
                    known_face_names.append(person_name)
                else:
                    print(f"AVERTISSEMENT : Aucun visage détecté dans {image_path}. Fichier ignoré.")

            except Exception as e:
                print(f"ERREUR lors du chargement de l'image {image_path}: {e}")

    print("Chargement terminé.")
    return known_face_encodings, known_face_names

# Charger les visages connus au démarrage
known_face_encodings, known_face_names = load_known_faces()

# --- 2. Initialisation de la capture vidéo et des variables ---

# Obtenir une référence à la webcam #0 (la webcam par défaut)
video_capture = cv2.VideoCapture(0)

# Initialiser quelques variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True # Pour ne traiter qu'une trame sur deux et économiser les ressources

# --- 3. Boucle principale pour le traitement vidéo en temps réel ---

while True:
    # Capturer une seule trame vidéo
    ret, frame = video_capture.read()
    if not ret:
        print("Erreur : Impossible de capturer la vidéo de la webcam.")
        break

    # Ne traiter qu'une trame sur deux pour gagner du temps
    if process_this_frame:
        # Redimensionner la trame à 1/4 de sa taille pour un traitement plus rapide
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Convertir l'image de la couleur BGR (utilisée par OpenCV) à RGB (utilisée par face_recognition)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Trouver tous les visages et leurs encodages dans la trame actuelle
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # Comparer le visage détecté avec les visages connus
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            name = "Inconnu" # Nom par défaut si aucune correspondance n'est trouvée

            # Utiliser le visage connu avec la plus petite distance par rapport au nouveau visage
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

    # --- 4. Affichage des résultats ---

    # Afficher les résultats sur la trame vidéo
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Redimensionner les coordonnées du visage car la trame a été redimensionnée à 1/4
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Définir la couleur du cadre en fonction de l'identification
        box_color = (0, 0, 255) if name == "Inconnu" else (0, 255, 0)

        # Dessiner un rectangle autour du visage
        cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)

        # Dessiner une étiquette avec le nom sous le visage
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Afficher l'image résultante
    cv2.imshow('Video', frame)

    # Appuyer sur 'q' sur le clavier pour quitter
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 5. Libération des ressources ---

# Libérer le handle de la webcam
video_capture.release()
cv2.destroyAllWindows()