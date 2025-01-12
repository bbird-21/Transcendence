from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from game.models import Game, Invitation
from django.urls import reverse
from core.models import Notification
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

@login_required
def	play(request):
	try:
		game = Game.objects.create(player_one=request.user)
	except:
		return redirect(reverse('core:home'))
	context = {
		"game_uuid": game.uuid
	}

	return render(request, "game/play.html", context)

@login_required
def	tournament(request):
	return render(request, "game/tournament.html")

@login_required
def	waiting_game(request, game_invitationID):
	try :
		game_invitation = Invitation.objects.get(id=game_invitationID)
		if ( game_invitation.invitation_receiver != request.user and game_invitation.invitation_sender != request.user ):
			raise Exception(f'No Game Invitation exists for {request.user}')
	except Exception as e:
		print(e)
		request.session["message_to_user"] = f"No Game Invitation exists for {request.user}"
		return redirect('core:home')

	context = {
		"game_id": game_invitationID,
		"player_one": game_invitation.invitation_sender,
		"player_two": game_invitation.invitation_receiver,
		"player": "player_one" if request.user == game_invitation.invitation_sender else "player_two",
	}
	return render(request, "game/waiting_game.html", context)

@login_required
def	game_invitation(request, userID):
	try:
		receiver			= User.objects.get(id=userID)
		game_invitation, created	= Invitation.objects.get_or_create(
			invitation_sender=request.user,
			invitation_receiver=receiver
		)
		Notification.objects.get_or_create(
			receiver=receiver,
			game_invitation=game_invitation
		)
	except User.DoesNotExist as e:
		request.session['notification'] = "User Does Not Exists"
		return redirect(reverse('core:social'))
	except Exception as e:
		print(e)
		return render(request, "core/500.html", {"exception": e})

	request.session['notification'] = "Invitation has been sent !"
	return redirect("game:waiting_game", game_invitationID=game_invitation.id)

def	test_game(request, userID):
	return render(request, "game/test_game.html")

@login_required
def	accept_game(request, game_invitationID):
	try:
		notification	= Notification.objects.get(game_invitation=game_invitationID)
		notification.delete()
	except Exception as e:
		print(e)
		return render(request, "core/500.html", { 'exception': e })

	return redirect("game:waiting_game", game_invitationID=game_invitationID)

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

@login_required
def	selection(request):
	return render(request, "game/selection.html")

@login_required
def invite(request):
	friend_list = request.user.userprofile.friends.all()
	context = {
		'friend_list': friend_list,
	}
	return render(request, 'game/invite.html', context)

@login_required
@csrf_exempt
def	add_victory(request, game_uuid):
	try:
		game = Game.objects.get(uuid=game_uuid)
		request.user.userprofile.victory+=1
		request.user.userprofile.save()
	except:
		request.session['message_to_user'] = "Game Does not Exist. Impossible to add a victory point"
		return redirect(reverse('core:home'))
	return HttpResponse("Victory Point Added", status=200)

@login_required
@csrf_exempt
def	add_defeat(request, game_uuid):
	try:
		game = Game.objects.get(uuid=game_uuid)
		request.user.userprofile.defeat+=1
		request.user.userprofile.save()
	except:
		request.session['message_to_user'] = "Game Does not Exist. Impossible to add a defeat point"
		return redirect(reverse('core:home'))
	return HttpResponse("Defeat Point Added", status=200)

@login_required
@csrf_exempt
def	delete_game(request, game_uuid):
	try:
		game = Game.objects.get(uuid=game_uuid)
		game.delete()
		game.save()
	except:
		request.session['message_to_user'] = "Game Does not Exist. Impossible to delete Game Session."
		return redirect(reverse('core:home'))
	return HttpResponse("Game Deleted", status=200)
