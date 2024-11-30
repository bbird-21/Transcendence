from django.urls import reverse
from django.shortcuts import render, redirect
from game.models import Game, Invitation
from django.urls import reverse
from core.models import Notification
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required
def	game(request):
	return render(request, "game/game.html")

@login_required
def	waiting_game(request):
	try :
		game = Game.objects.filter(Q(player_one=request.user) | Q(player_two=request.user)).first()

	except Exception as e:
		print(e)
		return render(request, "core/500.html", { "exception": e })

	context = {
		"game_id": game.id,
		"player_one": game.player_one,
		"player_two": game.player_two
	}
	return render(request, "game/waiting_game.html", context)

@login_required
def	game_invitation(request, userID):
	try:
		receiver			= User.objects.get(id=userID)
		invitation, created	= Invitation.objects.get_or_create(
			invitation_sender=request.user,
			invitation_receiver=receiver
		)
		Notification.objects.get_or_create(
			receiver=receiver,
			game_invitation=invitation
		)
	except User.DoesNotExist as e:
		request.session['notification'] = "User Does Not Exists"
		return redirect(reverse('core:social'))
	except Exception as e:
		print(e)
		return render(request, "core/500.html", {"exception": e})

	request.session['notification'] = "Invitation has been sent !"
	return redirect(reverse('game:waiting_game'))

def	test_game(request, userID):
	return render(request, "game/test_game.html")

@login_required
def	accept_game(request, game_invitationID):
	try:
		game_invitation	= Invitation.objects.get(id=game_invitationID)
		player_one		= game_invitation.invitation_sender
		player_two		= game_invitation.invitation_receiver
		# notification	= Notification.objects.get(game_invitation=game_invitation)
		game = Game.objects.get_or_create(
			player_one=player_one,
			player_two=player_two
		)
		print(f"GAME : {game}")
		game_invitation.delete()
		# notification.delete()
	except Exception as e:
		print(e)
		return render(request, "core/500.html", { 'exception': e })

	return redirect(reverse('game:waiting_game'))

@login_required
def	decline_game(request, game_invitationID):
	try:
		game_invitation	= Invitation.objects.get(id=game_invitationID)
		game_invitation.delete()
	except Exception as e:
		print(e)
		return render(request, "core/500.html", { "exception": e })

	request.session['message_to_user'] = "You have declined the Game Request"
	return redirect(reverse('core:notifications'))
