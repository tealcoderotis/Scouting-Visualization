import database
import pandas

data = database.getAllData("localhost", "root", "orfscouting789", "world", "city")

dataframe = pandas.DataFrame(data[1], columns=data[0])

print(dataframe)