from src.api import apiFinancialModelPrep
from src.api import apiYahooFinance

import matplotlib

priceDataFrame = apiYahooFinance.getDailyData('AAPL', None, 30)

incomeDataframe = apiFinancialModelPrep.getIncomeStatement('AAPL')

print(incomeDataframe)