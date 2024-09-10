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
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
# Create User
def login(request):
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                django_login(request, user)
                return HttpResponseRedirect("/home")
    else:
        form = SigninForm()
    return render(request, "core/login.html", {"form": form})

def home(request):
    user = request.user
    return render(request, "core/home.html", {"user": user})

def logout(request):
        django_logout(request)
        return redirect('login')  # If user is not authenticated, redirect to home

def signup(request):
    return render(request, "core/signup.html")


def test(request):
    return render(request, "core/test.html")

# Log in user
def signup(request):
    print("SIGNUP")
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = SignupForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            # process the data in form.cleaned_data as required
            print(f"form : {form}")
            form.save()
            user = User.objects.get(username=username)
            print(f"USER : {user}")
            user.set_password(password)
            user = authenticate(username=username, password=password)
            print(f"username  : {username}")
            print(f"password  : {password}")
            # A backend authenticated the credentials
            if user is not None:
                django_login(request, user)
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                # print(f"username  : {username}")
                # print(f"password  : {password}")
            # No backend authenticated the credentials
            else:
                print("")

            # redirect to a new URL:
            return HttpResponseRedirect("/home/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignupForm()
    return render(request, "core/login.html", {"form": form})
