import statistics

quartile = statistics.quantiles(data[column])[0]
passes = value >= quartile