import numpy as np
import pandas as pd


def drawdowns(dataframe, order_type, period):
    size = len(dataframe)

    ranges = [0, -0.5, -1, -2, -3, -4, -5, -10, -25, -50, -100]
    counter = counter_within_range(dataframe, order_type, period, ranges)

    percentages = np.divide(counter, size)

    result = {
        'less_than': ranges,
        'percentages': percentages
    }

    df = pd.DataFrame(result)
    df.set_index('less_than')
    return df


def counter_within_range(dataframe, order_type, period, ranges):
    column = dataframe[order_type + '_drawdown_' + str(period)]

    counter = [0] * len(ranges)
    for value in column:

        for i in range(len(ranges) - 1, -1, -1):
            reference = ranges[i]
            if value < reference:
                counter[i] += 1

    return counter
