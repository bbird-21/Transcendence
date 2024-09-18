# ---- Shorcuts -------------------------
from django.shortcuts import render
from django.shortcuts import redirect

# ---- Authentication -------------------
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# ---- Forms ----------------------------
from .forms import NameForm
from .forms import SignupForm
from .forms import SigninForm
from .forms import AvatarForm
from .forms import UsernameForm

# ---- Decorators ----------------------
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


# ---- Etc ------------------------------
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView


# ---- <login.html> ---------------------
def login(request):
    if request.method == "POST":
        signin_form = SigninForm(request.POST, prefix="signin")
        signup_form = SignupForm(request.POST, prefix="signup")
        if signin_form.is_valid():
            user = authenticate(username=signin_form.cleaned_data['username'], password=signin_form.cleaned_data['password'])
            if user:
                django_login(request, user)
                return HttpResponseRedirect("/home")
        elif signup_form.is_valid():
            username = signup_form.cleaned_data["username"]
            password = signup_form.cleaned_data["password"]
            # process the data in signup_form.cleaned_data as required
            signup_form.save()
            user = User.objects.get(username=username)
            user.set_password(password)
            user = authenticate(username=username, password=password)
            # A backend authenticated the credentials
            if user is not None:
                django_login(request, user)
                return HttpResponseRedirect("/home/")
    else:
        signin_form = SigninForm(prefix="signin")
        signup_form = SignupForm(prefix="signup")
    return render(request, "core/login.html", {
        "signin_form": signin_form,
        "signup_form": signup_form,
    })

def logout(request):
        django_logout(request)
        return redirect('login')  # If user is not authenticated, redirect to home

# ---- <home.html> ----------------------
@login_required
def home(request):
    user = request.user
    return render(request, "core/home.html", {"user": user})

@login_required
@never_cache
def profile(request):
    avatar_is_valid = True
    if request.method == "POST":
        # This form update the existing UserProfile for the current user, instead of creating a new one
        avatar_form = AvatarForm(request.POST, request.FILES, instance=request.user.userprofile, prefix="avatar")
        username_form = UsernameForm(request.POST, prefix="username", instance=request.user)
        if 'avatar-avatar' in request.FILES and avatar_form.is_valid():
            avatar_form.save()
            return HttpResponseRedirect("/profile/")
        elif username_form.is_valid:
            username_form.save()
            return HttpResponseRedirect("/profile/")
        else:
            avatar_is_valid = False
            print(avatar_form.errors)  # For debugging purposes
    avatar_form = AvatarForm(prefix="avatar")
    username_form = UsernameForm(prefix="username")
    avatar_url = request.user.userprofile.avatar.url
    return render(request, "core/profile.html", {
        "avatar_form": avatar_form,
        "username_form": username_form,
        "avatar": avatar_url,
        "avatar_is_valid": avatar_is_valid,
        "userprofile": request.user.userprofile
    })


# ---- <social.html> ---------------------------
def social(request):
    return render(request, "core/social.html")

# ------------- Test Purpose ---------------

def test(request):
    return render(request, 'core/test.html')
