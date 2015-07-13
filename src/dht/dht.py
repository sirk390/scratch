import unittest
from event import Event
from common import set_minlength

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

class Peer(object):
    def __init__(self, id, addr, lastseen=None):
        self.id = id
        self.addr = addr
        self.lastseen = lastseen

    def __repr__(self):
        return "<Peer id:%s addr:%s>" % (self.id, self.addr)

class KBucket():
    def __init__(self, peers=None):
        self.peers = peers or []

    def add(self, peer):
        self.peers.append(peer)

    def find_closest(self, id, nb=10):
        peerdists = sorted([(p.id.distance(id), p) for p in self.peers], key=lambda (dist, peer) : dist, reverse=True)
        return [peer for dist, peer in peerdists[:nb]]

class RoutingTables(object):
    def __init__(self, id=None, kbuckets=[]):
        self.id = id
        self.kbuckets = kbuckets

    def find_closest(self, key, nb=10):
        results = []
        dist = min(self.id.distance(key), len(self.kbuckets)-1)
        for i in range(dist, -1, -1):
            closests = self.kbuckets[i].find_closest(key, nb)
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

class Message():
    def __init__(self, msgtype, params, id):
        self.msgtype = msgtype
        self.params = params
        self.id = id
        
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
        self.network_node.ON_REQUEST.subscribe(self.handle_request)
        
    def search(self, key):
        self.searches.append(Search(key))

    def list_searches(self):
        return self.searches
        
    def run(self):
        pass
    
    def handle_request(self, req):
        pass
        
        
class DHTTests(unittest.TestCase):
    
    def test_RoutingTables_GetBuckets_ReturnsBuckets(self):
        r = RoutingTables.from_idstrings("101", {"110" : 1 , "011" : 2, "000" : 3, "100" : 4, "011" : 5})
        
        self.assertEquals(r.get_buckets(), [{'011': 5, '000': 3}, {'110': 1}, {'100': 4}])        

    def test_RoutingTables_FindClosests_ReturnsClosests(self):
        r = RoutingTables.from_idstrings("101", {"110" : 1 , "011" : 2, "000" : 3, "100" : 4, "011" : 5})
        
        print r.find_closest(Id("010"))     
        print r.find_closest(Id("100"), 1 )     
        

    """
    def test_1(self):
        n1 = DhtNode(RoutingTables())
        n1 = DhtNode()

        n1.search("k1")
        
        self.assertEquals(n1.list_searches(), [Search("k1")])
    """

if __name__ == '__main__':
    unittest.main()

        
        
        
        
        