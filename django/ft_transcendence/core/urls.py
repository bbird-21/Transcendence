from django.urls import path

from . import views

urlpatterns = [
	path("", views.hometest, name="hometest"),
]
