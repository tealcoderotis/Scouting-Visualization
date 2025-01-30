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

def getDataFrame(host, user, password, database, table):
    data = getDatabaseData(host, user, password, database, table)
    dataFrame = pandas.DataFrame(data[1], columns=data[0])
    dataFrame["robot_stop"] = dataFrame["robot_stop"].apply(getTextValueFromDropdown, args=(ROBOT_STOP_VALUES))
    return dataFrame

def getAllTeams(dataFrame):
    return dataFrame["team_number"].drop_duplicates().to_list()

def getDataFameForTeam(dataFrame, teamNumber):
    return dataFrame[dataFrame["team_number"].values == teamNumber]

def getTotalRobotStops(dataFrame, teamNumber):
    teamDataFrame = getDataFameForTeam(dataFrame, teamNumber)
    robotStops =  teamDataFrame[teamDataFrame["robot_stop"].values != 0]["robot_stop"].to_list()
    return len(robotStops)

def getStopDetails(dataFrame, teamNumber):
    teamDataFrame = getDataFameForTeam(dataFrame, teamNumber)
    robotStops =  teamDataFrame[teamDataFrame["robot_stop"].values != 0]["round_number", "robot_stop"].to_list()
    return robotStops