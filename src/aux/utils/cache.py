import os
from sys import path

import pandas as pd
from pathlib import Path
from os import path

def getFilePath(folder, ticker):
    # Get the file path
    script_location = Path(__file__).absolute().parent

    cacheFolderLocation = '../../../cache/'
    folderLocation = cacheFolderLocation + folder + '/'
    fileRelativeLocation = folderLocation + ticker + '.csv'

    file_location = script_location / fileRelativeLocation
    file_path = '/'.join(file_location.parts)

    # Guarantee that the folders exists
    os.makedirs(script_location / cacheFolderLocation, exist_ok=True)
    os.makedirs(script_location / folderLocation, exist_ok=True)

    return file_path

# Check if a file exists
def existsFile(folder, ticker):
    file_path = getFilePath(folder, ticker)
    exists = path.exists(file_path)
    return exists

# Save dataframe to a cache folder
def saveDataframe(dataframe, folder, ticker):

    file_path = getFilePath(folder, ticker)
    dataframe.to_csv(file_path)

# Load daframe from a cache folder
def loadDataframe(folder, ticker):
    file_path = getFilePath(folder, ticker)

    exists = path.exists(file_path)

    if exists:
        dataframe = pd.read_csv(file_path)
        return dataframe