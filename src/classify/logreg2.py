from sklearn import linear_model
import numpy as np
from sklearn import datasets, linear_model
from classify.gendata import gendata

N = 30
C = 30
M = 1000

# Use only one feature
X, Y, factors = gendata(n=N, m=M, c=C, seed=2)

# Create linear regression object
regr = linear_model.LogisticRegression(solver="newton-cg", C=1)

# Train the model using the training sets
regr.fit(X, Y)

# The coefficients
print('Coefficients: \n', regr.coef_)

print regr.predict(X) == Y
"""
print("Residual sum of squares: %.2f"
      % np.mean((regr.predict(diabetes_X_test) - diabetes_y_test) ** 2))
# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % regr.score(diabetes_X_test, diabetes_y_test))

# Plot outputs
plt.scatter(diabetes_X_test, diabetes_y_test,  color='black')
plt.plot(diabetes_X_test, regr.predict(diabetes_X_test), color='blue',
         linewidth=3)

plt.xticks(())
plt.yticks(())

plt.show()"""
