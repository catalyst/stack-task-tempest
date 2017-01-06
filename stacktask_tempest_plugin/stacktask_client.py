# stacktask_client

from oslo_serialization import jsonutils as json
from six.moves.urllib import parse as urllib

from tempest.lib.common import rest_client


class StacktaskClient(rest_client.RestClient):

    def user_list(self, params=None):
        """Lists all users within the tenant."""

        uri = 'openstack/users'
        if params:
            uri += '?%s' % urllib.urlencode(params)

        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def user_invite(self, username, email, roles):
        """ Invite a user to the tenant. """

        uri = 'openstack/users'
        data = {
            "username": username,
            "email": email,
            "roles": list(set(roles))
        }
        post_body = json.dumps(data)
        resp, body = self.post(uri, body=post_body)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def revoke_user(self, user_id):
        """ Revoke a user from the tenant
            This will remove pending or approved roles but
            will not not delete the user from Keystone.
        """

        uri = 'openstack/users/%s' % user_id
        try:
            resp = self.delete(uri)
        except AttributeError:
            # note: this breaks. stacktask returns a string, not json.
            return
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, None)

    def get_tokens(self, filters={}):
        """ Returns dict of tokens matching the provided filters """
        uri = 'tokens'

        if filters:
            filters = {'filters': json.dumps(filters)}
            uri += "?%s" % urllib.urlencode(filters, True)

        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def token_submit(self, token_id, json_data={}):
        """ Submits a given token, along with optional data """
        uri = 'tokens/%s' % token_id
        post_body = json.dumps(json_data)

        resp, body = self.post(uri, post_body)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def get_tasks(self, filters={}):
        """ Returns dict of tasks matching the provided filters """
        uri = 'tasks'

        if filters:
            filters = {'filters': json.dumps(filters)}
            uri = "%s?%s" % (uri, urllib.urlencode(filters, True))

        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def approve_task(self, task_id):
        """ Returns dict of tasks matching the provided filters """
        uri = 'tasks/%s' % task_id

        data = {"approved": True}

        resp, body = self.post(uri, json.dumps(data))
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def signup(self, project_name, email):
        """ Signup for a new project. """

        uri = 'openstack/sign-up'
        data = {
            "project_name": project_name,
            "email": email,
        }
        post_body = json.dumps(data)
        resp, body = self.post(uri, body=post_body)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)
