from modules.HeatClient import *
from modules.NeutronClient import *
from modules.NovaClient import *
import argparse, json, re, os, stat


def get_resources_from_stack(stack,pattern):
    '''
    expects the name of the stack. returns a list of all the VM resources of this stack
    it uses HeatClient's get_resources2 method, which recursively walks through the stack and returns only the non-compound resources, 
    i.e. stuff that belong to a resource group will be returned as separate resource. 
    '''
    h = HeatClient()
    resources = h.get_resources2(stack) #these are all the resources
    #print(json.dumps(resources, indent=4))
    #now let's get the servers out of it:
    heat_resources = []
    for i in resources:
        if re.match('.*' + pattern + '.*',i["resource_type"], re.IGNORECASE):
        #if i["resource_type"] == "OS::Nova::Server":
            heat_resources.append(i)
            
    
    return heat_resources
    
def get_servers_from_nova(heat_resource_list):
    '''
    expects a list of servers as heat resources (a list that get_servers_from_stack returns)
    and returns a list of the same VMs, with all details Nova can provide 
    i.e. resolving the physical_resource_id from Heat
    '''
    n = NovaClient()
    nova_servers = []
    for i in heat_resource_list:
        nova_servers.append(n.get_server(i["physical_resource_id"]))
        
    return nova_servers
    
def get_floating(server):
    '''
    expects a (single) server definition in a dictionary, in the form it comes from Nova. 
    returns the floating IP associated to the VM, if any, 0.0.0.0 if none.
    Note: it assumes there's only 1 floating IP, and stops looking once one is found.
    '''
    for i in server["server"]["addresses"]:
        for j in server["server"]["addresses"][i]:
            if j["OS-EXT-IPS:type"] == "floating": return j["addr"]
    
    #we only get here if nothing has been found
    return "0.0.0.0"
    

def get_private_key(keypair_list, key_name):
    '''
    takes the list of keypairs of the whole cluster. 
    also takes the name of the keypair we're looking for... 
    returns the private kay, if stored properly. or an empty string otherwise
    '''
    for i in keypair_list:
        if i["physical_resource_id"] == key_name: 
            for j in i["links"]: 
                if j["rel"] == "self": 
                    h = HeatClient()
                    
                    try:
                        return h.get_arbitrary_url(j["href"])["resource"]["attributes"]["private_key"]
                    except:
                        #in case no private key has been stored for the heat resource...
                        return ''
                    
    
    #wse only get here if there was no match...
    return ''
    
def write_file(name, content):
    '''
    it creates files with given nama and content
    if there's a conflicting file, it'll owerwrite... no questions asked!
    '''
    try:
        f = open(name,'w')
        f.write(content)
        os.chmod(name,stat.S_IRWXU)
        f.close()
    except Exception, e:
        print("something went wrong with writing the file: %s", str(e))
    
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stack", help="name of the Heat stack", type=str, required=True)
    args = parser.parse_args()
    STACK_NAME = args.stack

    nova_servers = get_servers_from_nova(get_resources_from_stack(STACK_NAME,'Server'))
    server_stuff = []
    for i in nova_servers:
        server_stuff.append({'uuid': i["server"]["id"], 
                            'key_name': i["server"]["key_name"], 
                            'floating_ip': get_floating(i),
                            'private_key': get_private_key(get_resources_from_stack(STACK_NAME,'KeyPair'),i["server"]["key_name"])} )
    
    for i in server_stuff:
        write_file(STACK_NAME+"_"+i["floating_ip"]+".pem", i["private_key"])
    #print(json.dumps(server_stuff, indent=4))
    
    
    