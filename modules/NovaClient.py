import requests, json
from OSClient import OSClient

__author__ = "Tamas Szabo"
__email__ = "tamas.e.szabo@ericsson.com"

class NovaClient(OSClient):
    def __init__(self):
        '''
        it calls the superclass constructor, which will fetch the config from OS env.
        then it'll request a token from OS/KeyStone
        '''
        OSClient.__init__(self)
    
    def get_private_key(self, keypair_id):
        '''
        keypair ID is the only incoming attribute
        returns the private key, if any... 
        '''
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        url=self.endpoints['nova']+"/"+str(self.tenant_id)+"/os-keypairs/"+str(keypair_id)
        response = requests.get(url=url, headers=headers)
        
        if response.status_code != requests.codes.ok:
            print('Something went wrong with getting the keypair!')
            print(response)
            return
        
        return response.json()
        
    
    def get_server(self, server_id):
        '''
        gets the server uuid
        returns its details
        '''
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        url=self.endpoints['nova']+"/servers/"+str(server_id)
        #print(url)
        response = requests.get(url=url, headers=headers)
        
        if response.status_code != requests.codes.ok:
            print('Something went wrong :( ')
            print(response, response.text)
            return
        
        return response.json()
        

#from NovaClient import *
#n = NovaClient()
#n.get_server('8220c0f0-f4fd-4dfa-a555-c1964742d6ab')