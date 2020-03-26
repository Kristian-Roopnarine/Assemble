from django.test import TestCase,Client,RequestFactory
from assemble.views import *
from django.urls import reverse,resolve
from assemble.models import *
import json
from django.core.exceptions import ObjectDoesNotExist

class TestUserAuthenticationViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.index_url = reverse('home')
        self.sign_up_url = reverse('sign-up')


    def test_index_view_GET(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'assemble/index.html')

    def test_sign_up_GET(self):
        response = self.client.get(self.sign_up_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'registration/sign_up.html')

    def test_sign_up_POST_creates_user(self):
        response = self.client.post(self.sign_up_url,{
            'username':'bob1',
            'password1':'andwhat13',
            'password2':'andwhat13',
        })
        self.assertEquals(response.status_code,302)
        user_count = User.objects.all()
        self.assertEquals(user_count.count(),1)

    def test_sign_up_POST_no_data(self):
        response = self.client.post(self.sign_up_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'registration/sign_up.html')
        user_count = User.objects.all().count()
        self.assertEquals(user_count,0)

class TestProjectViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        User.objects.create(username="bob")
        self.bob = Profile.objects.get(id=1)
        User.objects.create(username="bob2")
        self.bob2 = Profile.objects.get(id=2)

        self.test_project = Project.objects.create(
            name="test project",
            description="this is for testing",
            owner=self.bob,
        )
        self.test_project.user.add(self.bob)
        self.test_project2 = Project.objects.create(
            name="test project 2",
            description="this is for testing",
            owner=self.bob2,
        )
        self.test_project2.user.add(self.bob2)

        ProjectComponent.objects.create(
            name="test component",
            project=self.test_project,
            task=None,
        )

        self.project_list_url = reverse('project-list')
        self.project_create_view_url = reverse('project-create')
        self.project_detail_url = reverse('project-detail',args=[self.test_project.slug])
        self.project_delete_url = reverse('delete-project',args=[1])
        self.project_history_url = reverse('project-history',args=[1])

    def test_project_list_GET(self):
        # should display the projects the user is part of
        request = self.factory.get(self.project_list_url)
        request.user = self.bob.user
        response = ProjectList.as_view()(request)
        # class based views redirect?
        self.assertEqual(response.status_code,200)
        #self.assertTemplateUsed(response,'assemble/project_list.html')

    def test_project_list_get_queryset(self):
        request = self.factory.get(self.project_list_url)
        request.user = self.bob.user
        view = ProjectList()
        view.setup(request)
        queryset = view.get_queryset()
        total_queryset = Project.objects.all().count()
        self.assertEquals(len(queryset),1)
        self.assertEqual(total_queryset,2)

    def test_project_create_view_GET(self):
        request = self.factory.get(self.project_create_view_url)
        request.user = self.bob.user
        response = ProjectCreate.as_view()(request)
        self.assertEqual(response.status_code,200)

    def test_project_create_view_POST_valid_data(self):
        request = self.factory.post(self.project_create_view_url,{
            'name':'test project 3',
            'description':'adding another',
        })
        request.user = self.bob.user
        response = ProjectCreate.as_view()(request)
        self.assertEqual(response.status_code,302)
        self.assertEqual(response.url,'/home/project-list/')
        third_project = Project.objects.get(id=3)
        self.assertEqual(third_project.name,"test project 3")

    def test_project_create_view_POST_invalid_data(self):
        request = self.factory.post(self.project_create_view_url,{})
        request.user = self.bob.user
        response = ProjectCreate.as_view()(request)
        self.assertEqual(response.status_code,200)
        total_projects = Project.objects.all().count()
        self.assertEqual(total_projects,2)

    def test_project_create_POST_user_owner(self):
        request = self.factory.post(self.project_create_view_url,{
            'name':'testing user and owner',
            'description':'yayayaya',
        })
        request.user = self.bob.user
        response = ProjectCreate.as_view()(request)
        self.assertEqual(response.status_code,302)
        self.assertEqual(response.url,'/home/project-list/')
        total_projects=Project.objects.all().count()
        third_project = Project.objects.get(id=3)
        self.assertEquals(total_projects,3)
        self.assertEquals(third_project.name,"testing user and owner")
        self.assertEquals(third_project.owner,self.bob)
        self.assertIn(self.bob,third_project.user.all())
        self.assertNotIn(self.bob2,third_project.user.all())

    def test_project_detail_view_GET_user_in_project(self):
        request = self.factory.get(self.project_detail_url)
        request.user = self.bob.user
        response = project_detail_view(request,self.test_project.slug)

        self.assertEqual(response.status_code,200)

    def test_project_detail_view_GET_user_not_in_project(self):
        request = self.factory.get(self.project_detail_url)
        request.user = self.bob2.user
        try:
            response = project_detail_view(request,self.test_project.slug)
        except ObjectDoesNotExist:
            self.assertRaises(ObjectDoesNotExist)

    def test_delete_project_GET(self):
        request = self.factory.get(self.project_delete_url)
        request.user = self.bob.user
        response = delete_project(request,1)
        self.assertEqual(response.status_code,200)


    def test_delete_project_POST(self):
        request = self.factory.post(self.project_delete_url)
        request.user = self.bob.user
        response = delete_project(request,1)
        total_project = Project.objects.all().count()
        self.assertEqual(response.status_code,302)
        self.assertEqual(response.url,'/home/project-list/')
        self.assertEquals(total_project,1)

    def test_history_view(self):
        request = self.factory.get(self.project_history_url)
        request.user = self.bob.user
        response = history_view(request,1)
        self.assertEquals(response.status_code,200)


class TestProjectComponentTaskViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        User.objects.create(username="bob")
        self.bob = Profile.objects.get(id=1)
        User.objects.create(username="bob2")
        self.bob2 = Profile.objects.get(id=2)

        self.test_project = Project.objects.create(
            name="test project",
            description="this is for testing",
            owner=self.bob,
        )
        self.test_project.user.add(self.bob)
        self.test_project2 = Project.objects.create(
            name="test project 2",
            description="this is for testing",
            owner=self.bob2,
        )

        self.component = ProjectComponent.objects.create(
            name="test component",
            project=self.test_project,
            task=None,
        )

        self.test_project2.user.add(self.bob2)
        self.project_component_create_url = reverse('project-component-create', kwargs = {'project_slug':self.test_project.slug})
        self.project_component_delete_url = reverse('delete-task',args=[1])
        self.project_task_finish_url = reverse('finish-task',kwargs={'pk':1})
        self.component_edit_url = reverse('edit-details',kwargs={'pk':1})

    def test_project_delete_component_POST(self):
        request = self.factory.post(self.project_component_delete_url)
        request.user = self.bob.user
        response = delete_task(request,1)
        self.assertEquals(response.status_code,302)
        project_components = ProjectComponent.objects.all().count()
        self.assertEquals(project_components,0)

    def test_finish_task_view(self):
        request = self.factory.get(self.project_task_finish_url)
        request.user = self.bob.user
        response = finish_task_detail(request,1)
        self.assertEquals(response.status_code,302)
        component = ProjectComponent.objects.get(id=1)
        self.assertEquals(component.completed,True)

    def test_edit_component_GET(self):
        request = self.factory.get(self.component_edit_url)
        request.user = self.bob.user
        response = edit_component_or_task(request,1)
        self.assertEqual(response.status_code,200)
        form = ComponentEditForm(instance=self.test_project)
        self.assertEqual(form.instance.name,self.test_project.name)

    def test_edit_component_POST(self):
        request = self.factory.post(self.component_edit_url,{
            'name':'this name was changed'
        })
        request.user = self.bob.user
        response = edit_component_or_task(request,1)
        self.assertEqual(response.status_code,302)
        edited_component = ProjectComponent.objects.get(id=1)
        self.assertEqual(edited_component.name,'this name was changed')
        total_components = ProjectComponent.objects.all().count()
        self.assertEqual(total_components,1)

class TestUserInteractionViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        User.objects.create(username="bob")
        self.bob = Profile.objects.get(id=1)
        User.objects.create(username="bob2")
        self.bob2 = Profile.objects.get(id=2)

        self.profile_url = reverse('profile')
        self.profile_view_url = reverse('profile-view',args=[self.bob2.slug])
        self.search_user_url = reverse('search-user')
        self.send_friend_request_url = reverse('send-friend-request',args=[self.bob2.slug])
        self.accept_friend_request_url = reverse('accept-friend-request',args=[self.bob.slug])
        self.delete_friend_request_url = reverse('delete-friend-request',args=[1])

    def test_self_profile_(self):
        request = self.factory.get(self.profile_url)
        request.user = self.bob.user
        response = profile(request)
        self.assertEqual(response.status_code,200)

    def test_profile_view(self):
        request = self.factory.get(self.profile_view_url)
        request.user = self.bob.user
        response = profile_view(request,self.bob2.slug)
        self.assertEqual(response.status_code,200)
    """
    def test_search_user_GET(self):
        request = self.factory.get(self.search_user_url)
        request.user = self.bob.user
        response = search_user(request)
        self.assertEqual(response.status_code,200)
    """
    def test_search_user_POST_valid_data(self):
        request = self.factory.post(self.search_user_url,{
            'username':'bob2',
        })
        request.user = self.bob.user
        response = search_user(request)
        self.assertEqual(response.status_code,200)

    def test_send_friend_request(self):
        request = self.factory.get(self.send_friend_request_url)
        request.user = self.bob.user
        response = send_friend_request(request,self.bob2.slug)
        self.assertEqual(response.status_code,302)
        fr = FriendRequest.objects.all().count()
        self.assertEqual(fr,1)

    def test_accept_and_delete_friend_request(self):
        request = self.factory.get(self.send_friend_request_url)
        request.user=self.bob.user
        response = send_friend_request(request,self.bob2.slug)

        request = self.factory.get(self.accept_friend_request_url)
        request.user=self.bob2.user
        accept_response = accept_friend_request(request,self.bob.slug)
        self.assertEqual(accept_response.status_code,302)

        bob1 = Profile.objects.get(id=1)
        bob2 = Profile.objects.get(id=2)
        self.assertIn(bob2,bob1.friends.all())
        self.assertIn(bob1,bob2.friends.all())

        request = self.factory.get(self.delete_friend_request_url)
        request.user = self.bob2.user
        response = delete_friend_request(request,1)
        self.assertEqual(response.status_code,302)
        fr = FriendRequest.objects.all().count()
        self.assertEqual(fr,0)


    # TODO: add tests for projecthistory!
