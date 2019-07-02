import sys, argparse
from modules.KeystoneClient import *

def create_project(args):
    k = KeystoneClient()
    if args.description:
        k.create_project(args.project_name, args.description)
    else:
        k.create_project(args.project_name)
    
def create_user(args):
    k = KeystoneClient()
    k.create_user(args.username,args.password,k._get_project_id(args.project_name))
    
def create_rc_file(args):
    k = KeystoneClient()
    k.create_rc_file(args.username, args.password, args.filename)

if __name__ == "__main__":
    
    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    #SUB-COMMAND create-project
    parser_create_project = subparsers.add_parser('create-project')
    required_create_project = parser_create_project.add_argument_group('required arguments')
    required_create_project.add_argument("--project_name", help="Name for the project", type=str, required=True)
    parser_create_project.add_argument("--description", help="Description for the project. OPTIONAL", type=str, required=False, default=None)
    parser_create_project.set_defaults(func=create_project)

    #SUB-COMMAND create-user
    parser_create_user = subparsers.add_parser('create-user')
    required_create_user = parser_create_user.add_argument_group('required arguments')
    required_create_user.add_argument("-u", "--username", help="username of the user", type=str, required=True)
    required_create_user.add_argument("-p", "--password", help="password of the user", type=str, required=True)
    required_create_user.add_argument("--project_name", help="Name for the project user belongs to", type=str, required=True)
    parser_create_user.set_defaults(func=create_user)
    
    #SUB-COMMAND create-rc-file
    parser_create_user = subparsers.add_parser('create-rc-file')
    required_create_user = parser_create_user.add_argument_group('required arguments')
    required_create_user.add_argument("-u", "--username", help="username of the user", type=str, required=True)
    required_create_user.add_argument("-p", "--password", help="password of the user", type=str, required=True)
    required_create_user.add_argument("--filename", help="name of the file to be created", type=str, required=True)
    parser_create_user.set_defaults(func=create_rc_file)

    args = parser.parse_args()
    args.func(args)  #args.func is the function that was set for the particular subparser


