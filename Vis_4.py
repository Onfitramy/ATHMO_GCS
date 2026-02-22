import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import datetime
import matplotlib.dates as mdates
import serial
import serial.tools
import serial.tools.list_ports
import struct
import time


class StartKnopfi(QtWidgets.QDialog):
    def __init__(self, style):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
    
        self.AN_knopfi = QtWidgets.QPushButton("Start")
        self.AN_knopfi.setStyleSheet(style)
        self.AN_knopfi.setCheckable(True)
        self.AN_knopfi.toggle()
        #self.AN_knopfi.clicked.connect(lambda:self.welches_knopfi(self.AN_knopfi))
        #self.AN_knopfi.connect(self.knopfi_status)
        layout.addWidget(self.AN_knopfi)

        self.AUS_knopfi = QtWidgets.QPushButton("Stop")
        self.AUS_knopfi.setStyleSheet(style)
        self.AUS_knopfi.setCheckable(True)
        self.AUS_knopfi.toggle()
        #self.AUS_knopfi.clicked.connect(lambda:self.welches_knopfi(self.AUS_knopfi))
        #self.AUS_knopfi.connect(self.knopfi_status)
        layout.addWidget(self.AUS_knopfi)

        self.setLayout(layout)

class SignalLeseGerät(QtCore.QThread):
    header_signal = QtCore.pyqtSignal(list)
    werte_signal  = QtCore.pyqtSignal(list)

    def __init__(self, port = "COM3", bautrate = 115200):
        super().__init__()

        self.port = port
        self.bautrate = bautrate
        self.running = False

    def run(self):
        self.running = True
        self.werte = []
        header_eingelesen = False
        
        with serial.Serial(self.port, self.bautrate, timeout = 1) as ser:
            while self.running:
                line = ser.readline()
                if not line:
                    print("Warte auf Werte...")
                    continue
                try:
                    decoded_line = line.decode("utf-8").strip()
                    # Aufteilen der CSV
                    werte_zeilenweise = decoded_line.split(",")
                    #print(werte_zeilenweise)
                    if not header_eingelesen:
                        header = werte_zeilenweise
                        print(header, "____________________________________________________________________________________________________________________________")
                        header_eingelesen = True
                        self.header_signal.emit(header)
                        continue
                    
                    werte_zeilenweise = [float(x) for x in werte_zeilenweise]
                    self.werte_signal.emit(werte_zeilenweise)
                    self.werte.append(werte_zeilenweise)

                    

                except Exception as e:
                    print("Fehler beim Dekodieren:", e)
                    continue
                

    def stop(self):
        self.running = False
        self.wait()
        #print("******************************************************************************************************************************************************" \
        #"********************************************************************************", self.werte, "Ein Wert:", self.werte[1][1])
        #beispielwert = self.werte[1][1]
        #print("Ein Wert (repr):", repr(beispielwert))
        #print("Ein Wert (strip):", beispielwert)

class ImportWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        

        # Ermitteln der Liste an COM Ports:
        self.COM_port_list = serial.tools.list_ports.comports()

        self.layout = QtWidgets.QHBoxLayout()

        # Erstellen eines Titellabels:
        self.Importlabel = QtWidgets.QLabel("Input source: ")
        self.layout.addWidget(self.Importlabel)

        self.PortAuswahl = QtWidgets.QComboBox()
        for port in self.COM_port_list:
            self.PortAuswahl.addItem(port.device)
        self.layout.addWidget(self.PortAuswahl)        
        self.setLayout(self.layout)                             
        self.PortAuswahl.currentIndexChanged.connect(self.andere_auswahl)  

        
        


    def   andere_auswahl(self, i):
        print("Die Auswahlmöglichkeiten sind:")

        for n in range(self.PortAuswahl.count()):
            print(self.PortAuswahl.itemText(n))
        print("Ausgewählter Index: ", i, "; Ausgewählter Port: ", self.PortAuswahl.currentText())
        print("*********************************************************")

class Beispieldaten: # BEISPIELDATEN FÜR DIE DARSTELLUNG DER WIDGETS
    def __init__(self):
        # Für Graphen allgemein:
        self.x = np.linspace(0, 10, 100)
        self.y1 = np.sin(self.x)
        self.y2 = np.cos(self.x)
        self.y3 = np.tan(self.x)
        self.y4 = np.exp(-self.x)
        self.y5 = np.log(self.x + 1)
        
        # Für Timeline:
        self.time = [datetime.datetime(2023, 10, 1, 12, 0),
                      datetime.datetime(2023, 10, 1, 12, 30),
                      datetime.datetime(2023, 10, 1, 13, 0)]
        self.eventname = ["Start", "Mitte", "Ende"]

class GraphErstellen(QtWidgets.QWidget): # Plottet einen Graphen
    def __init__(self, title):
        super().__init__()
        self.canvas = FigureCanvas(Figure())
        # Festlegen der Hintergrundfarbe des Graphen
        self.canvas.figure.patch.set_facecolor("#414141") # Setzt die Hintergrundfarbe des Graphen außen
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.set_facecolor("#313131FF")  # Setzt die Hintergrundfarbe des Graphen innen
        self.ax.set_title(title)

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(10,10,10,10)  # Abstand vom Graph zum Rand des Widgets	 
        # Hinzufügen des Graphen zum Layout
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Formatierung der Achsen
        color = "white"
        self.ax.spines["bottom"].set_color(color)
        self.ax.spines["top"].set_color(color)
        self.ax.spines["left"].set_color(color)
        self.ax.spines["right"].set_color(color)

        # Formatierung der Zahlen an den Achsen
        self.ax.tick_params(axis='x', colors=color)
        self.ax.tick_params(axis='y', colors=color)

        # Formatierung der Achsenbeschriftungen
        self.ax.xaxis.label.set_color(color)
        self.ax.yaxis.label.set_color(color)

        # Formatierung des Titels
        self.ax.title.set_color(color)


    def plot(self, x, y, **kwargs): # erlaubt das Hinzufügen von Daten und weitern Parametern     
        self.ax.plot(x, y, **kwargs)
        self.canvas.draw()

class WertAnzeigen(QtWidgets.QWidget): # Dient zur Anzeige von (variablen) Werten ohne zeitlichen Verlauf
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def update_value(self, variable_name, value=0, unit="g"): # Aktualisiert die Anzeige eines Wertes
        self.label.setText(f"{variable_name}:\n{value}{unit}")

class TimelineErstellen(QtWidgets.QWidget): # Erstellt eine Timeline
    def __init__(self, title): 
        super().__init__()
        self.TimelineErstellen = GraphErstellen("Event Timeline")
        
        self.TimelineErstellen.ax.get_yaxis().set_visible(False)    # versteckt die y-Achse
        self.TimelineErstellen.ax.set_ylim(0.95, 1.05)
        

    def plot_timeline(self, time, eventname, **kwargs):
        t = [1] * len(time) # Setzt die y-Werte auf 1, um eine horizontale Linie zu zeichnen
        self.TimelineErstellen.ax.plot(time, t, **kwargs)
        for t, event in zip(time, eventname): # Fügt die beiden Spalten zusammen
            self.TimelineErstellen.ax.text(t, 1.009, event, rotation=45,
            ha='left', va='bottom', fontsize=8, color="white") 
            # fügt die Beschriftungen der Events hinzu
            # und formatiert sie

class yesnomaybeErstellen(QtWidgets.QWidget):   # Erstellt eine farbige Statusanzeige
    def __init__(self, title):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(title)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.title = title

    def yesnomaybe_update(self, status):    # Aktualisiert die Anzeige des Status je nach Eingabe
        if status == "yes":
            status = "green"
        elif status == "no":
            status = "red"
        elif status == "maybe":
            status = "yellow"
        else:
            status = "grey"
        self.label.setText(f'{self.title} <span style="color:{status}; font-size:16px;">&#9679;</span>') # ändert u.a. die Farbe des Statuspunktes

class FlightDataWindow(QtWidgets.QMainWindow): # Die Gesamtdarstellung der flight data
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATHMO DataVisualizer")
        self.setWindowIcon(QtGui.QIcon("Logo_A.png"))
        
        # Erzeugen des Hauptwidgets und Layouts & Einfügen in das generelle Layout
        main_widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        self.setStyleSheet("background-color: rgb(30, 30, 30)")
        self.title_label = QtWidgets.QLabel("ATHMO DataVisualizer - Flight Data")
        self.title_label.setStyleSheet("font-size: 24px; color: white; padding: 10px;")
        layout.addWidget(self.title_label, 0, 1, QtCore.Qt.AlignCenter)
        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setPixmap(QtGui.QPixmap("Logo_Original_transparent.png").scaled(400, 400, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logo_label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.logo_label, 0, 0, QtCore.Qt.AlignLeft)


        # TEMP___________________________________
        self.x_data = []
        self.y_data = []


        #GRAPHEN
        # Erstellen der Graphen
        self.xyposition_widget = GraphErstellen("Position über Grund")
        self.zposition_widget = GraphErstellen("Höhe über Grund")
        self.v_unendlich_widget = GraphErstellen("Geschwindigkeit in der Höhe (GPS)")
        self.v_uebergrund_widget = GraphErstellen("Geschwindigkeit über Grund")
        
        # Hinzufügen der Graphen zum Layout
        layout.addWidget(self.xyposition_widget, 2, 0)
        layout.addWidget(self.zposition_widget, 3, 0)
        layout.addWidget(self.v_unendlich_widget, 2, 1)
        layout.addWidget(self.v_uebergrund_widget, 3, 1)
        
        # Formatierung der Graphen:
        self.plot_style = {"color": "#5eaea3", "linewidth": 1.5}
        
        # Beispieldaten für die Graphen
        self.daten = Beispieldaten()
        self.xyposition_widget.plot(self.daten.x, self.daten.y1, label="Sinus", **self.plot_style)
        self.zposition_widget.plot(self.daten.x, self.daten.y2, label="Cosinus", **self.plot_style)
        #self.v_unendlich_widget.plot(self.daten.x, self.daten.y3, label="Tangens", **plot_style)
        self.v_unendlich_widget.plot(0, 0, label="Tangens", **self.plot_style)
        self.v_uebergrund_widget.plot(self.daten.x, self.daten.y5, label="Logarithmisch", **self.plot_style) 
        
        #TIMELINE
        # Erstellen der Timeline
        self.timeline_widget = TimelineErstellen("Event Timeline")

        # Formatieren der Timeline
        timeline_style = {"color": "#5eaea3", "ms": 20, "marker": "|"}
        self.timeline_widget.setMinimumHeight(1250)

        # Hinzufügen der Timeline zum Layout
        layout.addWidget(self.timeline_widget.TimelineErstellen, 5, 0, 2, 1)
        
    	# Beispieldaten für die Timeline
        self.daten = Beispieldaten()
        self.timeline_widget.plot_timeline(self.daten.time, self.daten.eventname, **timeline_style)
        
        #STATUSWIDGETS
        # Erstellen der Statuswidgets
        self.systemok_widget = yesnomaybeErstellen("System Status")

        # Formatierung der Statuswidgets
        label_style = "font-size: 16px; color: white; border: 2px solid rgb(175, 175, 175); padding: 1px; border-radius: 5px; background-color: rgb(65, 65, 65);"
        label_width = 170
        self.systemok_widget.setStyleSheet(label_style)
        self.systemok_widget.setMaximumWidth(label_width)

        # Beispiel für die Aktualisierung des Status
        self.systemok_widget.yesnomaybe_update("yes")
        layout.addWidget(self.systemok_widget, 7, 0)


        #COMWIDGET
        # Erstellen eines Widgets zur Auswahl des Input Ports
        self.COM_widget = ImportWidget()

        # Formatierung des COM-widgets
        self.COM_widget.setStyleSheet(label_style)
        self.COM_widget.setMaximumWidth(label_width*2)

        # Hinzufügen des COM-widgets zum layout
        layout.addWidget(self.COM_widget, 7, 1)


        #START/STOP DATENINPUT
        self.startstop_widget = StartKnopfi(label_style)
        #self.startstop_widget.setStyleSheet(label_style)
        self.startstop_widget.setMaximumWidth(label_width*2)
        layout.addWidget(self.startstop_widget, 6, 1)





        #DATENINPUT
        #Test:
        #COMPort = self.COM_widget.PortAuswahl.currentText()
        COMPort = "COM3"
        self.reader = SignalLeseGerät(COMPort)

        self.reader.header_signal.connect(self.Header_add)
        self.reader.werte_signal.connect(self.Werte_add)
        
        self.reader.start()
        QtCore.QTimer.singleShot(15000, self.reader.stop)          
        
        # Hinzufügen des Layouts zum Hauptwidget
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def closeEvent(self, event):
        #self.reader.stop()
        self.reader.wait()
        event.accept()

    def Header_add(self, header):
        #print("Neuer Header: ", header)
        self.header = header
        for i in range(0, len(self.header)):
            print("HEADER", i, ":", self.header[i])
        
    def Werte_add(self, daten_zeilenweise):
        #print("Neue Werte: ", daten_zeilenweise)
        a = 19
        b = 10
        self.v_unendlich_widget.ax.cla()
        self.x_data.append(daten_zeilenweise[0])
        self.y_data.append(daten_zeilenweise[a])

        time_limit = 1

        if self.x_data[len(self.x_data)-1]-self.x_data[0] >= time_limit:
            while self.x_data[len(self.x_data)-1]-self.x_data[0] >= time_limit:
                self.x_data.pop(0)
                self.y_data.pop(0)

        self.v_unendlich_widget.ax.plot(self.x_data, self.y_data, **self.plot_style)
        self.v_unendlich_widget.ax.set_xlabel(self.header[0])
        self.v_unendlich_widget.ax.set_ylabel(self.header[17])
        self.v_unendlich_widget.canvas.draw()


def main():
    app = QtWidgets.QApplication([])
    window = FlightDataWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

