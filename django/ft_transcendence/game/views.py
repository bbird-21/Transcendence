from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def	game(request):
	return render(request, "game/game.html")

@login_required
def	selection(request):
	return render(request, "game/selection.html")
