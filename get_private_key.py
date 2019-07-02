from HeatClient import *
from NovaClient import *
import argparse, json, os, stat

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stack", help="name of the Heat stack", type=str, required=True)
    args = parser.parse_args()
    STACK_NAME = args.stack
    
    keypair = None
    a = HeatClient()
    stack_id = a.get_stack(STACK_NAME)["stack"]["id"]
    stack_resources = a.get_resources(STACK_NAME)
    for resource in stack_resources["resources"]:
        if resource["resource_type"] == "OS::Nova::KeyPair":
            keypair = resource
            #break once found one. not interested if there are more... there should not be. 
            break

    if keypair:
        keypair_details = a.get_resource(STACK_NAME,stack_id,keypair["resource_name"])
        priv = open(STACK_NAME+'.pem','w')
        pub = open(STACK_NAME+'.pub','w')
        priv.write(keypair_details["resource"]["attributes"]["private_key"])
        pub.write(keypair_details["resource"]["attributes"]["public_key"])
        #need to change permission, too permissive will be rejected by ssh
        os.chmod(STACK_NAME+'.pem',stat.S_IRWXU)
        priv.close()
        pub.close()
    else:
        pritn("could not find any keypair resource in %s stack" % STACK_NAME)
        exit(1)
    
    
