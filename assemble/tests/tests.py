from django.test import TestCase
from django.contrib.auth.models import User
from assemble.models import *
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import datetime as dt

# Create your tests here.
class UserProfileTestCase(TestCase):

    def setUp(self):
        User.objects.create(username="Bob")
        User.objects.create(username="test")

    def test_user_queryset(self):
        """
        Tests whether we can retrieve user objects from their username.
        """
        bob_name = User.objects.get(username="Bob")
        test_name_ = User.objects.get(username="test")
        self.assertEqual(bob_name.username,"Bob")
        self.assertEqual(test_name_.username,"test")
    
    def test_profile_signal(self):
        """
        Test whether the profile signals work to create a profile when a new user is created.
        """

        bob_profile = Profile.objects.get(user__username="Bob")
        test_profile = Profile.objects.get(user__username="test")
        self.assertEqual(bob_profile.user.username,"Bob")
        self.assertEqual(test_profile.user.username,"test")

    def test_creating_same_user_error(self):
        """
        Test to ensure that User,Profiles and usernames are unique.
        """
        self.assertRaises(IntegrityError, User.objects.create ,username="Bob")
    

class ProjectTestCase(TestCase):

    def setUp(self):
        User.objects.create(username="bob")
        User.objects.create(username="test")
        User.objects.create(username="bob1")
        User.objects.create(username="bob2")
        User.objects.create(username="bob3")
        bob = Profile.objects.get(user__username="bob")
        test = Profile.objects.get(user__username="test")
        bob1 = Profile.objects.get(user__username="bob1")
        bob2 = Profile.objects.get(user__username="bob2")

        test_project = Project.objects.create(name="test1",owner=bob)
        test_project.user.set([bob,test,bob1,bob2])
    
    def test_project_queryset_by_user_object(self):
        """
        Testing querying a project based on a user profile.
        """
        bob = Profile.objects.get(user__username="bob")
        test = Project.objects.get(user=bob)
        self.assertEqual(test.name,"test1")
    
    def test_check_if_profile_is_owner(self):
        """
        Testing whether we can identify the owner of a project.
        """
        bob = Profile.objects.get(user__username="bob")
        test_project = Project.objects.get(id=1)
        self.assertEqual(test_project.owner,bob)

    def test_check_if_profile_not_owner(self):
        """
        Testing if we can tell if a profile is not an owner.
        """
        bob2 = Profile.objects.get(user__username="bob2")
        test_project=Project.objects.get(id=1)
        self.assertFalse(test_project.owner == bob2)
    
    def test_if_can_query_users_from_project(self):
        """
        Testing whether the query returns all users.
        """
        test_project=Project.objects.get(id=1)
        users=len(test_project.user.all())
        self.assertEqual(users,4)
    
    def test_profile_project_relationship(self):
        """
        Testing the relationship between Profile and Projects.
        """
        bob= Profile.objects.get(user__username="bob"
        )
        bob_project = bob.project_set.all()
        self.assertEqual(len(bob_project),1)
    
    def test_users_not_in_project(self):
        """
        Testing whether a user is in a project.
        """
        bob3 = Profile.objects.get(user__username="bob3")
        test_project=Project.objects.get(id=1)
        users = test_project.user.all()
        self.assertFalse(bob3 in users)

    def test_error_when_querying_project_user_not_in(self):
        """
        Testing the ObjectDoesNotExist exception raised when a user tries to query a project they're not in.
        """
        try:
            bob3 = Profile.objects.get(user__username="bob3")
            test_project = Project.objects.filter(user=bob3).get(slug="test_project")
        except ObjectDoesNotExist:
            pass


class ProjectHistoryTestCase(TestCase):

    def setUp(self):
        # need to create profile
        User.objects.create(username="bob")
        User.objects.create(username="bob1")
        bob,bob1 = Profile.objects.get(user__username="bob"),Profile.objects.get(user__username="bob1")
        # need to create project
        test_project = Project.objects.create(name="test1",owner=bob)
        test_project.user.set([bob,bob1])
        # create project component

        #id=1
        #project history id=1 for this instance created
        comp1=ProjectComponent.objects.create(name="test component",project=test_project)

        #id=2
        #project history id=2 for this instance created
        ProjectComponent.objects.create(name="test task",task=comp1,project=test_project)

        # test the post_save method to see if it saves when the project component is created

    
    def test_creating_project_component_and_project_history(self):
        """Test whether creating project components adds a projecthistory instance."""
        test = ProjectHistory.objects.get(id=1)
        self.assertEqual(test.after,"test component")

    def test_deleting_project_component_adds_project_history(self):
        """Test whether deleting project components adds a projecthistory instance."""
        test = ProjectComponent.objects.get(id=1)
        test.delete()
        test_history = ProjectHistory.objects.get(id=3)
        self.assertEqual(test_history.before,"test component")
        self.assertEqual(test_history.after,"deleted")
    
    def test_editing_project_component_adds_project_history(self):
        """Test whether editing project components adds a projecthistory instance."""
        test = ProjectComponent.objects.get(id=1)
        test.name = 'test'
        # force call the save method to trigger the signal
        test.save()
        #id=1 is the component that was created
        #id=2 is the edited component
        # it works!
        self.assertEqual(ProjectHistory.objects.get(id=1).after,'test component')
        self.assertEqual(ProjectHistory.objects.get(id=3).before,'test component')
        self.assertEqual(ProjectHistory.objects.get(id=3).after,'test')
    
    def test_multiple_edits_on_project_component(self):
        """ Testing whether projecthistory instances are created for multiple edits on project components."""
        # id = 1 is component
        test = ProjectComponent.objects.get(id=1)
        test.name="first change"
        test.save()
        first_history = ProjectHistory.objects.get(id=3)
        self.assertEqual(first_history.before,'test component')
        self.assertEqual(first_history.after,"first change")
        test.name="second change"
        test.save()
        second_history = ProjectHistory.objects.get(id=4)
        history_length = ProjectHistory.objects.all().count()
        self.assertEqual(second_history.before,'first change')
        self.assertEqual(second_history.after,"second change")
        self.assertEqual(history_length,4)

    def test_creating_tasks_for_components(self):
        test = ProjectComponent.objects.get(id=2)
        self.assertEqual(test.name,"test task")
    
    def test_editing_tasks_for_components(self):
        test = ProjectComponent.objects.get(id=2)
        test.name="first change"
        test.save()
        test_history=ProjectHistory.objects.get(id=3)
        total_history = ProjectHistory.objects.all().count()
        self.assertEqual(test_history.before,"test task")
        self.assertEqual(test_history.after,"first change")
        self.assertEqual(total_history,3)

    def test_history_string_method_when_creating(self):
        test1 = ProjectHistory.objects.get(id=1)
        test2 = ProjectHistory.objects.get(id=2)
        self.assertEqual(test1.list_string,"test component was created.")
        self.assertEqual(test2.list_string,"test task was created.")
    
    def test_history_string_method_when_editing(self):
        test1 = ProjectComponent.objects.get(id=1)
        test1.name = "changing"
        test1.save()
        test_history = ProjectHistory.objects.get(id=3)
        self.assertEqual(test1.name,"changing")
        self.assertEqual(test_history.before,"test component")
        self.assertEqual(test_history.after,"changing")
        self.assertEqual(test_history.list_string,"test component was edited to changing.")
    
    def test_history_string_method_when_deleting(self):
        test1 = ProjectComponent.objects.get(id=2)
        test1.delete()
        test_history = ProjectHistory.objects.get(id=3)
        self.assertEqual(test_history.before,"test task")
        self.assertEqual(test_history.after,"deleted")
        self.assertEqual(test_history.list_string,"test task was deleted.")