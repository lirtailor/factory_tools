from HeatClient import *
from NeutronClient import *
import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stack", help="name of the Heat stack", type=str, required=True)
    args = parser.parse_args()
    STACK_NAME = args.stack
    
    floating_IP = None
    a = HeatClient()
    stack_resources = a.get_resources(STACK_NAME)
    for resource in stack_resources["resources"]:
        if resource["resource_type"] == "OS::Neutron::FloatingIP":
            floating_IP = resource
            #break once found one. not interested if there are more... there should not be. 
            break

    if floating_IP:
        #we found a floating ip. let's get it from neutron
        b = NeutronClient()
        neutron_resource = b.get_floating_ip(floating_IP["physical_resource_id"])
        print(neutron_resource["floatingip"]["floating_ip_address"])
    else:
        #could not find any floating IPs in the stack
        exit(1)
    
    
