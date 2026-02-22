import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class GraphErstellen(QtWidgets.QWidget):
    def __init__(self, title):
        super().__init__()
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.set_title(title)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self, x, y, **kwargs):
        self.ax.plot(x, y, **kwargs)
        self.canvas.draw()



class WertAnzeigen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def update_value(self, variable_name, value=0, unit="g"):
        self.label.setText(f"{variable_name}:\n{value}{unit}")




class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATHMO DataVisualizer")
        self.setWindowIcon(QtGui.QIcon("Logo_A.png"))
        
        main_widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()

        # Erstellen der Graphen
        self.xyposition_widget = GraphErstellen("Position über Grund")
        self.zposition_widget = GraphErstellen("Höhe über Grund")
        self.v_unendlich_widget = GraphErstellen("Geschwindigkeit der Anströmung")
        self.Mach_widget = GraphErstellen("Machzahl der Anströmung")
        self.v_uebergrund_widget = GraphErstellen("Geschwindigkeit über Grund")

        # Hinzufügen der Graphen zum Layout
        layout.addWidget(self.xyposition_widget, 0, 0)
        layout.addWidget(self.zposition_widget, 1, 0)
        layout.addWidget(self.v_unendlich_widget, 0, 1)
        layout.addWidget(self.Mach_widget, 1, 1)
        layout.addWidget(self.v_uebergrund_widget, 2, 1)

        # Erstellen der WertAnzeigen Widgets
        self.gforce_widget = WertAnzeigen()
        self.gforcemax_widget = WertAnzeigen()

        # Formatieren der WertAnzeigen Widgets
        general_format = "font-size: 16px; border: 1px solid black; padding: 5px; background-color: rgba(94,174,163,0.7);"
        self.gforce_widget.setStyleSheet(general_format)
        self.gforcemax_widget.setStyleSheet(general_format)

        # Hinzufügen der WertAnzeigen Widgets zum Layout
        layout.addWidget(self.gforce_widget, 3, 0)
        layout.addWidget(self.gforcemax_widget, 4, 0)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        self.GraphPlotten()
        self.gforce_widget.update_value("g-Kraft", "0.0", "g")
        self.gforcemax_widget.update_value("max g-Kraft", "0.0", "g")

    def GraphPlotten(self):
        # Example data for plotting
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        y3 = np.tan(x)
        y4 = np.exp(-x)
        y5 = np.log(x + 1)

        self.xyposition_widget.plot(x, y1, label="Sinus")
        self.zposition_widget.plot(x, y2, label="Cosinus")
        self.v_unendlich_widget.plot(x, y3, label="Tangens")
        self.Mach_widget.plot(x, y4, label="Exponential")
        self.v_uebergrund_widget.plot(x, y5, label="Logarithmisch")





def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




if __name__ == "__main__":
    main()


