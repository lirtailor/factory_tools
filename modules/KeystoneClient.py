import requests, json, string, inspect
from OSClient import OSClient

__author__ = "Tamas Szabo"
__email__ = "tamas.e.szabo@ericsson.com"

class KeystoneClientError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class KeystoneClient(OSClient):
    def __init__(self):
        '''
        stores config
        then requests a token (by calling the superclass constructor)
        then it adds some customization to the inherited method: requests the admin endpoint url. 
            this is needed for all sorts of administrative tasks that we do here... 
        '''

        OSClient.__init__(self)
        self.admin_endpoint = ''
        for i in self.auth_data["access"]["serviceCatalog"]:
            if i["name"] == "keystone":
                self.admin_endpoint = i["endpoints"][0]["adminURL"]
                break
    def _talk_to_keystone(self,request_type, url, headers={}, data=None):
        
        methods = {
            "put":  requests.put,
            "post": requests.post,
            "get":  requests.get
        }
        if request_type not in methods.keys():
            raise KeystoneClientError('Invalid method %s' % str(request_type))
        
        response = methods[request_type](url=url, headers=headers, data=data)
        
        if not str(response.status_code).startswith('2'):
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            raise KeystoneClientError('Error: %s received a %d from Openstack!' % ( str(calframe[1][3]), response.status_code) )

        return response
        
    def _list_users(self):
        '''
        fetches and returns the list of users.
        internal method...
        '''
        
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = self._talk_to_keystone('get',url=self.admin_endpoint+"/users", headers=headers)
        return response.json()
        
    def get_users(self):
        '''
        getter method for _list_users. 
        prints the list in a pretty json format
        '''
        print(json.dumps(self._list_users(), indent=4))
        
    def _get_user(self, user_name):
        '''
        internal method; takes the user's name, returns 
        everything keystone knows about the user. 
        '''
        user_list = self._list_users()
        for i in user_list["users"]:
            if i["name"] == user_name:
                return i
        return None
        
    def _get_user_id(self, user_name):
        '''
        internal method; takes the user's name, returns its id
        if not found, returns None
        '''
        user_list = self._list_users()
        for i in user_list["users"]:
            if i["name"] == user_name:
                return i["id"]
        return None
        
        
        
    def _list_projects(self):
        '''
        fetches and returns the list of projects.
        internal method...
        '''
        
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = self._talk_to_keystone('get',url=self.admin_endpoint+"/tenants", headers=headers)
        return response.json()
        
    def get_projects(self):
        '''
        getter method for _list_projects. 
        prints the list in a pretty json format
        '''
        print(json.dumps(self._list_projects(), indent=4))
        
    def _get_project_id(self, project_name):
        '''
        internal method; takes the project's name, returns its id
        if not found, returns None
        '''
        project_list = self._list_projects()
        for i in project_list["tenants"]:
            if i["name"] == project_name:
                return i["id"]
        return None
        
        
    def _get_project_name(self, project_id):
        '''
        internal method; takes the project's id, returns its name
        if not found, returns None
        '''
        project_list = self._list_projects()
        for i in project_list["tenants"]:
            if i["id"] == project_id:
                return i["name"]
        return None
        
    def _list_roles(self):
        '''
        fetches and returns the list of roles.
        internal method...
        '''
        
        headers = {'X-Auth-Token': self.token, 'accept': 'application/json'}
        response = self._talk_to_keystone('get',url=self.admin_endpoint+"/OS-KSADM/roles", headers=headers)
        return response.json()
        
    def get_roles(self):
        '''
        getter method for _list_roles. 
        prints the list in a pretty json format
        '''
        print(json.dumps(self._list_roles(), indent=4))
        
    def _get_role_id(self, role_name):
        '''
        internal method; takes the role's name, returns its id
        if not found, returns None
        '''
        role_list = self._list_roles()
        for i in role_list["roles"]:
            if i["name"] == role_name:
                return i["id"]
        return None
        
    def create_user(self, name, password, tenantId=None):
        '''
        creates an OS user using the provided username and password
        returns True if succeeds
        '''
        #check if the user already exists
        if self._get_user_id(name):
            print('User %s has already been created. Not creating again...' % name)
            return
        
        json_payload = {"user":{}}
        json_payload["user"]["name"] = name
        json_payload["user"]["password"] = password
        if tenantId:
            json_payload["user"]["tenantId"] = tenantId
        
        headers = {'X-Auth-Token': self.token,
                    'accept': 'application/json',
                    'content-type': 'application/json'}
        response = self._talk_to_keystone('post',url=self.admin_endpoint+"/users", data=json.dumps(json_payload), headers=headers)
        #let the caller do whatever he want with it
        return response
            
            
    def create_project(self, project_name, description=None):
        '''
        creates a project with the provided name
        returns True if successful, False otherwise
        '''
        #check if the project already exists
        if self._get_project_id(project_name):
            print('Project %s has already been created. Not creating again...' % project_name)
            return
        json_payload = {"tenant":{}}
        json_payload["tenant"]["name"] = project_name
        if description:
            json_payload["tenant"]["description"] = description
        else:
            json_payload["tenant"]["description"] = project_name
            
        headers = {'X-Auth-Token': self.token,
                    'accept': 'application/json',
                    'content-type': 'application/json'}
        response = self._talk_to_keystone('post',url=self.admin_endpoint+"/tenants", data=json.dumps(json_payload), headers=headers)
        return response
            
    def add_user_to_project(self, user_name, project_name, role='_member_'):
        '''
        adds the provided user to the provided project with the provided role
        the format is <admin-endpoint>/tenants/{tenant_id}/users/{user_id}/roles/OS-KSADM/{role_id}
        this means we need to fetch the tenant_id, the user_id and the role_id as well
        #PainInTheButt
        '''
        
        user_id = self._get_user_id(user_name)
        project_id = self._get_project_id(project_name)
        role_id = self._get_role_id(role)
        
        headers = {'X-Auth-Token': self.token,
                    'accept': 'application/json'}
        url = "%s/tenants/%s/users/%s/roles/OS-KSADM/%s" % (self.admin_endpoint, project_id, user_id, role_id)
        response = self._talk_to_keystone('put',url,headers=headers)
        return response
        
    def create_rc_file(self, username, password, filename):
        '''
        takes username, password and a filename, will write openrc content for this user in the specified filename
        this should be stored in the user's (shered?) repository... of course it's up to the 
        method's consumer where he want the file... 
        
        THIS WILL ONLY WORK IF user is already member of a project (tenantId exists for the user)
        '''
        
        template = ('export OS_AUTH_URL=""\n'
                    'export OS_TENANT_ID=""\n'
                    'export OS_TENANT_NAME=""\n'
                    'export OS_PROJECT_NAME=""\n'
                    'export OS_USERNAME=""\n'
                    'export OS_PASSWORD=""\n'
                    'export OS_REGION_NAME=""\n'
                    'if [ -z "$OS_REGION_NAME" ]; then unset OS_REGION_NAME; fi\n')
            
        try:
            tenantId = self._get_user(username)["tenantId"]
        except KeyError:
            raise KeystoneClientError('User %s does not have a project associated with it!' % username)
        project_name = self._get_project_name(tenantId)
        
        template = string.replace(template, 'OS_AUTH_URL=""','OS_AUTH_URL="' + self.endpoints["keystone"] + '"')
        template = string.replace(template, 'OS_TENANT_ID=""', 'OS_TENANT_ID="' + tenantId + '"')
        template = string.replace(template, 'OS_TENANT_NAME=""', 'OS_TENANT_NAME="' + project_name + '"')
        template = string.replace(template, 'OS_PROJECT_NAME=""', 'OS_PROJECT_NAME="' + project_name + '"')
        template = string.replace(template, 'OS_USERNAME=""', 'OS_USERNAME="' + username + '"')
        template = string.replace(template, 'OS_PASSWORD=""', 'OS_PASSWORD="' + password + '"')
        
        try:
            template = string.replace(template, 'OS_REGION_NAME=""', 'OS_REGION_NAME="' + self.credentials['region_name'] + '"')
        except KeyError:
            #region_name is not in the env in older clouds such as Icehouse
            pass
            
        with open(filename,'w') as f:
            f.write(template)
        

        
#from modules.KeystoneClient import *
#k = KeystoneClient()
#k.get_users()
#k.create_user('etamsza', 'etamsza')
#k.create_project('etamproject')
        