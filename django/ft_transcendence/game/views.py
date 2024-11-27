from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def	game(request):
	return render(request, "game/game.html")

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