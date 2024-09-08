from django.urls import path
from . import views

urlpatterns = [
	path("", views.login, name="login"),
	path("home/", views.Home.as_view(), name="home"),
	path("logout/", views.logout, name="logout"),
	path("test/", views.test, name="test"),
]
