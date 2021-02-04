def buyAndHoldAnalysis(dataframe):
    trading_years = (dataframe.index[-1] - dataframe.index[0]).days / 365

    # Buy and hold stats setup
    buyAndHoldBuyPrice = dataframe['Close'][dataframe.index[0]]  # Buy in the close of the first day
    buyAndHoldSellPrice = dataframe['Close'][len(dataframe.index) - 1]  # Sell in the close of the last day
    buyAndHoldRentability = (buyAndHoldSellPrice / buyAndHoldBuyPrice - 1) * 100
    buyAndHoldMaxDrawdown = 0
    allTimeHigh = 0

    # Go for every data frame date, searching for an all time high,
    # if is not in an all times high, get drawdown from the all time high
    for i in dataframe.index:
        # Get date values

        # Update drawdown
        if dataframe['High'][i] > allTimeHigh:
            allTimeHigh = dataframe['High'][i]
        else:
            currentDrawdown = (dataframe['Low'][i] / allTimeHigh - 1) * 100
            buyAndHoldMaxDrawdown = min(buyAndHoldMaxDrawdown, currentDrawdown)

    CAGR = (pow(buyAndHoldSellPrice / buyAndHoldBuyPrice, 1 / trading_years) -1) * 100

    return {
        'startDate': dataframe.index[0],
        'endDate': dataframe.index[-1],
        'rentability':buyAndHoldRentability,
        'drawdown': buyAndHoldMaxDrawdown,
        'CAGR': CAGR,
        'MAR': CAGR / buyAndHoldMaxDrawdown * -1
    }

def buyAndHoldLog(buyAndHold):

    metrics = 'CAGR: ' + str(round(buyAndHold['CAGR'],3)) + ', MAR: ' + str(round(buyAndHold['MAR'],3))

    log = 'Buy and hold in the same period. Rentability : ' + str(round(buyAndHold['rentability'], 2)) + '%' \
          + ' | drawdown: ' + str(round(buyAndHold['drawdown'], 2)) + '%  | ' + metrics

    return log