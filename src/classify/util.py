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
    """ Applyies softmax to each row """
    #substract max for numerical stability, else for large values will get NaNs due to exp
    #print vec 
    vec1 = np.exp(vec - column_vector(vec.max(axis=1)))
    res = vec1 / column_vector(np.sum(vec1, axis=1))
    return res



