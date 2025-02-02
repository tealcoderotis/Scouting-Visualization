import mysql.connector
import pandas

CLIMB_VALUES = ["no_climb", "park_climb", "shallow_climb", "deep_climb"]
ROBOT_STOP_VALUES = ["no_stop", "one_stop", "many_stops", "end_stop"]
ROBOT_INJURE_VALUES = ["no_injure", "fixed_injure", "end_injure"]

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

def preprocessDataFrame(dataFrame):
    dataFrame["robot_stop"] = dataFrame["robot_stop"].apply(getTextValueFromDropdown, args=(ROBOT_STOP_VALUES,))
    dataFrame["robot_injure"] = dataFrame["robot_injure"].apply(getTextValueFromDropdown, args=(ROBOT_INJURE_VALUES,))
    return dataFrame

def getDataFrameFromDatabase(host, user, password, database, table):
    data = getDatabaseData(host, user, password, database, table)
    dataFrame = pandas.DataFrame(data[1], columns=data[0])
    return preprocessDataFrame(dataFrame)

def getDataFrameFromCSV(filePath):
    dataFrame = pandas.read_csv(filePath)
    return preprocessDataFrame(dataFrame)

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
    return [robotStops.columns.values.tolist()] + robotStops.values.tolist()