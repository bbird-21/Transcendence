from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path("", views.index, name="index"),
    path("message/<int:userID>", views.room, name="room"),
    path("direct_message/", views.direct_message, name='direct_message')
]
