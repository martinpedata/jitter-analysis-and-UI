
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QDialog, QFileDialog, QApplication, QMessageBox, QVBoxLayout,QHBoxLayout, QSizePolicy
from PyQt6.QtGui import QFontMetrics
from PyQt6.uic import load_ui
from coremodules import diagram, lecture
from coremodules.worker import Worker
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import scipy.signal as sc

chemin_csv = "" # variable globale pour determiner le chemin du dossier des fichiers csv. à changer quand button_csv est cliqué.
min_jitter = -1 # Données à illustrer sur l'interface. 
max_jitter = -1
std_jitter = -1
nr_fichiers = -1
mean_jitter = -1
noCsv = None
elc_clicked = 0
TIE = np.array([])
class Ui_widget(QtWidgets.QWidget):
    
    def setupUi(self, widget):
        widget.setObjectName("CSV scanner for jitter measurement")
        widget.resize(750, 630)
        widget.setMinimumSize(530, 570)
        
        main_layout = QVBoxLayout() # main layout of the interface, it will contain only one component (widget_layout)

        widget_layout = QVBoxLayout() # Layout containing all components of the interface

        '''CSV SECTION'''

        csv_layout = QHBoxLayout()

        self.frame_csv = QtWidgets.QFrame(parent=widget)
        self.frame_csv.setAutoFillBackground(False)
        self.frame_csv.setStyleSheet("background-color: rgb(244, 245, 181); border: 0.7px solid rgb(224, 225, 161); border-radius: 10px")
        self.frame_csv.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_csv.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_csv.setObjectName("frame_csv")
        self.frame_csv.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame_layout = QVBoxLayout(self.frame_csv)
        
        self.label_csv = QtWidgets.QLabel(parent=self.frame_csv)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setPointSize(12)
        self.label_csv.setFont(font)
        self.label_csv.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_csv.setObjectName("label_csv")
        self.label_csv.setStyleSheet("color: rgb(172, 168, 159);")
        self.label_csv.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_csv.setContentsMargins(10, 0, 0, 0)  # left, top, right, bottom
        self.label_csv.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame_layout.setContentsMargins(0, 0, 0, 0) 
        frame_layout.addWidget(self.label_csv)

        self.button_csv = QtWidgets.QPushButton(parent=widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.button_csv.setFont(font)
        self.button_csv.setStyleSheet("background-color: rgb(255, 255, 202); color: rgb(0, 0, 0);")
        self.button_csv.setText("📃")
        self.button_csv.setObjectName("button_csv")
        self.button_csv.setFixedSize(50,40)  # Fixed width
        self.button_csv.clicked.connect(self.on_button_csv_click)
        csv_layout.addWidget(self.frame_csv, stretch=4) # Add components to the csv_layout
        csv_layout.addWidget(self.button_csv, stretch=1)
        csv_layout.setContentsMargins(30, 0, 30, 0)  # left, top, right, bottom
        csv_layout.addSpacing(10)

        widget_layout.addLayout(csv_layout,4) # Add csv layout to the main layout
        widget_layout.addSpacing(10)

        '''DIAGRAM OF MA/ELC '''

        layout_diagram = QVBoxLayout()

        self.frame_diagram = QtWidgets.QFrame(parent=widget)
        self.frame_diagram.setStyleSheet("background-color: rgb(255, 255, 255); border: 0.5px solid gray; border-radius: 10px")
        self.frame_diagram.setMinimumHeight(180) 
        self.frame_diagram.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_diagram.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_diagram.setObjectName("frame_diagram")
        self.frame_diagram.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Buttons list to store the specific buttons
        self.button_list = {}
        # Parent horizontal layout
        horizontal_layout = QtWidgets.QHBoxLayout(self.frame_diagram)
        # Left vertical layout
        left_layout = QtWidgets.QVBoxLayout()

        label_ma = QtWidgets.QLabel("MASTER", self.frame_diagram)
        label_ma.setStyleSheet("border: 1px solid gray; color: black;")
        label_ma.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label_ma.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        tiny_button = QtWidgets.QPushButton("MA", self.frame_diagram)
        tiny_button.setFixedSize(27, 18) 
        tiny_button.setStyleSheet("color: black;")
        tiny_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        left_layout.addWidget(label_ma, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        left_layout.addWidget(tiny_button,alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch(1)

        horizontal_layout.addLayout(left_layout,1)

        # Right vertical layout
        right_layout = QtWidgets.QVBoxLayout()

        label_elc = QtWidgets.QLabel("SLAVES", self.frame_diagram)
        label_elc.setStyleSheet("border: 1px solid gray; color: black;")
        label_elc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label_elc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        right_layout.addWidget(label_elc)

        grid_layout = QtWidgets.QGridLayout()
        font.setPointSize(10)

        # Create an 8x4 matrix of push buttons within the grid layout
        for row in range(4):
            for column in range(8):
                index = row * 8 + column + 1
                button = QtWidgets.QPushButton(str(index), self.frame_diagram)
                button.setStyleSheet("background-color: white; color: black;")
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                button.setFont(font)
                grid_layout.addWidget(button, row, column)
                self.button_list[index-1] = button  # populate buttons list
        
        right_layout.addLayout(grid_layout)

        button_clear = QtWidgets.QPushButton("Effacer", self.frame_diagram)
        button_clear.setFixedSize(40, 18)
        font.setItalic(True)
        button_clear.setFont(font)
        button_clear.setStyleSheet("color: white; background-color: rgb(150, 0, 0)")  # Adjust the value as needed
        button_clear.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        right_layout.addSpacing(8)
        right_layout.addWidget(button_clear, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        right_layout.addSpacing(10)

        horizontal_layout.addLayout(right_layout,1)

        # Connect all 32 buttons + delete button to on_click functions
        for i in range(len(self.button_list)):
            button = self.button_list.get(i)
            button.clicked.connect(lambda checked, num=i: self.on_elc_clicked(num))

        button_clear.clicked.connect(self.on_clear_elc_button) #clear button connect

        layout_diagram.addWidget(self.frame_diagram) #Add the entire frame to the layout_diagram
        layout_diagram.setContentsMargins(10, 0, 20, 0) 


        widget_layout.addLayout(layout_diagram) # Add to main layout
        widget_layout.addSpacing(20)



        '''LINE EDITS + PARSE'''

        parsing_info_layout = QHBoxLayout() # Parsing info section --> element of widget_layout

        user_input_layout = QHBoxLayout() # User input section (inside parsing info)

        ref_layout = QHBoxLayout() #Ref section (inside user input)

        self.lineEdit_ref = QtWidgets.QLineEdit()
        self.lineEdit_ref.setObjectName("lineEdit_ref")
        self.lineEdit_ref.setDisabled(True)
        self.lineEdit_ref.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.label_textRef = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(11)
        self.label_textRef.setFont(font)
        self.label_textRef.setObjectName("label_textRef")
        self.label_textRef.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        ref_layout.addWidget(self.lineEdit_ref)
        ref_layout.addWidget(self.label_textRef)

        msr_layout = QHBoxLayout() #msr section

        self.lineEdit_msr = QtWidgets.QLineEdit()
        self.lineEdit_msr.setObjectName("lineEdit_msr")
        self.lineEdit_msr.setDisabled(True)
        self.lineEdit_msr.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.label_textMsr = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(11)
        self.label_textMsr.setFont(font)
        self.label_textMsr.setObjectName("label_textMsr")
        self.label_textMsr.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        msr_layout.addWidget(self.lineEdit_msr)
        msr_layout.addWidget(self.label_textMsr)

        user_input_layout.addLayout(ref_layout)
        user_input_layout.addLayout(msr_layout)
        user_input_layout.setContentsMargins(30,0,20,0)

        self.parseButton = QtWidgets.QPushButton()
        font = QtGui.QFont()
        font.setFamily("Calibri") 
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.parseButton.setFont(font)
        self.parseButton.setStyleSheet("background-color: rgb(0, 0, 0); color: rgb(255, 255, 202);")
        self.parseButton.setObjectName("parseButton")
        self.parseButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.parseButton.clicked.connect(self.on_parse_button_click)

        parsing_info_layout.addLayout(user_input_layout)
        parsing_info_layout.addWidget(self.parseButton)
        parsing_info_layout.setContentsMargins(0, 0, 20, 0) 


        widget_layout.addLayout(parsing_info_layout)

        main_layout.addLayout(widget_layout)

        widget.setLayout(main_layout)
        widget_layout.addSpacing(20)


        ''' OUTPUT FRAMES '''

        output_frames_layout = QHBoxLayout()

        self.frame_graph = QtWidgets.QFrame()
        self.frame_graph.setStyleSheet("background-color: rgb(255, 255, 255); border: 0.5px solid gray; border-radius: 10px")
        self.frame_graph.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_graph.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_graph.setObjectName("frame_graph")
        self.frame_graph.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.layout_graph = QtWidgets.QVBoxLayout(self.frame_graph) #Layout to store label and canvas
        # Initialize figure and canvas
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout_graph.addWidget(self.canvas)

        self.frame_data = QtWidgets.QFrame() 
        self.frame_data.setStyleSheet("background-color: rgb(255, 255, 255); border: 0.5px solid gray; border-radius: 10px")
        self.frame_data.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_data.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_data.setObjectName("frame_data")
        self.frame_data.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame_data_layout = QVBoxLayout()

        self.label_data = QtWidgets.QLabel(parent=self.frame_data)  
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.label_data.setStyleSheet("padding: 10px; color: rgb(132, 128, 119); border: 0.5px white")  # !! Tous les changements à la styleSheet doivent être sur la même ligne de code.
        self.label_data.setFont(font)
        self.label_data.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)  # Align text if needed.
        self.label_data.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame_data_layout.setContentsMargins(5, 5, 0, 0) 
        frame_data_layout.addWidget(self.label_data)
        
        self.frame_data.setLayout(frame_data_layout)

        output_frames_layout.addWidget(self.frame_graph,1)
        output_frames_layout.addWidget(self.frame_data,1)
        output_frames_layout.addSpacing(20)
        output_frames_layout.setContentsMargins(10, 0, 0, 0) 


        widget_layout.addLayout(output_frames_layout)
        widget_layout.addSpacing(10)
    

        ''' OUTPUT BUTTONS '''

        output_buttons_layout = QHBoxLayout()

        self.button_image = QtWidgets.QPushButton(parent=widget)
        self.button_image.clicked.connect(self.on_button_image_click)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(400)
        self.button_image.setFont(font)
        self.button_image.setStyleSheet("background-color: rgb(255, 255, 202); color: rgb(0, 0, 0); padding: 5px;")
        self.button_image.setText("Ouvrir l'image")
        self.button_image.adjustSize()
        self.button_image.setObjectName("button_image")
        self.button_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.button_sortie = QtWidgets.QPushButton(parent=widget)
        self.button_sortie.clicked.connect(self.on_button_sortie_click)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(400)
        self.button_sortie.setFont(font)
        self.button_sortie.setStyleSheet("background-color: rgb(255, 255, 202); color: rgb(0, 0, 0); padding: 5px;")
        self.button_sortie.setText("Ouvrir le fichier de sortie")
        self.button_sortie.adjustSize()
        self.button_sortie.setObjectName("button_sortie")
        self.button_sortie.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        output_buttons_layout.addWidget(self.button_image)
        output_buttons_layout.addWidget(self.button_sortie)
        output_buttons_layout.addSpacing(20)
        output_buttons_layout.setContentsMargins(10, 0, 0, 0) 


        widget_layout.addLayout(output_buttons_layout)
        widget_layout.addSpacing(20)

        ''' BOUTON RESET '''

        self.button_reset = QtWidgets.QPushButton(parent=widget)
        self.button_reset.clicked.connect(self.on_button_clear_all_click)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(700)
        self.button_reset.setFont(font)
        self.button_reset.setStyleSheet("background-color: rgb(255, 0, 0); color: white; padding: 7px;")
        self.button_reset.setText("Effacer Tout")
        self.button_reset.adjustSize()
        self.button_reset.setObjectName("button_clearAll")
        self.button_reset.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        widget_layout.addWidget(self.button_reset, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.retranslateUi(widget)
        QtCore.QMetaObject.connectSlotsByName(widget)

    def retranslateUi(self, widget):
        _translate = QtCore.QCoreApplication.translate
        widget.setWindowTitle(_translate("widget", "Form"))
        self.parseButton.setText(_translate("widget", "Parse"))
        self.label_csv.setText(_translate("widget", "Dossier contenant les .csv "))
        self.label_textRef.setText(_translate("widget", "Nr de REF"))
        self.label_textMsr.setText(_translate("widget", "Nr de MSR"))


    '''BUTTON_CLICK FUNCTIONS AND HELPER FUNCTIONS'''

    def set_truncated_label(self, text):
        '''Helper function: shortening the folder name in case it is too large to fit in the frame'''

        label_width = self.label_csv.width() - 10 
        # Use QFontMetrics to calculate the width of the text
        metrics = QFontMetrics(self.label_csv.font())
        text_width = metrics.horizontalAdvance(text)
        truncated_text = text

        
        if text_width > label_width:
            # Calculate maximum width for the text leaving space for '...'
            max_width = label_width - metrics.horizontalAdvance("...") - 10
            while metrics.horizontalAdvance(truncated_text) > max_width and len(truncated_text) > 0:
                truncated_text = truncated_text[:-1]  # Remove one character at a time
            truncated_text += "..."
        self.label_csv.setText(truncated_text) 
    
    def on_button_csv_click(self):
        global chemin_csv
        chemin_csv = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select the folder containing the CSV files', os.getcwd(), QtWidgets.QFileDialog.Option.DontResolveSymlinks)
        if chemin_csv != "":  # Vérifier si le fichier a été choisi
            name = os.path.basename(chemin_csv) # Cette ligne reprend le nom du dernier fichier/dossier d'un chemin.
            font = QtGui.QFont()
            font.setBold(True)
            self.label_csv.setFont(font)
            self.label_csv.setStyleSheet("color: rgb(0, 150, 0);")
            self.set_truncated_label(f"✔ Selected: '{name}'")
        else:
            self.label_csv.setText(f"✘ Please select a valid directory")
            self.label_csv.setStyleSheet("color: rgb(150, 0, 0);")
            font = QtGui.QFont()
            font.setBold(True)
            self.label_csv.setFont(font)

    def on_elc_clicked(self,num):
        global elc_clicked
        button = self.button_list.get(num)  # List index is zero-based
        font = QtGui.QFont()
        font.setPointSize(8)
        if elc_clicked == 0:
            # Reset all settings
            button.setText("REF")
            button.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.lineEdit_ref.setText(str(num+1))
            elc_clicked = 1
            button.setFont(font)
            
        elif elc_clicked == 1:
            button.setText("MSR")
            button.setStyleSheet("background-color: rgb(0, 150, 0);")
            self.lineEdit_msr.setText(str(num+1))
            elc_clicked = 2
            button.setFont(font)
        font.setPointSize(11)
        self.lineEdit_ref.setFont(font)
        self.lineEdit_msr.setFont(font)        

    def on_clear_elc_button(self):
        global elc_clicked
        for i in range(0,32):
            button = self.button_list.get(i)
            button.setText(str(i+1))
            font = QtGui.QFont()
            font.setPointSize(10)
            button.setFont(font)
            button.setStyleSheet("background-color: white; color: black;")
        self.lineEdit_msr.setText("")
        self.lineEdit_ref.setText("")

        elc_clicked = 0

    def on_parse_button_click(self):
        global chemin_csv
        ref_user = self.lineEdit_ref.text()  # Retrieve the text from lineEdit_ref
        msr_user = self.lineEdit_msr.text()
        if chemin_csv != "" and ref_user.isdigit() and msr_user.isdigit():
            if ref_user == msr_user:
                reply = QMessageBox.warning(
                    self,
                    "Avertissement",
                    "L'ELC de référence et de mesure choisi sont identiques.\nVoulez-vous continuer ?",
                    QMessageBox.StandardButton.Ignore| QMessageBox.StandardButton.Abort
                )
                if reply == QMessageBox.StandardButton.Abort:
                    return
            self.lineEdit_ref.setStyleSheet("")
            self.lineEdit_msr.setStyleSheet("")
            self.frame_csv.setStyleSheet("background-color: rgb(244, 245, 181); border: 0.7px solid rgb(224, 225, 161); border-radius: 10px")
            self.button_csv.setStyleSheet("background-color: rgb(255, 254, 207); background-color: rgb(255, 255, 202); color: rgb(0, 0, 0)")
            self.label_data.setText("Analyse des fichiers csv ...")
            ref_user = int(ref_user)
            msr_user = int(msr_user)

            # Disable all buttons
            self.parseButton.setEnabled(False)
            self.button_image.setEnabled(False)
            self.button_sortie.setEnabled(False)
            self.button_reset.setEnabled(False)

            # Créer et commencer un "background thread". Aussi créer un objet de la classe Worker
            self.worker_thread = QtCore.QThread()
            self.worker_thread.start()
            self.worker = Worker(chemin_csv, "jitter_sortie.txt", ref_user, msr_user)
            self.worker.moveToThread(self.worker_thread)

            # Connecter le Thread à la fonction run de l'objet worker
            # Connecter les signaux "finished" et "error" de la classe Worker aux méthode ci-dessous
            self.worker_thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_finished)
            self.worker.error.connect(self.on_error)
            self.worker.create_oscilloplot.connect(self.create_oscilloplot)

        else : 
            
            self.lineEdit_ref.setStyleSheet("border: 0.5px solid red; border-radius: 3px")
            self.lineEdit_msr.setStyleSheet("border: 0.5px solid red; border-radius: 3px")
            self.frame_csv.setStyleSheet("background-color: rgb(244, 245, 181); border: 0.5px solid red")
            self.button_csv.setStyleSheet("background-color: rgb(255, 254, 207); border: 0.5px solid red; border-radius: 5px")

    def smooth_rising_edge(self, t, center, width): 
        return 0.5 * (1 + np.tanh((t - center) / width))

    def create_oscilloplot(self, TIE, mean, std, density, scale=5, plot_oscillo=False, plot_fondu=False):
        ''' Function signalled by worker object '''

        nbr_point_resolution = 1000 
        time = np.linspace(mean-scale*std, mean+scale*std, nbr_point_resolution) #[s] 
        self.figure.clear()

        # Create one axis for plotting
        ax = self.figure.add_subplot(111)

        # Use `ax` for all plotting
        if plot_oscillo:
            for t_ns in TIE:
                signal = self.smooth_rising_edge(time, t_ns, 1.5)
                ax.plot(time, signal, color='blue', linewidth=0.5)

        if plot_fondu:
            for t_ns in TIE:
                signal = self.smooth_rising_edge(time, t_ns, 1)
                density_local = density[np.abs(time - t_ns).argmin()]
                alpha = 1e-10 + (1 - 1e-10) * density_local
                ax.plot(time, signal, color='blue', alpha=alpha, linewidth=0.5)

        # Add colorbar only once
        norm = colors.Normalize(vmin=np.min(density), vmax=np.max(density))
        colormap = matplotlib.colormaps['hot_r']
        cmap = colors.ListedColormap(colormap(np.linspace(0.3, 0.95, 256)))
        sm = cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        self.figure.colorbar(sm, ax=ax, label='Densité')

        # Formatting
        ax.set_xlabel("Temps [ns]")
        ax.set_ylabel("Amplitude")
        ax.set_title("Flancs montants pondérés par leur densité temporelle")
        ax.axvline(0, color='black', linestyle='--', linewidth=1)
        ax.axvline(x=100, color='r', linestyle='--', label='Limite : 100 ns')
        ax.axvline(x=-100, color='r', linestyle='--')
        ax.grid()

        self.canvas.draw()

    
    def on_finished(self, nr_fichiers_, TIE_, min_j_, max_j_, mean_j_, std_j_, noCsv_):
        ''' Function signalled by worker object '''

        global nr_fichiers, TIE, min_jitter, max_jitter, mean_jitter, std_jitter, noCsv

        # Retrieve all info from the Worker class (I.E. Reading of CSVs)
        nr_fichiers = nr_fichiers_
        TIE = TIE_
        min_jitter = min_j_
        max_jitter = max_j_
        mean_jitter = mean_j_
        std_jitter = std_j_
        noCsv = noCsv_

        self.parseButton.setEnabled(True)
        self.button_image.setEnabled(True)
        self.button_sortie.setEnabled(True)
        self.button_reset.setEnabled(True)

        isLagging = True if mean_jitter > 0 else False

        if not noCsv:
            if min_jitter < 0 and max_jitter < 0:
                self.label_data.setText(f"Nombre de fichiers: {int(nr_fichiers)}\nTemps d'avance maximum: {np.abs(min_jitter):.1f} ns\nTemps d'avance minimum: {np.abs(max_jitter):.1f} ns\nTemps moyen d'avance : {np.abs(mean_jitter):.1f} ns\nÉcart type: {std_jitter:.1f} ns")
            elif min_jitter > 0 and max_jitter > 0:
                self.label_data.setText(f"Nombre de fichiers: {int(nr_fichiers)}\nTemps de retard minimum: {min_jitter:.1f} ns\nTemps de retard maximum: {max_jitter:.1f} ns\nTemps moyen de retard: {mean_jitter:.1f} ns\nÉcart type: {std_jitter:.1f} ns")
            elif isLagging:
                self.label_data.setText(f"Nombre de fichiers: {int(nr_fichiers)}\nTemps d'avance maximum: {np.abs(min_jitter):.1f} ns\nTemps de retard maximum: {np.abs(max_jitter):.1f} ns\nTemps moyen de retard : {np.abs(mean_jitter):.1f} ns\nÉcart type: {std_jitter:.1f} ns")
            else:
                self.label_data.setText(f"Nombre de fichiers: {int(nr_fichiers)}\nTemps d'avance maximum: {np.abs(min_jitter):.1f} ns\nTemps de retard maximum: {np.abs(max_jitter):.1f} ns\nTemps moyen d'avance : {np.abs(mean_jitter):.1f} ns\nÉcart type: {std_jitter:.1f} ns")
            font = QtGui.QFont()
            font.setPointSize(11)
            self.label_data.setStyleSheet("padding: 10px; color: black; border: none;")
            self.label_data.setFont(font)

        else:
            self.label_data.setText("")
            QMessageBox.critical(self, "Erreur", "Aucun fichier CSV n'a été trouvé dans le dossier.")
        self.worker_thread.quit()
        self.worker_thread.wait()
        # Reactiver le bouton si le parsing a échoué

    def on_error(self, error_message):
        ''' Function signalled by worker object '''

        self.parseButton.setEnabled(True)
        self.button_image.setEnabled(True)
        self.button_sortie.setEnabled(True)
        self.button_reset.setEnabled(True)
        self.label_data.setText("")
        if error_message == "list index out of range":
            QMessageBox.critical(self, "Erreur", "Veuillez vérifier les numéros de REF et de MSR")
        else:
            QMessageBox.critical(self, "Erreur", error_message)
        self.worker_thread.quit()
        self.worker_thread.wait()

    def on_button_image_click(self):
        global TIE, mean_jitter, std_jitter
        if (TIE.size > 0 and mean_jitter != -1 and std_jitter != -1):
            density = diagram.density(TIE, mean_jitter,std_jitter)
            fig = diagram.oscilloplot(TIE, mean_jitter, std_jitter, density)
            fig.show()
        # Add your download logic here

    def on_button_sortie_click(self):
        global chemin_csv
        if (chemin_csv != ""):
            chemin_sortie = os.path.join(chemin_csv, "jitter_sortie.txt") # ! Always specify extension

            if os.path.isfile(chemin_sortie):
                try:
                    os.startfile(chemin_sortie)  # Windows
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"An error occurred: {e}")
            else: 
                QMessageBox.critical(self, "Erreur", f"file does not exist in path: {chemin_sortie}")
        
    # Reset method
    
    def on_button_clear_all_click(self):

        global chemin_csv, min_jitter, max_jitter, std_jitter, nr_fichiers, mean_jitter, noCsv, elc_clicked 
        chemin_csv = ""
        for i in [min_jitter, max_jitter, std_jitter, nr_fichiers, mean_jitter]:
            i = -1
        noCsv = None
        elc_clicked = 0

        self.label_csv.setText("Dossier contenant les csv")
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_csv.setFont(font)
        self.label_csv.setStyleSheet("color: rgb(172, 168, 159);")

        self.on_clear_elc_button()

        self.label_data.setText("")

        self.figure.clear()
        self.canvas.draw() # Even after clearing, canvas has to be refreshed.
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    ui = Ui_widget()
    ui.setupUi(widget)
    widget.show()
    sys.exit(app.exec())