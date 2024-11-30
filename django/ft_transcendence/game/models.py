from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
	player_one 			= models.OneToOneField(User, null=True, db_index=True, related_name="player_one", on_delete=models.CASCADE)
	player_two 			= models.OneToOneField(User, null=True, db_index=True, related_name="player_two", on_delete=models.CASCADE)
	player_one_conneted	= models.BooleanField(default=False)
	player_two_conneted	= models.BooleanField(default=False)
	cursor_player_one	= models.IntegerField(default=0)
	score_player_one	= models.IntegerField(default=0)
	cursor_player_two	= models.IntegerField(default=0)
	score_player_one	= models.IntegerField(default=0)
	x_ball_position		= models.IntegerField(default=0)
	y_ball_position		= models.IntegerField(default=0)
	timer				= models.IntegerField(default=0)

class Invitation(models.Model):
	invitation_sender	= models.ForeignKey(User, null=True, db_index=True, related_name="invitation_sender", on_delete=models.CASCADE)
	invitation_receiver	= models.ForeignKey(User, null=True, db_index=True, related_name="invitation_receiver", on_delete=models.CASCADE)
