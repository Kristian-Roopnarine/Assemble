from django.test import TestCase
from assemble.forms import *
from assemble.models import *
from assemble.views import *
from django.contrib.auth.models import User



class UserCreationFormTest(TestCase):

    def test_user_creation_form_valid_data(self):
        form = UserCreationForm(data = {
            'username':'bob',
            'password1':'andwhat13',
            'password2':'andwhat13'
        })

        self.assertTrue(form.is_valid())
    
    def test_user_creation_form_no_data(self):

        form = UserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),3)

    def test_user_creation_form_invalid_password(self):
        form = UserCreationForm(data = {
                'username':'bob',
                'password1':'andwhat13',
                'password2':'andwhat15'
        })
        
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),1)
    

class ComponentEditFormTest(TestCase):
    def setUp(self):
        User.objects.create(username="bob")
        self.bob1 = Profile.objects.get(id=1)
        test_project = Project.objects.create(name='testing',description="testing",owner=self.bob1)
        self.comp1=ProjectComponent.objects.create(name="test",project=test_project)

    def test_edit_form_valid_data_GET_request(self):
        form = ComponentEditForm(instance=self.comp1)
        self.assertEqual(form.instance.name,self.comp1.name)
    
    def test_edit_form_valid_POST_request(self):
        form = ComponentEditForm({'name':'changed'},instance=self.comp1)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEquals(self.comp1.name,'changed')

    # TODO: add test for invalid get request

    # TODO: add test for invalid POST request
