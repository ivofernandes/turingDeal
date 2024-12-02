import os

import pandas as pd
import requests

from src.aux import settings

# https://fred.stlouisfed.org/series/MABMM301USM189S
def get_dataframe_from_fred(industry='USRERENTLEARQGSP'):
    base_url = 'https://api.stlouisfed.org/fred/series/observations'
    url = f'{base_url}?series_id={industry}&api_key={settings.fred_api_key}&file_type=json&realtime_start=1776-07-04'

    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data['observations'])

    return df


def clean_fred(df):

    # Remove the column realtime_start
    df = df.drop(columns=['realtime_start', 'realtime_end'])

    # Keep just the last date when find duplicated dates
    df = df.drop_duplicates(subset='date', keep='last')
    # Set the date as index
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')

    # Convert to float, coercing errors to NaN
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # Drop rows with NaN values
    df = df.dropna(subset=['value'])

    # Ensure the column is of float type
    df['value'] = df['value'].astype(float)

    # Rename the column value to Close, Adj Close, High, Low, Open
    df = df.rename(columns={'value': 'Close'})
    columns = ['High', 'Low', 'Open', 'Adj Close', 'Unadjusted Close']
    for column in columns:
        df[column] = df['Close']

    # Add a column Volume with 1
    df['Volume'] = 1

    return df


def get_file_path(ticker):
    fred_folder_path = f'{settings.CACHE_FOLDER}/prices/fred/'
    os.makedirs(fred_folder_path, exist_ok=True)
    file_path = f'{fred_folder_path}{ticker}.csv'
    return file_path


def get_fred_from_cache(ticker):
    file_path = get_file_path(ticker)

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df

    return None


def store_fred_data(df, ticker):
    file_path = get_file_path(ticker)
    df.to_csv(file_path, index=False)


def get_price_dataframe(ticker):
    # Remove fred> from the ticker
    ticker = ticker.upper().replace('FRED>', '')

    df = get_fred_from_cache(ticker)
    if df is not None:
        df = clean_fred(df)
        return df, True

    # Get the data from the internet
    df = get_dataframe_from_fred(industry=ticker)
    store_fred_data(df, ticker)

    df = clean_fred(df)
    # Return the dataframe
    return df, True


def is_fred_ticker(ticker):
    if ticker.lower().startswith('fred>'):
        return True
    return False


fred_dataframe, has_data = get_price_dataframe('MABMM301USM189S')
print(fred_dataframe.head())
