import requests, json, time, inspect

__author__ = "Tamas Szabo"
__email__ = "tamas.e.szabo@ericsson.com"

class GitlabClientError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class GitlabClient(object):
    def __init__(self, host, username, password, users_json='data/gitlab_users.json', groups_json='data/gitlab_groups.json'):
        '''
        stores config and fetches private token
        '''
        
        self.host = host
        self.username = username
        self.password = password
        self.users_json = users_json
        self.groups_json = groups_json
        self.token = self._get_token()
        try:
            self.known_users = self._read_json(users_json)
        except ValueError:
            #could not parse? maybe the file is empty...
            self.known_users = {}
        except IOError:
            #could not open the file at all; maybe it's not there? don't worry, we'll create one!
            self.known_users = {}
            
        try:
            self.known_groups = self._read_json(groups_json)
        except ValueError:
            #could not parse? maybe the file is empty...
            self.known_groups = {}
        except IOError:
            #could not open the file at all; maybe it's not there? don't worry, we'll create one!
            self.known_groups = {}
        
    def _talk_to_gitlab(self,request_type, url, headers={}, data=None, max_retries=10):
        
        methods = {
            "put":  requests.put,
            "post": requests.post,
            "get":  requests.get
        }
        if request_type not in methods.keys():
            raise GitlabClientError('Invalid method %s' % str(request_type))
        counter = 1
        while counter < max_retries:
            response = methods[request_type](url=url, headers=headers, data=data)
            if response.status_code != 429:
                break
            print("Gitlab is throttling us! waiting %d seconds before re-try..." % (counter * 10))
            time.sleep(counter * 10)
            counter += 1
        
        if counter == max_retries:
            raise GitlabClientError('Giving up after %d retries' % counter)
        
        if not str(response.status_code).startswith('2'):
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            raise GitlabClientError('Error: %s received a %d from Gitlab!' % ( str(calframe[1][3]), response.status_code) )

        return response
        
    def _get_token(self):
        url = "http://%s/api/v3/session?login=%s&password=%s" % (self.host, self.username, self.password)
        response = self._talk_to_gitlab('post', url=url)
        response_body = response.json()
        return response_body["private_token"]
        
    def _read_json(self,filename):
        '''
        opens, reads, processes the content of a json file
        return its content in a dictionary
        '''
        d = {}
        try:
            d = json.loads(open(filename,'r').read())
        except ValueError:
            raise ValueError("Could not parse config file. Invalid JSON format. Exiting")
        except IOError: 
            raise IOError("The provided config file does not exist or not readable. Exiting")
        except:
            raise Exception("Unknown error while opening config file. Exiting")

        return d
        
    def _write_json(self, filename, data):
        '''
        takes the filename and writes data into it.
        if file already exists, this will OVERWRITE!!
        '''
        try:
            json.dump(data, fp=open(filename,'w'), indent=4)
        except IOError: 
            raise IOError("Could not write %s!" % filename)
        except:
            raise Exception("Unknown error while writing %s!" % filename)
            
        return True
        
    def list_groups(self):
        '''
        returns the list of groups owned by self.user
        '''
        url = "http://%s/api/v3/groups" % self.host
        headers = {'PRIVATE-TOKEN': self.token}
        response = self._talk_to_gitlab('get',url=url,headers=headers)
        response_body = response.json()
        return response_body
        
    def _list_users(self):
        '''
        shall be called only by other methods... 
        returns the list of users 
        '''
        url = "http://%s/api/v3/users" % self.host
        headers = {'PRIVATE-TOKEN': self.token}
        response = self._talk_to_gitlab('get',url=url,headers=headers)
        response_body = response.json()
        return response_body
        
    def get_groups(self):
        '''
        getter method for the group list...
        '''
        print(json.dumps(self.list_groups(),indent=4))
        
    def _list_group_members(self, group_name):
        '''
        returns the list of users that belong to the given group
        '''
        group_id = str(self._get_group_id(group_name))
        url = "http://%s/api/v3/groups/%s/members" % (self.host, group_id)
        headers = {'PRIVATE-TOKEN': self.token}
        response = self._talk_to_gitlab('get',url=url,headers=headers)
        response_body = response.json()
        return response_body
        
    def get_group_members(self, group_name):
        '''
        getter method for the group members list
        '''
        print(json.dumps(self._list_group_members(group_name),indent=4))
            
    def _get_group_id(self, group_name):
        '''
        takes a group name
        returns its ID.
        needed for creating projects under groups... (namespace_id)
        '''
        groups = self.list_groups()
        for i in groups:
            if i["name"] == group_name:
                return i["id"]
                
        return False
        
    def _get_user_id(self, user_name):
        '''
        takes a username
        returns its ID.
        needed for adding users to groups or projects
        '''
        users = self._list_users()
        for i in users:
            if i["username"] == user_name:
                return i["id"]
                
        return False
        
        
    def _list_projects(self):
        '''
        Returns a list of projects for which the authenticated user is a member.
        '''
        url = "http://%s/api/v3/projects" % self.host
        headers = {'PRIVATE-TOKEN': self.token}
        response = self._talk_to_gitlab('get',url=url,headers=headers)
        response_body = response.json()
        return response_body
        
    def get_projects(self):
        '''
        getter method for the project list...
        '''
        print(json.dumps(self._list_projects(),indent=4))
        
    def create_group(self, 
                     group_name, 
                     description="", 
                     visibility_level=10, 
                     lfs_enabled="true", 
                     request_access_enabled="true"):
        '''
        creates a group with name=group_name and path=group_name
        rest of parameters are optional
        '''
        print("Creating group %s" % group_name)
        url = "http://%s/api/v3/groups?name=%s&path=%s&description=%s&visibility_level=%s&lfs_enabled=%s&request_access_enabled=%s" % (self.host, group_name, group_name, description, str(visibility_level), lfs_enabled, request_access_enabled)
        headers = {'PRIVATE-TOKEN': self.token}
        response = self._talk_to_gitlab('post',url=url,headers=headers)
        
        #update json with the new group!
        self.known_groups["groups"].append(response.json())
        self._write_json(self.groups_json, self.known_groups)
        
        return True
    
    def create_project(self, project_name, 
                       group_name=None,
                       description="",
                       visibility_level=10):
        '''
        creates a project (part of a group, if group_name provided)
        if group_name provided:
          we'll need to look up the group first, and if it does not exist, 
          we have to create it
        else: simply create the project  
        '''
        if group_name:
            print("Creating project %s/%s" % (group_name, project_name))
            #create project within group
            namespace_id = str(self._get_group_id(group_name))
            url = "http://%s/api/v3/projects?name=%s&namespace_id=%s&description=%s&visibility_level=%s" % (self.host, project_name, namespace_id, description, str(visibility_level))
            headers = {'PRIVATE-TOKEN': self.token}
            response = self._talk_to_gitlab('post',url=url,headers=headers)
            return True

        else: 
            print("Creating project %s" % project_name)
            #create project w/o group 
            url = "http://%s/api/v3/projects?name=%s&description=%s&visibility_level=%s" % (self.host, project_name, description, str(visibility_level))
            headers = {'PRIVATE-TOKEN': self.token}
            response = self._talk_to_gitlab('post',url=url,headers=headers)
            return True
                
    def create_user(self, username, password, name, email, confirm="false"):
        '''
        creates a user
        '''
        print("creating %s" % username)
        #create a user
        url = "http://%s/api/v3/users?email=%s&password=%s&username=%s&name=%s" % (self.host, email, password, username, name)
        headers = {'PRIVATE-TOKEN': self.token}
        response = self._talk_to_gitlab('post',url=url,headers=headers)
        response_body = response.json()
        
        #update json with the new user!
        self.known_users["users"].append(response_body)
        self._write_json(self.users_json, self.known_users)
        
        return response_body
            
    def add_user_to_group(self, username, group_name, access_level=40):
        '''
        adds a user to a group
        if access_level not specified, defaults to 40 which is master: developer who can push to master branch as well.
        also, if a non-existing grup name is provided, this method will create that group, then add the user to it...
        '''
        
        have_it_already = False
        group_list = self.list_groups()
        for i in group_list:
            if i["name"] == group_name:
                have_it_already = True
                break
        
        if not have_it_already:
            #if the desired group is not created yet, we create it right here
            print("creating %s" % group_name)
            self.create_group(group_name)

        print("Adding %s to group %s" % (username, group_name))
        
        user_id = str(self._get_user_id(username))
        group_id = str(self._get_group_id(group_name))
        
        url = "http://%s/api/v3/groups/%s/members" % (self.host, group_id)
        data = "user_id=%s&access_level=%s" % (user_id, access_level)
        headers = {'PRIVATE-TOKEN': self.token}
        response = self._talk_to_gitlab('post',url=url,data=data,headers=headers)
        return True
