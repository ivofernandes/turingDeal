
"""
To make it work do a get an api key from here https://financialmodelingprep.com/developer/docs/dashboard
and export it to a file with a path of turingDeal/configs/variables.json file with a content like this one:

{
  "FINANCIAL_MODEL_PREP_API_KEY":"PUT YOUR KEY HERE!!!"
}

"""
import json
from pathlib import Path

def loadVariables():
    try:
        script_location = Path(__file__).absolute().parent
        file_location = script_location / '../../../configs/variables.json'
        file = file_location.open()

        data = json.load(file)
        return data
    except:
        return {}

def getConfig(key, default):
    variables = loadVariables()

    if key in variables:
        return variables[key]
    else:
        return default