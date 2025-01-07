from django import forms
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.files.images import get_image_dimensions
from core.models import UserProfile
from allauth.mfa.adapter import DefaultMFAAdapter
from allauth.mfa import totp
from allauth.mfa.models import Authenticator

from allauth.account.forms import LoginForm

# forms.py
from allauth.account.forms import LoginForm
from django import forms

class CustomLoginForm(LoginForm):
    # Modify the label for username field
    username = forms.CharField(
        label="Your Custom Username",  # Custom label for username
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your username',
            'class': 'form-control custom-class'
        })
    )

    # Modify the label for password field
    password = forms.CharField(
        label="Your Custom Password",  # Custom label for password
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control custom-class'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # You can modify the error messages or any additional field attributes here
        self.fields['username'].help_text = 'Your username should be unique.'
        self.fields['password'].help_text = 'Your password must be at least 8 characters long.'

    def login(self, *args, **kwargs):

        # Add your own processing here.

        # You must return the original result.
        return super(CustomLoginForm, self).login(*args, **kwargs)

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
            adapter = DefaultMFAAdapter()
        return cleaned_data


# --------------- MFAForm -----------------------
class MFAForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(MFAForm, self).__init__(*args, **kwargs)


    mfa_code = forms.CharField(
        required=True,  # Not required unless MFA is enabled
        label="",
        widget=forms.TextInput(attrs={
            'class': 'username-password-field invalid_credentials',  # CSS Class
            'placeholder': 'Enter MFA Code'  # HTML attribute placeholder
        })
    )

    def clean_mfa_code(self):
        cleaned_data = super().clean()
        mfa_code = cleaned_data.get('mfa_code')

        print("called clean")
        if not mfa_code:
            raise forms.ValidationError("MFA code is required for login.")
        else:
            totp_instance = Authenticator.objects.get(user=self.user, type=Authenticator.Type.TOTP)
            secret = DefaultMFAAdapter().decrypt(totp_instance.data["secret"])
            if not totp.validate_totp_code(secret, mfa_code):
                print("NOT VALID TOTP CODE")
                raise forms.ValidationError("Invalid MFA code. Please try again.")
        return cleaned_data

# --------------- User Management ---------------
class AvatarForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar"]
        labels = {
            'avatar': '',  # Remove the default "avatar" label
        }
        widgets = {
            'avatar': forms.ClearableFileInput(
                attrs={
                    'class': 'avataar',  # Custom class
                    'id': 'file-upload',  # Link to the label
                }
            ),
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
                'class': 'change-username-password-field',  # CSS class
                'placeholder': 'Change Username'            # HTML attribute placeolder
            })
        }

class SearchUser(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SearchUser, self).__init__(*args, **kwargs)
        self.fields['username'].label = ""  # Removes the label for username

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'social--search-username-field buttons-design',    # CSS Class
        'placeholder': 'Search User'           # HTML attribute placeolder
        }))
