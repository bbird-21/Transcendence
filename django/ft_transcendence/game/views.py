from django.urls import reverse
from django.shortcuts import render

def	game(request):
	return render(request, "game/game.html")

def	game_selection(request):
	return render(request, "game/game_selection.html")
