
from archivemodules import creation_data, histogram, spectrogram
from coremodules import diagram, lecture
import matplotlib.pyplot as plt
import numpy as np
import os
import time

chemin_default = os.path.dirname(__file__)
print(chemin_default)


''' FONCTIONS À UTILISER À LA CONSOLE À LA PLACE DE L'INTERFACE OU POUR PERFORMER UNE COMPARAISON DE TEMPS D'EXECUTION '''


### Création théorique ###
def theoritical_creation(save) :
    size = 300
    percentage_deterministic = 0.5

    parameters = {
        "period" : 116e-6, #[s]
        "period_sync0" : 1e-6, #[s]
        "time_offset" : 60e-6, #[s]
        "sigma" : (1-percentage_deterministic)*70*0.8*100e-9/3, #[s] corresponds to 0.8 * the delta of 100ns imposed by Alstom divided by 3
        "mu" : 1*15e-9, # [s]
        "frequency" : [500/size, 210/size, 120/size, 240/size], #[Hz] to have nbr cycle of jitter for the full Jitter
        "offset" : 40, #the first sample of TIE where jitter is nul
        "amplitude" : [percentage_deterministic*0.8*100e-9, 0*100e-9, 0*100e-9, 0*100e-9],
    }

    period, period_sync0, time_offset, TIE = creation_data.creation_data(size, parameters)

### Lecture du fichier TIE.txt ###
def txt_lecture(folder, name, fichier_sortie) :
    chemin_fichier = os.path.join(f"{chemin_default}", "Data", str(folder), str(name), fichier_sortie)
    nr_fichiers, min_j, max_j, mean_j, std_j = lecture.lecture_txt_sortie(chemin_fichier)
    print("success")



### Lecture du fichier TIE.txt progressivement ###
def txt_lecture_progressiv(folder, name, fichier_sortie) :
    period, period_sync0, time_offset, TIE = lecture.lecture_txt_sortie(folder, name, fichier_sortie, chemin_default)
    print(len(TIE))


''' ENTRÉS DE L'UTILISATEUR '''


compt = 0
while True :
    choice = input("Choix du mode :\n0 : Création théorique et affichage des résultats\n1 : Lecture d'un fichier '.csv' (signal sync0)\n2 : Lecture d'un fichier '.txt' (valeurs de TIE) et affichage des résultats\n3 : Lecture progressive d'un fichier '.txt'\n4 : Comparaison du temps d'execution \n5 : quitter\n")

    if choice == '0':
        save = input("1: Pour sauvegarder, 0: Dans le cas contraire\n")
        if save == '1' :
            theoritical_creation(True)
        elif save == '0' :
            theoritical_creation(False)
        else :
            print("Opération invalide")
        break

    elif choice == '1':
        folder = input("Nom du dossier parent : ")
        name = input("Nom du dossier avec les fichiers '.csv' : ")
        nbr_slv_msr = int(input("nombre de slaves enregistrés : "))
        ref = int(input("numéro du slave de référence : "))
        msr = int(input("numéro du slave de mesure : "))
        fichier_sortie = input("Nom du fichier de sortie '.txt' : ")

        # On appel la fonction qu'on veut et on trace le temps qu'il a pris pour l'executer en une ligne
        chemin_dossier = os.path.join(f"{chemin_default}", "Data", str(folder), str(name))

        lecture.lecture_csv(chemin_dossier, fichier_sortie, ref, msr, nbr_slv_msr)
        break

        # La lecture d'1 fichier csv(avec 1000 sync0) prend en moyenne 4min 
        # si ficchier csv avec plus de 2 slaves de mesurés changer nbr_slv_msr et surtout ref et msr pour chaque cas
        # Mais aussi changer fichier_sortie lors de la lecture des fichiers TIE.txt ainsi que le nom des figures pour ne pas les écraser à chaque exécution

    elif choice == '2':
        folder = input("Nom du dossier parent : ")
        name = input("Nom du dossier où se trouve le fichier '.txt' : ")
        fichier_sortie = input("Nom du fichier '.txt' : ")
        txt_lecture(folder, name, fichier_sortie)
        break

    elif choice == '3':
        folder = input("Nom du dossier parent : ")
        name = input("Nom du dossier où se trouve le fichier '.txt' : ")
        fichier_sortie = input("Nom du fichier '.txt' : ")
        txt_lecture_progressiv(folder, name, fichier_sortie)
        break

    elif choice == '4':
        fichier1 = input("Nom du premier fichier (celui qui devrait avoir des temps d'exécution plus bas) sans '.txt' : ")
        fichier2 = input("Nom du deuxième fichier sans '.txt': ")
        conf_intrvl = input("Rentrez un niveau de confiance (recommendé: entre 85 et 90%) : ")
        fichier_d = input("Nom du fichier final : ")

        alpha = 1 - (int(conf_intrvl)/100)
        lecture.lecture_txt_temps(fichier1, fichier2, chemin_default, alpha, fichier_d)
        break

    elif choice == '5':
        print("Au revoir !")
        break
    
    else :
        print("Opération invalide")
        break




### Calul covariance entre 2 fichiers TIE.txt ###

# folder = "ACC"
# name = "ACC_ALL_6"
# fichier_sortie_a = f"TIE_ALL_6_4_5"
# fichier_sortie_b = f"TIE_ALL_6_5_6"
# period, period_sync0, time_offset, TIE_a = lecture_csv.lecture(folder, name, fichier_sortie_a, chemin_default)
# period, period_sync0, time_offset, TIE_b = lecture_csv.lecture(folder, name, fichier_sortie_b, chemin_default)

# # Vérification que les vecteurs ont la même taille
# if TIE_a.shape != TIE_b.shape:
#     raise ValueError("Les vecteurs TIE_a et TIE_b doivent avoir la même taille pour calculer la covariance.")

# # Calcul de la covariance
# covariance_matrix = np.cov(TIE_a, TIE_b)

# print(f"Matrice de covariance entre TIE_a et TIE_b : {covariance_matrix}")