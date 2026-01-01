from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialog, QFileDialog, QApplication
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QFontMetrics
from PyQt6.uic import load_ui
from .diagram import density
from .lecture import lecture_csv
import numpy as np

'''Cette classe va s'occuper de lancer la fonction de lecture_csv dans un background thread.
Elle enverra également des signaux à la thread principale pour communiquer un échec ou un succés '''

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(int, np.ndarray, float, float, float, float, bool)  # Signal de succés
    error = QtCore.pyqtSignal(str)   # Signal d'erreur
    create_oscilloplot = QtCore.pyqtSignal(np.ndarray, int, int, np.ndarray)  # Signal to update TIE plot

    def __init__(self, chemin_csv, nom_sortie, ref_user, msr_user):
        super().__init__()
        self.chemin_csv = chemin_csv
        self.nom_sortie = nom_sortie
        self.ref_user = ref_user
        self.msr_user = msr_user
        
    def run(self):
        try:
            nr_fichiers, TIE, min_jitter, max_jitter, mean_jitter, std_jitter, noCsv = lecture_csv(self.chemin_csv, self.nom_sortie, self.ref_user, self.msr_user)
            if not noCsv : #Verification that there are CSV files
                density_TIE = density(TIE, mean_jitter,std_jitter)
                self.create_oscilloplot.emit(TIE, mean_jitter, std_jitter, density_TIE)
            self.finished.emit(nr_fichiers, TIE, min_jitter, max_jitter, mean_jitter, std_jitter, noCsv)  # Emit finished signal when reading is done
        except Exception as e:
            self.error.emit(str(e))  # Emit error signal if something goes wrong