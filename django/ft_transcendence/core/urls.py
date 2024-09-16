from django.urls import path
from . import views

urlpatterns = [
	path("", views.login, name="login"),
	path("home/", views.home, name="home"),
	path("logout/", views.logout, name="logout"),
	path("signup/", views.signup, name="signup"),
	path("profile/", views.profile, name="profile"),
	path("avatar/", views.avatar, name="avatar"),
	# path("form/", views.home, name="loginform"),
	path("test/", views.test, name="test"),
]
