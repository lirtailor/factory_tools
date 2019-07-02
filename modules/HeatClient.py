import requests, json, copy
from OSClient import OSClient

__author__ = "Tamas Szabo"
__email__ = "tamas.e.szabo@ericsson.com"

class HeatClient(OSClient):
    def __init__(self):
        '''
        stores config
        then requests a token (by calling the superclass constructor)
        '''
        OSClient.__init__(self)
        #self.endpoint = self.endpoints['heat']
    def list_stacks(self):
        '''
        no incoming param
        returns a list of current stacks
        '''

        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = requests.get(url=self.endpoints['heat']+"/stacks", headers=headers)
        
        if response.status_code != requests.codes.ok:
            print('Something went wrong with listing stacks!')
            print(response)
            return
        
        return response.json()
        
    def get_stack_id(self, stack_name):
        '''
        returns the id of the stack
        '''
        return self.get_stack(stack_name)["stack"]["id"]
        
    def get_stack(self, stack_name):
        '''
        takes in the name of a stack, 
        returns it's json representation 
        '''
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = requests.get(url=self.endpoints['heat']+"/stacks/"+stack_name, headers=headers)
        
        if response.status_code != requests.codes.ok:
            raise ValueError('stack %s could not be found' % stack_name)
                
        return response.json()
                
    def get_resources(self, stack_name):
        '''
        stack name is incoming param
        returns the list of resources that belong to the stack
        '''
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = requests.get(url=self.endpoints['heat']+"/stacks/"+stack_name+"/resources", headers=headers)
        
        if response.status_code != requests.codes.ok:
            print('Something went wrong with getting resources!')
            print(response)
            return
        
        return response.json()
        
    def get_resources2(self, stack_name):
        '''
        this one will recursively walk through the resources 
        and return all 'non-compound' resources, meaning that resource groups will
        be resolved into its components 
        '''
        def recursive(self,resource_list):
            return_list = []
            for i in resource_list:
                #print(i)
                #return_list.extend(i)
                if (i["resource_type"].endswith('ResourceGroup')) or (i["resource_type"].startswith('file:')):
                    return_list.extend(recursive(self,self.get_resources(i["physical_resource_id"])["resources"]))
                else:
                    return_list.extend([i])
            
            return return_list
        
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = requests.get(url=self.endpoints['heat']+"/stacks/"+stack_name+"/resources", headers=headers)
        
        if response.status_code != requests.codes.ok:
            print('Something went wrong with getting resources!')
            print(response)
            return
        
        return recursive(self,self.get_resources(stack_name)["resources"])
        
        
    def get_resources3(self, stack_name):
        '''
        this one will recursively walk through the resources 
        but unlike get_resources2, this one will preserve the structure
        e.g. there's a resource group in the stack. under that resource group you have %counter% number of 
        other resources. if that resources are of type 'nested template' then there, an additional layer with the resources 
        of those nested templates. 
        '''
        def recursive(self,resource_list):
            return_list = []
            for i in resource_list:
                #print(i)
                #return_list.extend(i)
                if (i["resource_type"].endswith('ResourceGroup')) or (i["resource_type"].startswith('file:')):
                    return_list.append(i) #append the resource, a dict in the end
                    return_list[-1]["resources"] = recursive(self,self.get_resources(i["physical_resource_id"])["resources"])   #the resource, a dict will have a new element... with a list
                else:
                    return_list += [i]
            
            return return_list
        
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = requests.get(url=self.endpoints['heat']+"/stacks/"+stack_name+"/resources", headers=headers)
        
        if response.status_code != requests.codes.ok:
            print('Something went wrong with getting resources!')
            print(response)
            return
        
        return {"resources": recursive(self,self.get_resources(stack_name)["resources"])}
        
    def get_resource(self, stack_name, stack_id, resource_name):
        '''
        stack name, stack id and resource name are the incoming parameters
        returns the details of the specific reaource
        '''
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        url=self.endpoints['heat']+"/stacks/"+stack_name+"/"+stack_id+"/resources/"+resource_name
        response = requests.get(url=url, headers=headers)
        
        if response.status_code != requests.codes.ok:
            print('Something went wrong with getting the resource!')
            print(response)
            return
        
        return response.json()
        
#from HeatClient import *
#a = HeatClient()
#print(a.list_stacks())
#print(a.get_resources('coreos_nodes'))
#print(a.get_stack_id('coreos_nodes'))