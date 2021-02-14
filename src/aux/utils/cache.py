import pandas as pd
from pathlib import Path
import os

# You should change 'test' to your preferred folder.

def saveDataframe(dataframe, folder, ticker):
    script_location = Path(__file__).absolute().parent

    cacheFolderLocation = '../../../cache/'
    folderLocation = cacheFolderLocation + folder + '/'
    fileRelativeLocation = folderLocation + ticker + '.csv'

    os.makedirs(script_location / cacheFolderLocation, exist_ok=True)
    os.makedirs(script_location / folderLocation, exist_ok=True)

    file_location = script_location / fileRelativeLocation
    dataframe.to_csv(file_location)