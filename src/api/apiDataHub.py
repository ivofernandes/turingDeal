import datapackage
import pandas as pd

NASDAQ = 'nasdaq-listings'
SP500 = 's-and-p-500-companies'


def get(market):
    data_url = 'https://datahub.io/core/' + market + '/datapackage.json'
    # to load Data Package into storage
    package = datapackage.Package(data_url)

    # to load only tabular data
    resources = package.resources
    for resource in resources:
        if resource.tabular:
            data = pd.read_csv(resource.descriptor['path'])

            return data