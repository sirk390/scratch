import numpy as np
import sys
print sys.executable
from itertools import izip
from gendata import gendata
from util import softmax
from classify.util import normalize_rows, column_vector

np.seterr(all='raise', under="ignore")

def cost_function(W, x, y):
    """function computes the negative log likelyhood over input dataset
    """
    m = x.shape[0]
    vec = np.dot(x, W);
    sigmoid_activation = softmax(vec)
    index = [range(0, np.shape(sigmoid_activation)[0]), y]
    p = sigmoid_activation[index]
    l = -np.mean(np.log(p ))
    return l
        
def compute_gradients(out, y, x):
    """Gradient of cost function over a single example"""
    out[y] = out[y] - 1
    return np.outer(out, x)  # C x M


def gradients(W, x, y):
    """Gradient of cost function over all examples"""
    vec = np.dot(x, W);
    sigmoid_activation = softmax(vec)

    e = [compute_gradients(a, c, b) for a, c, b in izip(sigmoid_activation, y, x)]
    mean1 = np.sum(e, axis=0)
    return mean1

def indicator_array(pos, width):
    """ Zero everywhere except 1 at pos"""
    result = np.zeros(width)
    result[pos] = 1
    return result 

def indicator_matrix(indexes, width):
    """ Contains all zeros except a 1 on each row at the index of 'indexes' """
    return np.apply_along_axis(lambda y: indicator_array(y, width), 1, column_vector(indexes))

def gradients2(W, x, y):
    """Gradient of cost function over all examples"""
    C = W.shape[1]
    vec = np.dot(x, W);
    #print vec
    probas = softmax(vec) # M x C
    indicator_y = indicator_matrix(y, C) # M x C
    gradients = - np.dot((indicator_y - probas).T, x)  # C * N
    return gradients

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
        print i, cost_function(W, X, Y)
        grads = gradients2(W, X, Y)
        W -= grads.T * l

    return predict(W, X)



if __name__ == '__main__':
    N = 10
    C = 30
    M = 100
    X, Y, factors = gendata(n=N, m=M, c=C, seed=1)
    #X = np.hstack((X, np.ones((M,1)))) # Add column of 1's

    print Y
    Y2 = batch_gradient_descent(X, Y, C, l=1, nbiter=200)
    print Y == Y2
    print
