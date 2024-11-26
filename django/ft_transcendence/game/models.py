from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
	player_one 			= models.ForeignKey(User, db_index=True, related_name="player_one", on_delete=models.SET_NULL, null=True)
	cursor_player_one	= models.IntegerField()
	score_player_one	= models.IntegerField()
	player_two 			= models.ForeignKey(User, db_index=True, related_name="player_two", on_delete=models.SET_NULL, null=True)
	cursor_player_two	= models.IntegerField()
	score_player_one	= models.IntegerField()
	x_ball_position		= models.IntegerField()
	y_ball_position		= models.IntegerField()
	timer				= models.IntegerField()



