from src.api import apiFinancialModelPrep
import matplotlib

incomeDataframe = apiFinancialModelPrep.getIncomeStatement('AAPL')

print(incomeDataframe)