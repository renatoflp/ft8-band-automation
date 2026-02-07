import xmlrpc.client
from config import FLRIG_URL

class FLRIGClient:
    def __init__(self):
        try: self.client = xmlrpc.client.ServerProxy(FLRIG_URL)
        except: self.client = None

    def get_ptt(self):
        try: return self.client.rig.get_ptt()
        except: return None

    def set_frequency(self, freq):
        try: 
            self.client.rig.set_frequency(float(freq))
            return True
        except: return False

    def get_frequency(self):
        try: return float(self.client.rig.get_frequency())
        except: return 0.0