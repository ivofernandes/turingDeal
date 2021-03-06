import datetime
import pandas_datareader
from pandas_datareader._utils import RemoteDataError

from src.aux import indicators

# Download daily data for ticker since a specific date
def downloadDailyData(ticker, startDate):

    # Define the interval
    if startDate is None:
        startyear = 1928
        startmonth = 1
        startday = 1
        startDate = datetime.datetime(startyear, startmonth, startday)
    now = datetime.datetime.now()

    # Get data from yahoo finance
    try:
        df = pandas_datareader.get_data_yahoo(ticker, startDate, now)
    except RemoteDataError as e:
        print(e)
        exit()

    # Drop any duplicated values for the same date
    df = df.reset_index().drop_duplicates(subset='Date').set_index('Date')

    # Adjust prices for splits/dividends
    df['adj'] = df['Close'] / df['Adj Close']
    for column in ['High', 'Low', 'Open', 'Close']:
        df[column] = df[column] / df['adj']

    del df['Adj Close']
    del df['adj']

    return df

def calculateIndicators(df, intervals):
    df['Volume_close'] = df['Close'] * df['Volume']

    # Volume based indicators
    for period in intervals:
        df['VMA_' + str(period)] = df['Volume'].rolling(window=period).mean()
        df['VWMA_' + str(period)] = df['Volume_close'].rolling(window=period).sum() / df['Volume'].rolling(window=period).sum()

    # Indicators
    for interval in intervals:
        df['EMA_' + str(interval)] = round(df['Close'].ewm(span=interval, adjust=False).mean(), 2)
        df['STDDEV_' + str(interval)] = round(df['Close'].ewm(span=interval, adjust=False).std() * 100, 2)
        df['RSI_' + str(interval)] = indicators.RSI(df['Close'], interval)
        df['SMA_' + str(interval)] = df['Close'].rolling(window=interval).mean()

    # Differences from indicators
    for indicator in ['EMA_', 'STDDEV_', 'RSI_', 'SMA_', 'VMA_', 'VWMA_']:
        for period1 in intervals:
            for period2 in intervals:
                if period1 < period2:
                    ema1_title = indicator + str(period1)
                    ema2_title = indicator + str(period2)
                    df[ema1_title + '_' + ema2_title] = round(df[ema1_title] / df[ema2_title] - 1, 5)

# Get the dataframe from yahoo finance
def getDailyData(ticker,startDate, startDay, intervals,calculateIndicatorsFlag):
    # Get daily data
    df = downloadDailyData(ticker, startDate)

    if calculateIndicatorsFlag:
        calculateIndicators(df, intervals)

    df = df.dropna()

    if calculateIndicatorsFlag:
        # Price changes since the day in the dataframe
        for period in [1, 7, 30]:
            df['future_var_' + str(period)] = (df['Close'].pct_change(periods=-period) * -1) * 100

    return df

