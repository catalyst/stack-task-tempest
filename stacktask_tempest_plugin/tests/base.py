from oslo_log import log as logging

from tempest import config
import tempest.test
from stacktask_tempest_plugin import stacktask_client

CONF = config.CONF
LOG = logging.getLogger(__name__)


class BaseStacktaskTest(tempest.test.BaseTestCase):
    """ Base test case for stacktask tests """

    @classmethod
    def skip_checks(cls):
        super(BaseStacktaskTest, cls).skip_checks()
        # Until config implemented, always enabled.
        return
        if not CONF.service_available.stacktask:
            skip_msg = ("%s skipped as stacktask is not available" %
                        cls.__name__)
            raise cls.skipException(skip_msg)

    @classmethod
    def setup_credentials(cls):
        super(BaseStacktaskTest, cls).setup_credentials()
        # NOTE(dalees): Should convert this to simply use cls.credentials
        cls.os = cls.get_client_manager(roles=cls.credential_roles)

    @classmethod
    def setup_clients(cls):
        super(BaseStacktaskTest, cls).setup_clients()
        cls.stacktask_client = stacktask_client.StacktaskClient(
            cls.os.auth_provider,
            'registration',
            CONF.identity.region,
            endpoint_type='publicURL',
            **cls.os.default_params)
        cls.projects_client = cls.os.projects_client
        cls.users_client = cls.os.users_v3_client
        cls.roles_client = cls.os.roles_v3_client

    def get_token_by_taskid(self, taskid):
        tokens = self.stacktask_client.get_tokens(
            filters={'task_id': {"exact": taskid}}
        )
        return tokens['tokens'][0]['token']

    def assert_user_has_role(self, project_id, user_id, role):
        ks_role_list = self.roles_client.list_user_roles_on_project(
            project_id,
            user_id)
        actual_roles = set([r['name'] for r in ks_role_list['roles']])
        self.assertIn(role, actual_roles)

    def assert_user_roles(self, project_id, user_id, expected_roles):
        ks_role_list = self.roles_client.list_user_roles_on_project(
            project_id,
            user_id)
        actual_roles = set([r['name'] for r in ks_role_list['roles']])

        joined_roles = actual_roles.intersection(expected_roles)
        self.assertEqual(len(joined_roles), len(expected_roles))

    def get_user_by_name(self, name, client='stacktask'):
        func = self.stacktask_client.user_list
        if client == 'keystone':
            func = self.users_client.list_users

        user_list = func()
        user = [u for u in user_list['users'] if u['name'] == name][0]
        return user

    def get_project_by_name(self, name):
        projects = self.projects_client.list_projects()
        project = [p for p in projects['projects'] if p['name'] == name][0]
        return project
