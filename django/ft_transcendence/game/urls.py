from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'game'

urlpatterns = [
	path("", views.game, name='game'),
	path("selection", views.selection, name='selection')
]

