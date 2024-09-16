from django.urls import path
from . import views

urlpatterns = [
	path("", views.login, name="login"),
	path("logout/", views.logout, name="logout"),
	path("home/", views.home, name="home"),
	path("profile/", views.profile, name="profile"),
	path("test/", views.test, name="test"),
]
