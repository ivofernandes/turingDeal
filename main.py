import datetime

from src.api import apiYahooFinance
from src.aux.strategy import strategyBuyAndHold

def routine():

    # Strategy start date
    startyear = 1920
    startmonth = 1
    startday = 1
    startDate = datetime.datetime(startyear, startmonth, startday)
    intervals = [3, 5, 8, 10, 12, 15, 30]

    # Get daily data from yahoo finance
    priceDataFrame = apiYahooFinance.getDailyData('^GSPC', startDate, None, intervals, False)

    # Analyse buy and hold results
    buyAndHold = strategyBuyAndHold.buyAndHoldAnalysis(priceDataFrame)
    priceDataFrame['Close'].plot()

    print(strategyBuyAndHold.buyAndHoldLog(buyAndHold))

routine()