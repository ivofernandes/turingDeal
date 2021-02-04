from src.api import apiFinancialModelPrep
from src.api import apiYahooFinance

from src.aux.strategy import strategyBuyAndHold

incomeDataframe = apiFinancialModelPrep.getIncomeStatement('AAPL')

intervals = [3, 5, 8, 10, 12, 15, 30]
priceDataFrame = apiYahooFinance.getDailyData('AAPL', None, 30, intervals)
buyAndHold = strategyBuyAndHold.buyAndHoldAnalysis(priceDataFrame)
print(strategyBuyAndHold.buyAndHoldLog(buyAndHold))
priceDataFrame['Close'].plot()

print(incomeDataframe)