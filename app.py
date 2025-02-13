import analyzer
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import json

class TeamLabel(QtWidgets.QWidget):
    def __init__(self, teamNumber, robotStops, parent=None):
        super().__init__(parent)
        self.teamNumber = teamNumber
        self.setMinimumHeight(50)
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)
        if any(i != 0 for i in robotStops[0]) or any(i != 0 for i in robotStops[1]):
            self.teamNumberLabel = QtWidgets.QLabel(text=f"{self.teamNumber}: ({", ".join(map(str, robotStops[0]))}) robot stops; ({", ".join(map(str, robotStops[1]))}) robot injures")
        else:
            self.teamNumberLabel = QtWidgets.QLabel(text=f"{self.teamNumber}")
        self.mainLayout.addWidget(self.teamNumberLabel, stretch=1)
        self.viewStopDetaisButton = QtWidgets.QPushButton(text="View timeline")
        self.viewStopDetaisButton.clicked.connect(self.showStopDetails)
        if any(i != 0 for i in robotStops[0]) or any(i != 0 for i in robotStops[1]):
            self.mainLayout.addWidget(self.viewStopDetaisButton)

    def showStopDetails(self):
        mainWindow.showStopDetailsDialog(self.teamNumber)

class KeySlider(QtWidgets.QWidget):
    def __init__(self, key, parent=None):
        super().__init__(parent)
        self.key = key
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.upperWidget = QtWidgets.QWidget()
        self.upperLayout = QtWidgets.QHBoxLayout()
        self.upperWidget.setLayout(self.upperLayout)
        self.keyLabel = QtWidgets.QLabel(text=f"{self.key}: 0.0")
        self.upperLayout.addWidget(self.keyLabel, stretch=1)
        self.typeCombobox = QtWidgets.QComboBox()
        self.typeCombobox.addItems(["Total", "Mean", "Mean (Q1 minimum)", "Max"])
        self.upperLayout.addWidget(self.typeCombobox)
        self.mainLayout.addWidget(self.upperWidget)
        self.slider = QtWidgets.QSlider(orientation=QtCore.Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.valueChanged)
        self.slider.setMinimum(-100)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.mainLayout.addWidget(self.slider)
    
    def valueChanged(self):
        self.keyLabel.setText(f"{self.key}: {self.slider.value() / 100}")

    def getValues(self):
        return [self.key, [self.typeCombobox.currentIndex(), self.slider.value()]]

class StopDetailsDialog(QtWidgets.QDialog):
    def __init__(self, teamNumber, data, parent=None):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainTable = QtWidgets.QTableWidget()
        self.mainTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.mainTable.setColumnCount(len(data[0]))
        self.mainTable.setRowCount(len(data) - 1)
        self.mainTable.setHorizontalHeaderLabels(data[0])
        for row in range(1, len(data)):
            for column in range(len(data[row])):
                self.mainTable.setItem(row - 1, column, QtWidgets.QTableWidgetItem(str(data[row][column])))
        self.mainLayout.addWidget(self.mainTable, stretch=1)
        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.mainLayout.addWidget(self.buttonBox)
        self.setWindowModality(True)
        self.setWindowTitle(f"{teamNumber}'s Robot Stops and Injures")
        self.setMinimumSize(500, 300)
        self.show()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainWidget = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.rightWidget = QtWidgets.QWidget()
        self.rightLayout = QtWidgets.QVBoxLayout()
        self.rightWidget.setLayout(self.rightLayout)
        self.sliderListScrollArea = QtWidgets.QScrollArea()
        self.sliderListScrollArea.setWidgetResizable(True)
        self.sliderListWidget = QtWidgets.QWidget()
        self.sliderListLayout = QtWidgets.QVBoxLayout()
        self.sliderListLayout.addStretch()
        self.sliderListWidget.setLayout(self.sliderListLayout)
        self.sliderListScrollArea.setWidget(self.sliderListWidget)
        self.rightLayout.addWidget(self.sliderListScrollArea, stretch=1)
        self.updateSlidersButton = QtWidgets.QPushButton(text="Update rankings")
        self.updateSlidersButton.clicked.connect(self.updateTeamScores)
        self.rightLayout.addWidget(self.updateSlidersButton)
        self.mainLayout.addWidget(self.rightWidget)
        self.teamListScrollArea = QtWidgets.QScrollArea()
        self.teamListScrollArea.setWidgetResizable(True)
        self.teamListWidget = QtWidgets.QWidget()
        self.teamListLayout = QtWidgets.QVBoxLayout()
        self.teamListLayout.addStretch()
        self.teamListWidget.setLayout(self.teamListLayout)
        self.teamListScrollArea.setWidget(self.teamListWidget)
        self.mainLayout.addWidget(self.teamListScrollArea)
        self.setMinimumSize(1000, 500)
        self.show()
        file = open("config.json", "r")
        config = json.loads(file.read())
        file.close()
        databaseSucessful = False
        if config["useDatabase"] == True:
            try:
                self.dataFrame = analyzer.getDataFrameFromDatabase(config["databaseInfo"]["host"], config["databaseInfo"]["user"], config["databaseInfo"]["password"], config["databaseInfo"]["database"], config["databaseInfo"]["table"])
            except:
                result = QtWidgets.QMessageBox.critical(self,  "Cannot Connect to Database", "A database connection cannot be established. Do you want to use a CSV file instead?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if result != QtWidgets.QMessageBox.Yes:
                    sys.exit()
            else:
                databaseSucessful = True
        if not databaseSucessful:
            filePath = QtWidgets.QFileDialog.getOpenFileName(self, filter="CSV files (*.csv)")[0]
            if filePath != "":
                self.dataFrame = analyzer.getDataFrameFromCSV(filePath)
            else:
                sys.exit()
        sliders = analyzer.getColumnsForZScore(self.dataFrame)
        for slider in sliders:
            self.addSlider(slider)
        self.updateTeamScores()
        
    def addTeam(self, teamNumber):
        teamLabel = TeamLabel(teamNumber, analyzer.getTotalRobotStopsForEachType(self.dataFrame, teamNumber))
        self.teamListLayout.insertWidget(self.teamListLayout.count() - 1, teamLabel)

    def showStopDetailsDialog(self, teamNumber):
        data = analyzer.getStopDetails(self.dataFrame, teamNumber)
        dialog = StopDetailsDialog(teamNumber, data, self)
        dialog.exec()

    def addSlider(self, key):
        keySlider = KeySlider(key)
        self.sliderListLayout.insertWidget(self.sliderListLayout.count() - 1, keySlider)

    def updateTeamScores(self):
        sliderValues = {}
        for i in range(self.sliderListLayout.count()):
            if type(self.sliderListLayout.itemAt(i).widget()) == KeySlider:
                values = self.sliderListLayout.itemAt(i).widget().getValues()
                sliderValues[values[0]] = values[1]
        for i in reversed(range(self.teamListLayout.count())):
            if type(self.teamListLayout.itemAt(i).widget()) == TeamLabel:
                self.teamListLayout.removeWidget(self.teamListLayout.itemAt(i).widget())
        zScores = analyzer.rankTeamsByZScore(self.dataFrame, sliderValues)
        for zScore in zScores:
            self.addTeam(zScore[0])

app = QtWidgets.QApplication(sys.argv)
mainWindow = MainWindow()
app.exec()