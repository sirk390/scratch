import unittest
from event import Event
from common import set_minlength
from futures import then
from random_source import FakeRandom
from network import FakeNetwork, NetworkNode
from concurrent.futures._base import Future
import sys

class Id(object):
    def __init__(self, id):
        self.id = id #string

    def distance(self, otherid):
        minlen = min(len(self.id), len(otherid.id))
        nb_equal = 0
        for i in range(minlen):
            if self.id[i] == otherid.id[i]:
                nb_equal += 1
            else:
                return nb_equal
        return nb_equal

    def __repr__(self):
        return str(self.id)
    def __eq__(self, other):
        return (self.id == other.id)
    def __hash__(self):
        return hash(self.id)

class Peer(object):
    def __init__(self, id, addr, lastseen=None):
        self.id = id
        self.addr = addr
        self.lastseen = lastseen

    def __repr__(self):
        return "<Peer id:%s addr:%s>" % (self.id, self.addr)
    def __eq__(self, other):
        return (self.id == other.id and self.addr == other.addr)
    def __hash__(self):
        return hash(self.id)
    
class KBucket():
    def __init__(self, peers=None):
        self.peers = peers or []

    def add(self, peer):
        self.peers.append(peer)

    def find_closest(self, id, nb=10, excluding=[]):
        peerdists = sorted([(p.id.distance(id), p) for p in self.peers], key=lambda (dist, peer) : dist, reverse=True)
        results = []
        for dist, peer in peerdists:
            if peer not in excluding:
                results.append(peer)
            if len(results) >= nb:
                break
        return results #[peer for dist, peer in peerdists[:nb]]

    def __repr__(self):
        return "[%s]" % (",".join(("%s:%s" % (p.id, p.addr) for p in self.peers)))

class RoutingTables(object):
    def __init__(self, id=None, kbuckets=None):
        self.id = id
        self.kbuckets = kbuckets or []

    def find_closest(self, key, nb=10, excluding=[]):
        results = []
        dist = min(self.id.distance(key), len(self.kbuckets)-1)
        for i in range(dist, -1, -1):
            closests = self.kbuckets[i].find_closest(key, nb, excluding=excluding)
            results += closests
            nb -= len(closests)
            if nb == 0:
                break
        return results

    def add(self, peer):
        dist = self.id.distance(peer.id)
        set_minlength(self.kbuckets, dist+1, lambda: KBucket())
        self.kbuckets[dist].add(peer)

    def get_buckets(self):
        result = []
        for bucket in self.kbuckets:
            res = {}
            for peer in bucket.peers:
                res[peer.id.id] = peer.addr
            result.append(res)
        return result

    @classmethod
    def from_idstrings(cls, id, peer_idaddr):
        r = cls(Id(id))
        for id, addr in peer_idaddr.iteritems():
            r.add(Peer(Id(id), addr))
        return r
    
    def __repr__(self):
        return "<RoutingTables: [%s]>" % ",".join([str(b) for b in self.kbuckets])

class Message():
    def __init__(self, msgtype, params, id):
        self.msgtype = msgtype
        self.params = params
        self.id = id

class ValueCache():
    def __init__(self):
        pass

class Search(object):
    def __init__(self, key, routing_tables, network_node, nb_parallel=3, nb_pool=10):
        self.key = key
        self.routing_tables = routing_tables
        self.network_node = network_node
        self.key = key
        self.request_in_progress = {}
        self.nb_parallel = nb_parallel
        self.completed = Future()
        self.canditate_peers = set()
        self.requested_peers = set()
        self.nb_pool = nb_pool
        
    def start(self):
        self.fillpeers()
        self.process_search()

    def fillpeers(self):
        closest = self.routing_tables.find_closest(self.key, self.nb_pool, excluding=self.requested_peers | self.canditate_peers)
        self.canditate_peers |= set(closest)
        
    def process_search(self):
        #nbmissing = self.nb_parallel - len(self.request_in_progress)
        #if nbmissing:
            #peers = self.routing_tables.find_closest(self.key, nbmissing, excluding=self.requested_peers)
            #print "found", self.key, self.routing_tables, peers
        while self.canditate_peers and len(self.request_in_progress) <= self.nb_parallel:
            p = self.canditate_peers.pop()
            
            print self.requested_peers, p
            self.requested_peers.add(p)
            future = self.network_node.request(p.addr, {"method" : "find_node", "params": str(self.key)})
            self.request_in_progress[future] = p
            #then(future, self.on_reply)
            future.add_done_callback(self.on_reply)
            
    def on_reply(self, future):
        print "ON reply"
        del self.request_in_progress[future] 
        exception = future.exception()
        if exception is None:
            result = future.result()
            print "Received reply", result
            if 'value' in result:
                self.completed.set_result(result['value'])
            elif 'peers' in result:
                for id, addr in result["peers"]:
                    peer = Peer(Id(id), addr)
                    if peer not in self.requested_peers:
                        self.canditate_peers.add(Peer(Id(id), addr))
                print "=================", self.canditate_peers
                self.process_search()

    def __eq__(self, other):
        return self.key == other.key

class DhtNode():
    def __init__(self, routing_tables=None, network_node=None, values=None, searches=[]):
        self.routing_tables = routing_tables
        self.network_node = network_node
        self.id = id
        self.searches = searches
        self.values = values or {}
        self.network_node.ON_REQUEST.subscribe(self.handle_request)
        
    def search(self, key):
        self.searches.append(Search(key))

    def store(self, key, value):
        pass

    def list_searches(self):
        return self.searches

    def run(self):
        pass

    def handle_request(self, reply_future, from_addr, request, id):
        #print "HANDLE-REQUEST", request, request.get(u'method') == u'find_node'
        if request.get(u'method') == u'find_node':
            id = Id(request.get('params')) # Add check if exists
            result = {}
            if id in self.values:
                result["value"] = self.values[id]
            else:
                peers = self.routing_tables.find_closest(id)
                result["peers"] = [(str(peer.id), peer.addr) for peer in peers]
            reply_future.set_result(result)
        
            
        #print r.find_closest(Id("010"))
        
        #reply_future.set_result("AADH")
        print "recefived request", from_addr, request, id

    def process_searches(self):
        pass

class FakeDHTNetwork(object):
    def __init__(self, dhtnodes):
        self.dhtnodes = dhtnodes
    @classmethod
    def create_from_desc(cls, desc):
        random = FakeRandom()
        network = FakeNetwork()
        addr_to_id = dict((addr, id) for addr, (id, known_addrs, values) in desc.iteritems())
        dhtnodes = {}
        for addr, (id, known_addrs, values) in desc.iteritems():
            node = NetworkNode(network.get_handler(addr), random=random)
            routing_tables_def = dict((addr_to_id[addr], addr) for addr in known_addrs)
            routing_tables = RoutingTables.from_idstrings(id, routing_tables_def)
            values_dict = dict((Id(id), value) for id, value in values.iteritems())
            dhtnodes[addr] = DhtNode(routing_tables, node, values_dict)
        return cls(dhtnodes)

class DHTTests(unittest.TestCase):

    def test_RoutingTables_GetBuckets_ReturnsBuckets(self):
        r = RoutingTables.from_idstrings("101", {"110" : 1 , "011" : 2, "000" : 3, "100" : 4, "011" : 5})

        self.assertEquals(r.get_buckets(), [{'011': 5, '000': 3}, {'110': 1}, {'100': 4}])

    def test_RoutingTables_FindClosests_ReturnsClosests(self):
        r = RoutingTables.from_idstrings("101", {"110" : 1 , "011" : 2, "000" : 3, "100" : 4, "011" : 5})

        print r.find_closest(Id("010"))
        print r.find_closest(Id("100"), 1 )

    def test_search(self):
        #routing_tables = RoutingTables.from_idstrings("101", {"110" : 1 , "011" : 2, "000" : 3, "100" : 4, "011" : 5})
        n = FakeDHTNetwork.create_from_desc({1 : ("001", {1, 2, 4, 6}, {}),
                                             2 : ("111", {3, 4}, {}),
                                             3 : ("110", {5, 6}, {"110" : "hello"}),
                                             4 : ("000", {1, 2, 3}, {}),
                                             5 : ("010", {4, 5, 6}, {}),
                                             6 : ("011", {1, 2, 4}, {})})
        dhtnode = n.dhtnodes[1]
        search = Search(Id("110"), dhtnode.routing_tables, dhtnode.network_node)
        search.start()
        search.completed.add_done_callback(lambda future: sys.stdout.write("FOUND RESULT " + future.result()))
        #Search(Id("010"), routing_tables)
        
        
    """
    def test_1(self):
        n1 = DhtNode(RoutingTables())
        n1 = DhtNode()

        n1.search("k1")

        self.assertEquals(n1.list_searches(), [Search("k1")])
    """

if __name__ == '__main__':
    unittest.main()





