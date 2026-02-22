import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATHMO DataVisualizer")
        self.setWindowIcon(QtGui.QIcon("Logo_A.png"))
        self.xyposition_widget()

    def xyposition_widget(self):
        layout = QtWidgets.QVBoxLayout()
        xyposition_widget = QtWidgets.QWidget()

        self.setCentralWidget(xyposition_widget)
        xyposition_widget.setLayout(layout)

        xyposition_widget.figure = matplotlib.figure.Figure()
        self.canvas = FigureCanvas(xyposition_widget.figure)
        layout.addWidget(self.canvas)

        self.plot_position()

        

    def plot_position(self):
        #ax = self.canvas.figure.add_subplot(111)
        #ax.clear()
        #ax.set_title("Position über Grund")
        #ax.set_xlabel("x")
        #ax.set_ylabel("y")
        #ax.plot([1, 2, 3], [4, 5, 6], label="Sample Data")
        # ax.legend()
        self.canvas.draw()

        

        

def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




if __name__ == "__main__":
    main()


