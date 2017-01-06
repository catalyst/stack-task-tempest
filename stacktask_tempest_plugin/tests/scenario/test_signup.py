from stacktask_tempest_plugin.tests import base
from tempest import test
from tempest.lib.common.utils import data_utils


class StacktaskSignup(base.BaseStacktaskTest):
    credential_roles = ['admin']

    @classmethod
    def resource_setup(cls):
        super(StacktaskSignup, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(StacktaskSignup, cls).resource_cleanup()

    @test.idempotent_id('ebb6a06d-198f-48d1-868c-f7e36f4fa76a')
    @test.services('identity')
    def test_signup(self):
        project_name = data_utils.rand_name('stacktask')
        u_email = '%s@example.com' % project_name
        u_password = data_utils.rand_password()

        # create new signup
        self.stacktask_client.signup(project_name, u_email)

        # now we need to approve the signup
        filters = {
            "task_type": {"exact": "signup"},
            "completed": {"exact": False},
            "approved": {"exact": False},
            "keystone_user": {
                "contains": self.os.credentials.project_id,
            },
        }
        signup_tasks = self.stacktask_client.get_tasks(filters=filters)
        found = None
        for task in signup_tasks['tasks']:
            for action in task['actions']:
                if (action['action_name'] == "NewProjectWithUserAction" and
                        action['data']['project_name'] == project_name):
                    found = task
                    break
            if found:
                break

        self.stacktask_client.approve_task(found['uuid'])

        # using the task id, bypass email and get the auth token
        # NOTE(dalees): Requires full 'admin' role to access sensitive tokens.
        token_id = self.get_token_by_taskid(found['uuid'])
        self.stacktask_client.token_submit(
            token_id,
            {"password": u_password}
        )

        # Confirm user has been created in keystone
        ks_user = self.get_user_by_name(u_email, client='keystone')
        self.addCleanup(self.users_client.delete_user, ks_user['id'])

        # Verify project_admin role with keystone
        project = self.get_project_by_name(project_name)
        self.assert_user_has_role(
            project['id'], ks_user['id'], "project_admin")
