from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path("send_direct_message/<int:userID>/", views.send_direct_message, name='send_direct_message')
]
