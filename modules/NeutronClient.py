import requests, json
from OSClient import OSClient

__author__ = "Tamas Szabo"
__email__ = "tamas.e.szabo@ericsson.com"

class NeutronClient(OSClient):
    def __init__(self):
        '''
        stores config
        then requests a token (by calling the superclass constructor)
        '''
        OSClient.__init__(self)
        #self.endpoint = self.endpoints['neutron']
    
    def get_floating_ip(self, floatingip_id):
        '''
        floating IP id is the only incoming attribute. 
        returns the Neutron object, if any...
        '''
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = requests.get(url=self.endpoints['neutron']+"/v2.0/floatingips/"+floatingip_id, headers=headers)
        
        if response.status_code != requests.codes.ok:
            print('Something went wrong with getting floating IP!')
            print(response)
            return
        
        return response.json()
        
#from HeatClient import *
#a = HeatClient()
#a.list_stacks()
#a.get_resources()