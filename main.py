import datetime
import time
import json
from pathlib import Path

from src.api import apiFinancialModelPrep, apiDataHub
from src.api import apiYahooFinance
from src.aux.strategy import strategyBuyAndHold, fundamentalsAnalyser
from src.aux.utils import cache

def buyAndHold(ticker):
    # Strategy start date
    startyear = 1920
    startmonth = 1
    startday = 1
    startDate = datetime.datetime(startyear, startmonth, startday)
    intervals = [3, 5, 8, 10, 12, 15, 30]

    # Get daily data from yahoo finance
    priceDataFrame = apiYahooFinance.getDailyData(ticker, startDate, None, intervals, True)

    # Analyse buy and hold results
    buyAndHold = strategyBuyAndHold.buyAndHoldAnalysis(priceDataFrame)
    #priceDataFrame['Close'].plot()

    print(ticker + ": " + strategyBuyAndHold.buyAndHoldLog(buyAndHold))

def routine():

    data = apiDataHub.get(apiDataHub.SP500)

    for index in data.index:
        ticker = data['Symbol'][index]

        # If don't have the daframe locally try to get it
        if cache.existsFile('fundamental', ticker):
            try:
                print(ticker)

                fundamentalData = apiFinancialModelPrep.getFundamentals(ticker)

                cache.saveDataframe(fundamentalData, 'fundamental', ticker)

                time.sleep(5)
            except:
                pass


        print(ticker)
        fundamentalData = cache.loadDataframe('fundamental', ticker)

        if fundamentalData is not None:
            fundamentalsAnalyser.printKeyMetrics(fundamentalData)

            #buyAndHold(ticker)

#routine()
buyAndHold('^GSPC')