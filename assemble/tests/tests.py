from django.test import TestCase
from django.contrib.auth.models import User
from assemble.models import *
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

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

