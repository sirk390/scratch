import numpy as np

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

with open("data1.csv", "wb") as fout:
    for x, y in zip(X, Y):
        data = list(x)
        data.append(int(y[0]))
        fout.write(",".join(str(e) for e in data)  + "\r\n")
