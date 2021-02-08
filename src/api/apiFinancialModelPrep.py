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
import urllib.request, json, pandas

import numpy

financialModelUrl = 'https://financialmodelingprep.com/api/v3/'
apiKey = 'demo'

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
def cleanIncomeStatement(dataframe):
    # Drop rows after lose notion of the filling index and put filling date as index
    dataframe['fillingDate'] = dataframe['fillingDate'].apply(lambda x: x.replace(' 00:00:00', '').strip())
    validFillingDate = True
    for i in dataframe.index[::-1]:
        if dataframe['fillingDate'][i] == '0':
            validFillingDate = False
        if not validFillingDate:
            dataframe.drop(i, inplace=True)
    dataframe['fillingDate'] = pandas.to_datetime(dataframe['fillingDate'], format='%Y-%m-%d')
    dataframe = dataframe.set_index('fillingDate')

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

    # Caculate revenue year over year, and it's last 4 quarters moving avering
    dataframe['revenue_yoy'] = (dataframe['revenue'].pct_change(periods=4)) * 100
    dataframe['revenue_yoy_avg4'] = dataframe['revenue_yoy'].rolling(window=4).mean()

    # Caculate net margin year over year, and it's last 4 quarters moving avering
    dataframe['netMargin_yoy'] = (dataframe['netIncomeRatio'].pct_change(periods=4)) * 100
    dataframe['netMargin_yoy_avg4'] = dataframe['netMargin_yoy'].rolling(window=4).mean()

    dataframe = cleanIncomeStatement(dataframe)

    return dataframe

# Get balance sheet and calculate useful metrics
def getBalanceSheet(ticker):
    balanceSheet = getBasicDataframe(ticker, 'balance-sheet-statement')

    balanceSheet = cleanIncomeStatement(balanceSheet)

    return balanceSheet

# join multiple dataframes in one unified dataframe
def joinQuarterDataframes(firstDataframe, secondDataframe):
    # Validate if the number of rows match
    valid = True
    if len(firstDataframe[firstDataframe.columns[0]]) != len(secondDataframe[secondDataframe.columns[0]]):
        valid = False
    # Validate if the quarters range is the same
    else:
        rows = len(firstDataframe[firstDataframe.columns[0]])
        for date in range(0, rows):
            if firstDataframe['absolute_quarter'][date] != secondDataframe['absolute_quarter'][date]:
                valid = False
                break

    if valid:
        # Add empty columns for the fundamentals
        ignoreColumns = ['date', 'period', 'reportedCurrency', 'symbol', 'acceptedDate','link', 'finalLink']
        for column in secondDataframe.columns:
            if column not in ignoreColumns:
                firstDataframe[column] = secondDataframe[column]

def getFundamentals(ticker):
    incomeStatement = getIncomeStatement(ticker)

    balanceSheet = getBalanceSheet(ticker)

    # join balance sheet with income statement
    joinQuarterDataframes(incomeStatement, balanceSheet)

    return incomeStatement