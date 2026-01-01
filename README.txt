
    # Created on February 2025
    # @author: Denis Albrecq & Margot Durou
    # @editor: Martin Pedata
    # Contact: albrecq.d@gmail.com | martin.pedata@gmail.com
    # Last update: 29-08-25

****** ENGLISH ******

Tool to analyze jitter between 2 slaves based on their TIE vector

WHAT TO DO:

        - "interface.py" is the entry point of the program. Run it to open the graphical interface that allows you to analyze CSV files.
        - To install all required packages:
                    $ pip install -r /path/to/requirements.txt

		- If facing issues despite having both python and pip, it may be a PATH problem. Run the following:
		   			$ python -m pip install -r /path/to/requirements.txt

----> Follow the file "UI - user guide", starting page 4, to navigate the app. ONLY IN FRENCH

Brief explanation in English: 

1) Click the button next to the .csv bar on top of the page, drop the folder "testing" (found in "Data" -> "testing_csv") containing dummy csv files. 
2) Now, first, choose the reference slave by clicking one of the numbers in the grid, then choose the measured slave. For this implementation containing dummy csv files, only numbers 1 and 2 are valid. 
3) Then click parse. 
4) You can open the rising edges visualization (along with jitter measurement) by clicking "ouvrir image". 
You can also open a text file containing the average delay time (leading or lagging) of the measured slave with respect to the reference for each CSV file by clicking "ouvrir fichier".


PYTHON NOTES:

        - "coremodules" contains the modules used by the interface.

        - "archivemodules" contains the modules that allow you to perform more advanced analyses
          (same analyses as the interface + creation of a spectrogram, a histogram, theoretical data generation,
          execution time comparison, ...).
          The entry point for these analyses is not "interface.py" but "main.py".

        - "utilmodules" contains the modules defining helper functions (empty for now).


NOTES ON TIME OPTIMIZATION:

        - The function "lecture_txt_temps" in the "lecture" module is used to *quantitatively* analyze the execution
          time difference between two parsing methods.
          It computes a confidence interval and performs a hypothesis test assuming paired samples
          (the two samples are the files "temps1" and "temps2").
          Use a t-test for sample sizes smaller than 30, and a z-test otherwise.
          Refer to the SciPy statistics documentation to understand how to handle this in Python
          (especially the functions "t()" and "norm()"):
          https://docs.scipy.org/doc/scipy/reference/stats.html

        Execution time analysis step-by-step:

        - First, run the first round of CSV parsing (using method 1). You will find a file named "temps_dex.txt"
          in the directory where the CSV files are located.
          Rename this file before running the second round of parsing (method 2).

        - You can now proceed to the execution time analysis. You should have 2 execution time files for this step.
          Copy their paths and modify the code in "lecture_txt_temps" so that the variables
          "chemin_complet1", "chemin_complet2", and "nouveau_chemin" are correct.

            To run the function, select option 4 once "main.py" has been launched.

        - For more information on hypothesis testing and confidence intervals:
          https://www.youtube.com/watch?v=JiQR0lHLe74


****** FRENCH ******

Outil pour analyser le jitter entre 2 esclaves à partir de son vecteur TIE


QUE FAIRE :

        - "interface.py" est le point d’entrée du programme. Lancez-le pour ouvrir l’interface graphique qui vous permettra d’analyser les fichiers CSV.
        - Pour installer tous les packages requis :
                    $ pip install -r /path/to/requirements.txt

		- En cas de problèmes malgré la présence de Python et de pip, il peut s’agir d’un problème de PATH. Exécutez la commande suivante :
		   			$ python -m pip install -r /path/to/requirements.txt

----> Suivez le fichier "UI - user guide", à partir de la page 4, pour naviguer dans l’application. UNIQUEMENT EN FRANÇAIS

NOTES PYTHON :

        - "coremodules" contient les modules utilisés par l’interface.

        - "archivemodules" contient les modules qui permettent d’effectuer des analyses plus avancées
          (mêmes analyses que l’interface + création d’un spectrogramme, d’un histogramme,
          génération théorique de données, comparaison des temps d’exécution, ...).
          Le point d’entrée pour ces analyses n’est pas "interface.py" mais "main.py".

        - "utilmodules" contient les modules définissant les fonctions utilitaires (vide pour le moment).



    NOTE SUR L'OPTIMIZATION DES TEMPS:

        - La fonction "lecture_txt_temps" dans le module "lecture" sert pour analyser *quantitativement* la différence de temps d'execution entre deux méthodes de parsing.
        Elle calcul un intervalle de confiance et fait un test d'hypothèse en considérant des échantillons appariés (les deux échantillons sont les fichiers "temps1" et "temps2").
        Utiliser un Test t pour des tailles d'échantillions inférieure à 30, et un Test z sinon. 
        Regarder la documentation stats de scipy pour savoir jongler avec cela sur python ( spécialement les fonctions "t()" et "norm()" ): https://docs.scipy.org/doc/scipy/reference/stats.html

        Analyse des temps Step-by-Step:

        - Lancez d'abord le premier round de parsing des csv (utilisant la méthode 1). Vous allez retrouver un fichier temps_dex.txt dans le chemin où se trouvent les csv; 
        Changer son nom avant de lancer le deuxième round de parsing (méthode 2)

        - Maintenant vous pouvez passer à l'analyse des temps d'execution. Vous devriez avoir 2 fichiers temps d'ex pour cette étape. Copiez les chemins et
        modifiez le code dans "lecture_txt_temps" afin que les variables "chemin_complet1", "chemin_complet2", et "nouveau_chemin" soient correctes.

            Pour lancer la fonction, choisir l'option 4 une fois "main.py" a été lancé.


        - Pour plus d'info sur les Tests d'Hypothèse et Intervalles de Confiance : https://www.youtube.com/watch?v=JiQR0lHLe74
