from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.http import HttpResponseRedirect
from .forms import SignupForm, SigninForm
from django.shortcuts import render

def create_user(request, signup_form):
	username = signup_form.cleaned_data["username"]
	password = signup_form.cleaned_data["password"]
	signup_form.save()
	user = User.objects.get(username=username)
	user.set_password(password)
	user = authenticate(username=username, password=password)

	return user

def login_page(request):
	signin_form = SigninForm(prefix="signin")
	signup_form = SignupForm(prefix="signup")
	return render(request, "core/login.html", {
		"signin_form": signin_form,
		"signup_form": signup_form,
	})


def sign_in_strategy(request):
	signin_form = SigninForm(request.POST, prefix="signin")
	if signin_form.is_valid():
		user = authenticate(username=signin_form.cleaned_data['username'], password=signin_form.cleaned_data['password'])
		if user:
			django_login(request, user)
			return HttpResponseRedirect("/home/")
		else:
			return render(request, "core/500.html")
	else:
		return render(request, "core/login.html", {
			"signin_invalid_credentials": True,
			"signin_form": signin_form
		})

def	sign_up_strategy(request):
	signup_form = SignupForm(request.POST, prefix="signup")
	if signup_form.is_valid():
		user = create_user(request, signup_form)
		if user is not None:
			django_login(request, user)
			return HttpResponseRedirect("/home/")
		else:
			return render(request, "core/500.html")
	else:
		return render(request, "core/login.html", {
			"signup_invalid_credentials": True,
			"signup_form": signup_form
		})
