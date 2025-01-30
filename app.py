import analyzer
from PyQt5 import QtWidgets, QtCore, QtGui
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainScrollArea = QtWidgets.QScrollArea()
        self.mainScrollArea.setWidgetResizable(True)
        self.mainWidget = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addStretch()
        self.mainWidget.setLayout(self.mainLayout)
        self.mainScrollArea.setWidget(self.mainWidget)
        self.setCentralWidget(self.mainScrollArea)
        self.dataFrame = analyzer.getDataFrame("localhost", "root", "orfscouting789", "scouting_database", "default")
        teams = analyzer.getAllTeams(self.dataFrame)
        for team in teams:
            self.addTeam(team)
        self.show()

    def addTeam(self, teamNumber):
        teamLabel = QtWidgets.QLabel(text=f"{teamNumber} - {analyzer.getTotalRobotStops(self.dataFrame, teamNumber)} - {analyzer.getStopDetails(self.dataFrame, teamNumber)}")
        self.mainLayout.insertWidget(self.mainLayout.count() - 1, teamLabel)

app = QtWidgets.QApplication(sys.argv)
mainWindow = MainWindow()
app.exec()