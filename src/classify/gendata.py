import numpy as np
import random
from util import softmax
from util import column_vector
from classify.util import normalize_cols

np.set_printoptions(suppress=True)

FEATURES = 10
EXAMPLES = 1000
CLASSES = 10

def gendata(n=FEATURES, m=EXAMPLES, c=CLASSES, seed=0):
    np.random.seed(seed)
    X = np.random.rand(m, n)
    X = np.hstack((X, np.ones((m,1)))) # Add column of 1's for bias
    factors = np.random.rand(n+1, c) * 20 - 10 
    factors = normalize_cols(factors)
    predict = np.dot(X, factors)
    Y = np.apply_along_axis(np.argmax, axis=1, arr=softmax(predict))
    return X, Y, factors
 
if __name__ == '__main__':
    X, Y, factors = gendata(300, 30, 100, seed=4)
    print Y
