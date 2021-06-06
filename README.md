# turingDeal
Hard science approach to investing

This project is being developed using python and the dataframe lib pandas

The IDE used is Pycharm Community
https://www.jetbrains.com/pycharm/download/

This is a screenshot of the dataframe you can analyse if you put a breakpoint at main.py:22

![price dataframe](https://github.com/ivofernandes/turingdeal/blob/master/screenshots/priceDataFrameWithPlot.png?raw=true)

Other screenshots from the app:

. Financial model prep data api to pandas dataframe:
![financial model prep data](https://github.com/ivofernandes/turingdeal/blob/master/screenshots/financialModelPrepDataframe.png?raw=true)


# Environment Setup
To setup the environment:
. pip install -r requirements.txt

Before do a pull request ensure that any package dependencies are saved in requirements.txt
.  pip freeze > requirements.txt

To use financial model prep with and API key create a folder "configs" with a file called variables.json in the following content:

{
  "FINANCIAL_MODEL_PREP_API_KEY":""
}

To know how this API key works and get an API key from 
https://financialmodelingprep.com/how-to/how-to-call-the-financial-modeling-prep-api-with-python

This logic can be seen in the file apiFinancialModelPrep.py

To run the POC of AI you may need to install tensorflow manually 
https://www.tensorflow.org/install
