from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'game'

urlpatterns = [
	path("play/", views.play, name='play'),
	path("tournament/", views.tournament, name='tournament'),
	path("waiting_game/<int:game_invitationID>", views.waiting_game, name='waiting_game'),
	path("invitation/<int:userID>", views.game_invitation, name='game_invitation'),
	path("accept_game/<int:game_invitationID>", views.accept_game, name="accept_game"),
	path("decline_game/<int:game_invitationID>", views.decline_game, name="decline_game"),
	path("test_game/", views.test_game, name='test_game'),
	path("selection", views.selection, name='selection'),
	path("invite", views.invite, name='invite'),
	path("add_victory/<uuid:game_uuid>/", views.add_victory, name='add_victory'),
	path("add_defeat/<uuid:game_uuid>/", views.add_defeat, name='add_defeat'),
	path("delete_game/<uuid:game_uuid>/", views.delete_game, name='delete_game')
]

