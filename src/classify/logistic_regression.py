import numpy as np
import sys
import traceback
print sys.executable
from itertools import izip
from gendata import gendata
from util import softmax
from classify.util import normalize_rows, column_vector, log_softmax

np.seterr(all='raise', under="ignore")

def cost_function(W, x, y):
    """function computes the negative log likelyhood over input dataset
    """
    m = x.shape[0]
    vec = np.dot(x, W);
    sigmoid_activation = np.apply_along_axis(log_softmax, 1, vec)
    index = [range(0, m), y]
    p = sigmoid_activation[index]
    l = -np.mean(p)
    regularization = 0.5 * np.sum(np.square(W)) # Should omit first class
    return l + regularization
        
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

def gradients2(W, x, y, reg_lambda=1.0):
    """Gradient of cost function over all examples"""
    C = W.shape[1]
    M, _ = X.shape
    vec = np.dot(x, W);
    #print vec
    probas = softmax(vec) # M x C
    indicator_y = indicator_matrix(y, C) # M x C
    gradients = - np.dot((indicator_y - probas).T, x).T  # C * N
    gradients += reg_lambda * W 
    return gradients

def predict(W, x):
    """function predicts the probability of input vector x
       the output y is MX1 vector (M is no of classse)
    """
    values = softmax(np.dot(x, W))
    return np.argmax(values, axis=1)


def batch_gradient_descent(X, Y, C, l_start=1, converge_percent=0.01, maxiter=1000, progress_callback=lambda *args: None):
    """ Batch gradient descent with 'bold driver' learning rate adaptation """
    
    n = X.shape[1]
    W = np.zeros((n, C)) #n+1, c
    l = l_start
    last_cost  = None
    for i in range(maxiter):
        cost = cost_function(W, X, Y)
        progress_callback(i, cost, l)
        grads = gradients2(W, X, Y)
        if last_cost is not None and cost is not None:
            change = (last_cost - cost) / last_cost
            if change < 0: # bold driver
                l /= 2.0
            elif change *100 < converge_percent:
                return W
        l = l * 1.1
        W -= grads * l
        last_cost = cost
    return W


if __name__ == '__main__':
    N = 8
    C = 30
    M = 1000
    X, Y, factors = gendata(n=N, m=M, c=C, seed=1)
    #X = np.hstack((X, np.ones((M,1)))) # Add column of 1's

    def print_progress(i, cost, l):
        print i, cost, l

    W = batch_gradient_descent(X, Y, C, maxiter=1000, progress_callback=print_progress)
    Y2 = predict(W, X)
    print Y == Y2
    print Y
    print W


