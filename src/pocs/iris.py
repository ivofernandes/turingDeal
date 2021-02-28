import numpy as np
from sklearn.datasets import load_iris
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical

iris = load_iris()
typeIris = type(iris)
print(iris.DESCR)

X = iris.data
y = iris.target

y = to_categorical(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

scaler_object = MinMaxScaler()

scaler_object.fit(X_train)

scaled_X_train = scaler_object.transform(X_train)
scaled_X_test = scaler_object.transform(X_test)

model = Sequential()
model.add(Dense(8, input_dim=4, activation='relu'))
model.add(Dense(8, input_dim=4, activation='relu'))
model.add(Dense(3, activation='softmax')) # [0.2,0.3,0.5]
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

model.fit(scaled_X_train, y_train,epochs=150, verbose=1)

predictions = model.predict_classes(scaled_X_test)

y_test .argmax(axis=1)

conf = confusion_matrix(y_test.argmax(axis=1), predictions)

print(classification_report(y_test.argmax(axis=1), predictions))

model.save('iris_model.h5')

new_model = load_model('iris_model.h5')

print('Done')
