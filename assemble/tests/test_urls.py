from django.test import TestCase
from django.urls import reverse,resolve
from assemble.views import *

class TestUserAuthURLS(TestCase):

    def test_user_sign_up(self):
        url = reverse('sign-up')
        self.assertEqual(resolve(url).func,sign_up)

    def test_logout_url(self):
        url = reverse('logged_out')
        self.assertEqual(resolve(url).func,log_out)

class TestProjectURLS(TestCase):

    def test_project_list(self):
        url = reverse('project-list')
        self.assertEqual(resolve(url).func.view_class,ProjectList)

    def test_project_create(self):
        url = reverse('project-create')
        self.assertEqual(resolve(url).func.view_class,ProjectCreate)

    def test_project_detail(self):
        url = reverse('project-detail',args=['slug-test'])
        self.assertEqual(resolve(url).func,project_detail_view)

    def test_delete_project(self):
        url = reverse('delete-project',args=[1])
        self.assertEqual(resolve(url).func,delete_project)

    def test_edit_project(self):
        url = reverse('edit-project',args=[1])
        self.assertEqual(resolve(url).func.view_class,ProjectEditView)

    def test_project_history(self):
        url = reverse('project-history',args=[1])
        self.assertEqual(resolve(url).func,history_view)

class TestProjectComponentAndTasks(TestCase):

    def test_project_component_create(self):
        url = reverse('project-component-create',args=['test'])

        self.assertEqual(resolve(url).func.view_class,ProjectComponentCreate)

    def test_project_task_create(self):
        url = reverse('create-task',args=['testing'])
        self.assertEqual(resolve(url).func.view_class,ProjectTaskCreate)

    def test_edit_components_or_task(self):
        url = reverse('edit-details',args=[1])
        self.assertEqual(resolve(url).func,edit_component_or_task)

    def test_finish_task(self):
        url = reverse('finish-task',args=[1])
        self.assertEqual(resolve(url).func,finish_task_detail)

    def test_delete_task(self):
        url = reverse('delete-task',args=[1])
        self.assertEqual(resolve(url).func,delete_task)

class TestUserProfileInteractions(TestCase):

    def test_user_profile(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func,profile)

    def test_search_user(self):
        url = reverse('search-user')
        self.assertEqual(resolve(url).func,search_user)

    def test_profile_view(self):
        url = reverse('profile-view',args=['test'])
        self.assertEqual(resolve(url).func,profile_view)

    def test_send_friend_request(self):
        url = reverse('send-friend-request',args=['test'])
        self.assertEqual(resolve(url).func,send_friend_request)

    def test_accept_friend_request(self):
        url = reverse('accept-friend-request',args=['test'])
        self.assertEqual(resolve(url).func,accept_friend_request)

    def test_delete_friend_request(self):
        url = reverse('delete-friend-request',args=['test'])
        self.assertEqual(resolve(url).func,delete_friend_request)
