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
        self.fields['username'].max_length = 10
        self.fields['username'].widget.attrs.update({'maxlength': '10'})
        self.fields['password'].label = ""  # Removes the label for password
        self.fields['password2'].label = ""  # Removes the label for password

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password',
        'class': 'username-password-field'
        }),
    )

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

    def cmp_passwords(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        cleaned_data['signup_invalid_credentials'] = False
        self.cmp_passwords()
        if len(password) < 6:
            raise forms.ValidationError("The password must contains at least 6 characters")
        return cleaned_data


# --------------- Login Form ---------------
class SigninForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)

    username = forms.CharField(
        label="",  # Removes the label for username
        widget=forms.TextInput(attrs={
        'class': 'username-password-field invalid_credentials',    # CSS Class
        'placeholder': 'username'              # HTML attribute placeolder
        }))
    password = forms.CharField(
        label="",  # Removes the label for username
        widget=forms.PasswordInput(attrs={
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
                raise forms.ValidationError("Incorrect Username or Password")
        return cleaned_data


# --------------- User Management ---------------
class AvatarForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar"]
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'multiple': False}),  # Single file upload
        }

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        w, h = get_image_dimensions(avatar)
        # validate dimensions
        print(f"content type : {avatar.content_type}")
        max_width = max_height = 100
        if w < max_width or h < max_height:
            raise forms.ValidationError(
                u'Please use an image that is at minumum'
                    '%s x %s pixels.' % (max_width, max_height))
        #validate content type
        main, sub = avatar.content_type.split('/')
        if not (main == 'image' and sub in ['jpeg', 'jpg', 'png']):
            raise forms.ValidationError(u'Please use a JPEG, '
                'JPG or PNG image.')
        # validate file size
        if len(avatar) > (1000 * 1024):
            raise forms.ValidationError(
                u'Avatar file size may not exceed 1Mo.')
        return avatar


class UsernameForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(UsernameForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = ''  # Remove help text for username
        self.fields['username'].label = ""  # Removes the label for username
        self.fields['username'].max_length = 10
        self.fields['username'].widget.attrs.update({'maxlength': '10'})

    class Meta:
        model = User
        fields = ["username"]

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'username-password-field',  # CSS class
                'placeholder': 'username'            # HTML attribute placeolder
            })
        }

class SearchUser(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SearchUser, self).__init__(*args, **kwargs)
        self.fields['username'].label = ""  # Removes the label for username

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'social--search-username-field',    # CSS Class
        'placeholder': 'Search User'           # HTML attribute placeolder
        }))
