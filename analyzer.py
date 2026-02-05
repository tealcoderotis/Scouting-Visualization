import mysql.connector
import pandas
from io import StringIO
from math import isnan, nan

'''CLIMB_VALUES = ["no_climb", "park_climb", "shallow_climb", "deep_climb"]
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
    "auto_algae_attempt": ["auto_algae", "auto_algae_missed"],
    "auto_coral_points": ["auto_coral_l1_points", "auto_coral_l2_points", "auto_coral_l3_points", "auto_coral_l4_points"],
    "auto_algae_points": ["auto_algae_processor_points", "auto_algae_net_points"],
    "tele_coral_points": ["tele_coral_l1_points", "tele_coral_l2_points", "tele_coral_l3_points", "tele_coral_l4_points"],
    "tele_algae_points": ["tele_algae_processor_points", "tele_algae_net_points"]
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
    "no_climb_accuracy": {
        "column": "climb",
        "favorableValue": "no_climb"
    },
    "park_climb_accuracy": {
        "column": "climb",
        "favorableValue": "park_climb"
    },
    "shallow_climb_accuracy": {
        "column": "climb",
        "favorableValue": "shallow_climb"
    },
    "deep_climb_accuracy": {
        "column": "climb",
        "favorableValue": "deep_climb"
    }
}
NOT_DATA_COLUMNS = ["PRIMARY_KEY", "team_number", "comp_level", "set_number", "match_number", "timestamp", "scouter_name", "scouting_team", "no_show", "competition", "alliance", "played_defense"]
POINT_VALUES = {
    "auto_leave_points": {
        "column": "auto_leave",
        "pointValue": 3
    },
    "auto_coral_l1_points": {
        "column": "auto_coral_l1",
        "pointValue": 3
    },
    "auto_coral_l2_points": {
        "column": "auto_coral_l2",
        "pointValue": 4
    },
    "auto_coral_l3_points": {
        "column": "auto_coral_l3",
        "pointValue": 6
    },
    "auto_coral_l4_points": {
        "column": "auto_coral_l4",
        "pointValue": 7
    },
    "auto_algae_processor_points": {
        "column": "auto_algae_processor",
        "pointValue": 6
    },
    "auto_algae_net_points": {
        "column": "auto_algae_net",
        "pointValue": 4
    },
    "tele_coral_l1_points": {
        "column": "tele_coral_l1",
        "pointValue": 2
    },
    "tele_coral_l2_points": {
        "column": "tele_coral_l2",
        "pointValue": 3
    },
    "tele_coral_l3_points": {
        "column": "tele_coral_l3",
        "pointValue": 4
    },
    "tele_coral_l4_points": {
        "column": "tele_coral_l4",
        "pointValue": 5
    },
    "tele_algae_processor_points": {
        "column": "tele_algae_processor",
        "pointValue": 6
    },
    "tele_algae_net_points": {
        "column": "tele_algae_net",
        "pointValue": 4
    },
    "climb_points": {
        "column": "climb",
        "dropdown": CLIMB_VALUES,
        "pointValue": [0, 2, 6, 12]
    }
}'''

NOT_DATA_COLUMNS = ["primary_key", "team_number", "comp_level", "set_number", "match_number", "timestamp", "scouter_name", "scouting_team", "no_show", "competition", "alliance", "device"]
CLIMB_VALUES = ["no_climb", "l1", "l2", "l3"]
DEFENSE_VALUES = ["no_defense", "some_defense", "mostly_defense"]
ROBOT_STOP_VALUES = ["no_stop", "one_stop", "many_stops", "end_stop"]
HIGH_CENTER_VALUES = ["no_high_center", "one_high_center", "many_high_centers", "end_high_centers"]
VALUE_GROUPS = {
    "auto_fuel_hub_attempt": ["auto_fuel_hub_success", "auto_fuel_hub_miss"],
    "auto_fuel_corral_attempt": ["auto_fuel_corral_success", "auto_fuel_corral_miss"],
    "tele_fuel_hub_attempt_active": ["tele_fuel_hub_success_active", "tele_fuel_hub_miss_active"],
    "tele_fuel_hub_attempt_inactive": ["tele_fuel_hub_success_inactive", "tele_fuel_hub_miss_inactive"],
    "tele_fuel_hub_success": ["tele_fuel_hub_success_active", "tele_fuel_hub_success_inactive"],
    "tele_fuel_hub_miss": ["tele_fuel_hub_miss_active", "tele_fuel_hub_miss_inactive"],
    "tele_fuel_hub_attempt": ["tele_fuel_hub_success", "tele_fuel_hub_miss"],
    "tele_fuel_corral_attempt": ["tele_fuel_corral_success", "tele_fuel_corral_miss"]
}
ACCURACY_VALUES = {
    "auto_fuel_hub_accuracy": ["auto_fuel_hub_success", "auto_fuel_hub_attempt"],
    "auto_fuel_corral_accuracy": ["auto_fuel_corral_success", "auto_fuel_corral_attempt"],
    "tele_fuel_hub_accuracy_active": ["tele_fuel_hub_success_active", "tele_fuel_hub_attempt_active"],
    "tele_fuel_hub_accuracy_inactive": ["tele_fuel_hub_success_inactive", "tele_fuel_hub_attempt_inactive"],
    "tele_fuel_hub_accuracy": ["tele_fuel_hub_success", "tele_fuel_hub_attempt"],
    "tele_corral_accuracy": ["tele_fuel_corral_success", "tele_fuel_corral_attempt"]
}
COUNTED_VALUES = {
    "auto_climb_accuracy": {
        "column": "auto_climb",
        "favorableValue": True
    },
    "tele_no_climb_accuracy": {
        "column": "tele_climb",
        "favorableValue": "no_climb"
    },
    "tele_l1_climb_accuracy": {
        "column": "tele_climb",
        "favorableValue": "l1"
    },
    "tele_l2_climb_accuracy": {
        "column": "tele_climb",
        "favorableValue": "l2"
    },
    "tele_l3_climb_accuracy": {
        "column": "tele_climb",
        "favorableValue": "l3"
    }
}
MULTIPLIED_VALUES = {
    "auto_fuel_hub_success": {
        "column": "auto_fuel_hub_cycles",
        "secondColumn": "auto_fuel_per_cycle"
    },
    "tele_fuel_hub_success_active": {
        "column": "tele_fuel_hub_cycles_active",
        "secondColumn": "tele_fuel_per_cycle"
    },
    "tele_fuel_hub_success_inactive": {
        "column": "tele_fuel_hub_cycles_inactive",
        "secondColumn": "tele_fuel_per_cycle"
    }
}
POINT_VALUES = {
    "auto_fuel_hub_points": {
        "column": "auto_fuel_hub_success",
        "pointValue": 1
    },
    "auto_climb_points": {
        "column": "auto_climb",
        "pointValue": 15
    },
    "tele_fuel_hub_points_active": {
        "column": "tele_fuel_hub_success_active",
        "pointValue": 1
    },
    "tele_climb_points": {
        "column": "tele_climb",
        "dropdown": CLIMB_VALUES,
        "pointValue": [0, 10, 20, 30]
    }
}
NOT_DATA_CYCLE_COLUMNS = ["primary_key", "team_number", "comp_level", "set_number", "match_number", "timestamp", "scouter_name", "scouting_team", "device"]

def getDatabaseData(host, user, password, database, table):
    db = mysql.connector.connect(host=host, user=user, password=password, buffered=True)
    cursor = db.cursor()
    cursor.execute(f"SHOW COLUMNS FROM {database}.{table}")
    columnData = cursor.fetchall()
    columnNames = []
    dataTypes = []
    for i in columnData:
        columnNames.append(i[0])
        dataTypes.append(i[1])
    cursor.execute(f"SELECT * FROM {database}.{table};")
    db.close()
    tableData = cursor.fetchall()
    return [columnNames, tableData, dataTypes]

def mergePointDataFrame(dataFrame, pointDataFrame):
    for column in getColumns(pointDataFrame):
        dataFrame[f"{column}_points"] = pointDataFrame[column]
    return dataFrame

def dropNaN(dataFrame):
    for column in getColumns(dataFrame):
        dataFrame[column] = dataFrame[column].dropna()
    return dataFrame

def getDataFrameFromDatabase(host, user, password, database, table):
    data = getDatabaseData(host, user, password, database, table)
    dataFrame = pandas.DataFrame(data[1], columns=data[0])
    return preProcessDataFrame(dataFrame, data[2])

def getCycleDataFrameFromDatabase(host, user, password, database, table):
    data = getDatabaseData(host, user, password, database, table)
    dataFrame = pandas.DataFrame(data[1], columns=data[0])
    return tinyIntToBoolean(dataFrame, data[2])

def preProcessDataFrame(dataFrame, dataTypes):
    return accuracyValues(groupValues(pointValues(multiplyValues(tinyIntToBoolean(dataFrame, dataTypes)))))

def applyTinyIntToBoolean(data):
    return bool(data)

def tinyIntToBoolean(dataFrame, dataTypes):
    columns = getColumns(dataFrame)
    for i in range(len(columns)):
        if dataTypes[i] == "tinyint(1)":
            dataFrame[columns[i]] = dataFrame[columns[i]].apply(applyTinyIntToBoolean)
    return dataFrame

def getDataFrameFromCSV(filePath):
    dataFrame = pandas.read_csv(filePath, sep=",", engine="python")
    dataFrame, dataTypes = dropDataTypes(dataFrame)
    return preProcessDataFrame(dataFrame, dataTypes)

def getCycleDataFrameFromCSV(filePath):
    dataFrame = pandas.read_csv(filePath, sep=",", engine="python")
    dataFrame, dataTypes = dropDataTypes(dataFrame)
    return tinyIntToBoolean(dataFrame, dataTypes)

def dropDataTypes(dataFrame):
    types = dataFrame.iloc[0].values.tolist()
    csv = dataFrame.drop(0).to_csv(sep=",", index=False)
    return pandas.read_csv(StringIO(csv), sep=",", engine="python"), types

def getDataTypeOfColumn(dataFrame, column):
    return dataFrame.dtypes[column]

def applyPointValue(data, ranking):
    if not isnan(data) or data != None:
        return data * ranking
    else:
        return nan

def applyPointValueFromDropdown(data, dropdown, ranking):
    if data != None and data in dropdown:
        return ranking[dropdown.index(data)]
    else:
        return nan

def pointValues(dataFrame):
    for key, value in POINT_VALUES.items():
        if "dropdown" in value:
            columnData = dataFrame[value["column"]].apply(applyPointValueFromDropdown, args=(value["dropdown"], value["pointValue"],))
        else:
            columnData = dataFrame[value["column"]].apply(applyPointValue, args=(value["pointValue"],))
        dataFrame.insert(dataFrame.columns.get_loc(value["column"]) + 1, key, columnData)
    return dataFrame

def applyMultipyValue(row, column1, column2):
    return row[column1] * row[column2]

def multiplyValues(dataFrame):
    for key, value in MULTIPLIED_VALUES.items():
        columnData = dataFrame.apply(applyMultipyValue, args=(value["column"], value["secondColumn"],), axis=1)
        dataFrame.insert(dataFrame.columns.get_loc(value["column"]) + 1, key, columnData)
    return dataFrame

def applyGroupValues(data, columns):
    sum = 0
    for column in columns:
        sum += data[column].sum()
    return sum

def applyAccuracyValues(data, columns):
    if data[columns[1]].sum() != 0:
        accuracy = data[columns[0]].sum() / data[columns[1]].sum()
    else:
        accuracy = 0
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
    return sorted(dataFrame["team_number"].drop_duplicates().to_list())

def getDataFrameForTeam(dataFrame, teamNumber):
    return dataFrame[dataFrame["team_number"].values == teamNumber]

def getDataFrameWithoutRobotStops(dataFrame):
    return dataFrame.loc[(dataFrame["robot_stop"] == ROBOT_STOP_VALUES[0])]

def getDataFrameWithoutNoShows(dataFrame):
    return dataFrame.loc[(dataFrame["no_show"] == 0)]

def getTotalRobotStopsForEachType(dataFrame, teamNumber):
    teamDataFrame = getDataFrameForTeam(dataFrame, teamNumber)
    stopList = []
    for i in range(1, len(ROBOT_STOP_VALUES)):
        robotStops = teamDataFrame.loc[(dataFrame["robot_stop"] == ROBOT_STOP_VALUES[i])].shape[0]
        stopList.append(robotStops)
    highCenterList = []
    for i in range(1, len(HIGH_CENTER_VALUES)):
        robotStops = teamDataFrame.loc[(dataFrame["high_center"] == HIGH_CENTER_VALUES[i])].shape[0]
        highCenterList.append(robotStops)
    noShows = teamDataFrame.loc[(dataFrame["no_show"] != False)].shape[0]
    defenseList = []
    for i in range(1, len(DEFENSE_VALUES)):
        robotStops = teamDataFrame.loc[(dataFrame["defense"] == DEFENSE_VALUES[i])].shape[0]
        defenseList.append(robotStops)
    return [stopList, highCenterList, defenseList, noShows]

def getStopDetails(dataFrame, teamNumber):
    teamDataFrame = getDataFrameForTeam(dataFrame, teamNumber)
    teamDataFrame = teamDataFrame.sort_values(by=["match_number"])
    robotStops = teamDataFrame.loc[(dataFrame["robot_stop"] != ROBOT_STOP_VALUES[0]) | (dataFrame["high_center"]  != HIGH_CENTER_VALUES[0]) | (dataFrame["no_show"]  != False) | (dataFrame["defense"] != DEFENSE_VALUES[0])][["timestamp", "match_number", "robot_stop", "high_center",  "defense", "no_show"]]
    return [getColumns(robotStops)] + robotStops.values.tolist()

def getColumns(dataFrame):
    return dataFrame.columns.values.tolist()

def getColumnsForZScore(dataFrame, getCountedValues=True):
    columns = getColumns(dataFrame)
    dataTypes = dataFrame.dtypes.values.tolist()
    columnsToReturn = []
    for i in range(len(columns)):
        if columns[i] not in NOT_DATA_COLUMNS:
            if dataTypes[i] == "int64" or dataTypes[i] == "float64":
                columnsToReturn.append(columns[i])
    if getCountedValues:
        for column, value in COUNTED_VALUES.items():
            columnsToReturn.append(column)
        return [columnsToReturn, list(COUNTED_VALUES.keys())]
    else:
        return columnsToReturn
    
def getColumnsForCycleZScore(dataFrame):
    columns = getColumns(dataFrame)
    dataTypes = dataFrame.dtypes.values.tolist()
    columnsToReturn = []
    for i in range(len(columns)):
        if columns[i] not in NOT_DATA_CYCLE_COLUMNS:
            if dataTypes[i] == "int64" or dataTypes[i] == "float64":
                columnsToReturn.append(columns[i])
    return columnsToReturn
    
def filterDataFrame(dataFrame, filters):
    if filters != None:
        for column, value in filters.items():
            data = dataFrame.to_dict("list")
            if value[0] != 0 and column in getColumns(dataFrame):
                dataType = getDataTypeOfColumn(dataFrame, column)
                if dataType == "int64" or dataType == "float64":
                    if value[0] == 1:
                        dataFrame = dataFrame.loc[(dataFrame[column] == value[1])]
                    if value[0] == 2:
                        dataFrame = dataFrame.loc[(dataFrame[column] != value[1])]
                    if value[0] == 3:
                        dataFrame = dataFrame.loc[(dataFrame[column] > value[1])]
                    if value[0] == 4:
                        dataFrame = dataFrame.loc[(dataFrame[column] < value[1])]
                    if value[0] == 5:
                        dataFrame = dataFrame.loc[(dataFrame[column] >= value[1])]
                    if value[0] == 6:
                        dataFrame = dataFrame.loc[(dataFrame[column] <= value[1])]
                    if value[0] == 7:
                        for index, rowDataFrame in dataFrame.iterrows():
                            row = rowDataFrame.to_dict()
                            rawValue = row[column]
                            globalValues = {
                                "input": None,
                                "print": None,
                                "data": data,
                                "row": row,
                                "value": rawValue,
                                "column": column
                            }
                            localValues = {
                                "passes": None
                            }
                            try:
                                code = compile(value[1], "<string>", "exec")
                                exec(code, globalValues, localValues)
                            except Exception as e:
                                raise Exception(f"Exception occured within custom filter\n\n{str(e)}")
                            else:
                                if type(localValues["passes"]) == bool:
                                    if not localValues["passes"]:
                                        dataFrame = dataFrame.drop(index)
                                else:
                                    raise TypeError("Custom filter did not return boolean")
                else:
                    if value[0] == 1:
                        dataFrame = dataFrame.loc[(dataFrame[column] == value[1])]
                    if value[0] == 2:
                        dataFrame = dataFrame.loc[(dataFrame[column] != value[1])]
                    if value[0] == 3:
                        for index, rowDataFrame in dataFrame.iterrows():
                            row = rowDataFrame.to_dict()
                            rawValue = row[column]
                            globalValues = {
                                "input": None,
                                "print": None,
                                "data": data,
                                "row": row,
                                "value": rawValue,
                                "column": column
                            }
                            localValues = {
                                "passes": None
                            }
                            try:
                                code = compile(value[1], "<string>", "exec")
                                exec(code, globalValues, localValues)
                            except Exception as e:
                                raise Exception(f"Exception occured within custom filter\n\n{str(e)}")
                            else:
                                if type(localValues["passes"]) == bool:
                                    if not localValues["passes"]:
                                        dataFrame = dataFrame.drop(index)
                                else:
                                    raise TypeError("Custom filter did not return boolean")
    return dataFrame

def filterTeam(dataFrame, teamNumber, column, filter):
    data = dataFrame.to_dict("list")
    row = dataFrame.loc[(dataFrame["team_number"] == teamNumber)].to_dict("records")[0]
    value = row[column]
    if filter[0] == 1:
        return value == filter[1]
    if filter[0] == 2:
        return value != filter[1]
    if filter[0] == 3:
        return value > filter[1]
    if filter[0] == 4:
        return value < filter[1]
    if filter[0] == 5:
        return value >= filter[1]
    if filter[0] == 6:
        return value <= filter[1]
    if filter[0] == 7:
        globalValues = {
            "input": None,
            "print": None,
            "data": data,
            "row": row,
            "value": value,
            "column": column
        }
        localValues = {
            "passes": None
        }
        try:
            code = compile(filter[1], "<string>", "exec")
            exec(code, globalValues, localValues)
        except Exception as e:
            raise Exception(f"Exception occured within custom filter\n\n{str(e)}")
        else:
            if type(localValues["passes"]) == bool:
                return localValues["passes"]
            else:
                raise TypeError("Custom filter did not returan boolen")
    else:
        return True
    
def getData(dataFrame, frameType, matchFilter=None, teamFilter=None, q1MinimumFilter=False, q3MaximumFilter=False):
    dataFrame = filterDataFrame(dataFrame, matchFilter)
    mainDataFrame = getDataFrame(dataFrame, frameType, q1MinimumFilter, q3MaximumFilter)
    for column in COUNTED_VALUES:
        mainDataFrame[column] = getAccuracyDataFrame(dataFrame, COUNTED_VALUES[column]["column"], COUNTED_VALUES[column]["favorableValue"], column)[column]
    for team in getAllTeams(mainDataFrame):
        for column in teamFilter:
            if not filterTeam(mainDataFrame, team, column, teamFilter[column]):
                mainDataFrame.drop(dataFrame.loc[(dataFrame["team_number"] == team)].index, inplace=True)
                break
    mainDataFrame.sort_values(by="team_number", inplace=True)
    return mainDataFrame

def getDataFrame(dataFrame, frameType, q1MinimumFilter=False, q3MaximumFilter=False):
    if frameType == 0:
        mainDataFrame = getTotalDataFrame(dataFrame, q1MinimumFilter, q3MaximumFilter)
    elif frameType == 1:
        mainDataFrame = getAverageDataFrame(dataFrame, q1MinimumFilter, q3MaximumFilter)
    elif frameType == 2:
        mainDataFrame = getMedianDataFrame(dataFrame, q1MinimumFilter, q3MaximumFilter)
    elif frameType == 3:
        mainDataFrame = getModeDataFrame(dataFrame, q1MinimumFilter, q3MaximumFilter)
    elif frameType == 4:
        mainDataFrame = getMaxDataFrame(dataFrame, q1MinimumFilter, q3MaximumFilter)
    return mainDataFrame

def dataFrameToList(dataFrame):
    return [getColumns(dataFrame)] + dataFrame.values.tolist()

def getTotalDataFrame(dataFrame, q1MinimumFilter=False, q3MaximumFilter=False):
    allColumns = getColumnsForZScore(dataFrame, False)
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame()
    for i in range(len(teams)):
        teamDataFrame = getDataFrameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        for column in allColumns:
            dataFrameToUse = teamDataFrame.copy()
            firstQuartile = dataFrameToUse[column].quantile(0.25)
            thirdQuartile = dataFrameToUse[column].quantile(0.75)
            if q1MinimumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] >= firstQuartile)]
            if q3MaximumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] <= thirdQuartile)]
            newDataFrame.loc[newDataFrame.index[i], column] = dataFrameToUse[column].sum()
    return newDataFrame

def getAverageDataFrame(dataFrame, q1MinimumFilter=False, q3MaximumFilter=False):
    allColumns = getColumnsForZScore(dataFrame, False)
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame()
    for i in range(len(teams)):
        teamDataFrame = getDataFrameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        for column in allColumns:
            dataFrameToUse = teamDataFrame.copy()
            firstQuartile = dataFrameToUse[column].quantile(0.25)
            thirdQuartile = dataFrameToUse[column].quantile(0.75)
            if q1MinimumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] >= firstQuartile)]
            if q3MaximumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] <= thirdQuartile)]
            newDataFrame.loc[newDataFrame.index[i], column] = dataFrameToUse[column].mean()
    return newDataFrame

def getMedianDataFrame(dataFrame, q1MinimumFilter=False, q3MaximumFilter=False):
    allColumns = getColumnsForZScore(dataFrame, False)
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame()
    for i in range(len(teams)):
        teamDataFrame = getDataFrameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        for column in allColumns:
            dataFrameToUse = teamDataFrame.copy()
            firstQuartile = dataFrameToUse[column].quantile(0.25)
            thirdQuartile = dataFrameToUse[column].quantile(0.75)
            if q1MinimumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] >= firstQuartile)]
            if q3MaximumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] <= thirdQuartile)]
            newDataFrame.loc[newDataFrame.index[i], column] = dataFrameToUse[column].median()
    return newDataFrame

def getModeDataFrame(dataFrame, q1MinimumFilter=False, q3MaximumFilter=False):
    allColumns = getColumnsForZScore(dataFrame, False)
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame()
    for i in range(len(teams)):
        teamDataFrame = getDataFrameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        for column in allColumns:
            dataFrameToUse = teamDataFrame.copy()
            firstQuartile = dataFrameToUse[column].quantile(0.25)
            thirdQuartile = dataFrameToUse[column].quantile(0.75)
            if q1MinimumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] >= firstQuartile)]
            if q3MaximumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] <= thirdQuartile)]
            modes = dataFrameToUse[column].mode().to_list()
            if len(modes) > 0:
                newDataFrame.loc[newDataFrame.index[i], column] = modes[0]
            else:
                newDataFrame.loc[newDataFrame.index[i], column] = nan
    return newDataFrame
    
def getMaxDataFrame(dataFrame, q1MinimumFilter=False, q3MaximumFilter=False):
    allColumns = getColumnsForZScore(dataFrame, False)
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame()
    for i in range(len(teams)):
        teamDataFrame = getDataFrameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        for column in allColumns:
            dataFrameToUse = teamDataFrame.copy()
            firstQuartile = dataFrameToUse[column].quantile(0.25)
            thirdQuartile = dataFrameToUse[column].quantile(0.75)
            if q1MinimumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] >= firstQuartile)]
            if q3MaximumFilter:
                dataFrameToUse = dataFrameToUse.loc[(dataFrame[column] <= thirdQuartile)]
            newDataFrame.loc[newDataFrame.index[i], column] = dataFrameToUse[column].max()
    return newDataFrame

def getAccuracyDataFrame(dataFrame, column, favorableColumn, finalName):
    teams = getAllTeams(dataFrame)
    newDataFrame = pandas.DataFrame()
    for i in range(len(teams)):
        teamDataFrame = getDataFrameForTeam(dataFrame, teams[i])
        newDataFrame.loc[i, "team_number"] = teams[i]
        totalValues = teamDataFrame[column].dropna().shape[0]
        favorableValues = teamDataFrame.loc[(dataFrame[column] == favorableColumn)].shape[0]
        if totalValues == 0:
            accuracy = nan
        else:
            accuracy = favorableValues / totalValues
        newDataFrame.loc[i, finalName] = accuracy
    return newDataFrame

def rankTeamsByZScore(dataFrame, cycleDataFrame, sliderValues, matchFilter=None, teamFilter=None):
    dataFrame = filterDataFrame(dataFrame, matchFilter)
    teams = getAllTeams(dataFrame)
    teamZScores = {}
    dataFrameBuffer = {}
    accuracyBuffer = {}
    for team in teams:
        eliminated = False
        currentScore = 0
        for column, ranking in sliderValues.items():
            if column in dataFrame.columns:
                if ranking[0] not in dataFrameBuffer:
                    dataFrameBuffer[ranking[0]] = {}
                if ranking[4] == False and ranking[5] == False:
                    bufferToUse = 0
                elif ranking[4] == True and ranking[5] == False:
                    bufferToUse = 1
                elif ranking[4] == False and ranking[5] == True:
                    bufferToUse = 2
                elif ranking[4] == True and ranking[5] == True:
                    bufferToUse = 3
                if bufferToUse not in dataFrameBuffer[ranking[0]]:
                    dataFrameBuffer[ranking[0]][bufferToUse] = [None, None, None, None]
                if ranking[2] and ranking[3]:
                    if dataFrameBuffer[ranking[0]][bufferToUse][3] is None and (ranking[1] != 0 or teamFilter[column][0] != 0):
                        dataFrameToGenerate = getDataFrameWithoutNoShows(getDataFrameWithoutRobotStops(dataFrame))
                        dataFrameToUse = getDataFrame(dataFrameToGenerate, ranking[0], ranking[4], ranking[5])
                        dataFrameBuffer[ranking[0]][bufferToUse][3] = dataFrameToUse.copy()
                    else:
                        dataFrameToUse = dataFrameBuffer[ranking[0]][bufferToUse][3]
                elif ranking[3]:
                    if dataFrameBuffer[ranking[0]][bufferToUse][2] is None and (ranking[1] != 0 or teamFilter[column][0] != 0):
                        dataFrameToGenerate = getDataFrameWithoutNoShows(dataFrame)
                        dataFrameToUse = getDataFrame(dataFrameToGenerate, ranking[0], ranking[4], ranking[5])
                        dataFrameBuffer[ranking[0]][bufferToUse][2] = dataFrameToUse.copy()
                    else:
                        dataFrameToUse = dataFrameBuffer[ranking[0]][bufferToUse][2]
                elif ranking[2]:
                    if dataFrameBuffer[ranking[0]][bufferToUse][1] is None and (ranking[1] != 0 or teamFilter[column][0] != 0):
                        dataFrameToGenerate = getDataFrameWithoutRobotStops(dataFrame)
                        dataFrameToUse = getDataFrame(dataFrameToGenerate, ranking[0], ranking[4], ranking[5])
                        dataFrameBuffer[ranking[0]][bufferToUse][1] = dataFrameToUse.copy()
                    else:
                        dataFrameToUse = dataFrameBuffer[ranking[0]][bufferToUse][1]
                else:
                    if dataFrameBuffer[ranking[0]][bufferToUse][0] is None and (ranking[1] != 0 or teamFilter[column][0] != 0):
                        dataFrameToUse = getDataFrame(dataFrame, ranking[0], ranking[4], ranking[5])
                        dataFrameBuffer[ranking[0]][bufferToUse][0] = dataFrameToUse.copy()
                    else:
                        dataFrameToUse = dataFrameBuffer[ranking[0]][bufferToUse][0]
                if teamFilter[column][0] != 0 and not filterTeam(dataFrameToUse, team, column, teamFilter[column]):
                    eliminated = True
                    break
                if ranking[1] != 0:
                    currentScore += getTeamZScoreForColumn(dataFrameToUse, team, column, ranking[1])
            elif column in COUNTED_VALUES:
                if column not in accuracyBuffer:
                    accuracyBuffer[column] = [None, None, None, None]
                if ranking[2] and ranking[3]:
                    if accuracyBuffer[column][3] is None and (ranking[1] != 0 or teamFilter[column][0] != 0):
                        dataFrameToGenerate = getDataFrameWithoutNoShows(getDataFrameWithoutRobotStops(dataFrame))
                        dataFrameToUse = getAccuracyDataFrame(dataFrameToGenerate, COUNTED_VALUES[column]["column"], COUNTED_VALUES[column]["favorableValue"], column)
                        accuracyBuffer[column][3] = dataFrameToUse.copy()
                    else:
                        dataFrameToUse = accuracyBuffer[column][3]
                elif ranking[3]:
                    if accuracyBuffer[column][2] is None and (ranking[1] != 0 or teamFilter[column][0] != 0):
                        dataFrameToGenerate = getDataFrameWithoutNoShows(dataFrame)
                        dataFrameToUse = getAccuracyDataFrame(dataFrameToGenerate, COUNTED_VALUES[column]["column"], COUNTED_VALUES[column]["favorableValue"], column)
                        accuracyBuffer[column][2] = dataFrameToUse.copy()
                    else:
                        dataFrameToUse = accuracyBuffer[column][2]
                elif ranking[2]:
                    if accuracyBuffer[column][1] is None and (ranking[1] != 0 or teamFilter[column][0] != 0):
                        dataFrameToGenerate = getDataFrameWithoutRobotStops(dataFrame)
                        dataFrameToUse = getAccuracyDataFrame(dataFrameToGenerate, COUNTED_VALUES[column]["column"], COUNTED_VALUES[column]["favorableValue"], column)
                        accuracyBuffer[column][1] = dataFrameToUse.copy()
                    else:
                        dataFrameToUse = accuracyBuffer[column][1]
                else:
                    if accuracyBuffer[column][0] is None and (ranking[1] != 0 or teamFilter[column][0] != 0):
                        dataFrameToUse = getAccuracyDataFrame(dataFrame, COUNTED_VALUES[column]["column"], COUNTED_VALUES[column]["favorableValue"], column)
                        accuracyBuffer[column][0] = dataFrameToUse.copy()
                    else:
                        dataFrameToUse = accuracyBuffer[column][0]
                if teamFilter[column][0] != 0 and not filterTeam(dataFrameToUse, team, column, teamFilter[column]):
                    eliminated = True
                    break
                currentScore += getTeamZScoreForColumn(dataFrameToUse, team, column, ranking[1])
        if not eliminated:
            teamZScores[team] = currentScore
    return sorted(teamZScores.items(), key=lambda x: x[1], reverse=True)

def getTeamZScoreForColumn(dataFrame, teamNumber, column, ranking):
    if ranking != 0:
        if dataFrame.loc[(dataFrame["team_number"] == teamNumber)][column].shape[0] > 0:
            rawValue = dataFrame.loc[(dataFrame["team_number"] == teamNumber)][column].values.tolist()[0]
            if rawValue != nan:
                mean = dataFrame[column].mean()
                standardDeviation = dataFrame[column].std()
                if standardDeviation != 0:
                    zScore = (rawValue - mean) / standardDeviation
                else:
                    zScore = 0
            else:
                zScore = 0
        else:
            zScore = 0
        if isnan(zScore):
            zScore = 0
        return zScore * ranking
    else:
        return 0.0

def getTeamZScoreAccuracyForColumn(dataFrame, teamNumber, column, favorableValue, finalName, ranking, dropRobotStops, dropNoShows):
    if ranking != 0:
        dataFrameToUse = dataFrame
        if dropRobotStops:
            dataFrameToUse = getDataFrameWithoutRobotStops(dataFrameToUse)
        if dropNoShows:
            dataFrameToUse = getDataFrameWithoutNoShows(dataFrameToUse)
        mainDataFrame = getAccuracyDataFrame(dataFrameToUse, column, favorableValue, finalName)
        if mainDataFrame.loc[(mainDataFrame["team_number"] == teamNumber)][finalName].shape[0] > 0:
            rawValue = mainDataFrame.loc[(mainDataFrame["team_number"] == teamNumber)][finalName].values.tolist()[0]
            mean = mainDataFrame[finalName].mean()
            standardDeviation = mainDataFrame[finalName].std()
            if standardDeviation != 0:
                zScore = (rawValue - mean) / standardDeviation
            else:
                zScore = 0
        else:
            zScore = 0
        if isnan(zScore):
            zScore = 0
        return zScore * ranking
    else:
        return 0