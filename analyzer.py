import mysql.connector
import pandas
from io import StringIO

CLIMB_VALUES = ["no_climb", "park_climb", "shallow_climb", "deep_climb"]
ROBOT_STOP_VALUES = ["no_stop", "one_stop", "many_stops", "end_stop"]
ROBOT_INJURE_VALUES = ["no_injure", "fixed_injure", "end_injure"]
VALUE_GROUPS = {
    "auto_coral": ["auto_coral_l1", "auto_coral_l2", "auto_coral_l3", "auto_coral_l4"],
    "tele_coral": ["tele_coral_l1", "tele_coral_l2", "tele_coral_l3", "tele_coral_l4"],
    "auto_coral_attempt": ["auto_coral", "auto_coral_missed"],
    "tele_coral_attempt": ["tele_coral", "tele_coral_missed"],
    "tele_algae_processor_attempt": ["tele_algae_processor", "tele_algae_processor_missed"],
    "tele_algae_net_attempt": ["tele_algae_net", "tele_algae_net_missed"],
    "tele_algae": ["tele_algae_processor", "tele_algae_net"],
    "tele_algae_missed": ["tele_algae_processor_missed", "tele_algae_net_missed"],
    "tele_algae_attempt": ["tele_algae", "tele_algae_missed"],
    "auto_algae_processor_attempt": ["auto_algae_processor", "auto_algae_processor_missed"],
    "auto_algae_net_attempt": ["auto_algae_net", "auto_algae_net_missed"],
    "auto_algae": ["auto_algae_processor", "auto_algae_net"],
    "auto_algae_missed": ["auto_algae_processor_missed", "auto_algae_net_missed"],
    "auto_algae_attempt": ["auto_algae", "auto_algae_missed"]
}
ACCURACY_VALUES = {
    "auto_coral_accuracy": ["auto_coral", "auto_coral_attempt"],
    "auto_algae_processor_accuracy": ["auto_algae_processor", "auto_algae_processor_attempt"],
    "auto_algae_net_accuracy": ["auto_algae_net", "auto_algae_net_attempt"],
    "auto_algae_accuracy": ["auto_algae", "auto_algae_attempt"],
    "tele_coral_accuracy": ["tele_coral", "tele_coral_attempt"],
    "tele_algae_processor_accuracy": ["tele_algae_processor", "tele_algae_processor_attempt"],
    "tele_algae_net_accuracy": ["tele_algae_net", "tele_algae_net_attempt"],
    "tele_algae_accuracy": ["tele_algae", "tele_algae_attempt"]
}
COUNTED_VALUES = {
    "climb": CLIMB_VALUES
}

NOT_DATA_COLUMNS = ["PRIMARY_KEY", "team_number", "round_number", "timestamp", "scouter_name", "scouting_team"]

def getDatabaseData(host, user, password, database, table):
    db = mysql.connector.connect(host=host, user=user, password=password, buffered=True)
    cursor = db.cursor()
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
    return accuracyValues(groupValues(dataFrame))

def getDataFrameFromCSV(filePath):
    dataFrame = pandas.read_csv(filePath, sep=", ", engine="python")
    return accuracyValues(groupValues(preprocessDataFrame(dataFrame)))

def preprocessDataFrame(dataFrame):
    csv = dataFrame.drop(0).to_csv(sep=",", index=False)
    return pandas.read_csv(StringIO(csv), sep=",", engine="python")

def applyGroupValues(data, columns):
    sum = 0
    for column in columns:
        sum += data[column].sum()
    return sum

def applyAccuracyValues(data, columns):
    accuracy = data[columns[0]].sum() / data[columns[1]].sum()
    return accuracy

def groupValues(dataFrame):
    for name, value in VALUE_GROUPS.items():
        columnData = dataFrame[value].apply(applyGroupValues, args=(value,), axis=1)
        dataFrame.insert(dataFrame.columns.get_loc(value[-1]) + 1, name, columnData)
    return dataFrame

def accuracyValues(dataFrame):
    for name, value in ACCURACY_VALUES.items():
        columnData = dataFrame[value].apply(applyAccuracyValues, args=(value,), axis=1)
        dataFrame.insert(dataFrame.columns.get_loc(value[-1]) + 1, name, columnData)
    return dataFrame

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

def getColumnsForZScore(dataFrame, getCountedValues=True):
    columns = getColumns(dataFrame)
    dataTypes = dataFrame.dtypes.values.tolist()
    columnsToReturn = []
    for i in range(len(columns)):
        if columns[i] not in NOT_DATA_COLUMNS:
            if (dataTypes[i] == int or dataTypes[i] == float):
                columnsToReturn.append(columns[i])
            elif columns[i] in COUNTED_VALUES and getCountedValues:
                for value in COUNTED_VALUES[columns[i]]:
                    columnsToReturn.append(value)
    return columnsToReturn

def getTotalDataFrame(dataFrame):
    allColumns = getColumnsForZScore(dataFrame, False)
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame(columns=allColumns)
    for i in range(len(teams)):
        teamDataFrame = getDataFameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        for column in allColumns:
            newDataFrame.loc[newDataFrame.index[i], column] = teamDataFrame[column].sum()
    return newDataFrame

def getAverageDataFrame(dataFrame):
    allColumns = getColumnsForZScore(dataFrame, False)
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame(columns=allColumns)
    for i in range(len(teams)):
        teamDataFrame = getDataFameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        for column in allColumns:
            newDataFrame.loc[newDataFrame.index[i], column] = teamDataFrame[column].mean()
    return newDataFrame
    
def getAverageDataFrameQ1Minimum(dataFrame):
    allColumns = getColumnsForZScore(dataFrame, False)
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame(columns=allColumns)
    for i in range(len(teams)):
        teamDataFrame = getDataFameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        for column in allColumns:
            columnQuartile = teamDataFrame[column].quantile(0.25)
            filteredColumn = teamDataFrame.loc[(dataFrame[column] >= columnQuartile)][column]
            newDataFrame.loc[newDataFrame.index[i], column] = filteredColumn.mean()
    return newDataFrame

def getCountedValue():
    pass
    
def getMaxDataFrame(dataFrame):
    allColumns = getColumnsForZScore(dataFrame, False)
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame(columns=allColumns)
    for i in range(len(teams)):
        teamDataFrame = getDataFameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        for column in allColumns:
            newDataFrame.loc[newDataFrame.index[i], column] = teamDataFrame[column].max()
    return newDataFrame

def rankTeamsByZScore(dataFrame, sliderValues):
    teams = getAllTeams(dataFrame)
    teamZScores = {}
    for team in teams:
        currentScore = 0
        for column, ranking in sliderValues.items():
            if column in dataFrame.columns:
                currentScore += getTeamZScoreForColumn(dataFrame, ranking[0], team, column, ranking[1])
        teamZScores[team] = currentScore
    return sorted(teamZScores.items(), key=lambda x: x[1])

def getTeamZScoreForColumn(dataFrame, frameType, teamNumber, column, ranking):
    if frameType == 0:
        mainDataFrame = getTotalDataFrame(dataFrame)
    elif frameType == 1:
        mainDataFrame = getAverageDataFrame(dataFrame)
    elif frameType == 2:
        mainDataFrame = getAverageDataFrameQ1Minimum(dataFrame)
    elif frameType == 3:
        mainDataFrame = getMaxDataFrame(dataFrame)
    rawValue = mainDataFrame.loc[(mainDataFrame["team_number"] == teamNumber)][column].values.tolist()[0]
    mean = mainDataFrame[column].mean().tolist()
    standardDeviation = mainDataFrame[column].std()
    if standardDeviation != 0:
        zScore = (rawValue - mean) / standardDeviation
    else:
        zScore = 0
    return zScore * ranking