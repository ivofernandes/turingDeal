def calculateBuyAndHoldDrawdown(dataframe):
    drawdown = 0
    allTimeHigh = 0

    # Go for every data frame date, searching for an all time high,
    # if is not in an all times high, get drawdown from the all time high
    for i in dataframe.index:
        # Update the all time high if it
        if dataframe['High'][i] > allTimeHigh:
            allTimeHigh = dataframe['High'][i]
        # Update drawdown if we are not in all time high
        else:
            currentDrawdown = (dataframe['Low'][i] / allTimeHigh - 1) * 100
            drawdown = min(drawdown, currentDrawdown)

    return drawdown

def buyAndHoldAnalysis(dataframe):
    trading_years = (dataframe.index[-1] - dataframe.index[0]).days / 365

    # Buy and hold stats setup
    buyAndHoldBuyPrice = dataframe['Close'][dataframe.index[0]]  # Buy in the close of the first day
    buyAndHoldSellPrice = dataframe['Close'][len(dataframe.index) - 1]  # Sell in the close of the last day
    buyAndHoldRentability = (buyAndHoldSellPrice / buyAndHoldBuyPrice - 1) * 100
    buyAndHoldMaxDrawdown = calculateBuyAndHoldDrawdown(dataframe)

    # https://www.investopedia.com/terms/c/cagr.asp
    CAGR = (pow(buyAndHoldSellPrice / buyAndHoldBuyPrice, 1 / trading_years) -1) * 100

    # https://www.investopedia.com/terms/m/mar-ratio.asp
    MAR = CAGR / buyAndHoldMaxDrawdown * -1

    return {
        'startDate': dataframe.index[0],
        'endDate': dataframe.index[-1],
        'rentability':buyAndHoldRentability,
        'drawdown': buyAndHoldMaxDrawdown,
        'CAGR': CAGR,
        'MAR': MAR
    }

def buyAndHoldLog(buyAndHold):

    metrics = 'CAGR: ' + str(round(buyAndHold['CAGR'],3)) + ', MAR: ' + str(round(buyAndHold['MAR'],3))

    log = 'Buy and hold since ' + str(buyAndHold['startDate']) + ' until ' + str(buyAndHold['endDate']) \
          +':\n\tRentability: ' + str(round(buyAndHold['rentability'], 2)) + '%' \
          + ' | drawdown: ' + str(round(buyAndHold['drawdown'], 2)) + '%  | ' + metrics

    return log