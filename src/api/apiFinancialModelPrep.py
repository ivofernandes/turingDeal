import urllib.request, json, pandas

financialModelUrl = 'https://financialmodelingprep.com/api/v3/'
apiKey = 'demo'

# Get a basic income statement dataframe
def getIncomeStatementBasic(symbol):

    urlString = financialModelUrl + 'income-statement/' + symbol + '?period=quarter&apikey=' + apiKey
    with urllib.request.urlopen(urlString) as url:
        # Get the dataframe
        data = json.loads(url.read().decode())
        dataframe = pandas.json_normalize(data).convert_dtypes()

        # Drop rows after lose notion of the filling index and put filling date as index
        dataframe['fillingDate'] = dataframe['fillingDate'].apply(lambda x: x.replace(' 00:00:00', '').strip())
        validFillingDate = True
        for i in dataframe.index:
            if dataframe['fillingDate'][i] == '0':
                validFillingDate = False
            if not validFillingDate:
                dataframe.drop(i, inplace=True)
        dataframe['fillingDate'] = pandas.to_datetime(dataframe['fillingDate'], format='%Y-%m-%d')
        dataframe = dataframe.set_index('fillingDate')

        dataframe['absolute_quarter'] = dataframe.index.year * 4 + dataframe.index.quarter - 1

        # Reverse the dataframe to go
        dataframe = dataframe.iloc[::-1]
        return dataframe

# Get income statement with some calculated data
def getIncomeStatement(symbol):
    dataframe = getIncomeStatementBasic(symbol)

    # Caculate revenue year over year, and it's last 4 quarters moving avering
    dataframe['revenue_yoy'] = (dataframe['revenue'].pct_change(periods=4)) * 100
    dataframe['revenue_yoy_avg4'] = dataframe['revenue_yoy'].rolling(window=4).mean()

    # Caculate net margin year over year, and it's last 4 quarters moving avering
    dataframe['netMargin_yoy'] = (dataframe['netIncomeRatio'].pct_change(periods=4)) * 100
    dataframe['netMargin_yoy_avg4'] = dataframe['netMargin_yoy'].rolling(window=4).mean()

    return dataframe


