import mysql.connector
import pandas
from io import StringIO

CLIMB_VALUES = ["no_climb", "park_climb", "shallow_climb", "deep_climb"]
ROBOT_STOP_VALUES = ["no_stop", "one_stop", "many_stops", "end_stop"]
ROBOT_INJURE_VALUES = ["no_injure", "fixed_injure", "end_injure"]
VALUE_GROUPS = {
    "auto_coral": ["auto_coral_l1", "auto_coral_l2", "auto_coral_l3", "auto_coral_l4"],
    "tele_coral": ["tele_coral_l1", "tele_coral_l2", "tele_coral_l3", "tele_coral_l4"]
}
NOT_DATA_COLUMNS = ["PRIMARY_KEY", "team_number", "round_number", "timestamp", "scouter_name", "scouting_team"]

def getDatabaseData(host, user, password, database, table):
    db = mysql.connector.connect(host=host, user=user, password=password, buffered=True)
    cursor = db.cursor()
    #cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=\"{table}\" AND TABLE_SCHEMA=\"{database}\";")
    cursor.execute(f"SHOW COLUMNS FROM {database}.{table}")
    columnData = cursor.fetchall()
    columnNames = []
    for i in columnData:
        columnNames.append(i[0])
    cursor.execute(f"SELECT * FROM {database}.{table};")
    db.close()
    tableData = cursor.fetchall()
    return [columnNames, tableData]

def getTextValueFromDropdown(value, dropdownList):
    return dropdownList[value]

def getDataFrameFromDatabase(host, user, password, database, table):
    data = getDatabaseData(host, user, password, database, table)
    dataFrame = pandas.DataFrame(data[1], columns=data[0])
    return dataFrame

def getDataFrameFromCSV(filePath):
    dataFrame = pandas.read_csv(filePath, sep=", ")
    return preprocessDataFrame(dataFrame)

def preprocessDataFrame(dataFrame):
    csv = dataFrame.drop(0).to_csv()
    return pandas.read_csv(StringIO(csv))

def getAllTeams(dataFrame):
    return dataFrame["team_number"].drop_duplicates().to_list()

def getDataFameForTeam(dataFrame, teamNumber):
    return dataFrame[dataFrame["team_number"].values == teamNumber]

def getTotalRobotStopsForEachType(dataFrame, teamNumber):
    teamDataFrame = getDataFameForTeam(dataFrame, teamNumber)
    stopList = []
    for i in range(1, len(ROBOT_STOP_VALUES)):
        robotStops = teamDataFrame.loc[(dataFrame["robot_stop"] == ROBOT_STOP_VALUES[i])].shape[0]
        stopList.append(robotStops)
    injureList = []
    for i in range(1, len(ROBOT_INJURE_VALUES)):
        robotStops = teamDataFrame.loc[(dataFrame["robot_injure"] == ROBOT_INJURE_VALUES[i])].shape[0]
        injureList.append(robotStops)
    return [stopList, injureList]

def getStopDetails(dataFrame, teamNumber):
    teamDataFrame = getDataFameForTeam(dataFrame, teamNumber)
    teamDataFrame = teamDataFrame.sort_values(by=["timestamp"])
    robotStops = teamDataFrame.loc[(dataFrame["robot_stop"] != ROBOT_STOP_VALUES[0]) | (dataFrame["robot_injure"]  != ROBOT_INJURE_VALUES[0])][["timestamp", "round_number", "robot_stop", "robot_injure"]]
    return [getColumns(robotStops)] + robotStops.values.tolist()


def getColumns(dataFrame):
    return dataFrame.columns.values.tolist()

def getColumnsForZScore(dataFrame):
    columns = getColumns(dataFrame)
    dataTypes = dataFrame.dtypes.values.tolist()
    columnsToReturn = []
    for i in range(len(columns)):
        if dataTypes[i] == int and not columns[i] in NOT_DATA_COLUMNS:
            columnsToReturn.append(columns[i])
    for name, value in VALUE_GROUPS.items():
        columnsToReturn.insert(columnsToReturn.index(value[-1]) + 1, name)
    return columnsToReturn

def getTotals(dataFrame):
    columns = getColumns(dataFrame)
    dataTypes = dataFrame.dtypes.values.tolist()
    columnsToUse = []
    for i in range(len(columns)):
        if dataTypes[i] == int and not columns[i] in NOT_DATA_COLUMNS:
            columnsToUse.append(columns[i])
    totals = pandas.DataFrame()
    for column in columnsToUse:
        totals[column] = dataFrame[column].sum()
    for name, value in VALUE_GROUPS.items():
        sum = 0
        for column in value:
            sum += dataFrame[column].sum()
        totals.insert(totals.columns.get_loc(value[-1]) - 1, name, sum)

def getTeamZScore(dataFrame, teamNumber, column, ranking):
    totalDataFrame = getTotals(dataFrame)
    teamDataFrame = getDataFameForTeam()
    rawValue = teamDataFrame[column].sum()
    mean = totalDataFrame[column].mean()
    standardDeviation = totalDataFrame[column].std()
    return ((rawValue - mean) / standardDeviation) * ranking