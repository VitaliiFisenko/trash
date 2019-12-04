from django import forms
from django.contrib.auth.forms import UsernameField, AuthenticationForm


class UserLoginForm(AuthenticationForm):
    """
    changing label of username field while authorization
    """
    username = UsernameField(label='Username/Email', widget=forms.TextInput(attrs={'autofocus': True}))