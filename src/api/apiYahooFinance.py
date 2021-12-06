import datetime
import pandas_datareader
from pandas_datareader._utils import RemoteDataError

from src.aux import indicators

# Download daily data for ticker since a specific date
from src.aux.utils import trading


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
def getDailyData(ticker,startDate, intervals,calculateIndicatorsFlag):
    # Get daily data
    df = downloadDailyData(ticker, startDate)

    if calculateIndicatorsFlag:
        calculateIndicators(df, intervals)
    calculateDrawdowns
    df = df.dropna(axis=1) # Drop columns that just have null values

    if calculateIndicatorsFlag:
        # Price changes since the day in the dataframe
        for period in [1, 7, 30]:
            # Future variation in price
            df['future_var_' + str(period)] = (df['Close'].pct_change(periods=-period) * -1) * 100
            # Past variation in volume
            df['volume_var_' + str(period)] = (df['Volume'].pct_change(periods=period)) * 100

    return df

def appendDailyAdj(ticker, targetDataFrame):

    tickerDf = getDailyData(ticker, None, [3, 5, 8, 10, 12, 15, 30], True).dropna(axis=1)
    for column in tickerDf.columns:
        targetDataFrame[ticker + '_' + column] = tickerDf[column]
        targetDataFrame[ticker + '_' + column] = targetDataFrame[ticker + '_' + column].astype(float)
    return targetDataFrame


def calculateDrawdowns(df, period, stop_loss):
    col_long_drawdown = 'long_drawdown_' + str(period)
    col_short_drawdown = 'short_drawdown_' + str(period)
    col_right_trade = 'right_trade_' + str(period)
    col_right_long_trade = 'right_long_trade_' + str(period)
    col_right_short_trade = 'right_short_trade_' + str(period)

    for column in [col_long_drawdown, col_short_drawdown, col_right_trade, col_right_long_trade, col_right_short_trade]:
        if column not in df:
            df.insert(5, column, 0.0)

    size = len(df.index)
    dates = df.index
    for i in range(0, size - period):
        date = dates[i]
        # Calculate the drawdown
        entry = df['Close'][date]
        var = df['future_var_' + str(period)][date]
        long_drawdown = 0
        short_drawdown = 0

        for j in range(i+1 , i+1 + period):
            low = df['Low'][dates[j]]
            high = df['High'][dates[j]]
            current_long_dd = trading.percentageChange(trading.LONG_POSITION, entry, low)
            long_drawdown = min(long_drawdown, current_long_dd)

            current_short_dd = trading.percentageChange(trading.SHORT_POSITION, entry, high)
            short_drawdown = min(short_drawdown, current_short_dd)

        right_trade = 0
        min_gain = 1

        if var > min_gain and long_drawdown * -1 < stop_loss:
            right_trade = 1
            df[col_right_long_trade][date] = 1
        elif var < min_gain * -1 and short_drawdown * -1 < stop_loss:
            right_trade = -1
            df[col_right_short_trade][date] = 1

        df[col_long_drawdown][date] = long_drawdown
        df[col_short_drawdown][date] = short_drawdown
        df[col_right_trade][date] = right_trade
    return df