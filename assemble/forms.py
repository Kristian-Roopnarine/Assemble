from django.contrib.auth.models import User
from django.contrib.auth import (
    password_validation
)
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext, gettext_lazy as _
from .models import Project,ProjectComponent,Profile,UserFeedback
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Field

class UserCreationForm(forms.ModelForm):
    """
        A form that creates a user, with no privileges, from the given username and password.
    """
    error_messages = {
        'password_mismatch':_("The two passwords fields didn't match.")
    }

    password1 = forms.CharField(
        label = _("Password"),
        strip=False,
        widget = forms.PasswordInput(attrs={'autocomplete':'new-password'}),
    )

    password2 = forms.CharField(
        label = _("Confirm Password"),
        widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}),
        strip=False,
    )


    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username':UsernameField}
    
    

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True
        self.helper = FormHelper()
        self.helper.form_class = 'form-group'
        self.helper.layout = Layout(
            Field('username',css_class='form-control mb-4'),
            Field('password1',css_class='form-control mb-3'),
            Field('password2',css_class='form-control mb-4')
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
        )
        return password2

    def _post_clean(self):
        super()._post_clean()
        #Validate the password after self.instance is updated with form data by super()
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password,self.instance)
            except forms.ValidationError as error:
                self.add_error('password2',error)

    def save(self,commit= True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ProjectCreateForm(forms.ModelForm):
    """
    A form that creates a project from the Project Model.
    
    Arguments:
        forms {[type]} -- [description]
    """
    class Meta:
        model = Project
        fields = ['name','description','user']

    # when creating this class
    def __init__(self,*args,**kwargs):
        # remove the user from key word arguments
        user = kwargs.pop('user')
        # call the init function to get the key word arguments
        super(ProjectCreateForm,self).__init__(*args,**kwargs)
        # get the profile of the user
        is_me = Profile.objects.get(user=user)
        # create a user field with the options of users friends only
        self.fields['user'].queryset = is_me.friends.all()
        self.fields['user'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['user'].help_text = "Add friends to this project."
        
class ProjectEditForm(forms.ModelForm):
    """
    A form that allows a user to edit a project they have a relationship with.
    
    Arguments:
        forms {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    class Meta:
        model = Project
        fields = ['name','description','user']


    def __init__(self,user,*args,**kwargs):
        # call the init function to get the key word arguments
        super(ProjectEditForm,self).__init__(*args,**kwargs)
        # get the profile of the user
        is_me = Profile.objects.get(user=user)
        # create a user field with the options of users friends only
        self.fields['user'].queryset = is_me.friends.all()
        self.fields['user'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['user'].help_text = "Choose the friends you want to add."
      
    """
    def get_form_kwargs(self):
        kwargs = super(ProjectEditForm,self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    """

class ComponentEditForm(forms.ModelForm):
    """
    Allows a user to edit components/tasks of a project.
    
    Arguments:
        forms {[type]} -- [description]
    """
    class Meta:
        model = ProjectComponent
        fields = ['name']

class UserFeedbackCreateForm(forms.ModelForm):
    """
    Allows user to provide feedback on Assemble after signing out.
    
    Arguments:
        forms {[type]} -- [description]
    """
    date_recorded = forms.DateTimeField(widget=forms.SelectDateWidget)
    class Meta:
        model = UserFeedback
        fields = '__all__'


        