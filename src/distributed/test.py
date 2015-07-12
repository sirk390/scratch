import unittest
from collections import deque

class SetKey(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
    def apply(self, dct):
        dct[self.key] = self.value
        
class DelKey(object):
    def __init__(self, key):
        self.key = key
    def apply(self, dct):
        del dct[self.key]
        
class LogSimple(object):
    def __init__(self, value=None):
        pass

class Transaction():
    def __init__(self, operations=None):
        self.operations = operations or []


class DictTransaction(Transaction):
    def __init__(self, dct, operations=None):
        self.dct = dct

    def set(self, key, value):
        self.operations.append(SetKey(key, value))

    def del_(self, key):
        self.dct.get(key, self)
        self.operations.append(DelKey(key))

    def get(self, key):
        return self.dct.get(key, self)

    def commit(self):
        self.dct.commit(self)

class LogCounter(object):
    """ keep record of applied tx
    """
    def __init__(self, value=0):
        self.value = value
        self.applied_txs = deque()
        self.version = 0

    def apply(self, ops):
        pass
    
    def simulate(self, tx_list, key):
        pass

class LogDict(object):
    """ keep record of applied tx
    """
    def __init__(self, values=None):
        self.values = {} if values is None else values
        self.applied_txs = deque()
        self.version = 0

    def apply(self, ops):
        for o in ops:
            o.apply(self.values)
        self.version += 1

    def get(self, key):
        return self.values[key]
    
    def simulate(self, tx_list, key):
        key_exists = key in self.values
        key_value = self.values.get(key)
        for tx in tx_list:
            for o in tx.operations:
                if type(o) is SetKey and o.key == key:
                    key_exists = True
                    key_value = o.value
                if type(o) is DelKey and o.key == key:
                    key_exists = False
        return key_exists, key_value

# track open transactions for a dict
# keep record of applied tx
# keep version number
# track operations of transactions
#
class TransactionalDict(LogDict):
    """ how to handle conflicts?
        * first commiter (ok)
        * first starter
    """
    def __init__(self, values=None):
        super(TransactionalDict, self).__init__(values)
        self.txs = deque()
        self.commited ={}

    def start(self, tx=None):
        tx = tx or Transaction(self)
        self.commited[tx] = False
        self.txs.append(tx)
        return tx

    def commit(self, tx):
        if tx == self.txs[0]:
            self.apply(tx.operations)
            del self.commited[tx]
        else:
            self.commited[tx] = True
            # wait as some other transactions stil need to be applied first
            
    def get(self, key, tx=None):
        if tx == None:
            return super(TransactionalDict, self).get(key)
        tx_list = [t for t in self.txs if (self.commited[t] or t == tx)]
        key_exists, key_value = super(TransactionalDict, self).simulate(tx_list, key)
        if not key_exists:
            raise KeyError(key)
        return key_value

    def __getitem__(self, key):
        pass


class Test1(unittest.TestCase):
    def test_UncommitedTransaction_WithValueSet_GetReturnsValue(self):
        a = TransactionalDict()
        tx = a.start()
        tx.set("a", "6")
        
        v = tx.get("a")
        
        self.assertEquals(v, "6")
        
    def test_UncommitedTransaction_WithValueUnSet_RaisesKeyError(self):
        a = TransactionalDict()
        tx = a.start()
        
        with self.assertRaises(KeyError):
            tx.get("a")

    def test_UnommitedTransaction_WithValueSet_GetOnDictRaises(self):
        d = TransactionalDict()
        tx = d.start()
        tx.set("a", "6")
        
        with self.assertRaises(KeyError):
            d.get("a")
        
    def test_CommitedTransaction_WithValueSet_GetOnDictReturnsValue(self):
        d = TransactionalDict()
        tx = d.start()
        tx.set("a", "6")
        tx.commit()
        
        v = d.get("a")
        
        self.assertEquals(v, "6")
  
    def test_UncommitedTransaction_WithValueRemoved_ReturnsValueOnDict(self):
        d = TransactionalDict({"a" : "6"})
        tx = d.start()
        tx.del_("a")
        
        v = d.get("a")
        
        self.assertEquals(v, "6")

    def test_UncommitedTransaction_WithValueRemoved_RaisesOnTx(self):
        d = TransactionalDict({"a" : "6"})
        tx = d.start()
        tx.del_("a")
        
        with self.assertRaises(KeyError):
            v = tx.get("a")

    def test_CommitedTransaction_ValueRemovedOnTxGetValueOnDict_RaisesKeyError(self):
        d = TransactionalDict({"a" : "6"})
        tx = d.start()
        tx.del_("a")
        tx.commit()
        
        with self.assertRaises(KeyError):
            d.get("a")

    def test_UncommitedTransaction_SetValueInTransactionGetInOther_RaisesKeyError(self):
        d = TransactionalDict()
        tx = d.start()
        tx2 = d.start()
        tx.set("a", 2)
        
        with self.assertRaises(KeyError):
            tx2.get("a")

    def test_CommitedTransaction_SetValueInTransactionCommitGetInOther_RaisesKeyError(self):
        d = TransactionalDict()
        tx = d.start()
        tx2 = d.start()
        tx.set("a", 2)
        tx.commit()
        
        with self.assertRaises(KeyError):
            tx2.get("a")

    def test_UncommitedTx_DeleteOnNotExistantKey_RaisesKeyError(self):
        d = TransactionalDict()
        tx = d.start()

        with self.assertRaises(KeyError):
            tx.del_("a")


    def test_commit_order(self):
        # conflicts
        

        pass
    
    def test_int(self):
        i = LogCounter()
        #tx = i.start()
        i.apply(Transaction([AddOp(2)]))
        
    def test_two_counters(self):
        # two counters need to synch after applying each a different tx
        i = LogCounter()
        #tx = i.start()
        i.apply(Transaction([AddOp(2)]))
        

        

        
if __name__ == '__main__':
    unittest.main()
