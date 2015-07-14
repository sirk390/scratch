
class Change(object):
    pass

class Delete(Change):
    def apply(self, dct, key):
        del dct[key]

class Set(Change):
    def __init__(self, value):
        self.value = value
    def apply(self, dct, key):
        dct[key] = self.value


class Transaction():
    """
    set + set => set
    set + delete => delete
    delete + delete => error
    delete + set => set
    """
    def __init__(self):
        self.changes = defaultdict(list)
        
    def delete(self, itemset, key):
        if self.isdeleted(itemset, key):
            raise KeyError()
        self.changes[(itemset, key)].append(Delete())
        
    def set(self, itemset, key, value):
        self.changes[(itemset, key)].append(Set(value))

    def isdeleted(self, itemset, key):
        return self.ischanged(itemset, key) and type(self.lastchange(itemset, key)) is Delete
    
    def lastchange(self, itemset, key):
        return self.changes[(itemset, key)][-1]

    def ischanged(self, itemset, key):
        return ((itemset, key) in self.changes and self.changes[(itemset, key)])
    
    def iterchanges(self):
        for key, changes in self.changes.iteritems():
            for change in changes:
                yield (key, change)
                
    def commit(self):
        for (itemset, key), change  in self.iterchanges():
            itemset.ON_CHANGING.fire(key=key, change=change)
        for (itemset, key), change  in self.iterchanges():
            itemset.apply_change(key, change)
        for (itemset, key), change  in self.iterchanges():
            itemset.ON_CHANGED.fire(change=change)

class TransactionalDict( object ):
    """
    Events:
        ON_CHANGING:  Fires for every change when a commit is started .
                      An exception can be thrown in the event to notify the 
                      ItemSet that the change cannot be applied 
                      (for example, there could be an error when writing to disk).
        ON_CHANGED:   The item was changed successfully.
        
    data_store: dict like object that stores the content. (For PrivateKeys, this is replaced by 
    something that ask for the password when querying or saving a PrivateKey)
    """
    def __init__(self, data_store=None):
        self.data_store = data_store or {}
        self.ON_CHANGING = Event()   
        return self.tx
    
    def apply_change(self, key, change):
        return change.apply(self.data_store, key)
    
    def commit_transaction(self):
        """ Commit the transaction. 
        
            If an exception is raised in an ON_CHANGING event, the transaction 
            is not applied"""
        self.tx.commit()

    def delete(self, key, tx=None):
        tx = tx or self.tx
        if not tx.ischanged(self, key) and key not in self.data_store:
            raise KeyError()
        tx.delete(self, key)
        
    def set(self, key, value, tx=None):
        tx = tx or self.tx
        assert tx != None
        tx.set(self, key, value)
        
    def get(self, key):
        return self.data_store[key]

    def contains(self, key):
        return key in self.data_store
