from django import forms
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.files.images import get_image_dimensions
from core.models import UserProfile

# --------------- Login Page ---------------
class NameForm(forms.Form):
    your_name = forms.CharField(label="Your name", max_length=100)
    second_name = forms.CharField(label="Second Name", max_length=100)

# --------------- Sign Up Form ---------------
class SignupForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = ''  # Remove help text for username
        self.fields['username'].label = ""  # Removes the label for username
        self.fields['password'].label = ""  # Removes the label for password

    class Meta:
        model = User
        fields = ["username", "password"]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'username-password-field',  # CSS class
                'placeholder': 'username'            # HTML attribute placeolder
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'username-password-field',   # CSS class
                'placeholder': 'password'             # HTML attribute placeolder
            }),
        }

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        # Hash the password before saving the user
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# --------------- Login Form ---------------
class SigninForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = ""  # Removes the label for username
        self.fields['password'].label = ""  # Removes the label for password
        
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'username-password-field',    # CSS Class
        'placeholder': 'username'              # HTML attribute placeolder 
        }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'username-password-field',    # CSS Class
        'placeholder': 'password'              # HTML attribute placeolder 
        }))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid login credentials")
        return cleaned_data


# --------------- User Management ---------------
class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar"]
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'multiple': False}),  # Single file upload
        }

    # def clean_avatar(self):
    #     avatar = self.cleaned_data['avatar']

    #     try:
    #         w, h = get_image_dimensions(avatar)

    #         #validate dimensions
    #         max_width = max_height = 100
    #         if w > max_width or h > max_height:
    #             raise forms.ValidationError(
    #                 u'Please use an image that is '
    #                  '%s x %s pixels or smaller.' % (max_width, max_height))

    #         #validate content type
    #         main, sub = avatar.content_type.split('/')
    #         if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
    #             raise forms.ValidationError(u'Please use a JPEG, '
    #                 'GIF or PNG image.')

    #         #validate file size
    #         if len(avatar) > (20 * 1024):
    #             raise forms.ValidationError(
    #                 u'Avatar file size may not exceed 20k.')

    #     except AttributeError:
    #         """
    #         Handles case when we are updating the user profile
    #         and do not supply a new avatar
    #         """
    #         pass

    #     return avatar
