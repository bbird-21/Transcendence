from django.views.generic import TemplateView
from django.shortcuts import render

def hometest(request):
    return render(request, "core/home-test.html")

class Home(TemplateView):
    template_name = "core/home.html"

def tennis(request):
    return render(request, "core/tennis.html")

# class HomeTest(TemplateView):
    # template_name = 'core/home-test.html'


