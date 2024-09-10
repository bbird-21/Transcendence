from django import forms
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class NameForm(forms.Form):
    your_name = forms.CharField(label="Your name", max_length=100)
    second_name = forms.CharField(label="Second Name", max_length=100)


class SignupForm(ModelForm):
    class Meta:
        model = User
        fields = ["username", "password"]
        widgets = {
            'password': forms.PasswordInput(),  # Hide password input
        }

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = ''  # Remove help text for username

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
# Hash the password before saving the user
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class SigninForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid login credentials")
        return cleaned_data
