from django.views.generic import TemplateView
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import logout as django_logout


def login(request):
    return render(request, "core/login.html")

class Home(TemplateView):
    template_name = "core/home.html"

def test(request):
    return render(request, "core/test.html")

def logout(request):
        django_logout(request)
        return redirect('login')  # If user is not authenticated, redirect to home
