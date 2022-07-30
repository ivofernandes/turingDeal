import sys
import time

from src.api import apiFinancialModelPrep, apiDataHub
from src.aux.strategy import fundamentalsAnalyser
from src.aux.utils import cache


def routine():
    data = apiDataHub.get(apiDataHub.SP500)

    for index in data.index:
        ticker = data['Symbol'][index]

        # If don't have the daframe locally try to get it
        if not cache.existsFile('fundamental', ticker):
            try:
                print(ticker)

                fundamental_data = apiFinancialModelPrep.getFundamentals(ticker)

                cache.saveDataframe(fundamental_data, 'fundamental', ticker)

                time.sleep(5)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                pass

        print(ticker)
        fundamental_data = cache.loadDataframe('fundamental', ticker)

        if fundamental_data is not None:
            fundamentalsAnalyser.printKeyMetrics(fundamental_data)

            # buyAndHold(ticker)


routine()
