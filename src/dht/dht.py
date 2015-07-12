# todo patch npp  replace by space by defaut in python
# 
import unittest
from event import Event

class RoutingTables():
    def __init__(self, key, kbuckets=[]):
        self.key = key
        self.kbuckets = kbuckets

    def find_closest(self, key, nb=10):
        pass

class Network():
    pass
    
class SimluatedNetwork(Network):
    def __init__(self, my_addr, addresses):
        self.addresses = addresses
        self.my_addr = my_addr
        self.ON_MESSAGE = Event()
    
    @classmethod
    def create(cls, size):
        my_addr = size
        addresses = range(size)
        return cls(my_addr, addresses)
        
    def getaddr(self):
        return self.my_addr
    
class Message():
    def __init__(self, msgtype, params, id):
        self.msgtype = msgtype
        self.params = params
        self.id = id


class NetworkNode():
    """ keep track of requests send to other nodes """
    def __init__(self, network, request_handler):
        self.network = network
        self.requests_in_progress = {}
        self.addr = self.network.getaddr()
        self.network.ON_MESSAGE.subscribe(self._on_message)
        self.request_handler = request_handler
        
    def request(self, addr, request):
        self.network.send(addr, request)
        id = makeid()
        f = Future()
        self.requests_in_progress[id] = (f, request)
        return f
    
    def _on_message(self, from_addr, message):
        pass# set future as completed
        
class ValueCache():
    def __init__(self):
        pass

class Search():
    ""
    def __init__(self, key):
        self.key = key
    
    def __eq__(self, other):
        return self.key == other.key
    
class DhtNode():
    def __init__(self, routing_tables=None, network_node=None, value_cache=None, searches=[]):
        self.routing_tables = routing_tables
        self.network_node = network_node
        self.id = id
        self.searches = searches
        self.value_cache = value_cache
        
    def search(self, key):
        self.searches.append(Search(key))

    def list_searches(self):
        return self.searches
        
    def run(self):
        pass
    
    def handle_request(self, req):
        pass
        
        
class DHTTests(unittest.TestCase):
    def test_1(self):
        n1 = DhtNode()

        n1.search("k1")
        
        self.assertEquals(n1.list_searches(), [Search("k1")])

if __name__ == '__main__':
    unittest.main()

        
        
        
        
        