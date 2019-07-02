import requests, json

__author__ = "Tamas Szabo"
__email__ = "tamas.e.szabo@ericsson.com"

class OSClient(object):
    def __init__(self):
        '''
        stores config
        then requests a token 
        from the response, extracts and stores the 
          tenant_id
          token
          public endpoints
        '''
        self.credentials = self._get_credentials()
        #let's store what keystore returns, because other modules may need other parts of it
        self.auth_data = self._get_token_and_endpoints()
        self.tenant_id = str(self.auth_data["access"]["token"]["tenant"]["id"])
        self.token = str(self.auth_data["access"]["token"]["id"])
        self.endpoints = {}
        
        for i in self.auth_data["access"]["serviceCatalog"]:
            if not i["name"] in self.endpoints.keys():
                self.endpoints[i["name"]] = str(i["endpoints"][0]["publicURL"])
            
    def _get_credentials(self):
        '''
        the method reads the OS specific env variables from Linux
        and then stores them in a dictionary
        '''
        import os
        d = {}
        d['username'] = os.environ['OS_USERNAME']
        d['password'] = os.environ['OS_PASSWORD']
        d['auth_url'] = os.environ['OS_AUTH_URL']
        d['tenant_name'] = os.environ['OS_TENANT_NAME']
        d['tenant_id'] = os.environ['OS_TENANT_ID']
        try:
            d['region_name'] = os.environ['OS_REGION_NAME']
        except KeyError:
            #region_name is not in the env in older clouds such as Icehouse
            pass
            
        return d
    
    def _get_token_and_endpoints(self):
        
        if not self.credentials['tenant_id']:
            json_payload = {
                "auth": {
                    "tenantName": self.credentials['tenant_name'],
                    "passwordCredentials": {
                        "username": self.credentials['username'],
                        "password": self.credentials['password']
                    }
                }
            }
        else:
            json_payload = {
                "auth": {
                    "tenantId": self.credentials['tenant_id'],
                    "passwordCredentials": {
                        "username": self.credentials['username'],
                        "password": self.credentials['password']
                    }
                }
            }

        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        response = requests.post(url=self.credentials['auth_url']+"/tokens",
                                 data=json.dumps(json_payload),
                                 headers=headers)

        if response.status_code != requests.codes.ok:
            #debug
            print(response.status_code, response.text)
            print('request was: ')
            print(response.request.text)
            print()
            print('Something went wrong!')
            exit(1)
        
        response_body = response.json()
        return response_body

    def get_arbitrary_url(self, url):
        '''
        this method is useful when you want to resolve a link href. these things typically appear in 
        heat stack but putting the method here makes it available for all descendants 
        expects url, returns whatever comes back from the server 
        '''
        
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = requests.get(url=url, headers=headers)
        
        if response.status_code != requests.codes.ok:
            print('Something went wrong with listing stacks!')
            print(response)
            return
        
        return response.json()
        