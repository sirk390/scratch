impo rt unittest
from collections import deque

class SetKey(object):
    def __init__(self, k, v):
        self.k = k
        self.v = v
    
class DelKey(object):
    def __init__(self, k):
        self.k = k

class VersionedDict():
    """ how to handle conflicts? 
    """
    def __init__(self, startvalues={}, version=0):
        self.startvalues = startvalues
        self.version = version
        self.changes = deque()
    
    def apply(self, changes):
        newversion = self.version + 1
        self.version = newversion
        self.changes.append((newversion, changes))
        return newversion
    
    def query(self, version, keys):
        for ver, ops in self.changes:
            if ver <= version:
                ops
    
    def __getitem__(self, key):
        return self.query(self.version, key)
    
class Test1(unittest.TestCase):
    def test_1(self):
        d = VersionedDict()
        
        d.apply([SetKey("n", 1), SetKey("p", 2)])
        
        self.assertEquals(d["n"], 1)

class Test2(unittest.TestCase):
    def test_1(self):
        d1 = Dict1()

        d2 = Dict1()
        
        d1["n"] = 1
        
        self.assertEquals(d["n"], 1)
        

        
if __name__ == '__main__':
    unittest.main()