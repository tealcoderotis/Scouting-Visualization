import analyzer
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import json
from os import path

class TeamLabel(QtWidgets.QWidget):
    def __init__(self, teamNumber, zScore, robotStops, parent=None):
        super().__init__(parent)
        self.teamNumber = teamNumber
        self.zScore = zScore
        self.setMinimumHeight(50)
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setLayout(self.mainLayout)
        if any(i != 0 for i in robotStops[0]) or any(i != 0 for i in robotStops[1]) or robotStops[2] != 0 or robotStops[3] != 0:
            self.teamNumberLabel = QtWidgets.QLabel(text=f"{self.teamNumber}; {zScore} z-score; ({', '.join(map(str, robotStops[0]))}) robot stops; ({', '.join(map(str, robotStops[1]))}) robot injures; {robotStops[3]} defense matches; {robotStops[2]} no shows")
        else:
            self.teamNumberLabel = QtWidgets.QLabel(text=f"{self.teamNumber}; {zScore} z-score")
        self.mainLayout.addWidget(self.teamNumberLabel, stretch=1)
        self.viewStopDetaisButton = QtWidgets.QPushButton(text="View timeline")
        self.viewStopDetaisButton.clicked.connect(self.showStopDetails)
        if any(i != 0 for i in robotStops[0]) or any(i != 0 for i in robotStops[1]) or robotStops[2] != 0 or robotStops[3] != 0:
            self.mainLayout.addWidget(self.viewStopDetaisButton)

    def showStopDetails(self):
        mainWindow.showStopDetailsDialog(self.teamNumber)

class UnscrollableComboBox(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def wheelEvent(self, *args, **kwargs):
        pass

class UnscrollableSlider(QtWidgets.QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def wheelEvent(self, *args, **kwargs):
        pass

class KeySlider(QtWidgets.QWidget):
    def __init__(self, key, comboBoxAvaliable=True, parent=None):
        super().__init__(parent)
        self.key = key
        self.filterCode = ""
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.upperWidget = QtWidgets.QWidget()
        self.upperLayout = QtWidgets.QHBoxLayout()
        self.upperWidget.setLayout(self.upperLayout)
        self.keyLabel = QtWidgets.QLabel(text=self.key)
        self.upperLayout.addWidget(self.keyLabel, stretch=1)
        self.valueInput = QtWidgets.QLineEdit()
        self.valueInput.setFixedWidth(50)
        self.valueInput.setText("0.0")
        self.valueInput.textEdited.connect(self.textInputValueChanged)
        self.upperLayout.addWidget(self.valueInput)
        self.typeCombobox = UnscrollableComboBox()
        self.typeCombobox.addItems(["Total", "Mean", "Median", "Mode", "Max"])
        if comboBoxAvaliable:
            self.upperLayout.addWidget(self.typeCombobox)
        self.mainLayout.addWidget(self.upperWidget)
        self.checkBoxWidget = QtWidgets.QWidget()
        self.checkBoxLayout = QtWidgets.QHBoxLayout()
        self.checkBoxLayout.addStretch()
        self.ignoreNoShowsCheckbox = QtWidgets.QCheckBox(text="Ignore no shows")
        self.checkBoxLayout.addWidget(self.ignoreNoShowsCheckbox)
        self.ignoreStopsAndInjuresCheckbox = QtWidgets.QCheckBox(text="Ignore stops and injures")
        self.checkBoxLayout.addWidget(self.ignoreStopsAndInjuresCheckbox)
        self.q1MinimumCheckBox = QtWidgets.QCheckBox(text="Q1 Minimum")
        self.q3MaximumCheckBox = QtWidgets.QCheckBox(text="Q3 Maximum")
        if comboBoxAvaliable:
            self.checkBoxLayout.addWidget(self.q1MinimumCheckBox)
            self.checkBoxLayout.addWidget(self.q3MaximumCheckBox)
        self.checkBoxWidget.setLayout(self.checkBoxLayout)
        self.mainLayout.addWidget(self.checkBoxWidget)
        self.filterWidget = QtWidgets.QWidget()
        self.filterLayout = QtWidgets.QHBoxLayout()
        self.filterLayout.addStretch()
        self.filterTypeComboBox = UnscrollableComboBox()
        self.filterTypeComboBox.addItems(["No filter", "=", "!=", ">", "<", ">=", "<=", "Custom"])
        self.filterTypeComboBox.currentIndexChanged.connect(lambda: self.updateFilterIndex())
        self.filterLayout.addWidget(self.filterTypeComboBox)
        self.filterValueInput = QtWidgets.QLineEdit(text="0.0")
        self.filterValueInput.setEnabled(False)
        self.filterValueInput.setFixedWidth(50)
        self.filterLayout.addWidget(self.filterValueInput)
        self.editCodeButton = QtWidgets.QPushButton(text="Edit code")
        self.editCodeButton.clicked.connect(self.editCode)
        self.filterLayout.addWidget(self.editCodeButton)
        self.filterWidget.setLayout(self.filterLayout)
        self.mainLayout.addWidget(self.filterWidget)
        self.slider = UnscrollableSlider(orientation=QtCore.Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.sliderValueChanged)
        self.slider.setMinimum(-100)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.mainLayout.addWidget(self.slider)
        self.updateFilterIndex()
    
    def sliderValueChanged(self):
        self.valueInput.setText(str(self.slider.value() / 100))

    def textInputValueChanged(self):
        try:
            value = float(self.valueInput.text())
            if value >= -1.0 and value <= 1.0:
                self.slider.valueChanged.disconnect()
                self.slider.setValue(int(value * 100))
                self.slider.valueChanged.connect(self.sliderValueChanged)
        except ValueError:
            pass

    def getValues(self):
        return [self.key, [self.typeCombobox.currentIndex(), self.slider.value() / 100, self.ignoreStopsAndInjuresCheckbox.isChecked(), self.ignoreNoShowsCheckbox.isChecked(), self.q1MinimumCheckBox.isChecked(), self.q3MaximumCheckBox.isChecked()]]
    
    def getFilter(self):
        if self.filterTypeComboBox.currentIndex() == 7:
            return [self.key, [self.filterTypeComboBox.currentIndex(), self.filterCode]]
        else:
            return [self.key, [self.filterTypeComboBox.currentIndex(), float(self.filterValueInput.text())]]
    
    def validateFilterValue(self):
        if not (self.filterTypeComboBox.currentIndex() == 0 or self.filterTypeComboBox.currentIndex() == 7):
            try:
                float(self.filterValueInput.text())
            except:
                return False
            else:
                return True
        else:
            return True
    
    def updateValues(self, valueList):
        self.typeCombobox.setCurrentIndex(valueList[0])
        self.slider.setValue(int(valueList[1] * 100))
        self.ignoreStopsAndInjuresCheckbox.setChecked(valueList[2])
        self.ignoreNoShowsCheckbox.setChecked(valueList[3])
        self.q1MinimumCheckBox.setChecked(valueList[4])
        self.q3MaximumCheckBox.setChecked(valueList[5])

    def updateFilter(self, filterList):
        self.filterTypeComboBox.setCurrentIndex(filterList[0])
        if type(filterList[1]) == float:
            self.filterValueInput.setText(str(filterList[1]))
        else:
            self.filterCode = filterList[1]
            self.filterValueInput.setText("0.0")
        self.updateFilterIndex()
    
    def getKey(self):
        return self.key
    
    def updateFilterIndex(self):
        self.filterValueInput.setEnabled(self.filterTypeComboBox.currentIndex() != 0)
        if self.filterTypeComboBox.currentIndex() == 0:
            self.filterValueInput.setText("0.0")
        if self.filterTypeComboBox.currentIndex() == 7:
            self.filterValueInput.setHidden(True)
            self.editCodeButton.setHidden(False)
        else:
            self.editCodeButton.setHidden(True)
            self.filterValueInput.setHidden(False)

    def editCode(self):
        dialog = CodeDialog(self.filterCode, self)
        if dialog.exec() == 1:
            self.filterCode = dialog.code
    
class StopViewerDialog(QtWidgets.QDialog):
    def __init__(self, data, title, parent=None):
        super().__init__(parent)
        self.data = data
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainTable = QtWidgets.QTableWidget()
        self.mainTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.mainLayout.addWidget(self.mainTable, stretch=1)
        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.mainLayout.addWidget(self.buttonBox)
        self.setWindowTitle(title)
        self.setMinimumSize(500, 300)
        self.show()
        self.addData()

    def addData(self):
        self.mainTable.setColumnCount(len(self.data[0]))
        self.mainTable.setRowCount(len(self.data) - 1)
        self.mainTable.setHorizontalHeaderLabels(self.data[0])
        for row in range(1, len(self.data)):
            for column in range(len(self.data[row])):
                self.mainTable.setItem(row - 1, column, QtWidgets.QTableWidgetItem(str(self.data[row][column])))

class DataViewerDialog(QtWidgets.QDialog):
    def __init__(self, dataFrame, title, comboBoxItems, matchFilters, teamFilters, parent=None):
        super().__init__(parent)
        self.dataFrame = dataFrame
        self.matchFilters = matchFilters
        self.teamFilters = teamFilters
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.dataComboBox = QtWidgets.QComboBox()
        self.dataComboBox.addItems(comboBoxItems)
        self.dataComboBox.currentIndexChanged.connect(lambda: self.addData())
        self.mainLayout.addWidget(self.dataComboBox)
        self.ignoreNoShowsCheckBox = QtWidgets.QCheckBox(text="Ignore no shows")
        self.ignoreNoShowsCheckBox.clicked.connect(lambda: self.addData())
        self.mainLayout.addWidget(self.ignoreNoShowsCheckBox)
        self.ignoreStopsCheckBox = QtWidgets.QCheckBox(text="Ignore stops and injues")
        self.ignoreStopsCheckBox.clicked.connect(lambda: self.addData())
        self.mainLayout.addWidget(self.ignoreStopsCheckBox)
        self.q1MinimumCheckBox = QtWidgets.QCheckBox(text="Q1 Minimum")
        self.q1MinimumCheckBox.clicked.connect(lambda: self.addData())
        self.mainLayout.addWidget(self.q1MinimumCheckBox)
        self.q3MaximumCheckBox = QtWidgets.QCheckBox(text="Q3 Maximum")
        self.q3MaximumCheckBox.clicked.connect(lambda: self.addData())
        self.mainLayout.addWidget(self.q3MaximumCheckBox)
        self.mainTable = QtWidgets.QTableWidget()
        self.mainTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.mainLayout.addWidget(self.mainTable, stretch=1)
        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.mainLayout.addWidget(self.buttonBox)
        self.setWindowTitle(title)
        self.setMinimumSize(500, 300)
        self.show()
        self.addData()

    def addData(self):
        dataFrame = self.dataFrame
        if self.ignoreNoShowsCheckBox.isChecked():
            dataFrame = analyzer.getDataFrameWithoutNoShows(dataFrame)
        if self.ignoreStopsCheckBox.isChecked():
            dataFrame = analyzer.getDataFrameWithoutRobotStops(dataFrame)
        try:
            data = analyzer.dataFrameToList(analyzer.getData(dataFrame, self.dataComboBox.currentIndex(), self.matchFilters, self.teamFilters, self.q1MinimumCheckBox.isChecked(), self.q3MaximumCheckBox.isChecked()))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
        else:
            for i in reversed(range(self.mainTable.rowCount())):
                self.mainTable.removeRow(i)
            self.mainTable.setColumnCount(len(data[0]))
            self.mainTable.setRowCount(len(data) - 1)
            self.mainTable.setHorizontalHeaderLabels(data[0])
            for row in range(1, len(data)):
                for column in range(len(data[row])):
                    self.mainTable.setItem(row - 1, column, QtWidgets.QTableWidgetItem(str(data[row][column])))

class FilterPoint(QtWidgets.QWidget):
    def __init__(self, column, filterList=[0, 0.0], dataType="number", parent=None):
        super().__init__(parent)
        self.column = column
        self.dataType = dataType
        if type(filterList[1]) == str and (filterList[0] == 3 or filterList[0] == 7):
            self.filterCode = filterList[1]
        else:
            self.filterCode = ""
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.columnLabel = QtWidgets.QLabel(text=self.column)
        self.mainLayout.addWidget(self.columnLabel, stretch=1)
        self.filterTypeComboBox = UnscrollableComboBox()
        if self.dataType == "number":
            self.filterTypeComboBox.addItems(["No filter", "=", "!=", ">", "<", ">=", "<=", "Custom"])
        else:
            self.filterTypeComboBox.addItems(["No filter", "=", "!=", "Custom"])
        self.filterTypeComboBox.setCurrentIndex(filterList[0])
        self.filterTypeComboBox.currentIndexChanged.connect(lambda: self.updateIndex())
        self.mainLayout.addWidget(self.filterTypeComboBox)
        self.filterValueInput = QtWidgets.QLineEdit()
        if self.dataType == "number":
            self.filterValueInput.setFixedWidth(50)
        else:
            self.filterValueInput.setFixedWidth(100)
        if not self.isInCodeMode():
            self.filterValueInput.setText(str(filterList[1]))
        else:
            self.filterValueInput.setText("0.0")
        self.mainLayout.addWidget(self.filterValueInput)
        self.filterBooleanComboBox = QtWidgets.QComboBox()
        self.filterBooleanComboBox.addItems(["False", "True"])
        self.filterBooleanComboBox.setFixedWidth(100)
        if not self.isInCodeMode() and self.dataType == "boolean":
            self.filterBooleanComboBox.setCurrentIndex(int(filterList[1]))
        self.mainLayout.addWidget(self.filterBooleanComboBox)
        self.editCodeButton = QtWidgets.QPushButton(text="Edit code")
        self.editCodeButton.clicked.connect(self.editCode)
        self.mainLayout.addWidget(self.editCodeButton)
        self.setLayout(self.mainLayout)
        self.updateIndex()

    def validateFloat(self):
        if (not (self.filterTypeComboBox.currentIndex() == 0 or self.isInCodeMode())) and self.dataType == "number":
            try:
                float(self.filterValueInput.text())
            except:
                return False
            else:
                return True
        else:
            return True
        
    def updateIndex(self):
        self.filterValueInput.setEnabled(self.filterTypeComboBox.currentIndex() != 0)
        self.filterBooleanComboBox.setEnabled(self.filterTypeComboBox.currentIndex() != 0)
        if self.filterTypeComboBox.currentIndex() == 0:
            self.filterValueInput.setText("0.0")
            self.filterBooleanComboBox.setCurrentIndex(0)
        if self.isInCodeMode():
            self.filterValueInput.setHidden(True)
            self.filterBooleanComboBox.setHidden(True)
            self.editCodeButton.setHidden(False)
        else:
            self.editCodeButton.setHidden(True)
            if self.dataType == "boolean":
                self.filterValueInput.setHidden(True)
                self.filterBooleanComboBox.setHidden(False)
            else:
                self.filterBooleanComboBox.setHidden(True)
                self.filterValueInput.setHidden(False)

    def getFilterList(self):
        if self.isInCodeMode():
            return [self.filterTypeComboBox.currentIndex(), self.filterCode]
        else:
            if self.dataType == "number":
                return [self.filterTypeComboBox.currentIndex(), float(self.filterValueInput.text())]
            elif self.dataType == "boolean":
                return [self.filterTypeComboBox.currentIndex(), bool(self.filterBooleanComboBox.currentIndex())]
            else:
                return [self.filterTypeComboBox.currentIndex(), self.filterValueInput.text()]
        
    def editCode(self):
        dialog = CodeDialog(self.filterCode, self)
        if dialog.exec() == 1:
            self.filterCode = dialog.code

    def isInCodeMode(self):
        if self.dataType == "number" and self.filterTypeComboBox.currentIndex() == 7:
            return True
        elif self.dataType != "number" and self.filterTypeComboBox.currentIndex() == 3:
            return True
        else:
            return False
        
class CodeDialog(QtWidgets.QDialog):
    def __init__(self, currentCode="", parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.setWindowTitle("Python Code")
        self.setMinimumSize(500, 300)
        self.setWindowModality(True)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.codeInput = QtWidgets.QTextEdit()
        self.codeInput.setAcceptRichText(False)
        self.codeInput.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        self.codeInput.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.codeInput.setPlainText(currentCode)
        self.mainLayout.addWidget(self.codeInput)
        self.dialogButtons = QtWidgets.QDialogButtonBox()
        self.dialogButtons.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Open)
        self.dialogButtons.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.dialogButtons.button(QtWidgets.QDialogButtonBox.Open).clicked.connect(self.getScript)
        self.dialogButtons.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.mainLayout.addWidget(self.dialogButtons)
        self.show()
    
    def accept(self):
        self.code = self.codeInput.toPlainText()
        return super().accept()
    
    def getScript(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, filter="Python scripts (*.py)")[0]
        if filePath != "":
            try:
                file = open(filePath, "r")
                self.codeInput.setPlainText(file.read())
                file.close()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", str(e))

class FilterDialog(QtWidgets.QDialog):
    def __init__(self, filterList, dataFrame, parent=None):
        super().__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.filterListScrollArea = QtWidgets.QScrollArea()
        self.filterListScrollArea.setWidgetResizable(True)
        self.filterListWidget = QtWidgets.QWidget()
        self.filterListScrollArea.setWidget(self.filterListWidget)
        self.filterListLayout = QtWidgets.QVBoxLayout()
        self.filterListLayout.addStretch()
        self.filterListWidget.setLayout(self.filterListLayout)
        self.mainLayout.addWidget(self.filterListScrollArea, stretch=1)
        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Edit Match Filters")
        self.setMinimumSize(500, 300)
        self.show()
        for column, value in filterList.items():
            dataType = analyzer.getDataTypeOfColumn(dataFrame, column)
            if dataType == "int64" or dataType == "float64":
                widget = FilterPoint(column, value, "number")
            elif dataType == "bool":
                widget = FilterPoint(column, value, "boolean")
            else:
                widget = FilterPoint(column, value, "string")
            self.filterListLayout.insertWidget(self.filterListLayout.count() - 1, widget)

    def validateFloats(self):
        for i in range(self.filterListLayout.count()):
            if type(self.filterListLayout.itemAt(i).widget()) == FilterPoint:
                if not self.filterListLayout.itemAt(i).widget().validateFloat():
                    return self.filterListLayout.itemAt(i).widget().column
        return True
    
    def accept(self):
        result = self.validateFloats()
        if result == True:
            super().accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"{result} has an invalid value")

    def getFilters(self):
        filter = {}
        for i in range(self.filterListLayout.count()):
            if type(self.filterListLayout.itemAt(i).widget()) == FilterPoint:
                filter[self.filterListLayout.itemAt(i).widget().column] = self.filterListLayout.itemAt(i).widget().getFilterList()
        return filter

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
        self.editFiltersButton = QtWidgets.QPushButton(text="Edit match filters")
        self.editFiltersButton.clicked.connect(self.editFilters)
        self.rightLayout.addWidget(self.editFiltersButton)
        self.viewDataButton = QtWidgets.QPushButton(text="View data")
        self.viewDataButton.clicked.connect(self.showDataViewDialog)
        self.rightLayout.addWidget(self.viewDataButton)
        self.mainLayout.addWidget(self.rightWidget)
        self.teamListScrollArea = QtWidgets.QScrollArea()
        self.teamListScrollArea.setWidgetResizable(True)
        self.teamListWidget = QtWidgets.QWidget()
        self.teamListLayout = QtWidgets.QVBoxLayout()
        self.teamListLayout.addStretch()
        self.teamListWidget.setLayout(self.teamListLayout)
        self.teamListScrollArea.setWidget(self.teamListWidget)
        self.mainLayout.addWidget(self.teamListScrollArea)
        fileMenu = self.menuBar().addMenu("File")
        loadSlidersAction = QtWidgets.QAction("Load sliders", self)
        loadSlidersAction.triggered.connect(self.loadSliders)
        fileMenu.addAction(loadSlidersAction)
        saveSlidersAction = QtWidgets.QAction("Save sliders as", self)
        saveSlidersAction.triggered.connect(self.saveSliders)
        fileMenu.addAction(saveSlidersAction)
        loadFiltersAction = QtWidgets.QAction("Load filters", self)
        loadFiltersAction.triggered.connect(self.loadFilters)
        fileMenu.addAction(loadFiltersAction)
        saveFiltersAction = QtWidgets.QAction("Save filters as", self)
        saveFiltersAction.triggered.connect(self.saveFilters)
        fileMenu.addAction(saveFiltersAction)
        fileMenu.addSeparator()
        exitAction = QtWidgets.QAction("Exit", self)
        exitAction.triggered.connect(sys.exit)
        fileMenu.addAction(exitAction)
        if path.exists("icon.ico"):
            self.setWindowIcon(QtGui.QIcon("icon.ico"))
        elif path.exists("_internal\\icon.ico"):
            self.setWindowIcon(QtGui.QIcon("_internal\\icon.ico"))
        self.setMinimumSize(1200, 600)
        self.setWindowTitle("Scouting Visualization")
        self.showMaximized()
        databaseSucessful = False
        if path.exists("config.json"):
            file = open("config.json", "r")
            config = json.loads(file.read())
            file.close()
            if config["useDatabase"] == True:
                try:
                    self.dataFrame = analyzer.getDataFrameFromDatabase(config["databaseInfo"]["host"], config["databaseInfo"]["user"], config["databaseInfo"]["password"], config["databaseInfo"]["database"], config["databaseInfo"]["table"])
                except Exception as e:
                    result = QtWidgets.QMessageBox.critical(self, "Cannot Connect to Database", f"A database connection cannot be established. Do you want to use a CSV file instead?\n\n{str(e)}", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if result != QtWidgets.QMessageBox.Yes:
                        sys.exit()
                else:
                    databaseSucessful = True
        if not databaseSucessful:
            filePath = QtWidgets.QFileDialog.getOpenFileName(self, filter="CSV files (*.csv)")[0]
            if filePath != "":
                try:
                    self.dataFrame = analyzer.getDataFrameFromCSV(filePath)
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", str(e))
                    sys.exit()
            else:
                sys.exit()
        sliders = analyzer.getColumnsForZScore(self.dataFrame)
        for slider in sliders[0]:
            self.addSlider(slider, slider in sliders[1])
        self.filter = {}
        for column in analyzer.getColumns(self.dataFrame):
            self.filter[column] = [0, 0.0]
        self.updateTeamScores()
        
    def addTeam(self, teamNumber, zScore):
        teamLabel = TeamLabel(teamNumber, zScore, analyzer.getTotalRobotStopsForEachType(self.dataFrame, teamNumber))
        self.teamListLayout.insertWidget(self.teamListLayout.count() - 1, teamLabel)

    def showStopDetailsDialog(self, teamNumber):
        data = analyzer.getStopDetails(self.dataFrame, teamNumber)
        dialog = StopViewerDialog(data, f"{teamNumber}'s Robot Stops, Injures, and No Shows", self)
        dialog.exec()

    def showDataViewDialog(self):
        teamFilters = {}
        for i in range(self.sliderListLayout.count()):
            if type(self.sliderListLayout.itemAt(i).widget()) == KeySlider:
                if self.sliderListLayout.itemAt(i).widget().validateFilterValue():
                    filter = self.sliderListLayout.itemAt(i).widget().getFilter()
                    teamFilters[filter[0]] = filter[1]
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", f"{self.sliderListLayout.itemAt(i).widget().key} has an invalid value")
                    return None
        comboBoxList = ["Total", "Mean", "Median", "Mode", "Max"]
        dialog = DataViewerDialog(self.dataFrame, "Data Viewer", comboBoxList, self.filter, teamFilters, self)
        dialog.exec()

    def addSlider(self, key, isCounted):
        keySlider = KeySlider(key, not isCounted)
        self.sliderListLayout.insertWidget(self.sliderListLayout.count() - 1, keySlider)

    def updateTeamScores(self):
        sliderValues = {}
        teamFilters = {}
        for i in range(self.sliderListLayout.count()):
            if type(self.sliderListLayout.itemAt(i).widget()) == KeySlider:
                values = self.sliderListLayout.itemAt(i).widget().getValues()
                sliderValues[values[0]] = values[1]
                if self.sliderListLayout.itemAt(i).widget().validateFilterValue():
                    filter = self.sliderListLayout.itemAt(i).widget().getFilter()
                    teamFilters[filter[0]] = filter[1]
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", f"{self.sliderListLayout.itemAt(i).widget().key} has an invalid value")
                    return None
        '''try:'''
        zScores = analyzer.rankTeamsByZScore(self.dataFrame, sliderValues, self.filter, teamFilters)
        '''except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
        else:'''
        for i in reversed(range(self.teamListLayout.count())):
            if type(self.teamListLayout.itemAt(i).widget()) == TeamLabel:
                self.teamListLayout.removeWidget(self.teamListLayout.itemAt(i).widget())
        for zScore in zScores:
            self.addTeam(zScore[0], zScore[1])

    def saveSliders(self):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, filter="JSON files (*.json)")[0]
        if filePath != "":
            sliderValues = {}
            for i in range(self.sliderListLayout.count()):
                if type(self.sliderListLayout.itemAt(i).widget()) == KeySlider:
                    values = self.sliderListLayout.itemAt(i).widget().getValues()
                    sliderValues[values[0]] = values[1]
            jsonFile = json.dumps(sliderValues)
            file = open(filePath, "w")
            file.write(jsonFile)
            file.close()

    def loadSliders(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, filter="JSON files (*.json)")[0]
        if filePath != "":
            valueNotInJson = False
            try:
                file = open(filePath, "r")
                jsonFile = json.loads(file.read())
                file.close()
                for i in range(self.sliderListLayout.count()):
                    if type(self.sliderListLayout.itemAt(i).widget()) == KeySlider:
                        slider = self.sliderListLayout.itemAt(i).widget()
                        if slider.getKey() in jsonFile:
                            slider.updateValues(jsonFile[slider.getKey()])
                        else:
                            valueNotInJson = True
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Sliders have been loaded up until the error\n\n{str(e)}")
            if valueNotInJson:
                QtWidgets.QMessageBox.warning(self, "Warning", "One or more slider values is not in the file")

    def editFilters(self):
        dialog = FilterDialog(self.filter, self.dataFrame, self)
        if dialog.exec() == 1:
            self.filter = dialog.getFilters()

    def saveFilters(self):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, filter="JSON files (*.json)")[0]
        if filePath != "":
            teamFilters = {}
            for i in range(self.sliderListLayout.count()):
                if type(self.sliderListLayout.itemAt(i).widget()) == KeySlider:
                    if self.sliderListLayout.itemAt(i).widget().validateFilterValue():
                        filter = self.sliderListLayout.itemAt(i).widget().getFilter()
                        teamFilters[filter[0]] = filter[1]
                    else:
                        QtWidgets.QMessageBox.critical(self, "Error", f"{self.sliderListLayout.itemAt(i).widget().key} has an invalid value")
                        return None
            finalObject = {
                "match": self.filter,
                "team": teamFilters
            }
            jsonFile = json.dumps(finalObject)
            file = open(filePath, "w")
            file.write(jsonFile)
            file.close()

    def loadFilters(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, filter="JSON files (*.json)")[0]
        if filePath != "":
            valueNotInJson = False
            try:
                file = open(filePath, "r")
                jsonFile = json.loads(file.read())
                file.close()
                self.filter = jsonFile["match"]
                teamFilter = jsonFile["team"]
                for i in range(self.sliderListLayout.count()):
                    if type(self.sliderListLayout.itemAt(i).widget()) == KeySlider:
                        slider = self.sliderListLayout.itemAt(i).widget()
                        if slider.getKey() in teamFilter:
                            slider.updateFilter(teamFilter[slider.getKey()])
                        else:
                            valueNotInJson = True

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Filters have been loaded up until the error\n\n{str(e)}")
            if valueNotInJson:
                QtWidgets.QMessageBox.warning(self, "Warning", "One or more filters is not in the file")

app = QtWidgets.QApplication(sys.argv)
app.setStyle(QtWidgets.QStyleFactory.create("fusion"))
palette = QtGui.QPalette()
palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
palette.setColor(QtGui.QPalette.Button, QtGui.QColor(50, 50, 50))
palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button, QtGui.QColor(33, 33, 33))
palette.setColor(QtGui.QPalette.Light, QtGui.QColor(75, 75, 75))
palette.setColor(QtGui.QPalette.Midlight, QtGui.QColor(62, 62, 62))
palette.setColor(QtGui.QPalette.Dark, QtGui.QColor(25, 25, 25))
palette.setColor(QtGui.QPalette.Mid, QtGui.QColor(33, 33, 33))
palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(255, 255, 255, 127))
palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 255, 255))
palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
palette.setColor(QtGui.QPalette.Base, QtGui.QColor(0, 0, 0))
palette.setColor(QtGui.QPalette.Window, QtGui.QColor(50, 50, 50))
palette.setColor(QtGui.QPalette.Shadow, QtGui.QColor(0, 0, 0))
palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(200, 174, 64))
palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(0, 0, 0))
palette.setColor(QtGui.QPalette.Link, QtGui.QColor(200, 174, 64))
palette.setColor(QtGui.QPalette.LinkVisited, QtGui.QColor(200, 174, 64))
palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(25, 25, 25))
palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 220))
palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(0, 0, 0))
palette.setColor(QtGui.QPalette.PlaceholderText, QtGui.QColor(255, 255, 255, 127))
app.setPalette(palette)
mainWindow = MainWindow()
sys.exit(app.exec())