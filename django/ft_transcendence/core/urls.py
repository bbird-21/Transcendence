from django.urls import path

from . import views

urlpatterns = [
	path("", views.hometest, name="hometest"),
	path("home/", views.Home.as_view(), name="home"),
	path("tennis/", views.tennis, name="tennis"),
]
