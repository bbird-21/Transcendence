from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'game'

urlpatterns = [
	path("game/", views.game, name='game'),
	path("waiting_game/<int:game_invitationID>", views.waiting_game, name='waiting_game'),
	path("invitation/<int:userID>", views.game_invitation, name='game_invitation'),
	path("accept_game/<int:game_invitationID>", views.accept_game, name="accept_game"),
	path("decline_game/<int:game_invitationID>", views.decline_game, name="decline_game"),
	path("test_game/", views.test_game, name='test_game')
]
