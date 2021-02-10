####################################################################################
# This apiFinancialModelPrep means to be an interface to financialmodelingprep.com #
# and do basic tasks like transform the returned json in pandas dataframe and join #
# different kind of data in the same dataframe:                                    #
# income statement, balance sheet and so on                                        #
#                                                                                  #
# For more documentation about financialmodeling prep you can see the documentaion #
# https://financialmodelingprep.com/developer/docs/                                #
####################################################################################

import math
import os
import urllib.request, json, pandas, numpy
from pathlib import Path

import numpy

from src.aux.utils import config

financialModelUrl = 'https://financialmodelingprep.com/api/v3/'
apiKey = config.getConfig('FINANCIAL_MODEL_PREP_API_KEY','demo')

# Get a basic income statement dataframe
def getBasicDataframe(ticker, endpoint):

    urlString = financialModelUrl + endpoint + '/' + ticker + '?period=quarter&apikey=' + apiKey
    with urllib.request.urlopen(urlString) as url:
        # Get the dataframe
        data = json.loads(url.read().decode())
        dataframe = pandas.json_normalize(data).convert_dtypes()

        # Reverse the dataframe to go from the first report until the last
        dataframe = dataframe.iloc[::-1]

        return dataframe

# Get income statement with some calculated data
def cleanQuarterData(dataframe, key):
    # Drop rows after lose notion of the filling index and put filling date as index
    dataframe = dataframe.dropna()
    dataframe[key] = dataframe[key].apply(lambda x: x.replace(' 00:00:00', '').strip())
    validFillingDate = True
    for i in dataframe.index[::-1]:
        if dataframe[key][i] == '0':
            validFillingDate = False
        if not validFillingDate:
            dataframe.drop(i, inplace=True)
    dataframe[key] = pandas.to_datetime(dataframe[key], format='%Y-%m-%d')
    dataframe = dataframe.set_index(key)

    dataframe['absolute_quarter'] = dataframe.index.year * 4 + dataframe.index.quarter

    # Ensure that we have one and only one report for each quarter
    reportDates = []
    previousQuarter = None

    dates = list( dict.fromkeys(dataframe.index))
    for date in dates:

        reportDates.append(date)

        # Check if a report is out of order or duplicated
        duplicatedReport = type(dataframe['absolute_quarter'][date]) == pandas.core.series.Series
        invalidReport = duplicatedReport \
                        or (previousQuarter is not None and dataframe['absolute_quarter'][date] != previousQuarter + 1)

        if invalidReport:
            # Update the last report quarter
            if duplicatedReport:
                previousQuarter = dataframe['absolute_quarter'][date][0]
            else:
                previousQuarter = dataframe['absolute_quarter'][date]

            # Clear all reports before the invalid report
            for reportDate in reportDates:
                dataframe = dataframe.drop(reportDate)
            reportDates.clear()
        else:
            previousQuarter = dataframe['absolute_quarter'][date]
    return dataframe

# Get income statement and calculate useful metrics
def getIncomeStatement(ticker):
    dataframe = getBasicDataframe(ticker, 'income-statement')

    # ratios for revenue spending
    dataframe['R&D_revenue'] = dataframe['researchAndDevelopmentExpenses'] / dataframe['revenue']
    dataframe['admin_revenue'] = dataframe['generalAndAdministrativeExpenses'] / dataframe['revenue']
    dataframe['sales_revenue'] = dataframe['sellingAndMarketingExpenses'] / dataframe['revenue']

    # Caculate revenue year over year, and it's last 4 quarters moving avering
    dataframe['revenue_yoy'] = (dataframe['revenue'].pct_change(periods=4)) * 100
    dataframe['revenue_yoy_avg4'] = dataframe['revenue_yoy'].rolling(window=4).mean()

    # Caculate net margin year over year, and it's last 4 quarters moving avering
    dataframe['netMargin_yoy'] = (dataframe['netIncomeRatio'].pct_change(periods=4)) * 100
    dataframe['netMargin_yoy_avg4'] = dataframe['netMargin_yoy'].rolling(window=4).mean()

    dataframe = cleanQuarterData(dataframe, 'fillingDate')

    return dataframe

# Get balance sheet and calculate useful metrics
def getBalanceSheet(ticker):
    dataframe = getBasicDataframe(ticker, 'balance-sheet-statement')

    dataframe['equity_yoy'] = (dataframe['totalStockholdersEquity'].pct_change(periods=4)) * 100

    dataframe = cleanQuarterData(dataframe, 'fillingDate')

    return dataframe


# Get cash flow statement
def getCashFlowStatement(ticker):
    dataframe = getBasicDataframe(ticker, 'cash-flow-statement')

    dataframe = cleanQuarterData(dataframe, 'fillingDate')

    return dataframe

# Get balance sheet and calculate useful metrics
def getKeyMetrics(ticker):
    dataframe = getBasicDataframe(ticker, 'key-metrics')

    return dataframe

# join multiple dataframes in one unified dataframe
def joinQuarterDataframes(firstDataframe, secondDataframe, keyToJoin):

    # Add columns
    ignoreColumns = ['date', 'period', 'reportedCurrency', 'symbol', 'acceptedDate','link', 'finalLink']
    for column in secondDataframe.columns:
        if column not in ignoreColumns:
            # Add an empty column
            firstDataframe[column] = pandas.Series(numpy.zeros(len(firstDataframe)), index=firstDataframe.index)
            firstDataframe[column] = math.nan

            # Add data to the new columns
    for date in firstDataframe.index:
        # Find the right row in the second dataframe
        row = None
        if keyToJoin is None:
            row = secondDataframe[secondDataframe.index == date]
        else:
            row = secondDataframe[secondDataframe[keyToJoin] == str(firstDataframe[keyToJoin][date])]

        # Join each column
        for column in secondDataframe.columns:
            if column not in ignoreColumns:
                if pandas.api.types.is_numeric_dtype(row[column]):
                    try:
                        firstDataframe[column][date] = row[column]
                    except:
                        pass # Best effort

    return firstDataframe




def getFundamentals(ticker):
    incomeStatement = getIncomeStatement(ticker)

    # join balance sheet with income statement
    balanceSheet = getBalanceSheet(ticker)
    finalDataframe = joinQuarterDataframes(incomeStatement, balanceSheet, None)

    # Join cash flow
    cashflow = getCashFlowStatement(ticker)
    finalDataframe = joinQuarterDataframes(finalDataframe, cashflow, None)

    # Join key metrics
    keyMetrics = getKeyMetrics(ticker)
    finalDataframe = joinQuarterDataframes(finalDataframe, keyMetrics,'date')

    return finalDataframe