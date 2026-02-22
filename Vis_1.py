import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATHMO DataVisualizer")
        self.setWindowIcon(QtGui.QIcon("Logo_A.png"))
        self.initUI()

        """""
        label = QtWidgets.QLabel("Dieses Programm dient zur Visualisierung der Flugdaten für ATHMO/ Aurora.\nEs befindet sich derzeit in der Erprobungsphase.", self)
        label.setFont(QtGui.QFont("Arial", 12))
        label.setGeometry(0, 0, 1000, 120)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        """""

    def initUI(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        label1 = QtWidgets.QLabel("Willkommen im ATHMO DataVisualizer!", self)
        label2 = QtWidgets.QLabel("Hier können Sie Ihre Flugdaten visualisieren.", self)
        label3 = QtWidgets.QLabel("Bitte wählen Sie einen Input aus, um fortzufahren.", self)
        label4 = QtWidgets.QLabel("ATHMO DataVisualizer", self)
        label1.setStyleSheet("background-color: black; color: white; font-size: 20px;")
        label2.setStyleSheet("background-color: blue; color: white; font-size: 20px;")
        label3.setStyleSheet("background-color: red; color: white; font-size: 20px;")
        label4.setStyleSheet("background-color: green; color: white; font-size: 20px;")

        verticalbox = QtWidgets.QVBoxLayout()
        verticalbox.addWidget(label1)
        verticalbox.addWidget(label2)
        verticalbox.addWidget(label3)
        verticalbox.addWidget(label4)
        central_widget.setLayout(verticalbox)

def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



    print("fertig!!")



if __name__ == "__main__":
    main()


