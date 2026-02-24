import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import numpy as np
import datetime
import matplotlib.dates as mdates
import serial
import serial.tools
import serial.tools.list_ports
import time
import pyqtgraph as pg
import os
import ctypes as ctype

pg.setConfigOptions(useOpenGL=False)

class GraphErstellen(QtWidgets.QWidget): # Plottet einen Graphen
    def __init__(self, title = "Titel"):
        super().__init__()
        self.canvas = pg.PlotWidget()
        # Festlegen der Hintergrundfarbe des Graphen
        self.canvas.setBackground("#414141") # Setzt die Hintergrundfarbe des Graphen
        #self.ax.set_facecolor("#313131FF")  # Setzt die Hintergrundfarbe des Graphen innen
        self.canvas.showGrid(x=True, y=True, alpha=0.3)
        self.canvas.setTitle(title, color = "white", size = "16pt")
        self.canvas.getAxis("left").setTextPen("w")
        self.canvas.getAxis("bottom").setTextPen("w")

        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(10,10,10,10)  # Abstand vom Graph zum Rand des Widgets	 
        # Hinzufügen des Graphen zum Layout
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # Formatierung der Achsen
        color = "w" # Kommentar
        self.canvas.getAxis("left").setTextPen(color)
        self.canvas.getAxis("bottom").setTextPen(color)

        self.curve = self.canvas.plot()

    def plot(self, x, y, **kwargs): # erlaubt das Hinzufügen von Daten und weitern Parametern     
        self.canvas.plot(x, y, **kwargs)

class StartKnopfi(QtWidgets.QDialog):
    def __init__(self, style):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()
    
        self.AN_knopfi = QtWidgets.QPushButton("Start")
        self.AN_knopfi.setStyleSheet(style)
        self.AN_knopfi.setCheckable(True)
        self.AN_knopfi.toggle()
        self.layout.addWidget(self.AN_knopfi)

        self.AUS_knopfi = QtWidgets.QPushButton("Stop")
        self.AUS_knopfi.setStyleSheet(style)
        self.AUS_knopfi.setCheckable(True)
        self.AUS_knopfi.toggle()
        self.layout.addWidget(self.AUS_knopfi)

        self.button_group = QtWidgets.QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.AN_knopfi)
        self.button_group.addButton(self.AUS_knopfi)


        self.setLayout(self.layout)

class SignalLeseGerät(QtCore.QThread):
    status_senden = QtCore.pyqtSignal(str)
    header_signal = QtCore.pyqtSignal(list)
    werte_signal  = QtCore.pyqtSignal(list)

    def __init__(self, port = None):
        super().__init__()

        self.port = port
        self.bautrate = 9600
        self.running = False

    def run(self):
        self.running = True
        self.werte = []
        self.serial_port = self.port
        with self.serial_port as ser:
            while self.running:
                try:    
                    line = ser.readline()
                    if not line:
                        print("Warte auf Werte...")
                        continue
                except (serial.SerialException, OSError):
                    print("Verbindung unterbrochen/ gestört")
                try:
                    decoded_line = line.decode("utf-8").strip()
                    #print("Empfangene Zeile:", decoded_line)

                    if not decoded_line:
                        continue

                    # Aufteilen der CSV
                    daten_zeilenweise = decoded_line.split(",")

                    if daten_zeilenweise[0].startswith("ID"):
                        id_str = daten_zeilenweise[0]
                        try:
                            id = int(id_str[2:])
                        except ValueError:
                            print("Ungültige ID:", id_str)
                            continue
                        raw_werte = daten_zeilenweise[1:]
                        daten_zeilenweise = [id] + raw_werte
                        #print("mit ID:", daten_zeilenweise)
                        self.werte_signal.emit(daten_zeilenweise)
                        self.werte.append(daten_zeilenweise)



                        if id == 1:
                            try:    
                                self.status_senden.emit(daten_zeilenweise[4])
                            except Exception as e:
                                print("Fehler beim Senden des Status:", e)



                    else:
                        print("Zeile ohne ID-Präfix empfangen, wird ignoriert:" , daten_zeilenweise)
                        continue
                    
                    #print(daten_zeilenweise)
                    
                except Exception as e:
                    print("Fehler beim Dekodieren:", e)
                    continue
                
    def stop(self):
        self.running = False
        self.wait()

class ActionButton(QtWidgets.QDialog):
    kommando_senden     = QtCore.pyqtSignal(str)
    def __init__(self, cat = None, command = None, style = None, port = None, mode = None):    # cat: Kategorie, text: Button-Text, command: zu sendender Befehl, style: StyleSheet, port: serieller Port, mode: "redgreen" für Toggle-Button
        super().__init__()
        self.cat = cat
        self.command = command
        self.port = port
        self.mode = mode
        self.layout = QtWidgets.QHBoxLayout()
        if mode == "redgreen":
            label_text = f"{cat} Standby"
            self.action_knopfi = QtWidgets.QPushButton(label_text)
            self.action_knopfi.setStyleSheet(style)
            self.action_knopfi.setCheckable(True)
            self.action_knopfi.setChecked(False)
            self.base_style = style or "font-size: 14px; color: white;"
            self.action_knopfi.setFixedWidth(356)
            self.action_knopfi.toggled.connect(self.KOMMANDOOO)
            self.layout.addWidget(self.action_knopfi)
            self.button_group = QtWidgets.QButtonGroup(self)   
            self.setLayout(self.layout)
        elif mode == "int_ext":
            label_text = f"{cat} Standby"
            self.action_knopfi = QtWidgets.QPushButton(label_text)
            self.action_knopfi.setStyleSheet(style)
            self.action_knopfi.setCheckable(True)
            self.action_knopfi.setChecked(False)
            self.base_style = style or "font-size: 14px; color: white;"
            self.action_knopfi.setFixedWidth(356)
            self.action_knopfi.toggled.connect(self.KOMMANDOOO)
            self.layout.addWidget(self.action_knopfi)
            self.button_group = QtWidgets.QButtonGroup(self)   
            self.setLayout(self.layout)
        elif mode == "nrf_xbee":
            label_text = f"{cat} Standby"
            self.action_knopfi = QtWidgets.QPushButton(label_text)
            self.action_knopfi.setStyleSheet(style)
            self.action_knopfi.setCheckable(True)
            self.action_knopfi.setChecked(False)
            self.base_style = style or "font-size: 14px; color: white;"
            self.action_knopfi.setFixedWidth(356)
            self.action_knopfi.toggled.connect(self.KOMMANDOOO)
            self.layout.addWidget(self.action_knopfi)
            self.button_group = QtWidgets.QButtonGroup(self)   
            self.setLayout(self.layout)
        else:
            label_text = f"{cat}"
            self.action_knopfi = QtWidgets.QPushButton(label_text)
            self.action_knopfi.setStyleSheet(style)
            self.action_knopfi.setCheckable(False)
            self.base_style = style
            self.action_knopfi.setFixedWidth(356)
            self.action_knopfi.clicked.connect(self.KOMMANDOOO)
            self.layout.addWidget(self.action_knopfi)
            self.button_group = QtWidgets.QButtonGroup(self)   
            self.setLayout(self.layout)

    def KOMMANDOOO(self, checked = False):
        #print(self.action_knopfi.width())
        self.befehl = "goy_cat"
        if self.mode == "redgreen":
            color = "#e74c3c" if checked else "#5eaea3"
            text = str(self.cat + " OFF") if checked else str(self.cat + " ON")
            self.action_knopfi.setStyleSheet(f"{self.base_style} background-color: {color};")
            self.action_knopfi.setText(text)
            if not checked:
                self.befehl = str(self.command + " 1")
            if checked:
                self.befehl = str(self.command + " 0")
        elif self.mode == "int_ext":
            color = "#4C7973"
            text = str(self.cat + " EXTERNAL") if checked else str(self.cat + " INTERNAL")
            self.action_knopfi.setStyleSheet(f"{self.base_style} background-color: {color};")
            self.action_knopfi.setText(text)
            if not checked:
                self.befehl = str(self.command + " internal")
            if checked:
                self.befehl = str(self.command + " external")
        elif self.mode == "nrf_xbee":
            color = "#4C7973"
            text = str(self.cat + " NRF") if checked else str(self.cat + " XBEE")
            self.action_knopfi.setStyleSheet(f"{self.base_style} background-color: {color};")
            self.action_knopfi.setText(text)
            if not checked:
                self.befehl = str(self.command + " NRF")
            if checked:
                self.befehl = str(self.command + " XBEE")
        else:
            self.befehl = self.command
        if not self.befehl:
            print("Kein Befehl definiert, sende nichts")
            return
        try:
            port = self.port
            if port is None:
                print("Kein offener Hafen, wird geöffnet...")
                port = serial.Serial(self.port, 9600, timeout = 1)
            if port.is_open:
                port.write((self.befehl + "\n").encode())
                self.kommando_senden.emit(self.befehl)
                print("Kommando gegeben o7", self.befehl)
        except Exception as e:
            print("Fehler beim Senden:", e)

class InputActionButton(QtWidgets.QDialog):
    kommando_senden = QtCore.pyqtSignal(str)
    stateforce_kommando = QtCore.pyqtSignal(str, bool)
    def __init__(self, cat = None, command = None, style = None, port = None, size = None, isserious = True):    # cat: Kategorie, command: zu sendender Befehl, style: StyleSheet, port: serieller Port, mode: "redgreen" für Toggle-Button
        super().__init__()
        #### Breite der Knöpfe: 356 px
        self.size = size
        self.isserious = isserious
        self.cat = cat
        self.command = command
        self.port = port
        self.style = style
        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self.cat)
        self.label.setStyleSheet(self.style + "; font-weight: bold;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFixedSize(int(0.6 * self.size[0]), self.size[1])

        self.line = QtWidgets.QLineEdit()
        self.line.setFixedSize(int(0.2 * self.size[0]), self.size[1])
        self.line.setStyleSheet(self.style + "; background-color: #4C7973; border: none; padding: 0px")
        
        senden = "➥" if self.isserious else "💅➥"
        self.btn = QtWidgets.QPushButton(senden)
        self.btn.setFixedSize(int(0.2 * self.size[0]), self.size[1])
        self.btn.setStyleSheet(self.style + "; font-weight: bold;")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line)
        self.layout.addWidget(self.btn)
        self.setFixedWidth(356)
        self.setLayout(self.layout)

        self.btn.clicked.connect(self.instantNudeln)
        self.line.returnPressed.connect(self.instantNudeln)
    def instantNudeln(self):
        eingegebener_wert = self.line.text().strip()
        if eingegebener_wert == "":
            print("dann sag doch was!!")
            return
        befehl = f"{self.command} {eingegebener_wert}"
        try:
            port = self.port
            if port is None:
                print("kein Hafen verfügbar")
                return
            if port.is_open:
                port.write((befehl + "\n").encode())
                self.kommando_senden.emit(befehl)
                
############################################################## experimentell ################

                if self.command == "State_Force":
                    self.stateforce_kommando.emit(eingegebener_wert, True)

#########################################################################

                print("Kommando gegeben o7 ", befehl)
            else:
                print("Nö")
        except Exception as e:
            print("Fehler beim Senden: ", e)

class WertAnzeigen(QtWidgets.QWidget): # Dient zur Anzeige von (variablen) Werten ohne zeitlichen Verlauf
    def __init__(self, name = ""):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()

        if name:
            self.label.setText(f"{name}:\n")

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def update_value(self, variable_name, value=0, unit="[ ]"): # Aktualisiert die Anzeige eines Wertes
        self.label.setText(f"{variable_name}:\n{value}{unit}")

class TextFenster(QtWidgets.QWidget):
    def __init__(self, title = "Verlauf", initial_text = "Die Kommando-Chroniken beginnen hier..."):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(title)
        self.label.setStyleSheet("background-color: #414141; font-size: 18px; padding: 6px; color: white;")
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background-color: #414141; color: white; font-size: 16px; border: none;")
        self.text_edit.setPlainText(initial_text)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.text_edit, 1)
        self.setLayout(self.layout)

    def Anhaengsel(self, new_text):
        if new_text is None:
            return

        new_text = f"sent: {new_text}"
        self.text_edit.append(str(new_text))

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.text_edit.setTextCursor(cursor)

class FlightStateDisplay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("Flight State: N/A")
        self.label.setStyleSheet("background-color: #414141; font-size: 22px; padding: 10px; color: white;")
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def Statuscheckl(self, state, forced = False):
        try:
            state = int(state)
        except (ValueError, TypeError):
            self.label.setText(f"Flight State: {state}")
            return
        if state == 0:
            state = "INIT"
        elif state == 1:
            state = "GNC_ALIGN"
        elif state == 2:
            state = "CHECKOUTS"
        elif state == 3:
            state = "ARMED"
        elif state == 4:
            state = "BURN"
        elif state == 5:
            state = "COAST"
        elif state == 6:
            state = "AWAIT_DROGUE"
        elif state == 7:
            state = "DESCEND_DROGUE"
        elif state == 8:
            state = "AWAIT_MAIN"
        elif state == 9:
            state = "DESCEND_MAIN"
        elif state == 10:
            state = "LANDED"
        else:
            state = "UNDEFINED"
        if forced:
            self.label.setText(f"Flight State: {state} (forced)")
        else:
            self.label.setText(f"Flight State: {state}")

class FlightDataWindow(QtWidgets.QMainWindow): # Die Gesamtdarstellung der flight data
    def __init__(self):
        super().__init__()

        self.isserious = True

        # ALLGEMEINES...........................................................................
        self.setWindowTitle("ATHMO DataVisualizer")
        
        # Fenstericon setzen
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if self.isserious:
            icon_path = os.path.join(base_dir, "Logo_A_transelol.ICO")
        else:
            icon_path = os.path.join(base_dir, "JoharnesSchnitt.jpg.jpg.ICO")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        

        self.port = serial.Serial("COM3", 9600, timeout = 1)
        self.reader = None

        main_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout()
        self.setStyleSheet("background-color: rgb(30, 30, 30)")
        self.title_label = QtWidgets.QLabel("GroundControl")
        self.title_label.setStyleSheet("font-size: 60px; color: #bebebe; padding: 15px; text-align: left;")
        self.title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.title_label, 0, 1)
        self.logo_label = QtWidgets.QLabel()

        # Logo einpflegen
        if not self.isserious:
            logo_path = os.path.join(base_dir, "Logo_Original_transparent_Maggus.PNG")
        else:
            logo_path = os.path.join(base_dir, "Logo_Original_transparent.PNG")
        if os.path.isfile(logo_path):
            pix = QtGui.QPixmap(logo_path)
            if not pix.isNull():
                self.logo_label.setPixmap(pix.scaled(400, 400, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logo_label.setStyleSheet("padding: 10px;")
        self.layout.addWidget(self.logo_label, 0, 0, QtCore.Qt.AlignLeft)

        myappid = 'hehehe.hihihi.hohoho'
        ctype.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


        # GRAPHEN...............................................................................
        self.DatGibtNeAnzeige()
        
        # Formatierung der Graphen:
        self.plot_style = {"color": "#5eaea3", "width": 1.5}
        self.plot_style_alarrm = {"color": "red", "width": 1.5}

        # KNOPFIS...............................................................................
        # Start/Stop-Widget hinzufügen
        startknopfistyle = "font-size: 18px; color: white; background-color: #5eaea3;"
        self.startstop_widget = StartKnopfi(startknopfistyle)
        self.layout.addWidget(self.startstop_widget, 2, 0)

        # TEXTFENSTER...........................................................................
        # Fenster zu Anzeigen der letzten gesendeten Commands
        self.kommando_fenster = TextFenster("Verlauf")
        self.layout.addWidget(self.kommando_fenster, 5, 0)

        # STATUSANZEIGE.........................................................................
        # Selbsterklärend, du dulli
        self.flight_state_display = FlightStateDisplay()
        self.layout.addWidget(self.flight_state_display, 2, 1)





        # -----------aktuelle Commands--------------
        # cls: Clears screen                                                                                    für GS nicht relevant
        # switchCLIMode <mode>: Switches the CLI mode (internal/external)                                       j
        # switchSerialData <1/0>: Switches the Serial Plotter data stream (on/off)                              j
        # switchGroundData <1/0>: Switches the Ground Station data stream (on/off)                              j
        # ...
        # RESET_PRIMARY: Resets the Primary MCU on the flight computer                                          
        # RESET_SECONDARY: Resets the Secondary MCU on the flight computer                                      
        # ...
        # Camera_Power <1/0>: Turns the camera power on or off                                                  j
        # Camera_Recording <1/0>: Turns the camera recording on or off                                          j   
        # Camera_SkipDate: Skips the current date for the camera                                                j
        # Camera_Wifi <1/0>: Turns the camera WiFi on or off                                                    j
        # ...
        # State_Force <x>: Force the Statemachine into state x                                                  j
        # SimulateEvent <event>: Simulate state machine event <event>                                           j
        # Logging_FlightDataOut <Enable/Disable>: Enables or disables flight data output logging to PC          j
        # ...
        # SPARK_SetAngle <float>: Sets target angle of the stepper motor                                        j
        # SPARK_SetSpeed <float>: Sets target speed of the stepper motor                                        j
        # SPARK_ExitMode: Exits the current target mode                                                         j
        # SPARK_ZeroStepper: Finds minimum position of Stepper                                                  j
        # SPARK_FindMax: Finds maximum position of Stepper                                                      j        
        # SPARK_TargetPositionMode: SPARK enters Target Position mode                                           j
        # SPARK_TargetSpeedMode: SPARK enters Target Speed mode                                                 j
        # ...
        # PU_setCAMPower <1/0>: toggles Camera power                                                            j                                   
        # PU_setRecoveryPower <1/0>: toggles Recovery power                                                     j
        # PU_setACSPower <1/0>: toggles ACS power                                                               j
        # ...
        # Buzzer_PlayNote <Note> <duration>: Plays Note from C0 to B8                                           j
        # Buzzer_PlaySong <Song>: Plays Song from Playlist                                                      j
        # Buzzer_PlaySongRepeat <Song> <Period>: Plays Song from Playlist on repeat each period                 j
        # Buzzer_Stop: Stops annoying buzzing activities                                                        j
        # ...
        # Set_HIL <1/0>: Enables or disables Hardware In the Loop (HIL) simulation                              j
        # Radio_Switch <NRF/XBEE>: Switch primary radio to specified radio module                               j

        self.button_height = 37
        button_width = 356
        self.size = (button_width, self.button_height)
        knopfistyle = "font-size: 14px; color: white; background-color: #5eaea3;"

        # PANELS +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+++-+-+-+--+-+-+-+-+-+-+
        gruppenkostuem = "font-size: 18px; color: white; background-color: #414141; font-weight: bold; padding: 10px"

        # KAMERAPanel -----------------------------
        cam_pow_widget      =  ActionButton("Camera Power",     "Camera_Power",      knopfistyle, self.port, "redgreen")
        cam_rec_widget      =  ActionButton("Camera Recording", "Camera_Recording",  knopfistyle, self.port, "redgreen")
        cam_skipdate_widget =  ActionButton("Skip date",        "Camera_SkipDate",   knopfistyle, self.port            )
        cam_wifi_widget     =  ActionButton("Camera WiFi",      "Camera_Wifi",       knopfistyle, self.port, "redgreen")

        cam_pow_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        cam_rec_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        cam_skipdate_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        cam_wifi_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)

        self.CAM_control = QtWidgets.QGroupBox()
        self.CAM_control.setStyleSheet(gruppenkostuem + ";border: none;")
        #self.CAM_control.setTitle("Camera Control")
        CAM_control_layout = QtWidgets.QVBoxLayout()
        CAM_control_layout.addWidget(cam_pow_widget)
        CAM_control_layout.addWidget(cam_rec_widget)
        CAM_control_layout.addWidget(cam_skipdate_widget)
        CAM_control_layout.addWidget(cam_wifi_widget)
        self.CAM_control.setLayout(CAM_control_layout)
        #self.layout.addWidget(self.CAM_control, 3, 0)

        CAM_control_tool = QtWidgets.QToolButton()
        CAM_control_tool.setText("Camera Control ▼")
        CAM_control_tool.setStyleSheet(gruppenkostuem + "; border: none;")
        CAM_control_tool.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        CAM_menu = QtWidgets.QMenu(CAM_control_tool)
        wa = QtWidgets.QWidgetAction(CAM_menu)
        wa.setDefaultWidget(self.CAM_control)
        CAM_menu.addAction(wa)
        CAM_control_tool.setMenu(CAM_menu)

        #self.layout.addWidget(CAM_control_tool, 3, 0)

        # RESETPanel -----------------------------
        reset_primary_widget   = ActionButton("Reset Primary",   "RESET_PRIMARY",   knopfistyle, self.port)
        reset_secondary_widget = ActionButton("Reset Secondary", "RESET_SECONDARY", knopfistyle, self.port)

        reset_primary_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        reset_secondary_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)

        self.RESET_control = QtWidgets.QGroupBox()
        self.RESET_control.setStyleSheet(gruppenkostuem + ";border: none;")
        #self.RESET_control.setTitle("Reset Control")
        RESET_control_layout = QtWidgets.QVBoxLayout()
        RESET_control_layout.addWidget(reset_primary_widget)
        RESET_control_layout.addWidget(reset_secondary_widget)
        self.RESET_control.setLayout(RESET_control_layout)
        #self.layout.addWidget(self.RESET_control, 3, 3)

        # DATAPanel -----------------------------
        cli_mode_widget       = ActionButton("CLI Mode",        "switchCLIMode",      knopfistyle, self.port, "int_ext")
        serialdata_widget     = ActionButton("Serial Data",     "switchSerialData",   knopfistyle, self.port, "redgreen")
        grounddata_widget     = ActionButton("Ground Data",     "switchGroundData",   knopfistyle, self.port, "redgreen")

        cli_mode_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        serialdata_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        grounddata_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)

        self.Data_control = QtWidgets.QGroupBox()
        self.Data_control.setStyleSheet(gruppenkostuem + ";border: none;")
        #self.Data_control.setTitle("Data Control")
        Data_control_layout = QtWidgets.QVBoxLayout()
        Data_control_layout.addWidget(cli_mode_widget)
        Data_control_layout.addWidget(serialdata_widget)
        Data_control_layout.addWidget(grounddata_widget)
        self.Data_control.setLayout(Data_control_layout)
        #self.layout.addWidget(self.Data_control, 4, 0)

        Data_control_tool = QtWidgets.QToolButton()
        Data_control_tool.setText("Data/ Mode Control ▼")
        Data_control_tool.setStyleSheet(gruppenkostuem + "; border: none;")
        Data_control_tool.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        Data_menu = QtWidgets.QMenu(Data_control_tool)
        wa = QtWidgets.QWidgetAction(Data_menu)
        wa.setDefaultWidget(self.Data_control)
        Data_menu.addAction(wa)
        Data_control_tool.setMenu(Data_menu)

        #self.layout.addWidget(Data_control_tool, 4, 0)


        # SPARKPanel ---------------------------
        spark_setangle_widget = InputActionButton("Set Angle", "SPARK_SetAngle", knopfistyle, self.port, self.size, self.isserious)
        spark_setspeed_widget = InputActionButton("Set Speed", "SPARK_SetSpeed", knopfistyle, self.port, self.size, self.isserious)
        spark_exitmode_widget  = ActionButton("Exit Mode", "SPARK_ExitMode", knopfistyle, self.port)
        spark_zerostepper_widget = ActionButton("Zero Stepper", "SPARK_ZeroStepper", knopfistyle, self.port)
        spark_findmax_widget    = ActionButton("Find Max", "SPARK_FindMax", knopfistyle, self.port)
        spark_targetpositionmode_widget = ActionButton("Target Position Mode", "SPARK_TargetPositionMode", knopfistyle, self.port)
        spark_targetspeedmode_widget    = ActionButton("Target Speed Mode", "SPARK_TargetSpeedMode", knopfistyle, self.port)

        spark_setangle_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        spark_setspeed_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        spark_exitmode_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        spark_zerostepper_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        spark_findmax_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        spark_targetpositionmode_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        spark_targetspeedmode_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)

        self.SPARK_control = QtWidgets.QGroupBox()
        self.SPARK_control.setStyleSheet(gruppenkostuem + ";border: none;")
        #self.SPARK_control.setTitle("SPARK Control")
        SPARK_control_layout = QtWidgets.QVBoxLayout()
        SPARK_control_layout.addWidget(spark_setangle_widget)
        SPARK_control_layout.addWidget(spark_setspeed_widget)
        SPARK_control_layout.addWidget(spark_exitmode_widget)
        SPARK_control_layout.addWidget(spark_zerostepper_widget)
        SPARK_control_layout.addWidget(spark_findmax_widget)
        SPARK_control_layout.addWidget(spark_targetpositionmode_widget)
        SPARK_control_layout.addWidget(spark_targetspeedmode_widget)
        self.SPARK_control.setLayout(SPARK_control_layout)
        #self.layout.addWidget(self.SPARK_control, 3, 3)

        SPARK_control_tool = QtWidgets.QToolButton()
        SPARK_control_tool.setText("SPARK Control ▼")
        SPARK_control_tool.setStyleSheet(gruppenkostuem + "; border: none;")
        SPARK_control_tool.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        SPARK_menu = QtWidgets.QMenu(SPARK_control_tool)
        wa = QtWidgets.QWidgetAction(SPARK_menu)
        wa.setDefaultWidget(self.SPARK_control)
        SPARK_menu.addAction(wa)
        SPARK_control_tool.setMenu(SPARK_menu)

        #self.layout.addWidget(SPARK_control_tool, 3, 3)


        # PUPanel -----------------------------
        pu_setcam_widget      = ActionButton("Camera Power",   "PU_setCAMPower",      knopfistyle, self.port, "redgreen")
        pu_setrecovery_widget = ActionButton("Recovery Power", "PU_setRecoveryPower", knopfistyle, self.port, "redgreen")
        pu_setacs_widget      = ActionButton("ACS Power",      "PU_setACSPower",      knopfistyle, self.port, "redgreen")

        pu_setcam_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        pu_setrecovery_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        pu_setacs_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)

        self.PU_control = QtWidgets.QGroupBox()
        self.PU_control.setStyleSheet(gruppenkostuem + ";border: none;")
        #self.PU_control.setTitle("Power Unit Control")
        PU_control_layout = QtWidgets.QVBoxLayout()
        PU_control_layout.addWidget(pu_setcam_widget)
        PU_control_layout.addWidget(pu_setrecovery_widget)
        PU_control_layout.addWidget(pu_setacs_widget)
        self.PU_control.setLayout(PU_control_layout)
        #self.layout.addWidget(self.PU_control, 4, 3)

        PU_control_tool = QtWidgets.QToolButton()
        PU_control_tool.setText("Power Unit Control ▼")
        PU_control_tool.setStyleSheet(gruppenkostuem + "; border: none;")
        PU_control_tool.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        PU_menu = QtWidgets.QMenu(PU_control_tool)
        wa = QtWidgets.QWidgetAction(PU_menu)
        wa.setDefaultWidget(self.PU_control)
        PU_menu.addAction(wa)
        PU_control_tool.setMenu(PU_menu)

        #self.layout.addWidget(PU_control_tool, 4, 3)


        # SOUNDPanel ----------------------------
        sound_playcnote_widget       = ActionButton("Play C4", "Buzzer_PlayNote C4 150", knopfistyle, self.port)
        sound_playnote_widget = InputActionButton("Play Note", "Buzzer_PlayNote", knopfistyle, self.port, self.size, self.isserious)
        sound_playsong_widget       = InputActionButton("Play Song", "Buzzer_PlaySong", knopfistyle, self.port, self.size, self.isserious)
        sound_playsongrepeat_widget = InputActionButton("Play Song Repeat", "Buzzer_PlaySongRepeat", knopfistyle, self.port, self.size, self.isserious)
        sound_stop_widget          = ActionButton("SEI LEISE", "Buzzer_Stop", knopfistyle, self.port)

        sound_stop_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        sound_playcnote_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        sound_playnote_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        sound_playsong_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        sound_playsongrepeat_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)

        self.SOUND_control = QtWidgets.QGroupBox()
        self.SOUND_control.setStyleSheet(gruppenkostuem + ";border: none;")
        #self.SOUND_control.setTitle("Sound Control")
        SOUND_control_layout = QtWidgets.QVBoxLayout()
        SOUND_control_layout.addWidget(sound_playcnote_widget)
        SOUND_control_layout.addWidget(sound_playnote_widget)
        SOUND_control_layout.addWidget(sound_playsong_widget)
        SOUND_control_layout.addWidget(sound_playsongrepeat_widget)
        SOUND_control_layout.addWidget(sound_stop_widget)
    
        self.SOUND_control.setLayout(SOUND_control_layout)
        #self.layout.addWidget(self.SOUND_control, 4, 1)

        SOUND_control_tool = QtWidgets.QToolButton()
        SOUND_control_tool.setText("Sound Control ▼")
        SOUND_control_tool.setStyleSheet(gruppenkostuem + "; border: none;")
        SOUND_control_tool.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        SOUND_menu = QtWidgets.QMenu(SOUND_control_tool)
        wa = QtWidgets.QWidgetAction(SOUND_menu)
        wa.setDefaultWidget(self.SOUND_control)
        SOUND_menu.addAction(wa)
        SOUND_control_tool.setMenu(SOUND_menu)

        #self.layout.addWidget(SOUND_control_tool, 5, 0)

        # SONSTIGESPanel----------------------------
        stateforce_widget = InputActionButton("Force State", "State_Force", knopfistyle, self.port, self.size, self.isserious)
        simulateevent_widget = InputActionButton("Simulate Event", "SimulateEvent", knopfistyle, self.port, self.size, self.isserious)
        loggingflightdataout_widget = ActionButton("Logging Flight Data Out", "Logging_FlightDataOut", knopfistyle, self.port, "redgreen")
        set_hil_widget = ActionButton("Set HIL", "Set_HIL", knopfistyle, self.port, "redgreen")
        radioswitch_widget = ActionButton("Radio Switch", "Radio_Switch", knopfistyle, self.port, "nrf_xbee")

        stateforce_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        simulateevent_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        loggingflightdataout_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        set_hil_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)
        radioswitch_widget.kommando_senden.connect(self.kommando_fenster.Anhaengsel)

        #################### experimentell #####################
        stateforce_widget.stateforce_kommando.connect(self.flight_state_display.Statuscheckl)

        self.OTHER_control = QtWidgets.QGroupBox()
        self.OTHER_control.setStyleSheet(gruppenkostuem + ";border: none;")
        #self.OTHER_control.setTitle("Other Control")
        OTHER_control_layout = QtWidgets.QVBoxLayout()
        OTHER_control_layout.addWidget(stateforce_widget)
        OTHER_control_layout.addWidget(simulateevent_widget)
        OTHER_control_layout.addWidget(loggingflightdataout_widget)
        OTHER_control_layout.addWidget(set_hil_widget)
        OTHER_control_layout.addWidget(radioswitch_widget)
        self.OTHER_control.setLayout(OTHER_control_layout)
        #self.layout.addWidget(self.OTHER_control, 5, 1)

        OTHER_control_tool = QtWidgets.QToolButton()
        OTHER_control_tool.setText("Other Control ▼")
        OTHER_control_tool.setStyleSheet(gruppenkostuem + "; border: none;")
        OTHER_control_tool.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        OTHER_menu = QtWidgets.QMenu(OTHER_control_tool)
        wa = QtWidgets.QWidgetAction(OTHER_menu)
        wa.setDefaultWidget(self.OTHER_control)
        OTHER_menu.addAction(wa)
        OTHER_control_tool.setMenu(OTHER_menu)

        #self.layout.addWidget(OTHER_control_tool, 5, 1)

        # ZUSAMMENFASSENDESPanel-------------------------#
        self.TOTAL_control = QtWidgets.QGroupBox()
        self.TOTAL_control.setStyleSheet(gruppenkostuem + ";border: none;")
        total_control_layout = QtWidgets.QGridLayout()
        total_control_layout.addWidget(CAM_control_tool,    1, 0)
        total_control_layout.addWidget(Data_control_tool,   0, 1)
        total_control_layout.addWidget(SPARK_control_tool,  1, 1)
        total_control_layout.addWidget(PU_control_tool,     0, 0)
        total_control_layout.addWidget(SOUND_control_tool,  2, 0)
        total_control_layout.addWidget(OTHER_control_tool,  2, 1)

        self.TOTAL_control.setLayout(total_control_layout)
        self.layout.addWidget(self.TOTAL_control, 3, 0)

        # HAUPTFENSTER..........................................................................
        main_widget.setLayout(self.layout)
        self.setCentralWidget(main_widget)

        # EINLESEN..............................................................................
        self.timelimit_5   = 5 # maximales Zeitfenster [s] für Batt.Spannung, anderes unwichtiges Zeugs
        self.timelimit_20  = 20 # maximales Zeitfenster [s] für minimal relevante Sachen
        self.timelimit_60  = 60 # maximales Zeitfenster [s] für das einzig wichtige - die Flugbahn (keine Garantie)
        self.reader = None
        #self.COM_widget.port_changed.connect(self.change_port)

        self.startstop_widget.AN_knopfi.clicked.connect(self.start_reader)
        self.startstop_widget.AUS_knopfi.clicked.connect(self.stop_reader)
        # ......................................................................................
    

    def init_reader(self):
        if hasattr(self, "reader") and self.reader is not None:
            self.reader.stop()
        if not self.port:
            self.reader = None
            return
        self.reader = SignalLeseGerät(self.port)
        self.reader.werte_signal.connect(self.Werte_add)
        self.reader.header_signal.connect(self.Header_add)
        self.reader.status_senden.connect(self.flight_state_display.Statuscheckl)

    def start_reader(self):
        if self.reader is None:
            self.init_reader()
            self.reader.header_signal.connect(self.Header_add)
            self.reader.werte_signal.connect(self.Werte_add)
            self.reader.start()
        if not self.reader.isRunning():
            self.reader.start()
    def stop_reader(self):
        if self.reader and self.reader.isRunning():
            self.reader.stop()

    def change_port(self, port_name):
        self.stop_reader()
        if self.port is not None:
            try:
                self.port.close()
            except Exception:
                pass
        try:
            self.port = serial.Serial(port_name, 9600, timeout = 1)
        except Exception as e:
            self.port = None

    def Header_add(self, header):
        self.header = header
        for i in range(0, len(self.header)):
            print("HEADER", i, ":", self.header[i])
        
    def Werte_add(self, daten_zeilenweise, timelimit = 5):  

        try:
            id = int(daten_zeilenweise[0])
        except ValueError:
            print("ungültige ID im Datenpaket")
            return
        
        struktur, skalierung, einheit, yachsenplot = self.Datenstruktur(id)
        datenlänge = len(struktur)
        daten_zeilenweise = daten_zeilenweise + ["0"] * (datenlänge - len(daten_zeilenweise))

        if not hasattr(self, "_data"):
            self._data = {}

        buffer = self._data.setdefault(id, [])
        last = buffer[-1] if buffer else [0.0] * datenlänge

        row = [None] * datenlänge
        row[0] = id
        for i in range(1, datenlänge):
            try:
                row[i] = float(daten_zeilenweise[i]) * skalierung[i]
            except Exception:
                row[i] = last[i] if last is not None else 0.0

        print(row)

        buffer.append(row)

        try:
            while len(buffer) > 1 and (buffer[-1][1] - buffer[0][1] > timelimit):
                buffer.pop(0)
        except Exception:
            pass

        alarrm_flags = getattr(self, f"alarrm_ID{id}", False)

        for i in range(2, datenlänge):
            plot_spec = yachsenplot[i]

            # Einzelanzeige ("solo")
            if plot_spec == "solo":
                widget_name = f"wertanzeige_{id}_{i-1}_widget"
                if not hasattr(self, widget_name):
                    continue
                widget = getattr(self, widget_name)
                try:
                    widget.update_value(struktur[i], buffer[-1][i], einheit[i])
                except Exception: pass
                continue

            # überspringen, wenn deaktiviert/0/False
            if not plot_spec:
                continue

            try:
                x_idx = int(plot_spec)
                if not (0 <= x_idx < datenlänge):
                    x_idx = 1
            except Exception:
                x_idx = 1         

            if isinstance(plot_spec, int) and 0 <= plot_spec < datenlänge:
                x_idx = plot_spec

            xs = [r[x_idx] for r in buffer]
            ys = [r[i] for r in buffer]

            widget_name = f"graph_{id}_{i-1}_widget"
            if not hasattr(self, widget_name): continue
            widget = getattr(self, widget_name)
            pen_kwargs = self.plot_style_alarrm if alarrm_flags else self.plot_style
            try:
                if hasattr(widget, "curve"):  widget.curve.setData(xs, ys, pen=pg.mkPen(**pen_kwargs))
                else:                         widget.setData(xs, ys, pen=pg.mkPen(**pen_kwargs))
                widget.canvas.setTitle(struktur[i], color = "w")
                widget.canvas.setLabel("left", einheit[i], color = "w")
            except Exception:
                pass

        

    def DatGibtNeAnzeige(self):
        # ANZEIGEBESTIMMUNGEN der Daten
        
        # ID1 - Status Packet...........................................................................
        # Status flags:
        self.view_statusflag = False
        self.pos_statusflag = [0, 0]
        self.view_value_statusflag = False
        self.pos_value_statusflag = [0, 0]
        # Sensor status flags:
        self.view_sensorstatusflags = False
        self.pos_sensorstatusflags = [0, 0]
        self.view_value_sensorstatusflags = False
        self.pos_value_sensorstatusflags = [0, 0]
        # State:
        self.view_state = False
        self.pos_state = [0, 0]
        self.view_value_state = False
        self.pos_value_state = [0, 0]

        graphpos_ID1 = [self.pos_statusflag, self.pos_sensorstatusflags, self.pos_state]
        graphview_ID1 = [self.view_statusflag, self.view_sensorstatusflags, self.view_state]
        valueview_ID1 = [self.view_value_statusflag, self.view_value_sensorstatusflags, self.view_value_state]
        valuepos_ID1 = [self.pos_value_statusflag, self.pos_value_sensorstatusflags, self.pos_value_state]
        graphname_ID1 = self.Datenstruktur(1)[0][2:len(self.Datenstruktur(1)[0])-1]

        # Auswahl der anzuzeigenden Graphen:
        for i in range(len(graphview_ID1)):
            if graphview_ID1[i] and not graphpos_ID1[i] == [0, 0]:
                widget_name = f"graph_1_{i+1}_widget"
                widget = GraphErstellen(graphname_ID1[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, graphpos_ID1[i][0], graphpos_ID1[i][1])
            if valueview_ID1[i]:
                widget_name = f"wertanzeige_1_{i+1}_widget"
                widget = WertAnzeigen(graphname_ID1[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, valuepos_ID1[i][0], valuepos_ID1[i][1])               

        # ID2 - Power Packet.............................................................................     
        # M1_5V_bus:
        self.view_M1_5V_bus = False
        self.pos_M1_5V_bus = [0, 0]
        self.view_value_M1_5V_bus = False
        self.pos_value_M1_5V_bus = [0, 0]
        # M1_BAT_bus:
        self.view_M1_BAT_bus = False
        self.pos_M1_BAT_bus = [0, 0]
        self.view_value_M1_BAT_bus = False
        self.pos_value_M1_BAT_bus = [0, 0]
        # unused1:
        self.view_unused1 = False
        self.pos_unused1 = [0, 0]
        self.view_value_unused1 = False
        self.pos_value_unused1 = [0, 0]
        # M2_bus_5V:
        self.view_M2_bus_5V = False
        self.pos_M2_bus_5V = [0, 0]
        self.view_value_M2_bus_5V = False
        self.pos_value_M2_bus_5V = [0, 0]
        # M2_bus_GPA_bat:
        self.view_M2_bus_GPA_bat = False
        self.pos_M2_bus_GPA_bat = [0, 0]
        self.view_value_M2_bus_GPA_bat = False
        self.pos_value_M2_bus_GPA_bat = [0, 0]
        # unused2:
        self.view_unused2 = False
        self.pos_unused2 = [0, 0]
        self.view_value_unused2 = False
        self.pos_value_unused2 = [0, 0]
        # PU_pow:
        self.view_PU_pow = False
        self.pos_PU_pow = [0, 0]
        self.view_value_PU_pow = False
        self.pos_value_PU_pow = [0, 0]
        # PU_curr:
        self.view_PU_curr = False
        self.pos_PU_curr = [0, 0]
        self.view_value_PU_curr = False
        self.pos_value_PU_curr = [0, 0]
        # PU_bat_bus:
        self.view_PU_bat_bus = False
        self.pos_PU_bat_bus = [0, 0]
        self.view_value_PU_bat_bus = False
        self.pos_value_PU_bat_bus = [0, 0]
        # unused3:
        self.view_unused3 = False
        self.pos_unused3 = [0, 0]
        self.view_value_unused3 = False
        self.pos_value_unused3 = [0, 0]

        graphpos_ID2 = [self.pos_M1_5V_bus, self.pos_M1_BAT_bus, self.pos_unused1, self.pos_M2_bus_5V,
                        self.pos_M2_bus_GPA_bat, self.pos_unused2, self.pos_PU_pow,
                        self.pos_PU_curr, self.pos_PU_bat_bus, self.pos_unused3]
        graphview_ID2 = [self.view_M1_5V_bus, self.view_M1_BAT_bus, self.view_unused1, self.view_M2_bus_5V,
                         self.view_M2_bus_GPA_bat, self.view_unused2, self.view_PU_pow,
                         self.view_PU_curr, self.view_PU_bat_bus, self.view_unused3]
        valueview_ID2 = [self.view_value_M1_5V_bus, self.view_value_M1_BAT_bus, self.view_value_unused1, self.view_value_M2_bus_5V,
                         self.view_value_M2_bus_GPA_bat, self.view_value_unused2, self.view_value_PU_pow,
                         self.view_value_PU_curr, self.view_value_PU_bat_bus, self.view_value_unused3]
        valuepos_ID2 = [self.pos_value_M1_5V_bus, self.pos_value_M1_BAT_bus, self.pos_value_unused1, self.pos_value_M2_bus_5V,
                         self.pos_value_M2_bus_GPA_bat, self.pos_value_unused2, self.pos_value_PU_pow,
                         self.pos_value_PU_curr, self.pos_value_PU_bat_bus, self.pos_value_unused3]
        graphname_ID2 = self.Datenstruktur(2)[0][2:len(self.Datenstruktur(2)[0])-1]

        # Auswahl der anzuzeigenden Graphen:
        for i in range(len(graphview_ID2)):
            if graphview_ID2[i] and not graphpos_ID2[i] == [0, 0]:
                widget_name = f"graph_2_{i+1}_widget"
                widget = GraphErstellen(graphname_ID2[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, graphpos_ID2[i][0], graphpos_ID2[i][1])
            if valueview_ID2[i]:
                widget_name = f"wertanzeige_2_{i+1}_widget"
                widget = WertAnzeigen(graphname_ID2[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, valuepos_ID2[i][0], valuepos_ID2[i][1])
    

        # ID3 - GPS Packet...............................................................................
        # latitude:
        self.view_latitude = False
        self.pos_latitude = [0, 0]
        self.view_value_latitude = False
        self.pos_value_latitude = [0, 0]
        # longitude:
        self.view_longitude = False
        self.pos_longitude = [0, 0]
        self.view_value_longitude = False
        self.pos_value_longitude = [0, 0]
        # altitude:
        self.view_altitude = False
        self.pos_altitude = [0, 0]
        self.view_value_altitude = False
        self.pos_value_altitude = [0, 0]
        # speed:
        self.view_speed = False
        self.pos_speed = [0, 0]
        self.view_value_speed = False
        self.pos_value_speed = [0, 0]
        # course:
        self.view_course = False
        self.pos_course = [0, 0]
        self.view_value_course = False
        self.pos_value_course = [0, 0]
        # unused1:
        self.view_unused1_id3 = False
        self.pos_unused1_id3 = [0, 0]
        self.view_value_unused1_id3 = False
        self.pos_value_unused1_id3 = [0, 0]
        # unused2:
        self.view_unused2_id3 = False
        self.pos_unused2_id3 = [0, 0]
        self.view_value_unused2_id3 = False
        self.pos_value_unused2_id3 = [0, 0]
        # unused3:
        self.view_unused3_id3 = False
        self.pos_unused3_id3 = [0, 0]
        self.view_value_unused3_id3 = False
        self.pos_value_unused3_id3 = [0, 0]
        # unused4:
        self.view_unused4_id3 = False
        self.pos_unused4_id3 = [0, 0]
        self.view_value_unused4_id3 = False
        self.pos_value_unused4_id3 = [0, 0]
        # unused5:
        self.view_unused5_id3 = False
        self.pos_unused5_id3 = [0, 0]
        self.view_value_unused5_id3 = False
        self.pos_value_unused5_id3 = [0, 0]

        graphpos_ID3 = [self.pos_latitude, self.pos_longitude, self.pos_altitude, self.pos_speed,
                        self.pos_course, self.pos_unused1_id3, self.pos_unused2_id3,
                        self.pos_unused3_id3, self.pos_unused4_id3, self.pos_unused5_id3]
        graphview_ID3 = [self.view_latitude, self.view_longitude, self.view_altitude, self.view_speed,
                         self.view_course, self.view_unused1_id3, self.view_unused2_id3,
                         self.view_unused3_id3, self.view_unused4_id3, self.view_unused5_id3]
        valueview_ID3 = [self.view_value_latitude, self.view_value_longitude, self.view_value_altitude, self.view_value_speed,
                         self.view_value_course, self.view_value_unused1_id3, self.view_value_unused2_id3,
                         self.view_value_unused3_id3, self.view_value_unused4_id3, self.view_value_unused5_id3]
        valuepos_ID3 = [self.pos_value_latitude, self.pos_value_longitude, self.pos_value_altitude, self.pos_value_speed,
                         self.pos_value_course, self.pos_value_unused1_id3, self.pos_value_unused2_id3,
                         self.pos_value_unused3_id3, self.pos_value_unused4_id3, self.pos_value_unused5_id3]
        graphname_ID3 = self.Datenstruktur(3)[0][2:len(self.Datenstruktur(3)[0])-1]

        # Auswahl der anzuzeigenden Graphen:
        for i in range(len(graphview_ID3)):
            if graphview_ID3[i] and not graphpos_ID3[i] == [0, 0]:
                widget_name = f"graph_3_{i+1}_widget"
                widget = GraphErstellen(graphname_ID3[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, graphpos_ID3[i][0], graphpos_ID3[i][1])
            if valueview_ID3[i]:
                widget_name = f"wertanzeige_3_{i+1}_widget"
                widget = WertAnzeigen(graphname_ID3[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, valuepos_ID3[i][0], valuepos_ID3[i][1])


        # ID4 - IMU Packet
        # IMU1_x_accel:
        self.view_IMU1_x_accel = False
        self.pos_IMU1_x_accel = [3, 1]
        self.view_value_IMU1_x_accel = False
        self.pos_value_IMU1_x_accel = [4, 0]
        # IMU1_y_accel:
        self.view_IMU1_y_accel = False
        self.pos_IMU1_y_accel = [4, 1]
        self.view_value_IMU1_y_accel = False
        self.pos_value_IMU1_y_accel = [0, 0]
        # IMU1_z_accel:
        self.view_IMU1_z_accel = False
        self.pos_IMU1_z_accel = [5, 1]
        self.view_value_IMU1_z_accel = False
        self.pos_value_IMU1_z_accel = [0, 0]
        # IMU1_x_gyro:
        self.view_IMU1_x_gyro = False
        self.pos_IMU1_x_gyro = [3, 2]
        self.view_value_IMU1_x_gyro = False
        self.pos_value_IMU1_x_gyro = [0, 0]
        # IMU1_y_gyro:
        self.view_IMU1_y_gyro = False
        self.pos_IMU1_y_gyro = [4, 2]
        self.view_value_IMU1_y_gyro = False
        self.pos_value_IMU1_y_gyro = [0, 0]
        # IMU1_z_gyro:
        self.view_IMU1_z_gyro = False
        self.pos_IMU1_z_gyro = [5, 2]
        self.view_value_IMU1_z_gyro = False
        self.pos_value_IMU1_z_gyro = [0, 0]
        # magX:
        self.view_magX = True
        self.pos_magX = [3, 1]
        self.view_value_magX = True   
        self.pos_value_magX = [4, 0]
        # magY:
        self.view_magY = True
        self.pos_magY = [4, 1]
        self.view_value_magY = False    
        self.pos_value_magY = [0, 0]
        # magZ:
        self.view_magZ = True
        self.pos_magZ = [5, 1]
        self.view_value_magZ = False    
        self.pos_value_magZ = [0, 0]
        # unused:
        self.view_unused_id4 = False
        self.pos_unused_id4 = [0, 0]
        self.view_value_unused_id4 = False    
        self.pos_value_unused_id4 = [0, 0]

        graphpos_ID4 = [self.pos_IMU1_x_accel, self.pos_IMU1_y_accel, self.pos_IMU1_z_accel, self.pos_IMU1_x_gyro,
                        self.pos_IMU1_y_gyro, self.pos_IMU1_z_gyro, self.pos_magX,
                        self.pos_magY, self.pos_magZ, self.pos_unused_id4]
        graphview_ID4 = [self.view_IMU1_x_accel, self.view_IMU1_y_accel, self.view_IMU1_z_accel, self.view_IMU1_x_gyro,
                         self.view_IMU1_y_gyro, self.view_IMU1_z_gyro, self.view_magX,
                         self.view_magY, self.view_magZ, self.view_unused_id4]  
        valueview_ID4 = [self.view_value_IMU1_x_accel, self.view_value_IMU1_y_accel, self.view_value_IMU1_z_accel, self.view_value_IMU1_x_gyro,
                            self.view_value_IMU1_y_gyro, self.view_value_IMU1_z_gyro, self.view_value_magX,
                            self.view_value_magY, self.view_value_magZ, self.view_value_unused_id4]
        valuepos_ID4 = [self.pos_value_IMU1_x_accel, self.pos_value_IMU1_y_accel, self.pos_value_IMU1_z_accel, self.pos_value_IMU1_x_gyro,
                            self.pos_value_IMU1_y_gyro, self.pos_value_IMU1_z_gyro, self.pos_value_magX,
                            self.pos_value_magY, self.pos_value_magZ, self.pos_value_unused_id4]
        graphname_ID4 = self.Datenstruktur(4)[0][2:len(self.Datenstruktur(4)[0])-1]

        # Auswahl der anzuzeigenden Graphen:
        for i in range(len(graphview_ID4)):
            if graphview_ID4[i] and not graphpos_ID4[i] == [0, 0]:
                widget_name = f"graph_4_{i+1}_widget"
                widget = GraphErstellen(graphname_ID4[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, graphpos_ID4[i][0], graphpos_ID4[i][1])
            if valueview_ID4[i]:
                widget_name = f"wertanzeige_4_{i+1}_widget"
                widget = WertAnzeigen(graphname_ID4[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, valuepos_ID4[i][0], valuepos_ID4[i][1])


        # ID5 - Temperature Packet
        # M1_DTS:
        self.view_M1_DTS = False
        self.pos_M1_DTS = [0, 0]
        self.view_value_M1_DTS = False    
        self.pos_value_M1_DTS = [0, 0]
        # M1_ADC:
        self.view_M1_ADC = False
        self.pos_M1_ADC = [0, 0]
        self.view_value_M1_ADC = False    
        self.pos_value_M1_ADC = [0, 0]
        # M1_BMP:
        self.view_M1_BMP = False
        self.pos_M1_BMP = [0, 0]
        self.view_value_M1_BMP = False    
        self.pos_value_M1_BMP = [0, 0]
        # M1_IMU1:
        self.view_M1_IMU1 = False
        self.pos_M1_IMU1 = [0, 0]
        self.view_value_M1_IMU1 = False
        self.pos_value_M1_IMU1 = [0, 0]
        # M1_IMU2:
        self.view_M1_IMU2 = False
        self.pos_M1_IMU2 = [0, 0]
        self.view_value_M1_IMU2 = False
        self.pos_value_M1_IMU2 = [0, 0]
        # M1_MAG:
        self.view_M1_MAG = False
        self.pos_M1_MAG = [0, 0]
        self.view_value_M1_MAG = False
        self.pos_value_M1_MAG = [0, 0]
        # M2_3V3:
        self.view_M2_3V3 = False
        self.pos_M2_3V3 = [0, 0]
        self.view_value_M2_3V3 = False
        self.pos_value_M2_3V3 = [0, 0]
        # M2_XBee:
        self.view_M2_XBee = False
        self.pos_M2_XBee = [0, 0]
        self.view_value_M2_XBee = False
        self.pos_value_M2_XBee = [0, 0]
        # PU_BAT:
        self.view_PU_BAT = False
        self.pos_PU_BAT = [0, 0]
        self.view_value_PU_BAT = False
        self.pos_value_PU_BAT = [0, 0]
        # Pressure:
        self.view_Pressure = False
        self.pos_Pressure = [0, 0]
        self.view_value_Pressure = False
        self.pos_value_Pressure = [0, 0]
        # unused1:
        self.view_unused1_id5 = False
        self.pos_unused1_id5 = [0, 0]
        self.view_value_unused1_id5 = False
        self.pos_value_unused1_id5 = [0, 0]
        # unused2:
        self.view_unused2_id5 = False
        self.pos_unused2_id5 = [0, 0]
        self.view_value_unused2_id5 = False
        self.pos_value_unused2_id5 = [0, 0]
        
        graphpos_ID5 = [self.pos_M1_DTS, self.pos_M1_ADC, self.pos_M1_BMP, self.pos_M1_IMU1,
                        self.pos_M1_IMU2, self.pos_M1_MAG, self.pos_M2_3V3,
                        self.pos_M2_XBee, self.pos_PU_BAT, self.pos_Pressure,
                        self.pos_unused1_id5, self.pos_unused2_id5]
        graphview_ID5 = [self.view_M1_DTS, self.view_M1_ADC, self.view_M1_BMP, self.view_M1_IMU1,
                         self.view_M1_IMU2, self.view_M1_MAG, self.view_M2_3V3,
                         self.view_M2_XBee, self.view_PU_BAT, self.view_Pressure,
                         self.view_unused1_id5, self.view_unused2_id5]
        valueview_ID5 = [self.view_value_M1_DTS, self.view_value_M1_ADC, self.view_value_M1_BMP, self.view_value_M1_IMU1,
                         self.view_value_M1_IMU2, self.view_value_M1_MAG, self.view_value_M2_3V3,
                         self.view_value_M2_XBee, self.view_value_PU_BAT, self.view_value_Pressure,
                         self.view_value_unused1_id5, self.view_value_unused2_id5]
        valuepos_ID5 = [self.pos_value_M1_DTS, self.pos_value_M1_ADC, self.pos_value_M1_BMP, self.pos_value_M1_IMU1,
                         self.pos_value_M1_IMU2, self.pos_value_M1_MAG, self.pos_value_M2_3V3,
                         self.pos_value_M2_XBee, self.pos_value_PU_BAT, self.pos_value_Pressure,
                         self.pos_value_unused1_id5, self.pos_value_unused2_id5]
        graphname_ID5 = self.Datenstruktur(5)[0][2:len(self.Datenstruktur(5)[0])-1]

        # Auswahl der anzuzeigenden Graphen:
        for i in range(len(graphview_ID5)):
            if graphview_ID5[i] and not graphpos_ID5[i] == [0, 0]:
                widget_name = f"graph_5_{i+1}_widget"
                widget = GraphErstellen(graphname_ID5[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, graphpos_ID5[i][0], graphpos_ID5[i][1])
            if valueview_ID5[i]:
                widget_name = f"wertanzeige_5_{i+1}_widget"
                widget = WertAnzeigen(graphname_ID5[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, valuepos_ID5[i][0], valuepos_ID5[i][1])


        # ID6 - Position Packet
        # posX:
        self.view_posX = False
        self.pos_posX = [0, 0]
        self.view_value_posX = False
        self.pos_value_posX = [0, 0]
        # posY:
        self.view_posY = False
        self.pos_posY = [0, 0]
        self.view_value_posY = False
        self.pos_value_posY = [0, 0]
        # posZ:
        self.view_posZ = False
        self.pos_posZ = [0, 0]
        self.view_value_posZ = False
        self.pos_value_posZ = [0, 0]
        # velX:
        self.view_velX = False
        self.pos_velX = [0, 0]
        self.view_value_velX = False
        self.pos_value_velX = [0, 0]
        # velY:
        self.view_velY = False
        self.pos_velY = [0, 0]
        self.view_value_velY = False
        self.pos_value_velY = [0, 0]
        # velZ:
        self.view_velZ = False
        self.pos_velZ = [0, 0]
        self.view_value_velZ = False
        self.pos_value_velZ = [0, 0]
        # unused1:
        self.view_unused1_id6 = False
        self.pos_unused1_id6 = [0, 0]
        self.view_value_unused1_id6 = False
        self.pos_value_unused1_id6 = [0, 0]

        graphpos_ID6 = [self.pos_posX, self.pos_posY, self.pos_posZ, self.pos_velX,
                        self.pos_velY, self.pos_velZ, self.pos_unused1_id6]
        graphview_ID6 = [self.view_posX, self.view_posY, self.view_posZ, self.view_velX,
                         self.view_velY, self.view_velZ, self.view_unused1_id6]
        valueview_ID6 = [self.view_value_posX, self.view_value_posY, self.view_value_posZ, self.view_value_velX,
                         self.view_value_velY, self.view_value_velZ, self.view_value_unused1_id6]
        valuepos_ID6 = [self.pos_value_posX, self.pos_value_posY, self.pos_value_posZ, self.pos_value_velX,
                         self.pos_value_velY, self.pos_value_velZ, self.pos_value_unused1_id6]
        graphname_ID6 = self.Datenstruktur(6)[0][2:len(self.Datenstruktur(6)[0])-1]

        # Auswahl der anzuzeigenden Graphen:
        for i in range(len(graphview_ID6)):
            if graphview_ID6[i] and not graphpos_ID6[i] == [0, 0]:
                widget_name = f"graph_6_{i+1}_widget"
                widget = GraphErstellen(graphname_ID6[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, graphpos_ID6[i][0], graphpos_ID6[i][1])
            if valueview_ID6[i]:
                widget_name = f"wertanzeige_6_{i+1}_widget"
                widget = WertAnzeigen(graphname_ID6[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, valuepos_ID6[i][0], valuepos_ID6[i][1])


        # ID7 - Attitude Packet
        # phi:
        self.view_phi = True
        self.pos_phi = [3, 2]
        self.view_value_phi = False
        self.pos_value_phi = [0, 0]
        # theta:
        self.view_theta = True
        self.pos_theta = [4, 2]
        self.view_value_theta = False
        self.pos_value_theta = [0, 0]
        # psi:
        self.view_psi = True
        self.pos_psi = [5, 2]   
        self.view_value_psi = False
        self.pos_value_psi = [0, 0]
        # unused1:
        self.view_unused1_id7 = False
        self.pos_unused1_id7 = [0, 0]
        self.view_value_unused1_id7 = False
        self.pos_value_unused1_id7 = [0, 0]
        # unused2:
        self.view_unused2_id7 = False
        self.pos_unused2_id7 = [0, 0]
        self.view_value_unused2_id7 = False
        self.pos_value_unused2_id7 = [0, 0]
        # unused3:
        self.view_unused3_id7 = False
        self.pos_unused3_id7 = [0, 0]
        self.view_value_unused3_id7 = False
        self.pos_value_unused3_id7 = [0, 0]
        # unused4:
        self.view_unused4_id7 = False
        self.pos_unused4_id7 = [0, 0]   
        self.view_value_unused4_id7 = False
        self.pos_value_unused4_id7 = [0, 0]
        # unused5:
        self.view_unused5_id7 = False
        self.pos_unused5_id7 = [0, 0] 
        self.view_value_unused5_id7 = False
        self.pos_value_unused5_id7 = [0, 0]
        # unused6:
        self.view_unused6_id7 = False
        self.pos_unused6_id7 = [0, 0] 
        self.view_value_unused6_id7 = False
        self.pos_value_unused6_id7 = [0, 0]

        graphpos_ID7 = [self.pos_phi, self.pos_theta, self.pos_psi, self.pos_unused1_id7,
                        self.pos_unused2_id7, self.pos_unused3_id7, self.pos_unused4_id7,
                        self.pos_unused5_id7, self.pos_unused6_id7]
        graphview_ID7 = [self.view_phi, self.view_theta, self.view_psi, self.view_unused1_id7,
                         self.view_unused2_id7, self.view_unused3_id7, self.view_unused4_id7,
                         self.view_unused5_id7, self.view_unused6_id7]
        valueview_ID7 = [self.view_value_phi, self.view_value_theta, self.view_value_psi, self.view_value_unused1_id7,
                         self.view_value_unused2_id7, self.view_value_unused3_id7, self.view_value_unused4_id7,
                         self.view_value_unused5_id7, self.view_value_unused6_id7]
        valuepos_ID7 = [self.pos_value_phi, self.pos_value_theta, self.pos_value_psi, self.pos_value_unused1_id7,
                         self.pos_value_unused2_id7, self.pos_value_unused3_id7, self.pos_value_unused4_id7,
                         self.pos_value_unused5_id7, self.pos_value_unused6_id7]
        graphname_ID7 = self.Datenstruktur(7)[0][2:len(self.Datenstruktur(7)[0])-1]

        # Auswahl der anzuzeigenden Graphen:
        for i in range(len(graphview_ID7)):
            if graphview_ID7[i] and not graphpos_ID7[i] == [0, 0]:
                widget_name = f"graph_7_{i+1}_widget"
                widget = GraphErstellen(graphname_ID7[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, graphpos_ID7[i][0], graphpos_ID7[i][1])
            if valueview_ID7[i]:
                widget_name = f"wertanzeige_7_{i+1}_widget"
                widget = WertAnzeigen(graphname_ID7[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, valuepos_ID7[i][0], valuepos_ID7[i][1])


        # ID8 - Kalman Matrix Packet
        # P11:
        self.view_P11 = False
        self.pos_P11 = [0, 0]
        self.view_value_P11 = False
        self.pos_value_P11 = [0, 0]
        # P22:
        self.view_P22 = False
        self.pos_P22 = [0, 0] 
        self.view_value_P22 = False
        self.pos_value_P22 = [0, 0]
        # P33:
        self.view_P33 = False
        self.pos_P33 = [0, 0] 
        self.view_value_P33 = False
        self.pos_value_P33 = [0, 0]
        # EKF2_Height:
        self.view_EKF2_Height = False
        self.pos_EKF2_Height = [0, 0] 
        self.view_value_EKF2_Height = False
        self.pos_value_EKF2_Height = [0, 0]
        # EKF2_vel:
        self.view_EKF2_vel = False
        self.pos_EKF2_vel = [0, 0] 
        self.view_value_EKF2_vel = False
        self.pos_value_EKF2_vel = [0, 0]
        # EKF2_refPres:
        self.view_EKF2_refPres = False
        self.pos_EKF2_refPres = [0, 0] 
        self.view_value_EKF2_refPres = False
        self.pos_value_EKF2_refPres = [0, 0]
        # unused1:
        self.view_unused1_id8 = False
        self.pos_unused1_id8 = [0, 0] 
        self.view_value_unused1_id8 = False
        self.pos_value_unused1_id8 = [0, 0]

        graphpos_ID8 = [self.pos_P11, self.pos_P22, self.pos_P33, self.pos_EKF2_Height,
                        self.pos_EKF2_vel, self.pos_EKF2_refPres, self.pos_unused1_id8]
        graphview_ID8 = [self.view_P11, self.view_P22, self.view_P33, self.view_EKF2_Height,
                         self.view_EKF2_vel, self.view_EKF2_refPres, self.view_unused1_id8]
        valueview_ID8 = [self.view_value_P11, self.view_value_P22, self.view_value_P33, self.view_value_EKF2_Height,
                         self.view_value_EKF2_vel, self.view_value_EKF2_refPres, self.view_value_unused1_id8]
        valuepos_ID8 = [self.pos_value_P11, self.pos_value_P22, self.pos_value_P33, self.pos_value_EKF2_Height,
                         self.pos_value_EKF2_vel, self.pos_value_EKF2_refPres, self.pos_value_unused1_id8]
        graphname_ID8 = self.Datenstruktur(8)[0][2:len(self.Datenstruktur(8)[0])-1]

        # Auswahl der anzuzeigenden Graphen:
        for i in range(len(graphview_ID8)):
            if graphview_ID8[i] and not graphpos_ID8[i] == [0, 0]:
                widget_name = f"graph_8_{i+1}_widget"
                widget = GraphErstellen(graphname_ID8[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, graphpos_ID8[i][0], graphpos_ID8[i][1])
            if valueview_ID8[i]:
                widget_name = f"wertanzeige_8_{i+1}_widget"
                widget = WertAnzeigen(graphname_ID8[i])
                setattr(self, widget_name, widget)

                self.layout.addWidget(widget, valuepos_ID8[i][0], valuepos_ID8[i][1])

    def Datenstruktur(self, id):
        # Struktur der Daten:
        # ID 1 - Status Packet
        # ID 2 - Power Packet
        # ID 3 - GPS Packet
        # ID 4 - IMU Packet
        # ID 5 - Temperature Packet
        # ID 6 - Position Packet
        # ID 7 - Attitude Packet
        # ID 8 - Kalman Matrix Packet
        
        # INDEXING: in plotwith beschreibt eine etwaige Zahl immer die y-Daten, mit denen geplottet
        #           werden soll. Der Index 1 beschreibt dabei "Time", (bsp.) 2 beschreibt "Status Flags" etc.
        # ACHTUNG: Immer die Indexe von Daten aus dem gleichen Datenpaket verwenden!


        if id == 1:
            struktur = ["ID", "Time", "Status flags", "Sensor status flags", "State"]
            scaling = [    1,   1e-3,              1,                     1,       1]
            unit = [   ""   ,    "s",             "",                    "",      ""]
            plotwith = [   1,      1,              1,                     1,       1]
        if id == 2:
            struktur = ["ID", "Time", "M1_5V_bus", "M1_BAT_bus", "unused1", "M2_bus_5V", "M2_bus_GPA_bat", "unused2", "PU_pow", "PU_curr", "PU_bat_bus", "unused3"]
            scaling = [    1,   1e-3,        1e-3,         1e-3,         1,        1e-3,             1e-3,         1,     1e-3,      1e-3,         1e-3,         1]
            unit = [      "",    "s",         "V",          "V",        "",         "V",              "V",        "",      "W",       "A",          "V",        ""]
            plotwith = [   1,      1,           1,            1,         1,           1,                1,         1,        1,         1,            1,         1]
        if id == 3:
            struktur = ["ID", "Time", "latitude", "longitude", "altitude", "speed", "course", "unused1", "unused2", "unused3", "unused4", "unused5"]
            scaling = [    1,   1e-3,       1e-7,        1e-7,          1,       1,     1e-5,         1,         1,         1,         1,         1]
            unit = [      "",    "s",        "°",         "°",       "mm",  "cm/s",      "°",        "",        "",        "",        "",        ""]
            plotwith = [   1,      1,          1,           1,          1,       1,        1,         1,         1,         1,         1,         1]
        if id == 4:
            struktur = ["ID", "Time", "IMU1_x_accel", "IMU1_y_accel", "IMU1_z_accel", "IMU1_x_gyro", "IMU1_y_gyro", "IMU1_z_gyro", "magX", "magY", "magZ", "unused"]
            scaling = [    1,   1e-3,           1e-6,           1e-6,           1e-6,          1e-6,          1e-6,          1e-6,   1e-4,   1e-4,   1e-4,        1]
            unit = [      "",    "s",        "m/s^2",        "m/s^2",        "m/s^2",            "",            "",            "",     "",     "",     "",       ""]
            plotwith = [   1,      1,              1,              1,              1,             1,             1,             1,      1,      1,      1,        1] 
        if id == 5:
            struktur = ["ID", "Time", "M1_DTS", "M1_ADC", "M1_BMP", "M1_IMU1", "M1_IMU2", "M1_MAG", "M2_3V3", "M2_XBee", "PU_Bat", "Pressure", "unused1", "unused2"]
            scaling = [    1,   1e-3,     1e-2,     1e-2,     1e-2,      1e-2,      1e-2,     1e-2,     1e-2,      1e-2,     1e-2,          1,         1,         1]
            unit = [      "",    "s",     "°C",     "°C",     "°C",      "°C",      "°C",     "°C",     "°C",      "°C",     "°C",       "Pa",        "",        ""]
            plotwith = [   1,      1,        1,        1,        1,         1,         1,        1,        1,         1,        1,          1,         1,         1]
        if id == 6:
            struktur = ["ID", "Time", "posX", "posY", "posZ", "velX", "velY", "velZ", "unused1"]
            scaling = [    1,   1e-3,   1e-3,   1e-3,   1e-3,   1e-3,   1e-6,   1e-6,         1]
            unit = [      "",    "s",    "m",    "m",    "m",  "m/s",  "m/s",  "m/s",        ""]
            plotwith = [   1,      1,      1,      1,      1,      1,      1,      1,         1]
        if id == 7:
            struktur = ["ID", "Time", "phi", "theta", "psi", "unused1", "unused2", "unused3", "unused4", "unused5", "unused6"]
            scaling = [    1,   1e-3,     1,    1e-6,  1e-6,         1,         1,         1,         1,         1,         1]
            unit = [      "",    "s",   "°",     "°",   "°",        "",        "",        "",        "",        "",        ""]
            plotwith = [   1,      1,     1,       1,     1,         1,         1,         1,         1,         1,         1]
        if id == 8:
            struktur = ["ID", "Time", "P11",  "P22", "P33", "EKF2_Height", "EKF2_vel", "EKF2_refPres", "unused1"]
            scaling = [    1,   1e-3,     1,      1,     1,             1,          1,              1,         1]
            unit = [      "", "Time",  "m²","m²/s²", "Pa²",           "m",      "m/s",           "Pa",         1]
            plotwith = [   1,      1,     1,      1,     1,             1,          1,              1,         1]
        return struktur, scaling, unit, plotwith

    def setData(self, x, y, **kwargs):
        pen = pg.mkPen(**kwargs)
        self.curve.setPen(pen)
        self.curve.setData(x, y)  

def main():
    app = QtWidgets.QApplication([])
    window = FlightDataWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

