from event import Event
import unittest
import json
from concurrent.futures import Future
from random_source import SystemRandom, FakeRandom
import mock
from futures import then
import traceback

class NetworkHandler(object):
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

class FakeNetwork(object):
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
    

class NetworkNode(object):
    
    MAX_REQUEST_ID = 1000000
    """ keep track of requests send to other nodes """
    def __init__(self, network_handler, random=SystemRandom()):
        self.network_handler = network_handler
        self.requests_sent = {}
        self.requests_received = {}
        self.addr = self.network_handler.getaddr()
        self.network_handler.ON_MESSAGE.subscribe(self._on_message)
        self.random = random
        self.ON_REQUEST = Event()
    
    def find_unique_requestid(self):
        result_id = self.random.randint(0, self.MAX_REQUEST_ID)
        while result_id in self.requests_sent:
            result_id = self.random.randint(0, self.MAX_REQUEST_ID)
        return result_id

    def request(self, addr, request):
        id = self.find_unique_requestid()
        f = Future()
        self.requests_sent[id] = (f, request)
        self._send_request(addr, request, id)
        return f

    def reply(self, reply_future):
        try:
            result = reply_future.result()
        except:
            traceback.print_exc()
        from_addr, request, id = self.requests_received[reply_future] 
        self._send_reply(from_addr, result, id)
    
    def _send_request(self, addr, request, id):
        data = json.dumps({"request": request, "id": id})
        self.network_handler.send(addr, data)

    def _send_reply(self, addr, reply, id):
        data = json.dumps({"reply": reply, "id": id})
        self.network_handler.send(addr, data)
        
    def _on_message(self, from_addr, data):
        data = json.loads(data)
        if "request" in data:
            reply_future = Future()
            self.requests_received[reply_future] = (from_addr, data["request"], data.get("id"))
            self.ON_REQUEST.fire(reply_future, from_addr, data["request"], id)
            reply_future.add_done_callback(self.reply)
            #then(reply_future, self.reply)
        if "reply" in data:
            if "id" not in data:
                print "error: missing 'id' in reply"
                return
            if not (isinstance(data["id"], basestring) or type(data["id"]) is int):
                print "error: 'id' should be an int or a string"
                return
            if data["id"] not in self.requests_sent:
                print self.requests_sent
                print data["id"]
                print "error: unknown 'id'"
                return
            future, request = self.requests_sent[data["id"]]
            future.set_result(data["reply"])
        
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