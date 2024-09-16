from django.views.generic import TemplateView
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import NameForm
from .forms import SignupForm
from .forms import SigninForm
from .forms import UserProfileForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# --------- <login.html> ---------
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
                # username = signup_form.cleaned_data["username"]
                # password = signup_form.cleaned_data["password"]
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

# --------- <home.html> ---------
@login_required
def home(request):
    user = request.user
    return render(request, "core/home.html", {"user": user})

@login_required
def profile(request):
    if request.method == "POST":
        # This form update the existing UserProfile for the current user, instead of creating a new one
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid:
            form.save()
            return HttpResponseRedirect("/home/")
        else:
            print(form.errors)  # For debugging purposes
            form = UserProfileForm()
    else:
        form = UserProfileForm()
        avatar_url = request.user.userprofile.avatar.url
        print(f"avatar url : {avatar_url}")
    return render(request, "core/profile.html", {
        "form": form,
        "avatar": avatar_url
    })


# ------------- Test Purpose ---------------
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.


def test(request):
    return render(request, 'core/test.html')
