import math
import numpy as np
from numpy import vectorize
from scipy.optimize import minimize

@vectorize
def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z));

@vectorize
def logid(p):
    return math.log(p / (1.0 - p));

def logistic_regression_cost(Theta, X, Y):
    """ Cost and gradient for logistic regression (non regularized)
    
        Theta: np.matrix
        X: np.matrix
        X: np.array
    """
    #Theta = np.matrix(Theta).transpose()
    m , n = X.shape
    Theta = Theta.reshape((n, 1))
    cost_y0 = -np.log(1 - sigmoid(np.dot(X, Theta))) * (1 - Y)
    cost_y1 = -np.log(sigmoid(np.dot(X, Theta))) * Y
    J = (1.0/m) * sum(cost_y0 + cost_y1)
    print J, Theta.reshape(n)
    return J

def logistic_regression_gradient(Theta, X, Y):
    #print Theta, X, Y
    #Theta = Theta.T
    m , n = X.shape
    Theta = Theta.reshape((n, 1))
    #print (1.0/m) * (np.dot((sigmoid(X.dot(Theta)) - Y).T, X))
    gradient = (1.0/m) * (np.dot((sigmoid(X.dot(Theta)) - Y).T, X)).T
    #print Theta
    #print "====", gradient.reshape(2)
    print "grad", gradient.reshape(n), Theta.reshape(n)
    return gradient.reshape(n)
    #return gradient[:,0]


if __name__ == "__main__":
    F = 2
    M = 1000
    def gentest(n=F, m=M):
        X = np.random.rand(m, n)
        factors = np.random.rand(n, 1)
        res_Y = (np.dot(X, factors)) / sum(factors) 
        #test_y > thresholds
        Y = (res_Y > 0.5) * 1.0
        #print np.count_nonzero(y)
        return X, Y, factors
    X, Y, factors = gentest()
    print "factors", factors.reshape(F)
    theta_0 = np.zeros(F)
    
    #print res_Y.1
    #exit()
    #f = 
    res = minimize(logistic_regression_cost, 
                   theta_0,
                   jac=logistic_regression_gradient,
                   args = (X, Y),
                   method='BFGS', 
                   options={})
    
    print "========", sum(((sigmoid(X.dot(res.x)) > 0.5) * 1.0) == Y.T[0,:])
    """a = np.matrix([[1, 2, 3], [4, 5, 2]])
    
    print sum(a)
    print np.log(a)"""  