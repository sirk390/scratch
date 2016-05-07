import numpy as np
from itertools import izip
from gendata import gendata
from util import softmax
from classify.util import normalize_rows

np.seterr(all='raise', under="ignore")

def cost_function(W, x, y):
    """function computes the negative log likelyhood over input dataset 
    """
    m = x.shape[0]                 
    vec = np.dot(x, W);
    sigmoid_activation = softmax(vec)
    index = [range(0, m), y]
    p = sigmoid_activation[index]
    l = -np.mean(np.log(p + 0.000001))
    return l


def compute_gradients(out, y, x):
    """Gradient of cost function over a single example"""
    out[y] = out[y] - 1  
    return np.outer(out, x)            


def gradients(W, x, y):
    """Gradient of cost function over all examples"""
    vec = np.dot(x, W);                 
    sigmoid_activation = softmax(vec)
     
    e = [compute_gradients(a, c, b) for a, c, b in izip(sigmoid_activation, y, x)]
    mean1 = np.sum(e, axis=0)        
    #  mean1 = mean1.T.flatten()
    return mean1


def predict(W, x):  
    """function predicts the probability of input vector x
       the output y is MX1 vector (M is no of classse) 
    """
    values = softmax(np.dot(x, W))
    return np.argmax(values, axis=1)


def batch_gradient_descent(X, Y, C, l=1, nbiter=10): 
    n = X.shape[1]
    W = np.zeros((n, C)) #n+1, c
    for i in range(nbiter):
        print cost_function(W, X, Y)
        grads = gradients(W, X, Y)
        W -= grads.T * l
    return predict(W, X)

 

if __name__ == '__main__':
    N = 10
    C = 10
    M = 1000
    X, Y, factors = gendata(n=N, m=M, c=C, seed=1)
    
    #X = np.hstack((X, np.ones((M,1)))) # Add column of 1's
    
    print Y
    Y2 = batch_gradient_descent(X, Y, C, l=1, nbiter=100)
    print Y == Y2
    print