import unittest
from collections import deque
from concurrent.futures import Future


class Dict(object):
    """ how to handle conflicts? 
    """
    def __init__(self, values={}):
        self.values = values
    
    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

class DictAccessor(object):
    def __init__(self, dict):
        self.dict = dict

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

class AsynchDict(object):
    def __init__(self):
        pass

    def set(self, key, value):
        f = Future()
        return f

    def get(self, key):
        pass

class Test2(unittest.TestCase):
    """
    def test_1(self):
        d1 = Dict()

        d2 = DictAccessor(d1)
        
        d1["n"] = 1
        
        self.assertEquals(d2["n"], 1)
    """
    def test_2(self):
        d1 = AsynchDict()
        
        tx = d1.start()
        tx.set("n", 1)
        tx.get("n")
        tx.commit()
        
        #d1.set("n", 1)# need transactions
        
        self.assertEquals(d2["n"], 1)

        
if __name__ == '__main__':
    unittest.main()