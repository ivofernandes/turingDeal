#https://colab.research.google.com/drive/1q_tnFbUQzzAkOZBP484jxke2Zr3Vm4jP#scrollTo=E1yEgGDGhP9T

import numpy as np
import pandas
from sklearn.datasets import load_iris
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from os import path
from src.api import apiYahooFinance

def createModel(X,y):

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    scaler_object = MinMaxScaler()

    scaler_object.fit(X_train)

    scaled_X_train = scaler_object.transform(X_train)
    scaled_X_test = scaler_object.transform(X_test)

    number_of_features = X.shape[1]
    possible_results = y.shape[1]
    model = None
    file = 'price_model30.h5'
    if path.exists(file):
        model = load_model(file)

    if model is None:
        model = Sequential()
        #
        for i in [3, 2, 1]:
            model.add(Dense(number_of_features*i, input_dim=number_of_features, activation='relu'))
            model.add(Dropout(0.2))
        model.add(Dense(possible_results, activation='softmax'))  # [0.2,0.3,0.5]
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.summary()

    model.fit(scaled_X_train, y_train, epochs=20, verbose=1)

    predictions = model.predict(scaled_X_test)

    conf = None
    #TODO make the confusion matrix work
    #conf = confusion_matrix(y_test, predictions)

    model.save('price_model30.h5', include_optimizer=True)

    new_model = load_model('price_model30.h5')

    print('Done')

    return model, conf

def cleanForTraining(dataframe):
    columnsToDrop = ['future_var_1', 'future_var_7', 'future_var_30', 'right_short_trade_30', 'short_drawdown_30',
                     'long_drawdown_30', 'right_long_trade_30', 'right_trade_30']
    for col in columnsToDrop:
        del dataframe[col]

# For AI we need to drop all the absolute data
def cleanDataFrameToAI(dataframe):
    columnsToDrop = ['Close', 'High', 'Low', 'Open', 'Volume', 'Volume_close']
    for col in columnsToDrop:
        del dataframe[col]

    for field in dataframe.columns:
        if field.count('_') == 1 and ('EMA' in field or 'SMA' in field):
            del dataframe[field]

# Get the dataframe results in y it is the right_short_trade_30, right_long_trade_30 matrix
# And also gets the X that is all the data possible to know in the current date
def getModelValuesFromDataframe(dataframe, cols):
    y = dataframe.filter(cols).values

    cleanForTraining(dataframe)

    X = dataframe.values

    return X, y

def getLastFromDataframe(limit):
    toTest = dataframe[-limit:]
    cleanForTraining(toTest)

    toTest = toTest.replace([np.inf, -np.inf], np.nan).dropna()

    return toTest

file = 'price_dataframe.csv'
dataframe = None

if path.exists(file):
    dataframe = pandas.read_csv('iris.csv', parse_dates=['Date'])
    dataframe = dataframe.set_index('Date')
else:
    dataframe = apiYahooFinance.getDailyData('^GSPC', None, [3, 5, 8, 10, 12, 15, 30], True)
    dataframe = apiYahooFinance.calculateDrawdowns(dataframe, 30, 4)

    selectedTickers = ['^VIX', '^IRX', '^TNX', '^IXIC',
               'XLE', 'XLF', 'XLU', 'XLI', 'XLV', 'XLY', 'XLP',
               'XLB']
    for ticker in selectedTickers:
        dataframe = apiYahooFinance.appendDailyAdj(ticker, dataframe)
        dataframe = dataframe.replace([np.inf, -np.inf], np.nan).dropna()
        print(ticker + ' > ' + str(dataframe.index[0]))
    dataframe.to_csv('price_dataframe.csv')

cleanDataFrameToAI(dataframe)

print('Dataframe ready')
dataframeToFit = dataframe.replace([np.inf, -np.inf], np.nan).dropna()

X, y = getModelValuesFromDataframe(dataframeToFit, ['right_short_trade_30', 'right_long_trade_30'])

toTest = getLastFromDataframe(30)

model, confusion_matrix = createModel(X,y)

real_prediction = model.predict_classes(toTest.values)
real_prediction_val = model.predict(toTest.values)
print(real_prediction)
