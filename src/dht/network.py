from event import Event
import unittest
import json
from concurrent.futures import Future
from random_source import SystemRandom, FakeRandom-
import mock

class NetworkHandler():
    def __init__(self):
        self.ON_MESSAGE = Event()
    def getaddr(self):
        pass

class FakeNetworkHandler(NetworkHandler):
    def __init__(self, my_addr, fake_network):
        self.ON_MESSAGE = Event()
        self.my_addr = my_addr
        self.fake_network = fake_network
        
    def getaddr(self):
        return self.my_addr
    
    def send(self, addr, data):
        return self.fake_network.routemessage(self.my_addr, addr, data)

class FakeNetwork():
    def __init__(self):
        self.handlers = {}
        
    def routemessage(self, from_addr, to_addr, data):
        if to_addr in self.handlers:
            self.handlers[to_addr].ON_MESSAGE.fire(from_addr, data)
        else:
            raise Exception("Unknown addr: %s" % (to_addr))
        
    def get_handler(self, id):
        self.handlers[id] = handler = FakeNetworkHandler(id, self)
        return handler
    

class NetworkNode():
    MAX_REQUEST_ID = 1000000
    """ keep track of requests send to other nodes """
    def __init__(self, network_handler, random=SystemRandom()):
        self.network_handler = network_handler
        self.requests_in_progress = {}
        self.addr = self.network_handler.getaddr()
        self.network_handler.ON_MESSAGE.subscribe(self._on_message)
        self.random = random
        self.ON_REQUEST = Event()
    
    def find_unique_requestid(self):
        result_id = self.random.randint(0, self.MAX_REQUEST_ID)
        while result_id in self.requests_in_progress:
            result_id = self.random.randint(0, self.MAX_REQUEST_ID)
        return result_id

    def request(self, addr, request):
        id = self.find_unique_requestid()
        data = json.dumps({"request": request, "id": id})
        self.network_handler.send(addr, data)
        f = Future()
        self.requests_in_progress[id] = (f, request)
        return f
    
    def _on_message(self, from_addr, data):
        data = json.loads(data)
        self.ON_REQUEST.fire(data)

class NetworkTests(unittest.TestCase):
    def test_NetworkNode_NodeSendsARequestToAnother_OnRequestIsFired(self):
        random = FakeRandom()
        network = FakeNetwork()
        n1 = NetworkNode(network.get_handler(1), random=random)
        n2 = NetworkNode(network.get_handler(2), random=random)
        m = mock.Mock()
        n2.ON_REQUEST.subscribe(m)
        
        n1.request(2, "uihhiu")
        
        m.assert_called_once_with({'request': 'uihhiu', 'id': 0})


if __name__ == "__main__":
    unittest.main()