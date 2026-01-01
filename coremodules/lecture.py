# fichier qui effectue la lecture des fichiers '.csv' de tests et les fichiers '.txt' des valeurs de TIE

import csv
import os
import numpy as np
import time as sys_time
from scipy import stats as sts
import pandas as pd

''' Module utilisé pour la lecture des fichiers csv '''

def lecture_csv(chemin_dossier, fichier_sortie, ref, msr, debug=False) :

    if debug :
        print(f"ref = {ref}, msr = {msr}")

    resultats = [] # Liste de delays de flanc montant entre ref et msr
    resultats_temps = [] # Liste de temps d'execution pour chaque fichier csv
    contents = os.listdir(chemin_dossier) # Création d'une liste contenant chaque fichier dans le dossier
    
    csv_files = [f for f in contents if f.endswith(".csv")] # List comprehension: creates a sub-list of csv files based on the content of the folder

    if not csv_files: #Checks whether list is empty (= no csv files), returns a True as last value if it is the case.
        return -1, np.array([]), -1, -1, -1, -1, True
    else:
        nr_fichiers = len(csv_files)

        '''Iteration des fichiers csv dans le dossier'''
        last_col = 0
        for file_name in contents:
            file_name = str(file_name)

            if file_name.endswith(".csv"): # Parsing que des fichiers .csv 
                start_time = sys_time.time() # Pour calculer le temps d'execution d'un fichier .csv
                chemin_fichier = os.path.join(chemin_dossier,file_name)
                with open(chemin_fichier, newline='') as f:
                    lecteur = csv.reader(f, delimiter=",") # !!! Les .csv doivent être sauvegardé avec virgule comme séparateur
                    en_tetes = next(lecteur) # variables tampon

                    if last_col == 0: # une fois last_col a été défini, pas besoin de le recalculer pour les autres csv
                        last_col = len(en_tetes) - 1 # index de la dernière colonne (timestamp)

                    lignes = list(lecteur) #liste bidimensionnelle de chaque ligne excel

                    i = 1
                    afterSync = False # Variable pour savoir si on est sur un flanc montant ou pas
                    while i < len(lignes):
                        colref = int(lignes[i][ref]) 
                        prev_colref = int(lignes[i - 1][ref])

                        # Détection du flanc montant dans colonne ref : 0 ➝ 1
                        if prev_colref == 0 and colref == 1:
                            afterSync = True
                            if " s" in lignes[i][last_col] :
                                t_base = float(lignes[i][last_col].replace(" s", ""))*1e9
                            elif " ms" in lignes[i][last_col] :
                                t_base = float(lignes[i][last_col].replace(" ms", ""))*1e6
                            elif " us" in lignes[i][last_col] :
                                t_base = float(lignes[i][last_col].replace(" us", ""))*1e3
                            elif " ns" in lignes[i][last_col] :
                                t_base = float(lignes[i][last_col].replace(" ns", ""))
                            colmsr_val = int(lignes[i][msr])
                            if debug:
                                print(f"\n Flanc montant colonne {ref} à la ligne {i}, t_base = {t_base} ns")

                            if colmsr_val == 0:
                                # Descente dans colonne msr jusqu'à trouver 1
                                j = i + 1
                                while j < len(lignes):
                                    if int(lignes[j][msr]) == 1:
                                        if " s" in lignes[j][last_col] :
                                            t_cible = float(lignes[j][last_col].replace(" s", ""))*1e9
                                        elif " ms" in lignes[j][last_col] :
                                            t_cible = float(lignes[j][last_col].replace(" ms", ""))*1e6
                                        elif " us" in lignes[j][last_col] :
                                            t_cible = float(lignes[j][last_col].replace(" us", ""))*1e3
                                        elif " ns" in lignes[j][last_col] :
                                            t_cible = float(lignes[j][last_col].replace(" ns", ""))
                                        decalage = float(t_cible - t_base)
                                        resultats.append(decalage)
                                        if debug:
                                            print(f"↓ Trouvé 1 dans colonne {msr} à ligne {j}, t_cible = {t_cible} ns → Δt = {decalage} ns")
                                        break
                                    j += 1

                            else:
                                # Remontée dans colonne msr jusqu'à trouver 0
                                j = i - 1
                                while j > 0:
                                    if int(lignes[j][msr]) == 0:
                                        if " s" in lignes[j+1][last_col] :
                                            t_cible = float(lignes[j+1][last_col].replace(" s", ""))*1e9
                                        elif " ms" in lignes[j+1][last_col] :
                                            t_cible = float(lignes[j+1][last_col].replace(" ms", ""))*1e6
                                        elif " us" in lignes[j+1][last_col] :
                                            t_cible = float(lignes[j+1][last_col].replace(" us", ""))*1e3
                                        elif " ns" in lignes[j+1][last_col] :
                                            t_cible = float(lignes[j+1][last_col].replace(" ns", ""))
                                        decalage = float(t_cible - t_base)
                                        resultats.append(decalage)
                                        if debug:
                                            print(f"↑ Trouvé 0 dans colonne {msr} à ligne {j}, t_cible = {t_cible} ns → Δt = {decalage} ns")
                                        break
                                    j -= 1        
                        # If we pass a rising edge, skip to right before the next rising edge considering a ≈ 2% error (i.e. 116μs - 2μs later). Then, continue parsing cell-by-cell until the next rising edge.     
                        if not afterSync: 
                            i += 1
                        else:
                            i += 114000 
                            afterSync = False

                end_time = sys_time.time()
                exec_time = end_time - start_time
                resultats_temps.append(exec_time) # Store the execution time of each csv in resultats_temps
            
    ''' Création du fichier de sortie '''

    if last_col != 2 :
        fichier_sortie_mdf = fichier_sortie.replace(f"{last_col}", f"{last_col}_{ref}_{msr}.txt")
        dossier_sortie = fichier_sortie.replace(".txt", "")
        dossier_sortie = dossier_sortie.replace("TIE", "ACC")
        chemin_complet = os.path.join(f"{chemin_dossier}", str(fichier_sortie_mdf))

    else : 
        fichier_sortie_mdf = f"{fichier_sortie}.txt"
        chemin_complet = os.path.join(f"{chemin_dossier}", str(fichier_sortie_mdf))

    with open(chemin_complet, "w") as f:
        for delta in resultats:
            f.write(str(delta))
            f.write("\n")

    ''' Création du fichier de temps d'execution (regarder la prochaine fonction dans ce module et le fichier README si interressé) '''

    fichier_temps_execution = "temps_dex.txt"
    chemin_complet_temps = os.path.join(f"{chemin_dossier}", str(fichier_temps_execution))

    with open(chemin_complet_temps, "w") as f:
        total_execution_time = sum(resultats_temps)
        for time in resultats_temps:
            f.write(str(time))
            f.write("\n")
        f.write("\n")
        f.write(f"{total_execution_time} \n")  # The total time

    if debug :
        print("\n Résultats des décalages temporels:")
        for idx, delta in enumerate(resultats):
            print(f"{idx+1}. Δt = {delta} us")
    
    TIE, min_j, max_j, mean_j, std_j = lecture_txt_sortie(chemin_complet)

    return nr_fichiers, TIE, min_j, max_j, mean_j, std_j, False # Returns False for the "noCsv" 
    
    

def lecture_txt_sortie(chemin_fichier_sortie):

    '''Lecture et Analyse du fichier de sortie'''
    
    with open(chemin_fichier_sortie) as f:
        lecteur = csv.reader(f)
        data = list(lecteur)
        data_floats = [float(val[0]) for val in data]
    
    TIE = np.array(data_floats) # pour avoir le TIE en [ns]
    max_j = np.max(TIE)
    min_j = np.min(TIE)
    std_j = np.std(TIE)
    mean_j = np.mean(TIE)
    # period = 116e-6    # temps en [s] entre chaque flanc montant du SYNC0 de la reférence.
    # period_sync0 = 1e-6 # periode en [s] du signal SYNC0
    # time_offset = 0
     
    #return period, period_sync0, time_offset, TIE #period |b| to sync0, duration of sync0=1, time of the first sync0, Time Interval Error |b| slave_1 and slave_x
    return TIE, min_j, max_j, mean_j, std_j





def lecture_txt_temps(fichier1, fichier2, chemin_default, alpha, fichier_d):

    '''  LECTURE DES FICHIERS DE TEMPS D'EXECUTION: ANALYSE QUANTITATIVE DE LA PERFORMANCE. '''

    # CHANGER LES CHEMINS CI DESSOUS AU CHEMINS DE VOS DEUX FICHIERS "TEMPS D'EXECUTION" à COMPARER

    chemin_complet1 = os.path.join(f"{chemin_default}", "Data", "test_csv", "ACC_1_2",f"{fichier1}.txt")
    chemin_complet2 = os.path.join(f"{chemin_default}", "Data", "test_csv", "ACC_1_2",f"{fichier2}.txt")
    
    data_floats1 = []
    data_floats2 = []

    with open(chemin_complet1) as f:
        lecteur = csv.reader(f)
        data1 = list(lecteur)
        data_floats1 = np.array([float(val[0]) for val in data1[:-2]]) # Pour négliger les derniers deux éléments qui corréspondent à une ligne vide et au temps total d'execution

    with open(chemin_complet2) as f:
        lecteur = csv.reader(f)
        data2 = list(lecteur)
        data_floats2 = np.array([float(val[0]) for val in data2[:-2]])
    
    data_final = data_floats2 - data_floats1 # Nouvelle liste contenant la différence des valeurs des deux échantillons.

    #Nouveau fichier contenant la liste ci-dessus. EGALEMENT, CHANGER LE CHEMIN

    nouveau_chemin =  os.path.join(f"{chemin_default}", "Data", "test_csv", "ACC_1_2", f"{fichier_d}.txt")

    with open(nouveau_chemin,"w") as f:
        for time in data_final:
            f.write(str(time))
            f.write("\n")

    # Tests statistiques
    # Pour plus d'info sur le test d'hypothèse et les intervalles de confiance : https://www.youtube.com/watch?v=JiQR0lHLe74 

    x_bar_d = np.average(data_final) 
    s_d = np.std(data_final) 
    n = data_final.size 
    D0 = 0  # Hypothèse Nulle: Il n'y a pas de différence entre les deux temps d'executions.

    test_t = (x_bar_d - D0)/(s_d/np.sqrt(n)) # Notre test t 
    t_distr = sts.t(n-1) # distribution t 
    t_critical = t_distr.ppf(1-alpha/2) # valeur t de reference (pour determiner si l'hypothèse nulle est correcte ou pas)

    std_e = t_critical*(s_d/np.sqrt(n)) #Standard error de l'intervalle de confiance
    conf_intrvl = [x_bar_d - std_e, x_bar_d + std_e]

    # Conclusions

    print("\n" + "*" * 50)
    print("                PERFORMANCE ANALYSIS              ")
    print("*" * 50 + "\n")

    fichier = ""
    fichier_not = ""
    if x_bar_d > 0:
        fichier = fichier2
        fichier_not = fichier1
    else:
        fichier = fichier1
        fichier_not = fichier2
        x_bar_d = np.abs(x_bar_d)
    
    print(f"Moyenne de temps d'execution pour le parsing des {data_final.size} fichiers csv dans '{fichier}.txt' est {x_bar_d*data_final.size} fois long que '{fichier_not}.txt' \n")

    print(f"L'Écart type des différences d'executions (en s) : {s_d} \n")

    print(f"Intervalle de confiance (à {(1-alpha)*100}%): [{conf_intrvl[0]:.8f}, {conf_intrvl[1]:.8f}]\n")

    print(f"t critical : {t_critical}"+ "\n")

    print(f"t test : {test_t}"+ "\n")

    isMoreEfficient = test_t > t_critical

    print(f"La méthode utilisée dans le fichier '{fichier1}.txt' peut être considerée plus efficace : {isMoreEfficient} \n") 

    if not isMoreEfficient:
        print(f" Si vous avez confiance dans votre méthode, vous pouvez soit utiliser des échantillons de plus grand taille (plus de fichiers csv), ou sinon baisser le niveau de confiance (à moins de 85%)" + "\n")

    else:
        print("Congratulations !!!")


# Note: Si le test t n'est pas plus large de la valuer t critical, alors l'Hypothèse Nulle (càd pas de différence de performance) ne peut pas être refusée
    
    


    