from django.contrib.auth.models import User
from django.contrib.auth import (
    password_validation
)
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext, gettext_lazy as _
from .models import Project,ProjectComponent
from django import forms

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
