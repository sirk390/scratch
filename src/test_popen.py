import unittest  
import sys
from bitcoinlib.popen import Popen
import time
from subprocess import PIPE, STDOUT


class TestPopen(unittest.TestCase):
    def setUp(self):
        pass

    def test_Popen_PrintingHello(self):
        python = sys.executable
        
        proc = Popen([python, '-c', "print('hello')"],
          stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        proc.wait()
        
        self.assertEquals(proc.recv(), "hello\n")



        
if __name__ == "__main__":
    unittest.main() 
        