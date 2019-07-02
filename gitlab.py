import sys, argparse
from modules.GitlabClient import *


def create_project(args):
    a = GitlabClient(args.host, args.gitlabuser, args.gitlabpass)
    #if group_name was provided
    if args.group_name:
        group_list = [ x["name"] for x in a.list_groups() ]
        #and the group does not exist
        if args.group_name not in group_list:
            #we create it, before creating the project
            a.create_group(args.group_name)
            
            #now we have created a new group... this will be useless unless we add our users to this group
            known_usernames = [x["username"] for x in a.known_users["users"]]
            for user in known_usernames:
                a.add_user_to_group(user, args.group_name)
        
    if a.create_project(args.project_name, args.group_name, args.description, args.visibility_level):
        print("Project created successfully!")
        
def get_group_members(args):
    a = GitlabClient(args.host, args.gitlabuser, args.gitlabpass)
    a.get_group_members(args.group_name)
    
def create_user(args):
    a = GitlabClient(args.host, args.gitlabuser, args.gitlabpass)
    if a.create_user(args.username, args.password, args.name, args.email):
        print("User created successfully!")
        
    #when adding a new user, add him/her to all the gruops jenkins handles
    group_list = [ x["name"] for x in a.list_groups() ]
    for group in group_list:
        a.add_user_to_group(args.username, group)
        
        
def add_user_to_group(args):
    a = GitlabClient(args.host, args.gitlabuser, args.gitlabpass)
    if a.add_user_to_group(args.username, args.group_name, args.access_level):
        print("User added to group successfully!")
        
    
if __name__ == "__main__":
    
    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    #SUB-COMMAND create-project
    parser_create_project = subparsers.add_parser('create-project')
    #by def. all non-positional arguments are optional. we need this trick to make them show up as required on the help page
    required_create_project = parser_create_project.add_argument_group('required arguments')
    #arguments for Gitlab
    required_create_project.add_argument("-H", "--host", help="IP or hostname of Gitlab server", type=str, required=True)
    required_create_project.add_argument("-U", "--gitlabuser", help="Root/admin user's username on Gitlab", type=str, required=True)
    required_create_project.add_argument("-P", "--gitlabpass", help="Password of root / admin user on Gitlab", type=str, required=True)
    #arguments for creating a project
    required_create_project.add_argument("--project_name", help="Name for the project", type=str, required=True)
    parser_create_project.add_argument("--group_name", help="Name of the group we want the project to belong to. OPTIONAL", type=str, required=False, default=None)
    parser_create_project.add_argument("--description", help="Description of the project. OPTIONAL", type=str, required=False, default="")
    parser_create_project.add_argument("--visibility_level", help="Optional, defaults to 10: ", type=str, required=False, default=10)
    #set the method for the subcommand:
    parser_create_project.set_defaults(func=create_project)

    #SUB-COMMAND create-user
    parser_create_user = subparsers.add_parser('create-user')
    required_create_user = parser_create_user.add_argument_group('required arguments')
    required_create_user.add_argument("-H", "--host", help="IP or hostname of Gitlab server", type=str, required=True)
    required_create_user.add_argument("-U", "--gitlabuser", help="Root/admin user's username on Gitlab", type=str, required=True)
    required_create_user.add_argument("-P", "--gitlabpass", help="Password of root / admin user on Gitlab", type=str, required=True)
    required_create_user.add_argument("-u", "--username", help="username of the user", type=str, required=True)
    required_create_user.add_argument("-p", "--password", help="password of the user", type=str, required=True)
    required_create_user.add_argument("-n", "--name", help="name of the user", type=str, required=True)
    required_create_user.add_argument("-e", "--email", help="email of the user", type=str, required=True)
    parser_create_user.set_defaults(func=create_user)
    
    #SUB-COMMAND get-group-members
    parser_get_group_members = subparsers.add_parser('get-group-members')
    required_get_group_members = parser_get_group_members.add_argument_group('required arguments')
    required_get_group_members.add_argument("-H", "--host", help="IP or hostname of Gitlab server", type=str, required=True)
    required_get_group_members.add_argument("-U", "--gitlabuser", help="Root/admin user's username on Gitlab", type=str, required=True)
    required_get_group_members.add_argument("-P", "--gitlabpass", help="Password of root / admin user on Gitlab", type=str, required=True)
    required_get_group_members.add_argument("--group_name", help="Name of the group.", type=str, required=True)
    parser_get_group_members.set_defaults(func=get_group_members)
    
    #SUB-COMMAND add-user-to-group
    parser_add_user_to_group = subparsers.add_parser('add-user-to-group')
    required_add_user_to_group = parser_add_user_to_group.add_argument_group('required arguments')
    required_add_user_to_group.add_argument("-H", "--host", help="IP or hostname of Gitlab server", type=str, required=True)
    required_add_user_to_group.add_argument("-U", "--gitlabuser", help="Root/admin user's username on Gitlab", type=str, required=True)
    required_add_user_to_group.add_argument("-P", "--gitlabpass", help="Password of root / admin user on Gitlab", type=str, required=True)
    required_add_user_to_group.add_argument("-u", "--username", help="username of the user", type=str, required=True)
    required_add_user_to_group.add_argument("--group_name", help="name of the group we add the user to", type=str, required=True)
    parser_add_user_to_group.add_argument("--access_level", help="Optional, defaults to 40 which means MASTER: ", type=str, required=False, default=40)
    parser_add_user_to_group.set_defaults(func=add_user_to_group)
    
    #in the end, parse the args and call the appropriate function with the subcommand's arguments:
    
    args = parser.parse_args()
    args.func(args)  #args.func is the function that was set for the particular subparser




    
    
