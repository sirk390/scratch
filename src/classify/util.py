import numpy as np
import math

def normalize_cols(vect):
    return  vect / vect.sum(axis=0)


def normalize_rows(vect):
    return  vect / (column_vector(vect.sum(axis=1)) + [0.00001])


def column_vector(values):
    """ Default ndarray transpose does not transpose to a column vector """
    return values[:,np.newaxis]


def sigmoid(X):
    den = 1.0 + math.e ** (-1.0 * X) 
    d = 1.0 / den 
    return d
    

def softmax(vec):
    """ Softmax (for matrix input) """
    #substract max for numerical stability, else for large values will get NaNs due to exp
    #print vec 
    vec1 = np.exp(vec - column_vector(vec.max(axis=1)))
    res = vec1 / column_vector(np.sum(vec1, axis=1))
    return res

def log_softmax(vec):
    ''' Log of softmax 
    
        Due to rounding errors the softmax probability of one values can get to 0. 
        Taking the log of 0 would generate -inf, so in this function we compute the log together with the softmax
        to avoid this issue.
    '''
    max_vec = max(0.0, np.max(vec))
    rebased_vec = vec - max_vec
    return rebased_vec - np.log(np.sum(np.exp(rebased_vec))) 


if __name__ == '__main__':
    print np.log(softmax(np.array([[0,0,100]])))
    
    print softmax(np.array([[1, 5,0.2]]))
    print np.log(softmax(np.array([[1, 5, 0.2]])))
    print log_softmax(np.array([1, 5,0.2]))
    
    print np.logaddexp.reduce([1, 5,0.2])
    print np.logaddexp(np.logaddexp(1, 5), 0.2)