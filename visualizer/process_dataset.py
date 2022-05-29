from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split

import pickle

Xs = []
Ys = []
with open('output.data', 'rb') as f:
    Xs, Ys = pickle.load(f)

X_train, X_test, y_train, y_test = train_test_split(Xs, Ys, test_size = 0.25, random_state=1)

print(len(X_train), len(X_test))

regr = MLPRegressor(random_state=1, hidden_layer_sizes=(1024, 1024, 1024,)).fit(X_train, y_train)
print(regr.score(X_test, y_test))

with open('regressor.data', 'wb') as f:
    pickle.dump(regr, f)

i = 1100
print(X_test[i])
print(y_test[i])
print(regr.predict([X_test[i]])[0])